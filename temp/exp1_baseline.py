# ============================================================
# 실험 1: Baseline CNN (직접 설계)
# 목적: 단순 CNN으로 피부 질환 7클래스 분류가 가능한지 기준선 확인
# 입력: 반려동물 피부 사진 (224×224×3)
# 출력: 7개 질환 클래스별 확률
# ============================================================

# ────────────────────────────────────────────
# 0. 라이브러리 임포트
# ────────────────────────────────────────────

import os                          # 파일/폴더 경로 처리용
import numpy as np                 # 수치 연산 (배열, 행렬)
import pandas as pd                # 데이터프레임 (CSV 읽기)
import matplotlib.pyplot as plt    # 그래프 시각화
from pathlib import Path           # 경로를 객체로 다루는 유틸리티

import tensorflow as tf            # 딥러닝 프레임워크 (텐서플로)
from tensorflow import keras       # 텐서플로의 고수준 API (케라스)

# keras에서 필요한 모듈들을 개별 임포트
from keras.models import Sequential          # 레이어를 순서대로 쌓는 모델 구조
from keras.layers import (
    Conv2D,                # 합성곱 레이어: 이미지에서 특징(패턴)을 추출
    MaxPooling2D,          # 최대 풀링: 특징맵 크기를 줄여 연산량 감소
    BatchNormalization,    # 배치 정규화: 학습 안정화, 수렴 속도 향상
    Flatten,               # 2D 특징맵 → 1D 벡터로 변환
    Dense,                 # 완전연결층: 최종 분류 수행
    Dropout,               # 드롭아웃: 과적합 방지 (일부 뉴런 비활성화)
    GlobalAveragePooling2D # 전역 평균 풀링: Flatten 대신 사용, 파라미터 수 감소
)

from keras.callbacks import (
    EarlyStopping,         # 조기 종료: val_loss 개선 없으면 학습 중단
    ModelCheckpoint,       # 체크포인트: 최고 성능 모델 자동 저장
    ReduceLROnPlateau      # 학습률 감소: val_loss 정체 시 lr을 줄여 미세 조정
)

from keras.preprocessing.image import ImageDataGenerator  # 이미지 데이터 로딩 + 증강

# 학습 곡선 외 평가 지표
from sklearn.metrics import classification_report, confusion_matrix  # 분류 리포트, 혼동 행렬
import seaborn as sns              # 히트맵 등 고급 시각화

# 한글 폰트 설정 (Windows 환경)
plt.rcParams['font.family'] = 'Malgun Gothic'    # 맑은 고딕 폰트 사용
plt.rcParams['axes.unicode_minus'] = False        # 마이너스(-) 기호 깨짐 방지

print(f"TensorFlow 버전: {tf.__version__}")
print(f"GPU 사용 가능: {len(tf.config.list_physical_devices('GPU')) > 0}")


# ────────────────────────────────────────────
# 1. 경로 설정 및 데이터 로딩
# ────────────────────────────────────────────

# 프로젝트 루트 경로 (이 파일이 models/ 안에 있으므로 ..으로 한 단계 위)
ROOT = Path('..')

# 전처리된 CSV가 있는 폴더
PROCESSED = ROOT / 'data' / 'processed'

# 그래프 저장 폴더 (없으면 자동 생성)
FIG_DIR = ROOT / 'outputs' / 'figures'
FIG_DIR.mkdir(parents=True, exist_ok=True)

# 모델 저장 폴더 (없으면 자동 생성)
MODEL_DIR = ROOT / 'models'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ── CSV 불러오기 ──
# dataset_cleaned.csv: 전처리 완료된 34,987개 샘플 정보
df = pd.read_csv(PROCESSED / 'dataset_cleaned.csv')

# 이미지 경로 컬럼 지정 (원본 이미지 경로 사용)
target_col = 'img_path'

