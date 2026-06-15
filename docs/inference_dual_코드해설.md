# `inference_dual.py` 코드 해설서

> 대상: 비전공자도 이해할 수 있게 작성
> 파일 위치: `SAG/inference_dual.py`
> 역할 한 줄 요약: **"사진 한 장을 받아 → AI 분석 결과(병변/확신도/위험도)를 돌려주는 창구"**
> 작성 맥락: 최종 모델이 PyTorch(.pt)로 나올지 Keras로 나올지 미확정이라, **둘 다 자동 처리**하도록 만든 교체용 초안.

---

## 0. 이 파일은 왜 중요한가 (비유)

이 파일은 **병원의 "접수·진단 창구"** 예요.

- **프론트(화면, `pages/2_detection.py`)** = 손님이 사진을 내미는 곳
- **이 파일(`inference_dual.py`)** = 사진을 받아 **모델에게 물어보고**, 결과를 정해진 양식으로 정리해 돌려주는 직원
- **모델 파일(`.pt`)** = 실제 판단을 내리는 전문의

이 창구의 핵심 설계 원칙은 딱 하나예요:

> **"프론트는 `predict(사진)` 한 번만 부르면 된다. 그 뒤에 뭐가 있든 신경 안 써도 된다."**

그래서 모델이 PyTorch든 Keras든, 아예 없든(더미), **프론트 코드는 한 줄도 안 바뀝니다.** 이게 이 파일이 잘 만들어진 이유예요.

---

## 1. 전체 흐름 (사진이 들어와서 결과가 나가기까지)

```
사진(PIL 이미지)
   │
   ▼
predict(image)  ← 프론트가 부르는 유일한 함수 (섹션 7)
   │
   ├─ load_model() 로 모델을 불러옴 (섹션 3, 최초 1회만·이후 캐시)
   │      └─ 파일 확장자로 백엔드 자동 결정
   │            .pt  → PyTorch / .keras·.h5 → Keras / 없으면 → 더미
   │
   ├─ 백엔드에 맞는 전처리 (섹션 4)
   │      torch:  letterbox + ImageNet 정규화 → (1,3,224,224)
   │      keras:  resize → (1,224,224,3)
   │      dummy:  전처리 없이 해시로 가짜 확률
   │
   ├─ 모델에 넣어 7개 클래스 점수 얻음 → softmax로 확률화
   │
   ▼
결과 dict 반환  {병변코드, 한글명, 확신도, 위험도, 7개 확률}
```

핵심: **"확장자만 보고 알아서 갈래길을 탄다"** 가 이 파일의 전부예요.

---

## 2. 섹션별 라인 해설

코드는 8개 섹션으로 나뉘어 있어요. 위에서부터 순서대로 봅니다.

### 섹션 1 — 클래스/라벨 상수

```python
LESION_MAP = { "A1": "구진/플라크", ... "A7": "무증상(정상)" }
CLASS_ORDER = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]
```

- `LESION_MAP`: 모델이 뱉는 **코드(A1~A7)를 사람이 읽는 한글 병변명**으로 바꾸는 사전(번역표).
- `CLASS_ORDER`: 모델 출력 7칸이 **어떤 순서**인지 정의. 모델은 숫자 0~6번 칸으로 답하는데, 그 0번이 A1, 6번이 A7이라는 약속.
- ⚠️ **이 순서가 학습 때와 다르면 결과가 통째로 뒤섞입니다.** 학습 노트북도 `sorted()`로 A1~A7 알파벳 순이라 일치함(확인 완료).

### 섹션 2 — 연결 설정 ⭐ (내일 아침 여기만 보면 됨)

```python
MODEL_CANDIDATES = [
    _BASE / "models" / "exp3_v4_final.pt",   # 1순위
    ...
]
IMG_SIZE = (224, 224)
_TORCH_MEAN = [0.485, 0.456, 0.406]
_TORCH_STD  = [0.229, 0.224, 0.225]
```

- `MODEL_CANDIDATES`: 모델 파일을 **위에서부터 찾아보는 후보 목록**. 먼저 발견되는 파일을 씁니다. 내일 최종 모델을 `models/exp3_v4_final.pt`에 두면 1순위로 잡혀요.
- `IMG_SIZE`: 모델 입력 크기(224×224). 학습과 같아야 함.
- `_TORCH_MEAN/_STD`: **정규화 값**(ImageNet 통계). 사진 색을 모델이 학습한 기준에 맞춰 보정하는 숫자. 학습 노트북의 `eval_transform`에서 그대로 가져왔어요.
- 💡 **이 4가지(파일경로·크기·정규화)만 학습과 맞으면 99% 성공**입니다.

