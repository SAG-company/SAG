# 🐾 반려동물 피부질환 CNN 모델 — 실험 1, 2, 3 전체 정리

---

## 전체 흐름: 왜 3개 실험을 하는가?

```
실험 1 (기준선)          실험 2 (성능 향상)         실험 3 (불균형 보정)
직접 설계 CNN            + Transfer Learning      + Class Weight
정규화만                 + 데이터 증강             + 종별 가중치
     ↓                       ↓                       ↓
  "분류 되는가?"         "얼마나 좋아지는가?"     "소수 클래스도 잘 되는가?"
     ↓                       ↓                       ↓
              3개 결과 비교 → 최고 성능 모델 선정
                              ↓
                     Streamlit 앱에 탑재
```

한 번에 최고 모델을 만드는 게 아니라, **단계적으로 기법을 추가하며 효과를 검증**하는 것이 실험의 목적입니다.

---

## 실험별 비교표

| 항목 | 실험 1 | 실험 2 | 실험 3 |
|------|--------|--------|--------|
| **모델** | Conv2D 4블록 직접 설계 | EfficientNetB0 (사전학습) | EfficientNetB0 (사전학습) |
| **데이터 증강** | ❌ 없음 | ✅ 7종 적용 | ✅ 7종 적용 |
| **Class Weight** | ❌ 없음 | ❌ 없음 | ✅ 적용 |
| **학습률** | 0.001 | 0.0001 | 0.0001 |
| **Dropout** | 0.5 | 0.3 | 0.3 |
| **학습 대상** | 전체 파라미터 | 분류층만 | 분류층만 |
| **핵심 질문** | 분류 가능한가? | 성능 향상? | 소수 클래스 개선? |
| **기대 역할** | 비교 기준선 | 성능 향상 확인 | 최종 배포 후보 |

---

## 실험 1: Baseline CNN (직접 설계)

### 설계 이유

> "우리 데이터로 피부 질환 분류가 아예 가능한가?"를 확인하는 **가장 기본적인 실험**

사전학습 모델이나 증강 없이 **순수한 CNN 성능**만 측정합니다.
이 결과가 실험 2, 3의 **비교 기준(Baseline)**이 됩니다.

### 모델 구조

```
입력 (128×128×3)
    ↓
[블록1] Conv2D(32) → BatchNorm → ReLU → MaxPool   → 112×112×32
  ↳ 기본 특징 추출: 엣지, 색상 변화 감지
    ↓
[블록2] Conv2D(64) → BatchNorm → ReLU → MaxPool   → 56×56×64
  ↳ 중간 특징: 질감, 패턴 조합
    ↓
[블록3] Conv2D(128) → BatchNorm → ReLU → MaxPool  → 28×28×128
  ↳ 고수준 특징: 피부 질감, 색상 패턴 복합
    ↓
[블록4] Conv2D(256) → BatchNorm → ReLU → MaxPool  → 14×14×256
  ↳ 질환 특화 특징: 질환별 고유 시각 패턴
    ↓
GlobalAveragePooling2D → 256
    ↓
Dense(256) → Dropout(0.5) → Dense(7, softmax)
    ↓
출력: [A1%, A2%, A3%, A4%, A5%, A6%, A7%]
```

### 주요 코드 설명

| 코드 | 설명 |
|------|------|
| `Conv2D(32, (3,3))` | 3×3 필터 32개로 이미지를 훑으며 특징 추출 |
| `BatchNormalization()` | 출력값 정규화 → 학습 안정화, 빠른 수렴 |
| `MaxPooling2D((2,2))` | 2×2 영역의 최댓값만 남김 → 크기 절반 축소 |
| `GlobalAveragePooling2D()` | 특징맵 전체를 평균 → 1D 벡터 압축 |
| `Dropout(0.5)` | 뉴런 50% 비활성화 → 과적합 방지 |
| `Dense(7, activation='softmax')` | 7클래스 확률 출력 (합계=1.0) |
| `rescale=1./255` | 픽셀값 0~255 → 0~1 정규화 |
| `EarlyStopping(patience=5)` | 2 에폭 개선 없으면 자동 중단 |