# split 컬럼으로 train/val/test 분리
# .copy()로 복사본 생성 → 원본 df에 영향 없음
df_train = df[df['split'] == 'train'].copy()   # 24,500개 (70%)
df_val   = df[df['split'] == 'val'].copy()     # 5,250개  (15%)
df_test  = df[df['split'] == 'test'].copy()    # 5,250개  (15%)

print(f"데이터 로드 완료")
print(f"  train : {len(df_train):,}장")
print(f"  val   : {len(df_val):,}장")
print(f"  test  : {len(df_test):,}장")


# ────────────────────────────────────────────
# 2. 하이퍼파라미터 설정
# ────────────────────────────────────────────

IMG_SIZE   = (224, 224)   # CNN 입력 이미지 크기 (가로 224 × 세로 224 픽셀)
BATCH_SIZE = 32           # 한 번에 모델에 넣는 이미지 수 (메모리에 따라 조절)
EPOCHS     = 30           # 전체 데이터를 최대 30번 반복 학습
NUM_CLASSES = 7           # 분류할 질환 클래스 수 (A1~A7)
LEARNING_RATE = 0.001     # 학습률: 가중치 업데이트 크기 (너무 크면 발산, 너무 작으면 느림)


# ────────────────────────────────────────────
# 3. 데이터 Generator 생성
# ────────────────────────────────────────────
# 실험 1은 Baseline이므로 증강(Augmentation) 없이 정규화만 적용

# ── Train용 Generator: 정규화만 ──
# rescale=1./255: 픽셀값 0~255를 0~1 범위로 변환
# → 모든 입력을 같은 스케일로 맞춰 학습 안정화
train_datagen = ImageDataGenerator(
    rescale=1./255     # 이게 실험 1의 핵심: 증강 없이 정규화만
)

# ── Val/Test용 Generator: 동일하게 정규화만 ──
# 검증/테스트 데이터는 항상 증강하지 않음 (원본 그대로 평가해야 공정)
val_test_datagen = ImageDataGenerator(
    rescale=1./255
)

# ── flow_from_dataframe: DataFrame의 경로에서 이미지를 읽어오는 함수 ──
# dataframe: 이미지 정보가 담긴 DataFrame
# x_col: 이미지 파일 경로가 있는 컬럼명
# y_col: 라벨(정답)이 있는 컬럼명 → 'lesion' (A1~A7)
# target_size: 이미지를 이 크기로 리사이즈
# batch_size: 한 번에 가져올 이미지 수
# class_mode: 'categorical' → 원핫인코딩 (A1=[1,0,0,0,0,0,0])
# shuffle: True → 매 에폭마다 순서 섞기 (과적합 방지)
# seed: 42 → 랜덤 시드 고정 (재현성 확보)

train_generator = train_datagen.flow_from_dataframe(
    dataframe=df_train,
    x_col=target_col,          # 이미지 파일 경로 컬럼
    y_col='lesion',            # 라벨 컬럼 (A1~A7)
    target_size=IMG_SIZE,      # (224, 224)로 리사이즈
    batch_size=BATCH_SIZE,     # 32장씩 묶어서 전달
    class_mode='categorical',  # 원핫인코딩 방식
    shuffle=True,              # 데이터 순서 섞기
    seed=42                    # 재현성을 위한 시드 고정
)

val_generator = val_test_datagen.flow_from_dataframe(
    dataframe=df_val,
    x_col=target_col,
    y_col='lesion',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False              # 검증 데이터는 순서 유지 (평가 일관성)
)

test_generator = val_test_datagen.flow_from_dataframe(
    dataframe=df_test,
    x_col=target_col,
    y_col='lesion',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False              # 테스트 데이터도 순서 유지
)

# 클래스 인덱스 확인: 어떤 클래스가 어떤 번호에 매핑되었는지
print(f"\n클래스 인덱스: {train_generator.class_indices}")


# ────────────────────────────────────────────
# 4. Baseline CNN 모델 구조 정의
# ────────────────────────────────────────────
# Sequential: 레이어를 위에서 아래로 순서대로 쌓는 방식
# 구조: Conv2D → BatchNorm → ReLU → MaxPool 을 4번 반복 → 분류층

