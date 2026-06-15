import json
from pathlib import Path

import pandas as pd
import streamlit as st

from ui import inject_global_css, render_nav, render_page_hero


st.set_page_config(
    page_title="Model Performance | AI 수의사",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
render_nav("Model Performance")

render_page_hero(
    eyebrow="Model Transparency",
    title="모델 성능 분석",
    subtitle=(
        "AI 피부 분석 모델의 Accuracy, Precision, Recall, F1-score와 Confusion Matrix를 통해 "
        "모델의 신뢰도와 한계를 투명하게 확인합니다."
    ),
)


# =========================================================
# 산출물 로드
# =========================================================

BASE = Path(__file__).resolve().parent.parent
FIG_DIR = BASE / "outputs" / "figures"
METRICS_FILE = BASE / "outputs" / "metrics.json"


def load_metrics() -> dict:
    if METRICS_FILE.exists():
        with open(METRICS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def show_figure(filename: str, caption: str) -> None:
    path = FIG_DIR / filename
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info(f"`{filename}` 산출물이 아직 없습니다. 학습 완료 후 자동 표시됩니다.")


metrics = load_metrics()

left_margin, content, right_margin = st.columns([0.06, 0.88, 0.06])

with content:

    # ---------- 핵심 지표 밴드 ----------
    def metric_value(key: str) -> str:
        if key in metrics:
            return f"{metrics[key] * 100:.1f}%"
        return "학습 중"

    st.html(
        f"""
<div class="metric-band">
    <div class="metric-card">
        <div class="metric-label">Accuracy</div>
        <div class="metric-value">{metric_value('accuracy')}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Precision</div>
        <div class="metric-value">{metric_value('precision')}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Recall</div>
        <div class="metric-value">{metric_value('recall')}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">F1-score</div>
        <div class="metric-value">{metric_value('f1')}</div>
    </div>
</div>
"""
    )

    if not metrics:
        st.info(
            "현재 표시되는 도표는 **실험 1(Baseline CNN)**의 산출물입니다. "
            "최종 모델(MobileNetV3) 학습이 끝나면 `outputs/metrics.json`을 통해 "
            "지표가 자동으로 채워집니다."
        )

    st.html("<br>")

    # =========================================================
    # Confusion Matrix + 해석
    # =========================================================
    st.html(
        """
<div class="card">
    <div class="section-title">Confusion Matrix</div>
    <div class="section-desc">실제 클래스와 모델 예측 클래스가 어떻게 일치하거나 혼동되는지 확인합니다.</div>
</div>
<br>
"""
    )

    cm_chart, cm_text = st.columns([3, 2], gap="large")

    with cm_chart:
        show_figure("exp1_confusion_matrix.png", "실험 1 혼동 행렬")

    with cm_text:
        st.markdown("#### 해석")
        st.markdown(
            """
**대각선이 밝을수록** 해당 클래스를 올바르게 분류한 비율이 높다는 의미입니다.

- **A1(구진/플라크) ↔ A2(비듬/각질)** 간 혼동이 가장 많습니다. 두 병변이 시각적으로 유사하여 모델도 구분에 어려움을 겪습니다.
- **A7(무증상/정상)** 은 다른 병변과 외형 차이가 비교적 뚜렷해 분류 성능이 상대적으로 높습니다.
- **A5(미란/궤양), A6(결절/종괴)** 는 데이터 수가 적고 외형 다양성이 커서 오분류 빈도가 높을 수 있습니다.
- 고양이 전용 샘플이 일부 클래스에 없어 고양이 이미지 입력 시 특정 병변 예측이 불안정할 수 있습니다.
"""
        )

    st.html("<br>")

    # =========================================================
    # Learning Curve + 해석
    # =========================================================
    st.html(
        """
<div class="card">
    <div class="section-title">Loss / Accuracy Curve</div>
    <div class="section-desc">학습 과정에서 Train과 Validation 성능이 어떻게 변화했는지 확인합니다.</div>
</div>
<br>
"""
    )

    lc_chart, lc_text = st.columns([3, 2], gap="large")

    with lc_chart:
        show_figure("exp1_learning_curve.png", "실험 1 학습 곡선")

    with lc_text:
        st.markdown("#### 해석")
        st.markdown(
            """
**Train / Validation 두 곡선의 관계**로 학습 상태를 진단합니다.

- **두 곡선이 함께 수렴** → 학습이 안정적으로 진행된 정상 상태입니다.
- **Train만 계속 향상, Validation 정체·하락** → 과적합(overfitting) 신호입니다. Dropout 강화, 데이터 증강, 조기 종료(Early Stopping)가 필요합니다.
- **둘 다 개선되지 않음** → 학습률이 너무 낮거나 모델 표현력이 부족한 과소적합(underfitting) 상태입니다.
- 현재 실험 1은 Baseline CNN으로 **backbone을 고정**하여 학습했기 때문에 Validation Accuracy의 상한이 낮게 나타납니다. 전체 레이어 fine-tuning 시 유의미한 성능 향상이 기대됩니다.
"""
        )

    st.html("<br>")

    # =========================================================
    # Class-wise Performance + 해석
    # =========================================================
    st.html(
        """
<div class="card">
    <div class="section-title">Class-wise Performance</div>
    <div class="section-desc">병변 유형별 Precision, Recall, F1-score를 비교합니다.</div>
</div>
<br>
"""
    )

    if "class_report" in metrics:
        cw_chart, cw_text = st.columns([3, 2], gap="large")

        with cw_chart:
            report_df = pd.DataFrame(metrics["class_report"]).T
            st.dataframe(report_df, use_container_width=True)

        with cw_text:
            st.markdown("#### 해석")
            st.markdown(
                """
- **Precision(정밀도)** 이 낮으면 실제 정상인데 병변으로 잘못 경보(False Positive)가 많다는 뜻입니다.
- **Recall(재현율)** 이 낮으면 실제 병변인데 정상으로 놓치는(False Negative) 경우가 많습니다. 의료 맥락에서는 Recall을 더 중요하게 봅니다.
- **F1-score** 는 둘의 조화평균으로, 클래스 불균형 상황에서 종합 지표로 활용합니다.
- F1이 낮은 클래스는 데이터 추가 수집 또는 클래스 가중치 조정 우선 대상입니다.
"""
            )
    else:
        st.info("클래스별 지표는 최종 모델 평가(classification_report) 후 표시됩니다.")

    st.html(
        """
<div class="warning-notice">
    <strong>모델 한계 설명</strong><br>
    본 모델은 학습 데이터와 유사한 촬영 조건에서 더 안정적으로 작동합니다.
    특히 고양이 일부 병변 클래스는 데이터가 부족하거나 존재하지 않아,
    고양이 분석 결과는 병변 유형에 따라 신뢰도가 낮을 수 있습니다.
</div>
"""
    )
