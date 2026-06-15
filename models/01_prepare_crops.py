# -*- coding: utf-8 -*-
# =============================================================================
# 01_prepare_crops.py  —  병변 bbox 크롭 데이터셋 생성 (1회 실행, CPU/IO 작업)
# 목적: 전체 사진 대신 'JSON 라벨의 병변 박스 영역만 잘라낸' 학습 이미지를 만든다.
#       (배경·털 노이즈 제거 → 공식 베이스라인 81%에 가까워지는 핵심 단계)
# 입력: data/processed/dataset_local.csv  (abs_path=원본 jpg 절대경로, lesion, split, img_file)
# 출력: data/crops/<split>/<lesion>/<파일명>.jpg   (224x224 크롭본)
# 실행: python models/01_prepare_crops.py   (이 PC에서, GPU 불필요)
# =============================================================================
import os, json, sys, io                                  # 파일·JSON·표준출력 처리
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # 한글 출력 깨짐 방지
import pandas as pd                                        # CSV 로딩
from PIL import Image                                      # 이미지 열기/크롭/리사이즈
from concurrent.futures import ThreadPoolExecutor          # 멀티스레드로 I/O 가속

PROJ  = r"C:\Users\금정산2-PC02\SAG_project"               # 프로젝트 루트
CSV   = os.path.join(PROJ, "data", "processed", "dataset_local.csv")  # 매핑된 CSV
OUT   = os.path.join(PROJ, "data", "crops")               # 크롭 결과 저장 루트
IMG_SIZE = (224, 224)                                      # 저장 크기(백본 입력과 동일)
MARGIN   = 0.20                                            # 박스 주변 20% 여유(맥락 포함)

df = pd.read_csv(CSV)                                      # 34,987행 로드
print(f"대상 이미지: {len(df):,}장")                       # 진행 로그

# 저장 폴더 미리 생성: crops/<split>/<lesion>/
for split in df['split'].unique():                        # train/val/test
    for lesion in sorted(df['lesion'].unique()):          # A1~A7
        os.makedirs(os.path.join(OUT, split, lesion), exist_ok=True)  # 폴더 생성


def bbox_from_json(jpath):
    """JSON에서 가장 넓은 병변 박스(x,y,w,h)를 반환. 없으면 polygon→박스 변환, 둘 다 없으면 None."""
    with open(jpath, encoding='utf-8') as f:              # 라벨 JSON 열기
        data = json.load(f)                               # 파싱
    best, best_area = None, -1                            # 가장 큰 박스 추적
    for item in data.get('labelingInfo', []):            # 라벨 객체들 순회
        if 'box' in item:                                 # 박스 어노테이션이 있으면
            loc = item['box']['location'][0]              # 첫 위치 dict
            x, y = loc['x'], loc['y']                     # 좌상단 좌표
            w, h = loc['width'], loc['height']            # 폭/높이
        elif 'polygon' in item:                           # 박스 없고 폴리곤만 있으면
            pts = item['polygon']['location'][0]          # 점들 dict (x1,y1,...)
            xs = [v for k, v in pts.items() if k.startswith('x')]  # x좌표 모음
            ys = [v for k, v in pts.items() if k.startswith('y')]  # y좌표 모음
            x, y = min(xs), min(ys)                        # 폴리곤의 좌상단
            w, h = max(xs) - x, max(ys) - y               # 폴리곤 외접 박스 크기
        else:
            continue                                      # 둘 다 없으면 건너뜀
        if w * h > best_area:                              # 더 큰 병변이면 갱신
            best, best_area = (x, y, w, h), w * h
    return best                                           # (x,y,w,h) 또는 None


def crop_one(row):
    """한 행: 원본 열기 → 병변 박스(+여유) 크롭 → 224 리사이즈 → 저장. 박스 없으면 전체 사용."""
    jpg   = row['abs_path']                                # 원본 jpg 경로
    jpath = jpg[:-4] + '.json'                             # 같은 폴더의 동일 이름 JSON
    try:
        img = Image.open(jpg).convert('RGB')              # RGB로 강제 변환
        W, H = img.size                                   # 실제 해상도(클리핑 기준)
        box = bbox_from_json(jpath) if os.path.exists(jpath) else None  # 박스 추출
        if box:                                           # 병변 박스가 있으면
            x, y, w, h = box                              # 좌표 풀기
            mx, my = w * MARGIN, h * MARGIN              # 여유 마진(폭·높이의 20%)
            l = max(0, int(x - mx))                       # 좌(0 이상)
            t = max(0, int(y - my))                       # 상(0 이상)
            r = min(W, int(x + w + mx))                   # 우(이미지 폭 이하)
            b = min(H, int(y + h + my))                   # 하(이미지 높이 이하)
            if r > l and b > t:                           # 유효한 박스일 때만 크롭
                img = img.crop((l, t, r, b))             # 병변 영역만 잘라냄
        img = img.resize(IMG_SIZE)                        # 224x224로 통일
        out = os.path.join(OUT, row['split'], row['lesion'], row['img_file'])  # 저장 경로
        img.save(out, quality=92)                         # JPEG로 저장
        return True
    except Exception as e:                                # 손상 파일 등은 건너뜀
        return False


# ThreadPoolExecutor로 병렬 처리(이미지 I/O가 병목이라 스레드가 효과적)
rows = df.to_dict('records')                              # 행을 dict 리스트로
ok = 0                                                    # 성공 카운트
with ThreadPoolExecutor(max_workers=16) as ex:           # 16스레드
    for i, r in enumerate(ex.map(crop_one, rows)):       # 각 행 크롭
        ok += int(r)                                      # 성공 누적
        if (i + 1) % 3000 == 0:                           # 3,000장마다 로그
            print(f"  {i+1:,}/{len(rows):,}  (성공 {ok:,})")

print(f"\n완료: {ok:,}/{len(rows):,}장 크롭 저장 → {OUT}")  # 최종 요약
