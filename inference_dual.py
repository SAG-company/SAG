"""
AI 수의사 - 추론(predict) 모듈  [듀얼 백엔드 버전]
====================================================================
이 파일은 기존 inference.py의 '교체 후보 초안'입니다.
검토 후 문제 없으면 이 파일을 inference.py 로 이름만 바꾸면
2_detection.py 등 프론트 페이지는 한 줄도 고칠 필요가 없습니다.
(predict()/gradcam()/risk_score() 의 이름과 반환 형식이 기존과 동일하기 때문)

------------------------------------------------------------------
왜 '듀얼 백엔드'인가?
    최종 모델이 PyTorch(.pt)로 나올지 Keras(.keras/.h5)로 나올지
    아직 확정되지 않았다. 그래서 모델 파일의 '확장자'를 보고
    백엔드를 자동으로 골라 추론한다.
        .pt / .pth     → PyTorch  (현재 exp3_v4_final.pt 가 이 형식)
        .keras / .h5   → TensorFlow/Keras
    둘 다 없거나 해당 프레임워크가 설치 안 돼 있으면 → '더미 모드'
    (이미지 해시 기반의 안정적 가짜 결과. 데모가 끊기지 않는다.)

------------------------------------------------------------------
⭐ 내일 아침 모델 붙일 때 확인할 단 3가지
    (1) MODEL_CANDIDATES 에 실제 모델 파일 경로가 들어 있는가
    (2) [PyTorch면] build_torch_model() 의 분류 헤드 구조가
        학습 노트북(exp3_v4_final.ipynb)과 '완전히' 동일한가
    (3) 전처리(_TORCH_* / _KERAS_*)가 학습 때와 같은가
        ← 이게 틀리면 에러는 안 나고 '정확도만' 폭락한다 (가장 잡기 어려움)

학습 노트북에서 추출한 사실 (exp3_v4_final.ipynb 기준):
    - 백본        : torchvision EfficientNetB0
    - 분류 헤드    : Linear(1280→256) → ReLU → Dropout(0.5) → Linear(256→7)
    - 입력 크기    : 224 x 224
    - 전처리      : LetterboxResize(224) → ToTensor → Normalize(ImageNet)
    - 정규화 통계  : mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]
    - 클래스 순서  : A1,A2,...,A7 (알파벳 정렬, 인덱스 0~6)
    - 저장 방식    : torch.save(model.state_dict())  ← 구조 재정의 후 로드 필요
    - 출력        : softmax 안 거친 '로짓' (CrossEntropyLoss 사용) → 추론 시 softmax 필요
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
# 1. 클래스 / 라벨 상수
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

# 모델 출력 순서. 학습 시 sorted(lesion) → A1~A7 알파벳 순(인덱스 0~6)과 동일하게 유지.
CLASS_ORDER = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]


# =========================================================
# 2. 연결 설정 (내일 여기만 확인하면 됨)
# =========================================================

_BASE = Path(__file__).resolve().parent

# 위에서부터 '먼저 존재하는' 파일을 사용한다. 확장자로 백엔드를 자동 결정.
MODEL_CANDIDATES = [
    # --- PyTorch 후보 (현재 학습 중인 최종본) ---
    _BASE / "models" / "exp3_v4_final.pt",        # 1순위: 노트북이 저장하는 이름
    _BASE / "models" / "best_model.pt",           # 대체 경로
    # --- Keras 후보 (혹시 최종이 Keras로 나올 경우) ---
    _BASE / "outputs" / "models" / "best_model.keras",
    _BASE / "models" / "mobilenetv3_skin.keras",
]

# 입력 크기 (H, W) — 학습과 동일해야 함
IMG_SIZE = (224, 224)

# --- PyTorch 전처리 상수 (학습 노트북의 eval_transform과 동일) ---
_TORCH_MEAN = [0.485, 0.456, 0.406]   # ImageNet 통계
_TORCH_STD = [0.229, 0.224, 0.225]
_TORCH_DROPOUT = 0.5                   # 분류 헤드 Dropout (구조 일치용, 추론 영향 없음)

# --- Keras 전처리 상수 ---
# 주의: TF EfficientNet 계열은 '0~255 원본'을 그대로 받는다(내부 정규화 보유).
#       만약 Keras 최종 모델이 다른 정규화로 학습됐다면 여기 맞춰야 함.
_KERAS_RESCALE = None   # None=0~255 그대로 / 예: 1/255.0


# =========================================================
# 3. 모델 로드 (한 번만 로드하고 캐시)
# =========================================================

def find_model_path():
    """존재하는 첫 번째 모델 파일 경로를 반환. 없으면 None."""
    for path in MODEL_CANDIDATES:
        if path.exists():
            return path
    return None


def model_available() -> bool:
    """실제 모델로 추론 가능한 상태인지 여부."""
    model, _ = load_model()
    return model is not None


def build_torch_model(num_classes: int = 7, dropout: float = _TORCH_DROPOUT):
    """
    학습 노트북과 '완전히 동일한' EfficientNetB0 + 커스텀 헤드를 만든다.
    state_dict(.pt)는 가중치만 들어있으므로, 이 구조를 먼저 만든 뒤 그 위에 얹는다.
    ⭐ 헤드 구조가 1픽셀이라도 다르면 load_state_dict가 실패하거나 키가 어긋난다.
    """
    import torch.nn as nn
    import torchvision.models as models

    backbone = models.efficientnet_b0(weights=None)  # 구조만(사전학습 X), 가중치는 .pt에서 로드
    backbone.classifier = nn.Sequential(
        nn.Linear(1280, 256),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(256, num_classes),
    )
    return backbone


@cache_resource
def load_model():
    """
    모델을 1회 로드해 캐시. 반환: (model, backend)
        backend: 'torch' | 'keras' | None(=더미)
    프레임워크 미설치/로드 실패 시에도 앱이 더미로 계속 동작하도록 (None, None) 반환.
    """
    path = find_model_path()
    if path is None:
        return None, None

    ext = path.suffix.lower()

    # ---- PyTorch ----
    if ext in {".pt", ".pth"}:
        try:
            import torch

            model = build_torch_model(len(CLASS_ORDER))
            state = torch.load(path, map_location="cpu", weights_only=True)
            # 혹시 {'state_dict': ...} 형태로 저장된 경우도 방어
            if isinstance(state, dict) and "state_dict" in state:
                state = state["state_dict"]
            model.load_state_dict(state)
            model.eval()
            return model, "torch"
        except Exception as e:  # 미설치/구조 불일치 시 더미로 폴백
            print(f"[inference] PyTorch 모델 로드 실패 → 더미 모드: {e}")
            return None, None

    # ---- Keras ----
    if ext in {".keras", ".h5"}:
        try:
            import tensorflow as tf

            return tf.keras.models.load_model(path, compile=False), "keras"
        except Exception as e:
            print(f"[inference] Keras 모델 로드 실패 → 더미 모드: {e}")
            return None, None

    return None, None


# =========================================================
# 4. 전처리 (백엔드별)
# =========================================================

def _letterbox(img: Image.Image, size: tuple) -> Image.Image:
    """
    16:9 종횡비를 보존하며 size로 맞추고 남는 곳을 검정으로 패딩.
    학습 노트북의 LetterboxResize와 동일한 결과를 내도록 torchvision 사용.
    """
    import torchvision.transforms.functional as TF

    w, h = img.size
    scale = min(size[0] / h, size[1] / w)
    new_h, new_w = int(h * scale), int(w * scale)
    img = TF.resize(img, [new_h, new_w])
    pad_t = (size[0] - new_h) // 2
    pad_b = size[0] - new_h - pad_t
    pad_l = (size[1] - new_w) // 2
    pad_r = size[1] - new_w - pad_l
    return TF.pad(img, [pad_l, pad_t, pad_r, pad_b], fill=0)


def preprocess_torch(image: Image.Image):
    """PIL → (1, 3, H, W) float 텐서. 학습 eval_transform과 동일."""
    import torchvision.transforms as T

    img = _letterbox(image.convert("RGB"), IMG_SIZE)
    transform = T.Compose([
        T.ToTensor(),                                  # 0~1, (C,H,W)
        T.Normalize(mean=_TORCH_MEAN, std=_TORCH_STD),  # ImageNet 정규화
    ])
    return transform(img).unsqueeze(0)                 # 배치 차원 추가 → (1,3,H,W)


def preprocess_keras(image: Image.Image, size: tuple) -> np.ndarray:
    """PIL → (1, H, W, 3) numpy. (단순 resize. Keras 최종 모델 전처리에 맞춰 조정)"""
    image = image.convert("RGB").resize((size[1], size[0]))  # resize는 (W, H)
    arr = np.asarray(image, dtype=np.float32)
    if _KERAS_RESCALE is not None:
        arr = arr * _KERAS_RESCALE
    return np.expand_dims(arr, axis=0)


def _softmax(x: np.ndarray) -> np.ndarray:
    """로짓 → 확률. (수치 안정 버전)"""
    e = np.exp(x - np.max(x))
    return e / e.sum()


def _ensure_prob(arr: np.ndarray) -> np.ndarray:
    """이미 확률분포(합≈1, 0~1)면 그대로, 아니면(=로짓) softmax 적용."""
    arr = np.asarray(arr, dtype=np.float64).ravel()
    if arr.min() >= 0.0 and abs(arr.sum() - 1.0) < 1e-3:
        return arr
    return _softmax(arr)


# =========================================================
# 5. 위험도 매핑 (기존 inference.py와 동일)
# =========================================================

_SEVERE = {"A5", "A6"}  # 임상적으로 더 시급한 병변(미란/궤양, 결절/종괴)


def risk_from_prediction(top_label: str, confidence: float) -> str:
    """예측 클래스와 확신도로 4단계 위험도를 결정."""
    if top_label == "A7":
        return "정상 가능성 높음"
    if top_label in _SEVERE and confidence >= 0.4:
        return "빠른 진료 권장"
    if confidence >= 0.6:
        return "진료 권장"
    return "관찰 필요"


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
# 6. 더미 추론 (모델 없을 때) — 같은 이미지엔 항상 같은 결과
# =========================================================

def _dummy_probs(image: Image.Image) -> np.ndarray:
    """이미지 바이트 해시를 seed로 써서 '안정적인' 가짜 확률을 생성."""
    digest = hashlib.md5(image.tobytes()).hexdigest()
    seed = int(digest[:8], 16)
    rng = np.random.default_rng(seed)
    logits = rng.normal(size=len(CLASS_ORDER))
    return _softmax(logits)


# =========================================================
# 7. 공개 API: predict()
# =========================================================

def predict(image: Image.Image) -> dict:
    """
    이미지 1장에 대한 예측 결과를 표준 형식으로 반환한다. (기존과 동일한 dict)

    반환 dict:
        available  : 실제 모델 추론 여부 (False면 더미)
        backend    : 'torch' | 'keras' | 'dummy'  (디버깅용, 프론트는 무시해도 됨)
        probs      : {클래스코드: 확률} 7개 (합=1.0)
        top_label  : 최상위 클래스 코드 (예: 'A2')
        top_name   : 최상위 클래스 한국어명
        confidence : 최상위 클래스 확률 (0~1)
        risk       : 위험도 4단계 문자열
    """
    model, backend = load_model()

    if model is not None and backend == "torch":
        import torch

        batch = preprocess_torch(image)
        with torch.no_grad():
            logits = model(batch)[0].cpu().numpy()
        probs = _ensure_prob(logits)         # 로짓 → softmax
        available = True

    elif model is not None and backend == "keras":
        batch = preprocess_keras(image, IMG_SIZE)
        raw = model.predict(batch, verbose=0)[0]
        probs = _ensure_prob(raw)            # softmax 층 있으면 그대로, 없으면 적용
        available = True

    else:
        probs = _dummy_probs(image)
        available = False
        backend = "dummy"

    prob_map = {cls: float(p) for cls, p in zip(CLASS_ORDER, probs)}
    top_idx = int(np.argmax(probs))
    top_label = CLASS_ORDER[top_idx]
    confidence = float(probs[top_idx])

    return {
        "available": available,
        "backend": backend,
        "probs": prob_map,
        "top_label": top_label,
        "top_name": LESION_MAP[top_label],
        "confidence": confidence,
        "risk": risk_from_prediction(top_label, confidence),
    }


# =========================================================
# 8. Grad-CAM (백엔드별 / 실패 시 None → 앱은 안내문만 표시)
# =========================================================

def gradcam(image: Image.Image):
    """Grad-CAM 히트맵(0~1, HxW numpy)을 반환. 불가하면 None."""
    model, backend = load_model()
    if model is None:
        return None
    if backend == "torch":
        return _gradcam_torch(model, image)
    if backend == "keras":
        return _gradcam_keras(model, image)
    return None


def _gradcam_torch(model, image: Image.Image):
    """
    PyTorch Grad-CAM. EfficientNetB0의 마지막 특징맵(model.features[-1])을 대상으로,
    forward/backward hook으로 활성값과 기울기를 잡아 가중합한다.
    """
    try:
        import torch

        batch = preprocess_torch(image)
        activations, gradients = {}, {}

        target = model.features[-1]  # 마지막 conv 블록(특징맵)

        def f_hook(m, i, o):
            activations["v"] = o

        def b_hook(m, gi, go):
            gradients["v"] = go[0]

        h1 = target.register_forward_hook(f_hook)
        h2 = target.register_full_backward_hook(b_hook)

        out = model(batch)                 # (1, 7) 로짓
        idx = int(out.argmax(1))
        model.zero_grad()
        out[0, idx].backward()             # 최상위 클래스 점수 역전파

        h1.remove()
        h2.remove()

        act = activations["v"][0]          # (C, H, W)
        grad = gradients["v"][0]           # (C, H, W)
        weights = grad.mean(dim=(1, 2))    # 채널별 중요도 (C,)
        cam = torch.relu((weights[:, None, None] * act).sum(dim=0))  # 가중합 + 양수만
        cam = cam / (cam.max() + 1e-8)     # 0~1 정규화
        return cam.detach().cpu().numpy()
    except Exception as e:
        print(f"[inference] torch Grad-CAM 실패: {e}")
        return None


def _gradcam_keras(model, image: Image.Image):
    """
    Keras Grad-CAM. 마지막 4D(배치,H,W,채널) 출력 계층을 대상으로 계산.
    (Keras 최종 모델이 들어올 경우를 대비한 경로)
    """
    try:
        import tensorflow as tf

        batch = tf.convert_to_tensor(preprocess_keras(image, IMG_SIZE), dtype=tf.float32)

        # 마지막 4D 출력 계층 찾기
        target_idx = None
        for i, layer in enumerate(model.layers):
            try:
                if len(layer.output.shape) == 4:
                    target_idx = i
            except Exception:
                continue
        if target_idx is None:
            return None

        with tf.GradientTape() as tape:
            x = batch
            feature = None
            for i, layer in enumerate(model.layers):
                if layer.__class__.__name__ == "InputLayer":
                    continue
                x = layer(x, training=False)
                if i == target_idx:
                    feature = x
                    tape.watch(feature)
            preds = x
            class_idx = tf.argmax(preds[0])
            class_score = preds[:, class_idx]

        if feature is None:
            return None
        grads = tape.gradient(class_score, feature)
        if grads is None:
            return None
        weights = tf.reduce_mean(grads, axis=(0, 1, 2))
        cam = tf.reduce_sum(feature[0] * weights, axis=-1)
        cam = tf.nn.relu(cam)
        cam = cam / (tf.reduce_max(cam) + 1e-8)
        return cam.numpy()
    except Exception as e:
        print(f"[inference] keras Grad-CAM 실패: {e}")
        return None
