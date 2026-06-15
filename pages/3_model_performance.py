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
# 산출물 로드 (없으면 graceful fallback)
# =========================================================

BASE = Path(__file__).resolve().parent.parent
FIG_DIR = BASE / "outputs" / "figures"
METRICS_FILE = BASE / "outputs" / "metrics.json"


def load_metrics() -> dict:
    """학습 결과 metrics.json이 있으면 읽고, 없으면 빈 dict."""
    if METRICS_FILE.exists():
        with open(METRICS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def show_figure(filename: str, caption: str) -> None:
    """outputs/figures의 이미지를 있으면 표시, 없으면 안내."""
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
        """metrics.json에 값이 있으면 %로, 없으면 '학습 중'."""
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

    left, right = st.columns(2, gap="large")

    with left:
        st.html(
            """
<div class="card">
    <div class="section-title">Confusion Matrix</div>
    <div class="section-desc">
        실제 클래스와 모델 예측 클래스가 어떻게 일치하거나 혼동되는지 확인합니다.
    </div>
</div>
<br>
"""
        )
        show_figure("exp1_confusion_matrix.png", "실험 1 혼동 행렬")

    with right:
        st.html(
            """
<div class="card">
    <div class="section-title">Loss / Accuracy Curve</div>
    <div class="section-desc">
        학습 과정에서 Train과 Validation 성능이 어떻게 변화했는지 확인합니다.
        두 곡선의 간격이 커지면 과적합 가능성을 의심해야 합니다.
    </div>
</div>
<br>
"""
        )
        show_figure("exp1_learning_curve.png", "실험 1 학습 곡선")

    # ---------- 클래스별 성능 표 ----------
    st.html(
        """
<br>
<div class="card">
    <div class="section-title">Class-wise Performance</div>
    <div class="section-desc">
        병변 유형별 Precision, Recall, F1-score를 비교합니다.
    </div>
</div>
<br>
"""
    )

    if "class_report" in metrics:
        # metrics.json 안에 classification_report(dict)가 있으면 표로 변환
        report_df = pd.DataFrame(metrics["class_report"]).T
        st.dataframe(report_df, use_container_width=True)
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
