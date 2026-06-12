"""
exp1_baseline.ipynb에 tf.data 파이프라인 최적화 셀을 추가하는 스크립트.
Jupyter 커널이 멈춘 뒤 실행하세요: python patch_notebook.py
"""
import json, copy, uuid
from pathlib import Path

NB_PATH = Path(__file__).parent / "exp1_baseline.ipynb"

def make_code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "outputs": [],
        "execution_count": None,
        "source": source,
    }

def make_md_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "source": source,
    }

# ── 추가할 셀 내용 ──────────────────────────────────────────

CPU_OPT = """\
# ── CPU 성능 최적화 (i7-10700K: 8코어 / 16스레드) ──
tf.config.threading.set_intra_op_parallelism_threads(16)
tf.config.threading.set_inter_op_parallelism_threads(8)
tf.config.optimizer.set_jit(True)  # XLA JIT 컴파일 활성화

print(f"intra_op threads : {tf.config.threading.get_intra_op_parallelism_threads()}")
print(f"inter_op threads : {tf.config.threading.get_inter_op_parallelism_threads()}")
print("XLA JIT 컴파일   : 활성화")\
"""

TFDATA_MD = """\
## 3-2. tf.data 파이프라인 (성능 최적화)

`ImageDataGenerator` 대신 `tf.data` API를 사용합니다. 기존 Generator 코드는 참조용으로 유지됩니다.

| 기능 | 효과 |
|------|------|
| `num_parallel_calls=AUTOTUNE` | CPU 멀티스레드 병렬 이미지 로딩 |
| `.cache()` | 32GB RAM에 전처리 결과 캐시 → 2회차 에폭부터 디스크 I/O 없음 |
| `.prefetch(AUTOTUNE)` | 다음 배치를 학습 중에 미리 준비 |\
"""

TFDATA_CODE = """\
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

AUTOTUNE = tf.data.AUTOTUNE

# 라벨 인코더: A1~A7 알파벳 순 (train_generator.class_indices와 동일 순서)
le = LabelEncoder()
le.fit(sorted(df_train['lesion'].unique()))

def load_and_preprocess(path, label):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = tf.cast(img, tf.float32) / 255.0
    return img, label

def make_dataset(df, shuffle=False):
    paths = df[target_col].values
    labels = to_categorical(le.transform(df['lesion']), num_classes=NUM_CLASSES).astype('float32')
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(load_and_preprocess, num_parallel_calls=AUTOTUNE)
    ds = ds.cache()          # 32GB RAM에 전처리 결과 캐시
    if shuffle:
        ds = ds.shuffle(buffer_size=2048, seed=42)
    ds = ds.batch(BATCH_SIZE)
    ds = ds.prefetch(AUTOTUNE)
    return ds

train_dataset = make_dataset(df_train, shuffle=True)
val_dataset   = make_dataset(df_val,   shuffle=False)
test_dataset  = make_dataset(df_test,  shuffle=False)

print("✅ tf.data 파이프라인 완료")
print(f"  클래스 순서  : {list(le.classes_)}")
print(f"  Train 배치 수: {len(train_dataset)}")
print(f"  Val 배치 수  : {len(val_dataset)}")
print(f"  Test 배치 수 : {len(test_dataset)}")\
"""

MODEL_FIT = """\
print("=" * 50)
print("🚀 실험 1: Baseline CNN 학습 시작 (tf.data 최적화)")
print("=" * 50)

history = model.fit(
    train_dataset,               # ← tf.data Dataset (기존: train_generator)
    epochs=EPOCHS,
    validation_data=val_dataset, # ← tf.data Dataset (기존: val_generator)
    callbacks=callbacks,
    verbose=1
)

print("\\n✅ 학습 완료!")
print(f"   실제 학습 에폭 수: {len(history.history['loss'])}회")\
"""

EVALUATE = """\
print("=" * 50)
print("📝 테스트 데이터 평가")
print("=" * 50)

test_loss, test_acc = model.evaluate(test_dataset, verbose=1)  # ← tf.data Dataset

print(f"\\n테스트 Loss    : {test_loss:.4f}")
print(f"테스트 Accuracy: {test_acc:.4f} ({test_acc*100:.1f}%)")\
"""

PREDICT = """\
y_pred_proba = model.predict(test_dataset)  # ← tf.data Dataset
y_pred = np.argmax(y_pred_proba, axis=1)

# tf.data Dataset에서 실제 라벨 추출 (원핫인코딩 → 클래스 인덱스)
y_true = np.concatenate([
    np.argmax(labels.numpy(), axis=1) for _, labels in test_dataset
])

class_names = list(le.classes_)
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

print("=== Classification Report ===")
print(classification_report(y_true, y_pred, target_names=class_labels))\
"""

# ── 노트북 수정 ─────────────────────────────────────────────

nb = json.loads(NB_PATH.read_text(encoding="utf-8"))
cells = nb["cells"]

def find_cell(cell_id: str):
    for i, c in enumerate(cells):
        if c.get("id") == cell_id:
            return i
    return -1

def replace_cell_source(cell_id: str, new_source: str):
    idx = find_cell(cell_id)
    if idx == -1:
        print(f"  ⚠️  셀 ID {cell_id} 를 찾지 못했습니다.")
        return
    cells[idx] = {**cells[idx], "source": new_source, "outputs": [], "execution_count": None}
    print(f"  ✅ 셀 {cell_id} 교체 완료")

def insert_after(cell_id: str, new_cells: list):
    idx = find_cell(cell_id)
    if idx == -1:
        print(f"  ⚠️  셀 ID {cell_id} 를 찾지 못했습니다.")
        return
    for offset, cell in enumerate(new_cells):
        cells.insert(idx + 1 + offset, cell)
    print(f"  ✅ 셀 {cell_id} 뒤에 {len(new_cells)}개 삽입 완료")

print("▶ 패치 시작...")

# 1. 임포트 셀(30dae91f) 뒤에 CPU 최적화 셀 삽입
insert_after("30dae91f", [make_code_cell(CPU_OPT)])

# 2. Generator 셀(7fc51e69) 뒤에 tf.data 섹션 삽입 (markdown + code)
insert_after("7fc51e69", [make_md_cell(TFDATA_MD), make_code_cell(TFDATA_CODE)])

# 3. model.fit 셀(d8adf885) 교체
replace_cell_source("d8adf885", MODEL_FIT)

# 4. evaluate 셀(1528a0f4) 교체
replace_cell_source("1528a0f4", EVALUATE)

# 5. predict 셀(7e8042b4) 교체
replace_cell_source("7e8042b4", PREDICT)

NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n✅ 패치 완료 → {NB_PATH}")
print("   Jupyter에서 노트북을 다시 열거나 Reload 하면 변경사항이 반영됩니다.")
