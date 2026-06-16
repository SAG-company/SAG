"""
AI 수의사 - 추론(predict) 모듈

연결 대상 모델 (notebooks/04_modeling.ipynb 에서 학습·저장):
    - 백본      : Keras EfficientNetB3 (include_top=False, ImageNet)
    - 분류 헤드 : GAP → BatchNorm → Dense(512,relu) → Dropout
                  → Dense(256,relu) → Dropout → Dense(7, softmax)
    - 입력      : 224 x 224 RGB, '0~255 원본 그대로'
                  (efficientnet.preprocess_input 은 pass-through.
                   정규화는 EfficientNet 내부 Normalization 층이 처리)
    - 출력      : softmax 확률 7개 (A1~A7, 알파벳 순 = class_indices 순)
    - 저장 위치 : final_models/efficientnetb3_final_*.keras

설계:
    - final_models/ 의 '가장 최근' efficientnetb3_final_*.keras 를 자동 선택해 추론
    - 모델/TensorFlow 가 없으면 → 이미지 해시 기반 '안정적 더미'로 폴백
      (데모가 끊기지 않도록. 반환 dict 형식은 두 경우 모두 동일)
    - 공개 API(predict / gradcam / risk_score / LESION_MAP / CLASS_ORDER)는
      기존과 동일하므로 pages/2_detection.py 는 수정할 필요가 없다.
"""

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

# Streamlit 캐시(있으면 사용, 노트북/단독 테스트에서 import 실패해도 동작하도록 방어)
try:
    import streamlit as st

    cache_resource = st.cache_resource
except Exception:  # pragma: no cover - streamlit 밖에서 import될 때
    def cache_resource(func):
        return func


# =========================================================
# 1. 클래스 / 전처리 상수  (04_modeling.ipynb 와 동일하게 유지)
# =========================================================

# 클래스 코드 → 한국어 병변명
LESION_MAP = {
    "A1": "구진/플라크",
    "A2": "비듬/각질/상피성잔고리",
    "A3": "태선화/과다색소침착",
    "A4": "농포/여드름",
    "A5": "미란/궤양",
    "A6": "결절/종괴",
    "A7": "무증상(정상)",
}

# 모델 출력 순서.
# flow_from_dataframe 의 class_indices 는 라벨을 알파벳 정렬하므로 A1~A7(인덱스 0~6)과 동일.
CLASS_ORDER = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]

# 입력 크기 (H, W) — 학습과 동일해야 함
IMG_SIZE = (224, 224)


# =========================================================
# 2. 모델 파일 탐색
# =========================================================

_BASE = Path(__file__).resolve().parent
_FINAL_DIR = _BASE / "final_models"

# final_models 가 비었을 때 대비한 보조 후보 (위에서부터 먼저 존재하는 파일 사용)
MODEL_CANDIDATES = [
    _BASE / "outputs" / "models" / "best_model.keras",
    _BASE / "models" / "exp2_transfer_finetuned.keras",
]


