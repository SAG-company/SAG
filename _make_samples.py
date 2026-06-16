"""
Detection 페이지용 샘플 이미지 생성 (저장본 기준 선별).

핵심: 앱은 '저장된 512px JPEG'를 읽으므로, 후보를 '저장될 형태(리사이즈+JPEG
라운드트립)'로 변환한 뒤 그 상태로 예측해 가장 또렷하게 정답 분류되는 이미지를 고른다.
=> 선택 시점 신뢰도 = 앱에서 보이는 신뢰도 (불일치 없음).

클래스(A1~A7)당 1장을 골라 assets/samples/sample_A{n}.jpg 로 저장한다.
원본은 로컬 D: 드라이브(dataset_local.csv의 abs_path)에서 가져온다.
"""
import os
import sys
import io
import warnings

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input

import inference

CLASS_ORDER = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]  # 모델 출력 인덱스 0~6
N_CANDIDATES = 15
MAXSIDE = 512
OUT = os.path.join("assets", "samples")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv("data/processed/dataset_local.csv")
df = df[df["split"] == "test"]
df = df[df["abs_path"].apply(lambda p: isinstance(p, str) and os.path.isfile(p))]

model = tf.keras.models.load_model(inference.find_model_path(), compile=False)


def to_saved(path):
    """원본 → 저장될 형태(max 512px). 저장 시와 동일한 리사이즈."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = MAXSIDE / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    return img


def predict_as_app(img_saved):
    """저장본을 JPEG 라운드트립 후 앱(inference.preprocess)과 동일 경로로 예측."""
    buf = io.BytesIO()
    img_saved.save(buf, "JPEG", quality=85)
    buf.seek(0)
    rt = Image.open(buf).convert("RGB").resize((224, 224), Image.Resampling.NEAREST)
    arr = preprocess_input(np.asarray(rt, dtype="float32"))
    return model.predict(arr[None], verbose=0)[0]


for ci, code in enumerate(CLASS_ORDER):
    pool = df[df["lesion"] == code]
    if len(pool) == 0:
        print(f"{code}: 후보 없음")
        continue
    cand = pool.sample(min(len(pool), N_CANDIDATES), random_state=42)
    best_key, best_img = None, None
    for _, row in cand.iterrows():
        saved = to_saved(row["abs_path"])
        p = predict_as_app(saved)
        key = (int(p.argmax()) == ci, float(p[ci]))  # 정답 우선 → 해당 클래스 확률 높은 순
        if best_key is None or key > best_key:
            best_key, best_img = key, saved

    out = os.path.join(OUT, f"sample_{code}.jpg")
    best_img.save(out, "JPEG", quality=85)
    tag = "정답분류" if best_key[0] else "best-effort"
    print(f"{code}: {tag}  앱예측확률={best_key[1] * 100:.0f}%  {best_img.size}  {os.path.getsize(out) // 1024}KB")