### 섹션 3 — 모델 로드 (창구가 전문의를 모셔오는 부분)

```python
def find_model_path(): ...          # 존재하는 첫 모델 파일 찾기
def build_torch_model(): ...        # PyTorch 모델 '뼈대'를 만든다
@cache_resource
def load_model(): ...               # 실제 로드 + 백엔드 판별
```

- `find_model_path()`: 후보 목록을 돌며 **실제로 있는 파일**을 반환. 없으면 `None`(→ 더미).
- `build_torch_model()`: ⭐ 가장 주의할 함수.
  - PyTorch의 `.pt`는 **가중치(숫자)만** 저장돼 있어요. 그릇(모델 구조)은 따로 코드로 만들어야 합니다.
  - 그래서 학습 노트북과 **똑같은 구조**(EfficientNetB0 + `Linear(1280→256)→ReLU→Dropout→Linear(256→7)`)를 여기서 다시 만들어요.
  - ⚠️ **이 구조가 학습 때와 1군데라도 다르면 로드가 실패**합니다. (내일 모델 구조가 바뀌면 여기를 고쳐야 함)
- `load_model()`: 파일 확장자를 보고
  - `.pt`/`.pth` → PyTorch로 로드, `.keras`/`.h5` → Keras로 로드
  - 실패하면(프레임워크 미설치 등) **조용히 `None`을 돌려줘서 앱이 죽지 않고 더미로 전환**됩니다.
  - `@cache_resource`: 모델을 **딱 한 번만 불러오고 재사용**(매번 불러오면 느리니까).

### 섹션 4 — 전처리 (사진을 모델이 먹을 수 있는 형태로 손질)

```python
def _letterbox(img, size): ...       # 종횡비 보존 + 검정 패딩
def preprocess_torch(image): ...     # PyTorch용 손질
def preprocess_keras(image, size): ...# Keras용 손질
def _softmax(x): ...                  # 점수 → 확률
def _ensure_prob(arr): ...           # 이미 확률이면 그대로, 아니면 softmax
```

- `_letterbox`: 사진을 **찌그러뜨리지 않고** 224×224에 맞추는 방법. 비율을 지키며 줄이고 남는 공간을 검정으로 채워요. (학습 때 `LetterboxResize`와 동일)
- `preprocess_torch`: 위 letterbox + 숫자 변환 + ImageNet 정규화 → `(1,3,224,224)` 모양 텐서.
- `_softmax`: 모델이 주는 **날것의 점수(로짓)를 0~1 확률**로 바꿔 합이 1이 되게 함.
- `_ensure_prob`: 안전장치. 출력이 이미 확률이면 그대로, 아니면 softmax 적용. (PyTorch는 로짓을 주므로 softmax가 필요)

### 섹션 5 — 위험도 매핑 (확률 → 보호자가 이해할 4단계)

```python
def risk_from_prediction(top_label, confidence): ...
def risk_score(risk): ...
```

- `risk_from_prediction`: 규칙 기반 판단.
  - A7(정상) → "정상 가능성 높음"
  - A5/A6(미란·결절 = 시급) + 확신도 40%↑ → "빠른 진료 권장"
  - 확신도 60%↑ → "진료 권장" / 그 외 → "관찰 필요"
- `risk_score`: 위 4단계를 화면 게이지용 점수(12/42/72/92)로 변환.
- 💡 이 부분은 모델과 무관한 **순수 규칙**이라 기존 코드 그대로 유지했어요.

### 섹션 6 — 더미 추론 (모델 없을 때의 가짜 결과)

```python
def _dummy_probs(image): ...
```

- 모델이 없을 때도 데모가 끊기지 않게 **가짜 확률**을 만듭니다.
- 핵심 트릭: 이미지의 **지문(해시)을 seed로** 사용 → **같은 사진엔 항상 같은 가짜 결과**가 나와요. (랜덤이지만 일관성 있음)

### 섹션 7 — `predict()` ⭐ 프론트가 부르는 유일한 함수