model = Sequential([

    # ── 블록 1: 첫 번째 합성곱 블록 ──
    # Conv2D(32, (3,3)): 3×3 크기의 필터 32개로 이미지를 훑으며 특징 추출
    # 32개 필터 = 32가지 서로 다른 패턴(엣지, 색상 변화 등)을 감지
    # padding='same': 입력과 출력 크기를 동일하게 유지
    # input_shape: 첫 번째 레이어에만 입력 크기를 명시 (224, 224, 3)
    Conv2D(32, (3, 3), padding='same', activation='relu',
           input_shape=(224, 224, 3)),

    # BatchNormalization: 각 배치의 출력값을 정규화
    # → 학습이 안정적이고 빠르게 수렴함
    BatchNormalization(),

    # MaxPooling2D(2,2): 2×2 영역에서 최댓값만 남김
    # → 특징맵 크기 224→112로 절반 축소, 중요한 특징만 보존
    MaxPooling2D((2, 2)),

    # ── 블록 2: 두 번째 합성곱 블록 ──
    # 필터 수 32→64로 증가: 더 복잡한 패턴 감지
    # 블록 1에서 추출한 기본 특징(엣지 등)을 조합하여 중간 수준 특징 학습
    Conv2D(64, (3, 3), padding='same', activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),   # 112→56

    # ── 블록 3: 세 번째 합성곱 블록 ──
    # 필터 수 64→128: 질감, 색상 패턴 등 고수준 특징 학습
    Conv2D(128, (3, 3), padding='same', activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),   # 56→28

    # ── 블록 4: 네 번째 합성곱 블록 ──
    # 필터 수 128→256: 질환별 특화된 복합 패턴 학습
    # 예: "붉은 울퉁불퉁한 영역" = A1 구진, "하얀 거친 표면" = A2 비듬
    Conv2D(256, (3, 3), padding='same', activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),   # 28→14

    # ── 분류 헤드 (Classification Head) ──
    # GlobalAveragePooling2D: 14×14×256 특징맵을 256차원 벡터로 압축
    # Flatten 대신 사용하는 이유: 파라미터 수가 훨씬 적어 과적합 방지
    GlobalAveragePooling2D(),

    # Dense(256): 256개의 뉴런으로 구성된 완전연결층
    # 추출된 특징들을 조합하여 최종 판단 준비
    Dense(256, activation='relu'),

    # Dropout(0.5): 학습 중 뉴런의 50%를 랜덤으로 끔
    # → 특정 뉴런에 의존하지 않도록 하여 과적합 방지
    Dropout(0.5),

    # Dense(7): 최종 출력층 — 7개 클래스에 대한 확률 출력
    # softmax: 7개 출력값의 합을 1.0으로 만듦
    # → [0.03, 0.02, 0.02, 0.87, 0.03, 0.02, 0.01] 이런 식으로 확률 출력
    Dense(NUM_CLASSES, activation='softmax')
])


# ────────────────────────────────────────────
# 5. 모델 컴파일
# ────────────────────────────────────────────
# 모델 구조를 정의한 후, 학습 방법을 설정하는 단계

model.compile(
    # optimizer: 가중치를 어떻게 업데이트할지 결정
    # Adam: 학습률을 자동 조절하는 옵티마이저 (가장 범용적)
    optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),

    # loss: 모델의 예측과 정답의 차이를 측정하는 함수
    # categorical_crossentropy: 원핫인코딩된 다중 클래스 분류에 사용
    # 예측이 정답과 가까울수록 loss 값이 작아짐
    loss='categorical_crossentropy',

    # metrics: 학습 중 모니터링할 지표
    # accuracy: 전체 예측 중 맞춘 비율
    metrics=['accuracy']
)

# 모델 구조 요약 출력: 레이어별 출력 크기와 파라미터 수 확인
model.summary()


