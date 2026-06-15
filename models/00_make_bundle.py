# -*- coding: utf-8 -*-
# =============================================================================
# 00_make_bundle.py  —  GPU PC 업로드용 이미지 번들 생성 (이 PC에서 1회 실행)
# 목적: crop 없이(전처리 X) 전체 이미지를 224로 줄여 클래스별 폴더로 정리 → zip.
# 입력: data/processed/dataset_local.csv (abs_path, split, lesion, img_file)
# 출력: data/images/<split>/<lesion>/<파일명>.jpg  +  data/images.zip
# 실행: python models/00_make_bundle.py
# =============================================================================
import os, sys, io, shutil                                  # 경로/표준출력/압축
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # 한글 출력
import pandas as pd                                          # CSV
from PIL import Image                                        # 이미지 리사이즈
from concurrent.futures import ThreadPoolExecutor            # I/O 병렬

PROJ = r"C:\Users\금정산2-PC02\SAG_project"                  # 프로젝트 루트
CSV  = os.path.join(PROJ, "data", "processed", "dataset_local.csv")  # 매핑 CSV
OUT  = os.path.join(PROJ, "data", "images")                 # 번들 폴더
SIZE = (224, 224)                                            # 저장 크기

df = pd.read_csv(CSV)                                        # 34,987행
print(f"대상: {len(df):,}장 → 224 리사이즈 번들 생성", flush=True)

for split in df['split'].unique():                          # train/val/test
    for lesion in sorted(df['lesion'].unique()):           # A1~A7
        os.makedirs(os.path.join(OUT, split, lesion), exist_ok=True)  # 폴더 생성

def one(row):
    """원본 열기 → RGB → 224 리사이즈 → <split>/<lesion>/ 에 저장."""
    try:
        img = Image.open(row['abs_path']).convert('RGB').resize(SIZE)  # 로드+리사이즈
        img.save(os.path.join(OUT, row['split'], row['lesion'], row['img_file']),
                 quality=92)                                # JPEG 저장
        return True
    except Exception:                                       # 손상 파일 방어
        return False

rows = df.to_dict('records')                                # 행 리스트
ok = 0                                                       # 성공 수
with ThreadPoolExecutor(max_workers=16) as ex:             # 16스레드
    for i, r in enumerate(ex.map(one, rows)):              # 병렬 처리
        ok += int(r)
        if (i + 1) % 3000 == 0:                            # 진행 로그
            print(f"  {i+1:,}/{len(rows):,} (성공 {ok:,})", flush=True)

print(f"\n리사이즈 완료: {ok:,}/{len(rows):,}장 → {OUT}", flush=True)

# zip 압축 (data/images.zip)
print("zip 압축 중...", flush=True)
zip_base = os.path.join(PROJ, "data", "images")            # → data/images.zip
shutil.make_archive(zip_base, 'zip', OUT)                  # 폴더 통째 압축
mb = os.path.getsize(zip_base + ".zip") / 1024 / 1024      # 용량
print(f"완료: {zip_base}.zip  ({mb:.0f}MB)", flush=True)
