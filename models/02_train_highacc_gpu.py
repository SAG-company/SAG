# -*- coding: utf-8 -*-
# =============================================================================
# 02_train_highacc_gpu.py  —  고정확도 학습 (GPU 권장: Colab / WSL2)
# 전략: 병변 크롭 + 올바른 전처리 + 증강 + 2단계 전이학습(헤드 워밍업 → 전체 미세조정)
# 입력: data/crops/<split>/<lesion>/*.jpg   (01_prepare_crops.py 산출물)
# 출력: outputs/models/best_model.keras (앱 연동), outputs/metrics.json,
#       outputs/figures/final_confusion_matrix.png
# 실행: python models/02_train_highacc_gpu.py   (GPU 환경에서)
# =============================================================================
import os, json                                            # 경로·JSON 저장
import numpy as np                                          # 수치 연산
import tensorflow as tf                                     # 딥러닝 프레임워크
from tensorflow import keras                                # 고수준 API
from tensorflow.keras import layers                         # 레이어 모음 (tf.keras → TF 2.10·최신 모두 호환)
from tensorflow.keras.applications import EfficientNetB0    # 백본(원하면 EfficientNetV2S로 교체)
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

# ---------------------------------------------------------------------------
# 0. 환경 설정 (GPU 확인 + 혼합정밀도로 속도 향상)
# ---------------------------------------------------------------------------
gpus = tf.config.list_physical_devices('GPU')              # 사용 가능한 GPU 목록
print("GPU:", gpus)                                         # 비어있으면 CPU로 도는 것
for g in gpus:                                              # 각 GPU에 대해
    tf.config.experimental.set_memory_growth(g, True)      # 메모리 점진 할당(OOM 방지)
if gpus:                                                    # GPU가 있을 때만
    keras.mixed_precision.set_global_policy('mixed_float16')  # float16 혼합정밀도 → 2배가량 가속

# ---------------------------------------------------------------------------
# 1. 하이퍼파라미터 / 경로
# ---------------------------------------------------------------------------
CROPS    = "data/images"                                    # 학습 이미지 루트 (crop 없이 224 리사이즈 번들 사용)
OUT_DIR  = "outputs"                                        # 산출물 루트
IMG_SIZE = (224, 224)                                       # 입력 크기
BATCH    = 64                                               # 배치 크기(GPU 메모리에 맞게 조정)
NUM_CLASSES = 7                                             # A1~A7
EPOCHS_HEAD = 10                                            # 1단계(헤드만) 에폭
EPOCHS_FT   = 25                                            # 2단계(미세조정) 에폭
os.makedirs(f"{OUT_DIR}/models", exist_ok=True)            # 모델 저장 폴더
os.makedirs(f"{OUT_DIR}/figures", exist_ok=True)           # 그림 저장 폴더

# ---------------------------------------------------------------------------
# 2. 데이터 로딩 (폴더 구조 = 라벨, image_dataset_from_directory)
# ---------------------------------------------------------------------------
def make_ds(split, shuffle):
    """crops/<split> 폴더에서 tf.data.Dataset 생성. 라벨은 폴더명(A1~A7) 정수 인코딩."""
    return keras.utils.image_dataset_from_directory(
        f"{CROPS}/{split}",                                # 해당 split 폴더
        image_size=IMG_SIZE,                               # 자동 리사이즈(이미 224지만 안전)
        batch_size=BATCH,                                  # 배치
        label_mode='int',                                  # 정수 라벨(0~6)
        shuffle=shuffle,                                   # train만 셔플
        seed=42,                                           # 재현성
    )

train_ds = make_ds('train', shuffle=True)                  # 학습셋
val_ds   = make_ds('val',   shuffle=False)                 # 검증셋
test_ds  = make_ds('test',  shuffle=False)                 # 테스트셋
class_names = train_ds.class_names                          # ['A1',...,'A7'] (알파벳 순)
print("클래스 순서:", class_names)                          # 인덱스 매핑 확인