```python
def predict(image) -> dict:
    model, backend = load_model()
    if backend == "torch": ...   # PyTorch 추론
    elif backend == "keras": ... # Keras 추론
    else: ...                    # 더미
    return { available, backend, probs, top_label, top_name, confidence, risk }
```

- 백엔드에 따라 알맞은 길로 추론하고, **항상 똑같은 모양의 dict**를 돌려줍니다.
- `available`: 진짜 모델로 분석했는지(True) 더미인지(False). 프론트가 이걸 보고 "더미 결과" 경고를 띄울지 정해요.
- `backend`: 디버깅용("torch"/"keras"/"dummy"). 내일 연결 성공 여부를 여기로 바로 확인할 수 있어요.

### 섹션 8 — Grad-CAM (AI가 어디를 보고 판단했는지 히트맵)

```python
def gradcam(image): ...          # 백엔드 분기
def _gradcam_torch(model, image): ...
def _gradcam_keras(model, image): ...
```

- 모델이 사진의 **어느 부위에 주목**했는지 빨갛게 표시하는 기능.
- PyTorch용(`_gradcam_torch`)을 새로 구현했어요. EfficientNet의 마지막 특징맵을 hook으로 잡아 계산합니다.
- 실패하면 `None`을 돌려주고, 화면엔 "Grad-CAM은 모델 연결 시 표시" 안내만 떠요(앱 안 죽음).

---

## 3. 자주 나오는 용어집

| 용어 | 쉬운 설명 |
|------|-----------|
| **백엔드(backend)** | 모델을 돌리는 엔진 종류. 여기선 PyTorch / Keras 두 가지 |
| **PyTorch / Keras** | 둘 다 딥러닝 도구(프레임워크). 서로 파일 형식이 달라 호환 안 됨 |
| **state_dict (.pt)** | PyTorch가 **가중치 숫자만** 저장한 파일. 구조는 코드로 따로 만들어야 함 |
| **로짓(logit)** | 모델이 내는 **날것의 점수**. 아직 확률이 아님 |
| **softmax** | 로짓을 **0~1 확률**로 바꾸고 합을 1로 만드는 계산 |
| **정규화(Normalize)** | 사진 색 값을 학습 기준에 맞춰 보정. 틀리면 정확도 폭락 |
| **letterbox** | 사진을 안 찌그러뜨리고 정사각형에 맞추는 법(남는 곳 검정 패딩) |
| **EfficientNetB0** | 이미지 분류용 사전학습 모델(백본). 이 프로젝트의 두뇌 |
| **백본(backbone)** | 이미지 특징을 뽑는 모델의 몸통 |
| **더미(dummy) 모드** | 진짜 모델이 없을 때 쓰는 가짜 결과. 데모 유지용 |
| **Grad-CAM** | AI가 주목한 영역을 색으로 보여주는 시각화 |
| **캐시(cache)** | 한 번 한 일을 저장해뒀다 재사용(속도↑) |

---

## 4. 내일 모델 붙일 때 / 문제 생기면

### 정상 연결 순서
1. `pip install torch torchvision` (이 PC에서 추론할 경우)
2. 최종 `.pt`를 `models/exp3_v4_final.pt`에 둠
3. `inference_dual.py` → `inference.py`로 이름 변경 (기존 건 `inference_old.py`로 백업)
4. `streamlit run app.py` → Detection에서 사진 업로드 → 경고 없으면 성공

### 증상별 대처
| 증상 | 원인 후보 | 확인 위치 |
|------|----------|-----------|
| "더미 결과" 경고가 계속 뜸 | torch 미설치 / 파일 경로 틀림 | 섹션 2 `MODEL_CANDIDATES`, torch 설치 |
| 로드 시 에러 + 더미 전환 | 모델 **구조 불일치** | 섹션 3 `build_torch_model()`을 노트북과 대조 |
| 모델은 붙었는데 **정확도가 이상** | **전처리 불일치**(에러 없이 조용히 틀림) | 섹션 2 정규화 값, 섹션 4 letterbox |
| 결과 클래스가 통째로 뒤섞임 | 클래스 순서 불일치 | 섹션 1 `CLASS_ORDER` |

> 가장 잡기 어려운 건 **"전처리 불일치"** 예요. 에러가 안 나고 정확도만 떨어져서요. 모델이 붙었는데 결과가 이상하면 **정규화 값(`_TORCH_MEAN/_STD`)과 letterbox 적용 여부**부터 의심하세요.