# ────────────────────────────────────────────
# 6. 콜백 설정
# ────────────────────────────────────────────
# 학습 중 자동으로 실행되는 기능들

callbacks = [
    # EarlyStopping: val_loss가 5 에폭 연속 개선 안 되면 학습 중단
    # patience=5: 5번 참고 기다림
    # restore_best_weights=True: 중단 시 가장 좋았던 가중치로 복원
    EarlyStopping(
        monitor='val_loss',          # 검증 손실을 모니터링
        patience=5,                  # 5 에폭 동안 개선 없으면 중단
        restore_best_weights=True,   # 최고 성능 가중치로 복원
        verbose=1                    # 중단 시 메시지 출력
    ),

    # ModelCheckpoint: 매 에폭마다 val_loss가 최소인 모델을 파일로 저장
    ModelCheckpoint(
        filepath=str(MODEL_DIR / 'exp1_baseline.h5'),  # 저장 경로
        monitor='val_loss',          # 검증 손실 기준
        save_best_only=True,         # 최고 성능일 때만 저장 (용량 절약)
        verbose=1                    # 저장 시 메시지 출력
    ),

    # ReduceLROnPlateau: val_loss가 정체되면 학습률을 줄임
    # 학습 후반에 미세 조정할 때 유용
    ReduceLROnPlateau(
        monitor='val_loss',          # 검증 손실 모니터링
        factor=0.5,                  # 학습률을 절반으로 줄임
        patience=3,                  # 3 에폭 동안 개선 없으면 학습률 감소
        min_lr=1e-6,                 # 최소 학습률 (이 이하로는 안 내림)
        verbose=1                    # 감소 시 메시지 출력
    )
]


# ────────────────────────────────────────────
# 7. 모델 학습
# ────────────────────────────────────────────

print("\n" + "=" * 50)
print("🚀 실험 1: Baseline CNN 학습 시작")
print("=" * 50)

# model.fit: 실제 학습을 수행하는 함수
history = model.fit(
    train_generator,              # 훈련 데이터 (24,500장, 32장씩 묶음)
    epochs=EPOCHS,                # 최대 30 에폭 (EarlyStopping으로 일찍 끝날 수 있음)
    validation_data=val_generator,  # 매 에폭마다 검증 데이터로 성능 체크
    callbacks=callbacks,          # 위에서 설정한 콜백 3개 적용
    verbose=1                     # 학습 진행 상황 출력 (프로그레스바)
)

print("\n✅ 학습 완료!")


# ────────────────────────────────────────────
# 8. 학습 곡선 시각화
# ────────────────────────────────────────────
# history 객체에 매 에폭의 loss, accuracy 값이 기록되어 있음

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# ── 왼쪽: Loss 곡선 ──
# train_loss는 내려가는데 val_loss가 올라가면 → 과적합 신호
axes[0].plot(history.history['loss'], label='Train Loss', linewidth=2)
axes[0].plot(history.history['val_loss'], label='Val Loss', linewidth=2)
axes[0].set_title('Loss 곡선', fontsize=14)
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Loss')
axes[0].legend(fontsize=12)
axes[0].grid(True)

# ── 오른쪽: Accuracy 곡선 ──
# train_acc와 val_acc가 비슷하게 올라가면 → 정상 학습
axes[1].plot(history.history['accuracy'], label='Train Accuracy', linewidth=2)
axes[1].plot(history.history['val_accuracy'], label='Val Accuracy', linewidth=2)
axes[1].set_title('Accuracy 곡선', fontsize=14)
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Accuracy')
axes[1].legend(fontsize=12)
axes[1].grid(True)

plt.suptitle('실험 1: Baseline CNN 학습 곡선', fontsize=16, fontweight='bold')
plt.tight_layout()

# 그래프를 파일로 저장
plt.savefig(FIG_DIR / 'exp1_learning_curve.png', dpi=150, bbox_inches='tight')
plt.show()
print(f"📊 학습 곡선 저장 → {FIG_DIR / 'exp1_learning_curve.png'}")