AUTOTUNE = tf.data.AUTOTUNE                                 # 자동 병렬도
train_ds = train_ds.prefetch(AUTOTUNE)                     # 다음 배치 미리 준비
val_ds   = val_ds.prefetch(AUTOTUNE)                       # (속도)
test_ds  = test_ds.prefetch(AUTOTUNE)                      # (속도)

# ---------------------------------------------------------------------------
# 3. 데이터 증강 (학습 시에만 동작하는 전처리 레이어)
# ---------------------------------------------------------------------------
data_augmentation = keras.Sequential([                     # 증강 파이프라인
    layers.RandomFlip("horizontal"),                       # 좌우 반전(병변 방향 무관)
    layers.RandomRotation(0.08),                           # ±약 30도 회전
    layers.RandomZoom(0.1),                                # ±10% 확대/축소
    layers.RandomTranslation(0.1, 0.1),                    # 상하좌우 10% 이동
    layers.RandomContrast(0.1),                            # 대비 ±10%
], name="augment")                                         # 추론 시 자동 비활성

# ---------------------------------------------------------------------------
# 4. 모델 구성 (EfficientNetB0 + 커스텀 헤드)
#    주의: EfficientNet은 내부에 정규화가 있어 입력은 '0~255 원본'을 그대로 받는다.
#         image_dataset_from_directory가 0~255 float를 주므로 별도 rescale 불필요(=버그 회피).
# ---------------------------------------------------------------------------
base = EfficientNetB0(                                      # 백본 로드
    weights='imagenet',                                    # ImageNet 사전학습
    include_top=False,                                     # 분류층 제거
    input_shape=(*IMG_SIZE, 3),                            # 224x224x3
)
base.trainable = False                                      # 1단계: 백본 동결

inputs = keras.Input(shape=(*IMG_SIZE, 3))                 # 입력층(0~255)
x = data_augmentation(inputs)                              # 증강 적용
x = base(x, training=False)                                # 백본 통과(추론 모드: BN 고정)
x = layers.GlobalAveragePooling2D()(x)                     # 7x7x1280 → 1280 벡터
x = layers.Dropout(0.3)(x)                                 # 과적합 방지
x = layers.Dense(256, activation='relu')(x)               # 특징 조합
x = layers.Dropout(0.3)(x)                                 # 한 번 더 드롭아웃
outputs = layers.Dense(NUM_CLASSES, activation='softmax',  # 7클래스 확률
                       dtype='float32')(x)                 # 혼합정밀도에서도 출력은 float32
model = keras.Model(inputs, outputs)                       # 모델 완성

# ---------------------------------------------------------------------------
# 5. 콜백 (조기종료 / LR 감소 / 베스트 저장)
# ---------------------------------------------------------------------------
ckpt = f"{OUT_DIR}/models/best_model.keras"               # inference.py가 찾는 후보 경로
callbacks = [
    keras.callbacks.EarlyStopping(monitor='val_loss', patience=6,
                                  restore_best_weights=True),   # 6에폭 정체 시 중단
    keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                      patience=3, min_lr=1e-7),  # 정체 시 LR 절반
    keras.callbacks.ModelCheckpoint(ckpt, monitor='val_accuracy',
                                    save_best_only=True),        # 최고 정확도 모델 저장
]

# ---------------------------------------------------------------------------
# 6. 1단계 학습 — 헤드만 (백본 동결, 큰 LR)
# ---------------------------------------------------------------------------
model.compile(optimizer=keras.optimizers.Adam(1e-3),       # 헤드 학습엔 1e-3
              loss='sparse_categorical_crossentropy',      # 정수 라벨용 손실
              metrics=['accuracy'])                         # 정확도 모니터
print("\n=== 1단계: 헤드 워밍업 ===")
model.fit(train_ds, validation_data=val_ds,                # 학습
          epochs=EPOCHS_HEAD, callbacks=callbacks)         # 콜백 적용