### 산출물

- `models/exp1_baseline.h5` — 학습된 모델
- `outputs/figures/exp1_learning_curve.png` — Loss/Accuracy 곡선
- `outputs/figures/exp1_confusion_matrix.png` — 혼동 행렬

---

## 실험 2: Transfer Learning + 데이터 증강

### 설계 이유

> "이미 검증된 모델의 시각적 특징 추출 능력을 빌려오고, 데이터 다양성을 높이면 얼마나 좋아지는가?"

#### Transfer Learning을 쓰는 이유

직접 설계한 CNN은 우리 데이터(35,000장)만으로 특징을 학습해야 합니다.
하지만 **EfficientNetB0**은 ImageNet(1,400만 장)으로 이미 학습되어 있어서
엣지, 질감, 형태 등 **범용적인 시각 특징**을 이미 알고 있습니다.
우리는 이 능력을 가져와서 **피부 질환 분류에 맞게 분류층만 학습**합니다.

#### 데이터 증강을 쓰는 이유

같은 이미지를 회전, 반전, 밝기 조절하여 **다양한 변형을 생성**합니다.
모델이 "이 각도에서만 A2처럼 보인다"가 아니라
"어떤 각도, 밝기에서도 A2를 A2로 인식"할 수 있도록 **일반화 성능을 향상**시킵니다.

#### EfficientNetB0을 선택한 이유

| 모델 | 파라미터 | 정확도 | 판단 |
|------|---------|--------|------|
| VGG16 | 138M | 71.3% | 너무 무거움 |
| ResNet50 | 25.6M | 76.0% | 보통 |
| **EfficientNetB0** | **5.3M** | **77.1%** | **가볍고 정확 → 채택** |

### 모델 구조

```
입력 (128×128×3)
    ↓
┌────────────────────────────┐
│ EfficientNetB0             │
│ (ImageNet 사전학습)         │
│ 🔒 가중치 고정 (freeze)     │  ← 이미 학습된 특징 추출 능력 그대로 사용
│ → 1280차원 특징맵 출력      │
└────────────────────────────┘
    ↓
GlobalAveragePooling2D → 1280
    ↓
Dense(256, relu) → Dropout(0.3)  ← 이 부분만 새로 학습
    ↓
Dense(7, softmax)
    ↓
출력: [A1%, A2%, A3%, A4%, A5%, A6%, A7%]
```

### 실험 1 대비 코드 차이점

| 항목 | 실험 1 코드 | 실험 2 코드 |
|------|-----------|-----------|
| 모델 로드 | `Sequential([Conv2D(...)])` | `EfficientNetB0(weights='imagenet')` |
| 가중치 고정 | 없음 | `base_model.trainable = False` |
| 모델 구성 | Sequential | **함수형 API** (`Model(inputs, outputs)`) |
| 학습률 | 0.001 | **0.0001** (1/10로 줄임) |
| Dropout | 0.5 | **0.3** (사전학습 모델은 과적합 위험 낮음) |
| 증강 | `rescale` 만 | **+ flip, rotation, brightness, zoom, shift** |

### 데이터 증강 설정

| 증강 기법 | 값 | 적용 이유 |
|----------|-----|----------|
| `horizontal_flip` | True | 피부 병변은 좌우 방향 무관 |
| `rotation_range` | 30° | 카메라 촬영 각도 다양성 |
| `brightness_range` | [0.8, 1.2] | 조명 차이 극복 |
| `zoom_range` | 0.1 | 병변 크기 다양성 |
| `width/height_shift` | 0.1 | 병변 위치 다양성 |
| ❌ `vertical_flip` | 미적용 | 상하 방향은 의미 있음 (몸통 위/아래) |
| ❌ `shear/channel` | 미적용 | 피부색 왜곡으로 병변 특징 손실 위험 |

