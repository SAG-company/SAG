"""
AI 수의사 - 추론(predict) 모듈

목표:
    Detection 페이지가 random 더미 대신 이 모듈의 predict()만 호출하면
    되도록 '추론 인터페이스'를 한 곳에 모은다.

핵심 설계:
    - 학습된 모델 파일(.keras / .h5)이 있으면 → 실제 추론
    - 아직 없으면 → 이미지 해시 기반 '안정적 더미'를 반환 (데모가 끊기지 않게)
    반환 형식(dict)은 두 경우 모두 동일하므로, 모델이 준비되면
    이 파일의 MODEL_CANDIDATES 경로에 파일만 떨어뜨리면 바로 실제 추론으로 전환된다.
"""

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

# Streamlit 캐시(있으면 사용, 노트북/단독 테스트 시 import 실패해도 동작하도록 방어)
try:
    import streamlit as st

    cache_resource = st.cache_resource
except Exception:  # pragma: no cover - streamlit 밖에서 import될 때
    def cache_resource(func):
        return func


# =========================================================
# 1. 클래스 / 전처리 상수  (04_modeling.ipynb와 동일하게 유지)
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

# 모델 출력 순서. flow_from_dataframe는 라벨을 알파벳 정렬하므로 A1~A7 순서가 맞다.
CLASS_ORDER = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]

# EDA에서 산출한 우리 데이터 채널별 평균/표준편차 (z-score 정규화용)
MEAN = np.array([0.5616, 0.5263, 0.5056], dtype=np.float32)
STD = np.array([0.1819, 0.1841, 0.1837], dtype=np.float32)

# 학습 산출물 후보 경로 (위에서부터 먼저 존재하는 파일을 사용)
# 주의: 최종 모델(MobileNetV3, 224x224 + z-score 정규화)만 후보로 둔다.
# exp1_baseline.h5는 입력 크기(128)와 정규화 방식(1/255)이 달라 여기 넣으면
# 잘못된 전처리로 추론되므로 제외한다. (최종 모델이 오기 전엔 더미 모드 유지)
_BASE = Path(__file__).resolve().parent
MODEL_CANDIDATES = [
    _BASE / "models" / "mobilenetv3_skin.keras",       # 최종 모델(예정) — 1순위
    _BASE / "outputs" / "models" / "best_model.keras",  # 대체 경로
]


# =========================================================
# 2. 모델 로드 (한 번만 로드하고 캐시)
# =========================================================

def find_model_path():
    """존재하는 첫 번째 모델 파일 경로를 반환. 없으면 None."""
    for path in MODEL_CANDIDATES:
        if path.exists():
            return path
    return None


def model_available() -> bool:
    """실제 모델로 추론 가능한 상태인지 여부."""
    return find_model_path() is not None


@cache_resource
def load_model():
    """모델을 1회 로드해 캐시. 모델/텐서플로가 없으면 None을 반환(→ 더미 모드)."""
    path = find_model_path()
    if path is None:
        return None
    try:
        import tensorflow as tf

        return tf.keras.models.load_model(path, compile=False)
    except Exception:
        # 텐서플로 미설치 또는 로드 실패 시에도 앱은 더미로 계속 동작
        return None


# =========================================================
# 3. 전처리
# =========================================================

def _infer_input_size(model) -> tuple:
    """모델의 input_shape에서 (H, W)를 읽어온다. 못 읽으면 224x224."""
    try:
        shape = model.input_shape  # 예: (None, 224, 224, 3)
        h, w = int(shape[1]), int(shape[2])
        if h and w:
            return (h, w)
    except Exception:
        pass
    return (224, 224)


def preprocess(image: Image.Image, size: tuple) -> np.ndarray:
    """PIL 이미지를 모델 입력 배치(1, H, W, 3)로 변환 + z-score 정규화."""
    image = image.convert("RGB").resize((size[1], size[0]))  # resize는 (W, H)
    arr = np.asarray(image, dtype=np.float32) / 255.0
    arr = (arr - MEAN) / STD
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
# 5. 더미 추론 (모델 없을 때) — 같은 이미지엔 항상 같은 결과
# =========================================================

def _dummy_probs(image: Image.Image) -> np.ndarray:
    """이미지 바이트 해시를 seed로 써서 '안정적인' 가짜 확률을 생성."""
    digest = hashlib.md5(image.tobytes()).hexdigest()
    seed = int(digest[:8], 16)
    rng = np.random.default_rng(seed)
    logits = rng.normal(size=len(CLASS_ORDER))
    exp = np.exp(logits - logits.max())
    return exp / exp.sum()


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
        probs = np.asarray(raw, dtype=np.float32)
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

    주의: 백본(MobileNetV3 등)이 중첩 Model로 들어와도 그 '안쪽' 계층을
    잡으면 안 된다. 안쪽 계층의 출력은 바깥 모델 그래프와 끊겨 있어
    grad_model을 만들 때 'graph disconnected' 오류가 난다.
    따라서 바깥 model.layers 수준에서 마지막 4D 출력 계층(= 보통 백본 그 자체,
    또는 평탄한 CNN이면 마지막 Conv)을 고른다.
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
    실제 모델이 없거나 계산 실패 시 None을 반환해 앱이 멈추지 않게 한다.
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

        # Keras 3에서는 functional 모델의 중간 텐서를 재조합할 수 없으므로,
        # GradientTape 안에서 계층을 순차로 직접 호출하며 특징맵을 watch한다.
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
    except Exception:
        return None