# ---------------------------------------------------------------------------
# 7. 2단계 학습 — 백본 미세조정 (전체 해제, 아주 작은 LR) ⭐ 정확도 핵심
# ---------------------------------------------------------------------------
base.trainable = True                                      # 백본 전체 학습 허용
# (선택) 하위층은 그대로 두고 상위 일부만: for l in base.layers[:-60]: l.trainable=False
model.compile(optimizer=keras.optimizers.Adam(1e-5),       # 미세조정엔 1e-5(10~100배 작게)
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
print("\n=== 2단계: 전체 미세조정 ===")
model.fit(train_ds, validation_data=val_ds,                # 이어서 학습
          epochs=EPOCHS_FT, callbacks=callbacks)           # EarlyStopping이 종료 결정

# ---------------------------------------------------------------------------
# 8. 평가 — 테스트셋 정확도 / 클래스별 리포트 / 혼동행렬 / 종별 정확도
# ---------------------------------------------------------------------------
print("\n=== 테스트 평가 ===")
y_true = np.concatenate([y.numpy() for _, y in test_ds])   # 실제 라벨(순서 보존)
y_prob = model.predict(test_ds)                            # 예측 확률
y_pred = np.argmax(y_prob, axis=1)                         # 예측 클래스

acc = float(np.mean(y_pred == y_true))                     # 전체 정확도
prec, rec, f1, _ = precision_recall_fscore_support(        # macro 지표
    y_true, y_pred, average='macro', zero_division=0)
print(f"Test Accuracy: {acc*100:.2f}%")                    # 핵심 수치
print(classification_report(y_true, y_pred, target_names=class_names, digits=3))

# 종별(개/고양이) 정확도 — 파일명 IMG_<종>_<클래스>_*.jpg 에서 종 추출
paths = test_ds.file_paths                                 # shuffle=False라 y_true와 순서 일치
species = np.array(['C' if os.path.basename(p).split('_')[1] == 'C' else 'D' for p in paths])
for sp, name in [('D', '반려견'), ('C', '반려묘')]:        # 종별 반복
    m = species == sp                                       # 해당 종 마스크
    if m.sum():                                             # 표본이 있으면
        print(f"{name}({sp}) 정확도: {np.mean(y_pred[m]==y_true[m])*100:.1f}%  ({m.sum()}장)")

# 혼동행렬 그림 저장
import matplotlib                                           # 그림 백엔드
matplotlib.use('Agg')                                       # 화면 없이 파일 저장
import matplotlib.pyplot as plt                             # 플롯
cm = confusion_matrix(y_true, y_pred)                       # 혼동행렬 계산
plt.figure(figsize=(8, 7))                                  # 캔버스
plt.imshow(cm, cmap='Blues')                                # 히트맵
plt.xticks(range(7), class_names, rotation=45)             # x축 라벨
plt.yticks(range(7), class_names)                           # y축 라벨
plt.xlabel('예측'); plt.ylabel('실제'); plt.title('Confusion Matrix')  # 라벨
for i in range(7):                                          # 각 칸에
    for j in range(7):                                      # 숫자 표기
        plt.text(j, i, cm[i, j], ha='center', va='center')
plt.tight_layout()                                          # 여백 정리
plt.savefig(f"{OUT_DIR}/figures/final_confusion_matrix.png", dpi=150)  # 저장

# ---------------------------------------------------------------------------
# 9. 앱 연동용 산출물 저장 (Model Performance 페이지가 자동으로 읽음)
# ---------------------------------------------------------------------------
report = classification_report(y_true, y_pred, target_names=class_names,
                               output_dict=True, zero_division=0)  # dict 형태 리포트
metrics = {                                                 # 앱이 기대하는 키들
    "accuracy": acc, "precision": float(prec),
    "recall": float(rec), "f1": float(f1),
    "class_report": report,                                 # 클래스별 표
}
with open(f"{OUT_DIR}/metrics.json", "w", encoding="utf-8") as f:  # 저장
    json.dump(metrics, f, ensure_ascii=False, indent=2)

model.save(ckpt)                                            # 최종 모델 저장(앱 후보 경로)
print(f"\n저장 완료: {ckpt} / {OUT_DIR}/metrics.json / 혼동행렬 png")
print("→ inference.py 전처리를 '0~255 원본'으로 맞춰야 함(아래 Phase 5 참고)")