# ────────────────────────────────────────────
# 9. 테스트 데이터 평가
# ────────────────────────────────────────────

print("\n" + "=" * 50)
print("📝 테스트 데이터 평가")
print("=" * 50)

# model.evaluate: 테스트 데이터로 최종 성능 측정
# loss와 accuracy를 반환
test_loss, test_acc = model.evaluate(test_generator, verbose=1)
print(f"\n테스트 Loss    : {test_loss:.4f}")
print(f"테스트 Accuracy: {test_acc:.4f} ({test_acc*100:.1f}%)")


# ────────────────────────────────────────────
# 10. 상세 평가 (Classification Report + Confusion Matrix)
# ────────────────────────────────────────────

# 모델이 테스트 데이터 전체에 대해 예측 수행
# predict: 각 이미지에 대해 7개 클래스 확률 배열을 반환
y_pred_proba = model.predict(test_generator)

# np.argmax: 확률이 가장 높은 클래스의 인덱스를 선택
# 예: [0.03, 0.02, 0.02, 0.87, 0.03, 0.02, 0.01] → 3 (A4)
y_pred = np.argmax(y_pred_proba, axis=1)

# test_generator.classes: 실제 정답 라벨 (인덱스 형태)
y_true = test_generator.classes

# 클래스 이름 매핑
class_names = list(train_generator.class_indices.keys())  # ['A1','A2',...,'A7']

# 질환명 매핑 (한글)
LESION_MAP = {
    'A1': 'A1 구진/플라크',
    'A2': 'A2 비듬/각질',
    'A3': 'A3 태선화/색소',
    'A4': 'A4 농포/여드름',
    'A5': 'A5 미란/궤양',
    'A6': 'A6 결절/종괴',
    'A7': 'A7 무증상(정상)'
}
class_labels = [LESION_MAP[c] for c in class_names]

# ── Classification Report ──
# precision: 모델이 A1이라고 예측한 것 중 실제 A1인 비율
# recall: 실제 A1인 것 중 모델이 A1이라고 맞춘 비율
# f1-score: precision과 recall의 조화 평균
print("\n=== Classification Report ===")
print(classification_report(y_true, y_pred, target_names=class_labels))

# ── Confusion Matrix (혼동 행렬) ──
# 행: 실제 클래스, 열: 예측 클래스
# 대각선 값이 높을수록 좋음 (정답을 맞춘 것)
# 대각선 외 값은 어떤 클래스를 어떤 클래스로 잘못 예측했는지 보여줌
cm = confusion_matrix(y_true, y_pred)

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_labels, yticklabels=class_labels, ax=ax)
ax.set_xlabel('예측 (Predicted)', fontsize=12)
ax.set_ylabel('실제 (Actual)', fontsize=12)
ax.set_title('실험 1: Baseline CNN — Confusion Matrix', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

plt.savefig(FIG_DIR / 'exp1_confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.show()
print(f"📊 혼동 행렬 저장 → {FIG_DIR / 'exp1_confusion_matrix.png'}")


# ────────────────────────────────────────────
# 11. 결과 요약
# ────────────────────────────────────────────

print("\n" + "=" * 50)
print("📋 실험 1 결과 요약")
print("=" * 50)
print(f"모델 구조       : 직접 설계 CNN (Conv2D × 4블록)")
print(f"데이터 증강     : 없음 (정규화만)")
print(f"Class Weight    : 없음")
print(f"학습 에폭       : {len(history.history['loss'])}회")
print(f"최종 Train Acc  : {history.history['accuracy'][-1]:.4f}")
print(f"최종 Val Acc    : {history.history['val_accuracy'][-1]:.4f}")
print(f"테스트 Accuracy : {test_acc:.4f} ({test_acc*100:.1f}%)")
print(f"테스트 Loss     : {test_loss:.4f}")
print(f"모델 저장 경로  : models/exp1_baseline.h5")
print("=" * 50)