### 산출물

- `models/exp2_transfer.h5`
- `outputs/figures/exp2_learning_curve.png`
- `outputs/figures/exp2_confusion_matrix.png`

---

## 실험 3: Transfer Learning + 증강 + Class Weight

### 설계 이유

> "반려견(88.6%)과 반려묘(11.4%)의 데이터 불균형을 보정하면 소수 클래스(반려묘) 성능이 올라가는가?"

실험 2는 성능이 좋지만, **반려견 데이터에 편향**될 수 있습니다.
서비스에 배포할 모델은 반려묘도 공정하게 분류해야 하므로,
**Class Weight로 불균형을 보정**합니다.

#### Class Weight 동작 원리

```
반려견(D): 31,010장 → 가중치 0.563 (많으니까 줄임)
반려묘(C):  3,990장 → 가중치 4.443 (적으니까 4.4배 높임)
```

모델이 반려묘 이미지를 틀리면 **4.4배 큰 벌점**을 받습니다.
→ 모델이 반려묘도 신경 써서 학습하게 됩니다.

### 실험 2 대비 코드 차이점 (단 1곳)

```python
# 실험 2
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=callbacks,
    verbose=1
)

# 실험 3 (이 한 줄만 추가)
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=callbacks,
    class_weight=class_weight_dict,    # ⭐ 이것만 추가!
    verbose=1
)
```

### 실험 3 전용 분석: 종별 정확도

실험 3에서만 **반려견/반려묘 각각의 정확도**를 별도로 측정합니다.

```python
dog_mask = (test_species == 'D')
cat_mask = (test_species == 'C')
dog_acc = np.mean(y_pred[dog_mask] == y_true[dog_mask])
cat_acc = np.mean(y_pred[cat_mask] == y_true[cat_mask])
```

이 값을 실험 2와 비교하여 **Class Weight가 효과 있었는지** 판단합니다.

### 산출물

- `models/exp3_weighted.h5`
- `outputs/figures/exp3_learning_curve.png`
- `outputs/figures/exp3_confusion_matrix.png`
- 종별 정확도 분석 결과

---

## 공통 학습 설정 (3개 실험 모두 동일)

| 항목 | 값 | 이유 |
|------|-----|------|
| Loss | `categorical_crossentropy` | 원핫인코딩된 7클래스 분류에 표준 |
| Optimizer | `Adam` | 학습률 자동 조절, 가장 범용적 |
| Metrics | `accuracy` | 전체 예측 중 맞춘 비율 |
| EarlyStopping | patience=2 | 2 에폭 개선 없으면 자동 중단 → 과적합 방지 |
| ModelCheckpoint | save_best_only | 최고 성능 모델만 저장 → 디스크 절약 |
| ReduceLROnPlateau | factor=0.5, patience=2 | 정체 시 학습률 절반 → 미세 조정 |
| 데이터 분할 | 70/15/15 | train/val/test 고정 (3개 실험 동일) |
| 이미지 크기 | 128×128 | EfficientNetB0 기본 입력 크기 |
| 배치 크기 | 64 | GPU 메모리 고려한 표준값 |

---

## 최종 모델 선정 기준

3개 실험 결과를 아래 표에 채운 후 **최고 성능 모델을 Streamlit 앱에 탑재**합니다.

| 지표 | 실험 1 | 실험 2 | 실험 3 |
|------|--------|--------|--------|
| Test Accuracy | ? | ? | ? |
| F1-Score (macro) | ? | ? | ? |
| 반려견 정확도 | ? | ? | ? |
| 반려묘 정확도 | ? | ? | ? |
| 과적합 여부 | ? | ? | ? |

선정 기준:
1. **Test Accuracy**가 가장 높은 모델
2. 동점이면 **F1-Score (macro)**가 높은 모델
3. 동점이면 **반려묘 정확도**가 높은 모델 (공정성)