def find_model_path():
    """사용할 모델 파일 경로를 반환. 없으면 None.

    우선순위:
        1) final_models/efficientnetb3_final_*.keras 중 '가장 최근' 파일
        2) MODEL_CANDIDATES 중 먼저 존재하는 파일
    """
    if _FINAL_DIR.exists():
        finals = sorted(
            _FINAL_DIR.glob("efficientnetb3_final_*.keras"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if finals:
            return finals[0]

    for path in MODEL_CANDIDATES:
        if path.exists():
            return path
    return None


def model_available() -> bool:
    """실제 모델로 추론 가능한 상태인지 여부."""
    return load_model() is not None


@cache_resource
def load_model():
    """모델을 1회 로드해 캐시. 모델/TensorFlow 가 없으면 None 반환(→ 더미 모드)."""
    path = find_model_path()
    if path is None:
        return None
    try:
        import tensorflow as tf

        return tf.keras.models.load_model(path, compile=False)
    except Exception as e:  # 텐서플로 미설치/로드 실패 시에도 앱은 더미로 계속 동작
        print(f"[inference] 모델 로드 실패 → 더미 모드: {e}")
        return None


# =========================================================
# 3. 전처리
#    EfficientNet 계열은 '0~255 원본'을 그대로 받는다(내부 정규화 보유).
#    학습 때 efficientnet.preprocess_input(=pass-through)을 썼으므로 동일하게 적용한다.
# =========================================================

def _infer_input_size(model) -> tuple:
    """모델의 input_shape 에서 (H, W)를 읽어온다. 못 읽으면 IMG_SIZE."""
    try:
        shape = model.input_shape  # 예: (None, 224, 224, 3)
        h, w = int(shape[1]), int(shape[2])
        if h and w:
            return (h, w)
    except Exception:
        pass
    return IMG_SIZE


def preprocess(image: Image.Image, size: tuple) -> np.ndarray:
    """PIL 이미지를 모델 입력 배치 (1, H, W, 3) 로 변환.

    - 학습 시 flow_from_dataframe 의 기본 보간(nearest)과 동일하게 리사이즈
    - efficientnet.preprocess_input 적용(없으면 0~255 원본 그대로 — 결과 동일)
    """
    image = image.convert("RGB").resize(
        (size[1], size[0]),  # resize 는 (W, H)
        resample=Image.Resampling.NEAREST,
    )
    arr = np.asarray(image, dtype=np.float32)  # 0~255
    try:
        from tensorflow.keras.applications.efficientnet import preprocess_input

        arr = preprocess_input(arr)  # EfficientNet: pass-through(0~255 유지)
    except Exception:
        pass  # TF 없거나 import 실패 → 원본 0~255 그대로 사용
    return np.expand_dims(arr, axis=0)


# =========================================================
# 4. 위험도 매핑
# =========================================================

# 임상적으로 더 시급한 병변(미란/궤양, 결절/종괴)
_SEVERE = {"A5", "A6"}


def risk_from_prediction(top_label: str, confidence: float) -> str:
    """예측 클래스와 확신도로 4단계 위험도를 결정."""
    if top_label == "A7":
        return "정상 가능성 높음"
    if top_label in _SEVERE and confidence >= 0.4:
        return "빠른 진료 권장"
    if confidence >= 0.6:
        return "진료 권장"
    return "관찰 필요"


# 위험도 문자열 → 게이지(0~100)에 쓸 점수
RISK_SCORE = {
    "정상 가능성 높음": 12,
    "관찰 필요": 42,
    "진료 권장": 72,
    "빠른 진료 권장": 92,
}


def risk_score(risk: str) -> int:
    """위험도 4단계를 게이지용 0~100 점수로 변환."""
    return RISK_SCORE.get(risk, 50)


# =========================================================
# 5. 확률 보정 / 더미 추론
# =========================================================

def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum()


def _ensure_prob(arr: np.ndarray) -> np.ndarray:
    """이미 확률분포(합≈1, 0~1)면 그대로, 아니면(=로짓) softmax 적용.

    최종 모델은 Dense(softmax) 출력이라 그대로 통과하지만,
    혹시 로짓 출력 모델이 들어와도 안전하게 동작하도록 방어한다.
    """
    arr = np.asarray(arr, dtype=np.float64).ravel()
    if arr.min() >= 0.0 and abs(arr.sum() - 1.0) < 1e-3:
        return arr
    return _softmax(arr)


def _dummy_probs(image: Image.Image) -> np.ndarray:
    """이미지 바이트 해시를 seed 로 써서 '안정적인' 가짜 확률을 생성(같은 이미지=같은 결과)."""
    digest = hashlib.md5(image.tobytes()).hexdigest()
    seed = int(digest[:8], 16)
    rng = np.random.default_rng(seed)
    logits = rng.normal(size=len(CLASS_ORDER))
    return _softmax(logits)


# =========================================================
# 6. 공개 API: predict()
# =========================================================

def predict(image: Image.Image) -> dict:
    """
    이미지 1장에 대한 예측 결과를 표준 형식으로 반환한다.

    반환 dict:
        available  : 실제 모델 추론 여부 (False면 더미)
        probs      : {클래스코드: 확률} 7개 (합=1.0)
        top_label  : 최상위 클래스 코드 (예: 'A2')
        top_name   : 최상위 클래스 한국어명
        confidence : 최상위 클래스 확률 (0~1)
        risk       : 위험도 4단계 문자열
    """
    model = load_model()

    if model is not None:
        size = _infer_input_size(model)
        batch = preprocess(image, size)
        raw = model.predict(batch, verbose=0)[0]
        probs = _ensure_prob(raw)
        available = True
    else:
        probs = _dummy_probs(image)
        available = False

    prob_map = {cls: float(p) for cls, p in zip(CLASS_ORDER, probs)}
    top_idx = int(np.argmax(probs))
    top_label = CLASS_ORDER[top_idx]
    confidence = float(probs[top_idx])

    return {
        "available": available,
        "probs": prob_map,
        "top_label": top_label,
        "top_name": LESION_MAP[top_label],
        "confidence": confidence,
        "risk": risk_from_prediction(top_label, confidence),
    }


# =========================================================
# 7. Grad-CAM (실제 모델이 있을 때만 동작)
# =========================================================

def _find_last_conv_layer(model):
    """
    Grad-CAM 대상이 될 마지막 4D(배치,H,W,채널) 출력 계층을 찾는다.

    최종 모델은 [InputLayer → efficientnetb3(Functional) → GAP → ...] 의 선형 스택이라,
    마지막 4D 출력 계층 = 백본(efficientnetb3) 자체가 된다.
    바깥 model.layers 수준에서 고르므로 'graph disconnected' 문제를 피한다.
    """
    candidate = None
    for layer in model.layers:
        try:
            if len(layer.output.shape) == 4:  # (배치, H, W, 채널) = 특징맵
                candidate = layer
        except Exception:
            continue
    return candidate


def gradcam(image: Image.Image):
    """
    Grad-CAM 히트맵(0~1, HxW numpy)을 반환.
    실제 모델이 없거나 계산 실패 시 None 을 반환해 앱이 멈추지 않게 한다.
    """
    model = load_model()
    if model is None:
        return None

    try:
        import tensorflow as tf

        size = _infer_input_size(model)
        batch = tf.convert_to_tensor(preprocess(image, size), dtype=tf.float32)

        target = _find_last_conv_layer(model)
        if target is None:
            return None
        target_idx = model.layers.index(target)

        # Keras 3 에서는 functional 모델의 중간 텐서를 재조합할 수 없으므로,
        # GradientTape 안에서 계층을 순차로 직접 호출하며 특징맵을 watch 한다.
        with tf.GradientTape() as tape:
            x = batch
            feature = None
            for i, layer in enumerate(model.layers):
                if layer.__class__.__name__ == "InputLayer":
                    continue
                x = layer(x, training=False)        # 추론 모드(Dropout/BN 고정)
                if i == target_idx:
                    feature = x                     # 마지막 특징맵
                    tape.watch(feature)             # 변수가 아니므로 명시적 watch
            preds = x
            class_idx = tf.argmax(preds[0])
            class_score = preds[:, class_idx]

        if feature is None:
            return None

        grads = tape.gradient(class_score, feature)            # 기울기
        if grads is None:
            return None
        weights = tf.reduce_mean(grads, axis=(0, 1, 2))        # 채널별 중요도
        cam = tf.reduce_sum(feature[0] * weights, axis=-1)     # 가중합 = 관심 영역

        cam = tf.nn.relu(cam)                                  # 음수 제거(양의 기여만)
        cam = cam / (tf.reduce_max(cam) + 1e-8)                # 0~1 정규화
        return cam.numpy()
    except Exception as e:
        print(f"[inference] Grad-CAM 실패: {e}")
        return None
