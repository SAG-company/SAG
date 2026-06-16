"""
연결된 모델을 로컬 테스트셋(dataset_local.csv의 abs_path)으로 재평가.

사용:
    python _eval_testset.py 50      # 클래스당 50장만 (빠른 검증)
    python _eval_testset.py 0       # 전체 테스트셋 + metrics.json 저장

주의:
    학습은 raw_sub(크롭) 이미지를 썼는데 로컬엔 abs_path(원본)만 있다.
    먼저 소표본 정확도가 권위값(test_acc=0.5758)에 근접하는지로
    '원본=테스트이미지' 여부를 검증한 뒤 전체 평가를 진행한다.
"""
import os
import sys
import io
import json
import warnings

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

SAMPLE_PER_CLASS = int(sys.argv[1]) if len(sys.argv) > 1 else 50
AUTH_ACC = 0.5758  # 연결 모델(20260614_1146)의 학습 시 test_acc

CLASS_ORDER = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]
LESION_NAME = {
    "A1": "A1 구진/플라크", "A2": "A2 비듬/각질", "A3": "A3 태선화/색소",
    "A4": "A4 농포/여드름", "A5": "A5 미란/궤양", "A6": "A6 결절/종괴",
    "A7": "A7 무증상(정상)",
}

# ── 테스트셋 구성 ──
df = pd.read_csv("data/processed/dataset_local.csv")
df = df[df["split"] == "test"].copy()
df = df[df["abs_path"].apply(lambda p: isinstance(p, str) and os.path.isfile(p))]
print(f"abs_path 존재하는 test 이미지: {len(df)}장")

if SAMPLE_PER_CLASS > 0:
    parts = [g.sample(min(len(g), SAMPLE_PER_CLASS), random_state=42)
             for _, g in df.groupby("lesion")]
    df = pd.concat(parts).reset_index(drop=True)
    print(f"빠른 검증 모드: 클래스당 {SAMPLE_PER_CLASS}장 → {len(df)}장")

print("클래스 분포:", df["lesion"].value_counts().sort_index().to_dict())

# ── 모델 로드 ──
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.efficientnet import preprocess_input

import inference
model_path = inference.find_model_path()
print("모델:", model_path)
model = tf.keras.models.load_model(model_path, compile=False)

datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
gen = datagen.flow_from_dataframe(
    dataframe=df, x_col="abs_path", y_col="lesion",
    target_size=(224, 224), batch_size=32,
    class_mode="categorical", shuffle=False,
)
print("generator class_indices:", gen.class_indices)
class_indices = gen.class_indices

# ── 예측 (항상 현재 연결된 모델로 새로 추론 → metrics가 모델과 어긋나지 않음) ──
probs = model.predict(gen, verbose=1)
y_pred = probs.argmax(axis=1)
y_true = gen.classes

idx_to_class = {v: k for k, v in class_indices.items()}  # 0->A1 ...
acc = float((y_pred == y_true).mean())
print(f"\n=== 정확도: {acc*100:.2f}%  (권위값 {AUTH_ACC*100:.1f}%, 차이 {abs(acc-AUTH_ACC)*100:.1f}%p) ===")

if SAMPLE_PER_CLASS > 0:
    ok = abs(acc - AUTH_ACC) <= 0.07
    print("판정:", "✅ 근접 → 원본=테스트이미지, 전체 재평가 유효" if ok
          else "⚠️ 크게 빗나감 → 원본≠크롭, 재평가로 metrics.json 만들면 안 됨")
    sys.exit(0)

# ── 전체 모드: 완전한 metrics.json 저장 ──
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

target_names = [LESION_NAME[idx_to_class[i]] for i in range(len(idx_to_class))]
report = classification_report(y_true, y_pred, target_names=target_names, output_dict=True, zero_division=0)
p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)

# 축종별 정확도 (dtype 명시 + 길이 방어 + 실패해도 None)
species = df["species"].astype(str).values
yp = np.asarray(y_pred)
yt = np.asarray(y_true)
def species_acc(tag):
    try:
        mask = np.array([s.upper().startswith(tag) for s in species], dtype=bool)
        n = min(len(mask), len(yp), len(yt))
        mask, a, b = mask[:n], yp[:n], yt[:n]
        return float((a[mask] == b[mask]).mean()) if mask.sum() else None
    except Exception as e:
        print(f"  (species_acc({tag}) 건너뜀: {e})")
        return None

class_report = {
    name: {
        "precision": report[name]["precision"],
        "recall": report[name]["recall"],
        "f1-score": report[name]["f1-score"],
        "support": report[name]["support"],
    } for name in target_names
}

metrics = {
    "accuracy": acc,
    "precision": float(p),
    "recall": float(r),
    "f1": float(f1),
    "dog_accuracy": species_acc("D"),
    "cat_accuracy": species_acc("C"),
    "model_file": os.path.basename(str(model_path)),
    "eval_note": "로컬 abs_path(원본) 재평가",
    "class_report": class_report,
}
with open("outputs/metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)
print("\n✅ outputs/metrics.json 저장 완료")
print(json.dumps({k: v for k, v in metrics.items() if k != "class_report"}, ensure_ascii=False, indent=2))

# 혼동행렬 그림
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

cm = confusion_matrix(y_true, y_pred)
short = [idx_to_class[i] for i in range(len(idx_to_class))]
fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks(range(len(short))); ax.set_xticklabels(short)
ax.set_yticks(range(len(short))); ax.set_yticklabels(short)
ax.set_xlabel("Predicted"); ax.set_ylabel("True")
ax.set_title("Confusion Matrix - EfficientNetB3 (Test set)")
for i in range(len(short)):
    for j in range(len(short)):
        ax.text(j, i, cm[i, j], ha="center", va="center",
                color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=8)
plt.colorbar(im); plt.tight_layout()
plt.savefig("outputs/figures/eval_confusion_matrix.png", dpi=150, bbox_inches="tight")
print("✅ outputs/figures/eval_confusion_matrix.png 저장")
