import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

import inference
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


def latest_figure(*patterns: str) -> str:
    """주어진 glob 패턴들에 대해 가장 최근(mtime) 그림 파일명을 반환.

    패턴은 우선순위 순서. 앞 패턴에서 파일을 찾으면 그걸 쓴다.
    재학습으로 새 타임스탬프 그림이 생겨도 자동으로 최신본을 가리키도록 한다.
    못 찾으면 첫 패턴 문자열을 그대로 반환(→ show_figure가 안내문 표시).
    """
    for pat in patterns:
        files = sorted(FIG_DIR.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            return files[0].name
    return patterns[0]


def model_timestamp() -> str:
    """연결된 최종 모델 파일명에서 타임스탬프(예: 20260614_1146)를 추출. 없으면 빈 문자열."""
    path = inference.find_model_path()
    if path is None:
        return ""
    m = re.search(r"(\d{8}_\d{4})", path.name)
    return m.group(1) if m else ""


TS = model_timestamp()  # 그림을 '연결된 모델'과 동일 학습 run에 맞추기 위한 타임스탬프
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

    if metrics:
        st.caption(
            f"위 지표는 최종 모델 **EfficientNetB3** 를 테스트셋으로 평가한 결과입니다."
            + (f" (모델: `{metrics['model_file']}`)" if metrics.get("model_file") else "")
        )
    else:
        st.info(
            "아직 `outputs/metrics.json` 이 없습니다. "
            "`python _eval_testset.py 0` 으로 테스트셋 평가를 실행하면 지표가 자동으로 채워집니다."
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
        show_figure(
            latest_figure(
                "eval_confusion_matrix.png",
                f"confusion_matrix_{TS}.png" if TS else "confusion_matrix_*.png",
                "confusion_matrix_*.png",
            ),
            "EfficientNetB3 혼동 행렬 (테스트셋)",
        )

    with cm_text:
        st.markdown("#### 해석")
        st.markdown(
            """
**대각선이 밝을수록** 해당 클래스를 올바르게 분류한 비율이 높다는 의미입니다. (EfficientNetB3 · 테스트 5,246장)

- **A2(비듬/각질) ↔ A3(태선화/색소)** 혼동이 가장 큽니다. 실제 A3의 약 21%가 A2로, A2의 약 17%가 A3로 잘못 분류됩니다. 색상·질감이 유사해 EDA 예측대로 모델도 구분에 어려움을 겪습니다.
- **A5(미란/궤양, F1 0.74), A6(결절/종괴, F1 0.72)** 가 가장 잘 분류됩니다. 외형이 뚜렷해 대각선이 가장 밝습니다.
- **A7(무증상/정상)** 은 재현율이 낮습니다(0.40). 정상 피부의 약 19%를 A2(비듬)로 오인하는데, 이는 모델이 '정상'보다 '이상' 쪽으로 보수적으로 판단한다는 뜻이라 초기 선별 도구로는 안전한 방향입니다.
- **A2(비듬/각질, F1 0.44)** 가 가장 낮습니다. 여러 클래스의 오분류가 A2로 몰리는 경향이 있습니다.
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
        show_figure(
            latest_figure(
                f"phase2_curves_{TS}.png" if TS else "phase2_curves_*.png",
                f"phase1_curves_{TS}.png" if TS else "phase1_curves_*.png",
                "phase2_curves_*.png",
                "phase1_curves_*.png",
            ),
            "EfficientNetB3 학습 곡선 (Phase 2: Fine-tuning)",
        )

    with lc_text:
        st.markdown("#### 해석")
        st.markdown(
            """
**Train / Validation 두 곡선의 관계**로 학습 상태를 진단합니다.

- **두 곡선이 함께 수렴** → 학습이 안정적으로 진행된 정상 상태입니다.
- **Train만 계속 향상, Validation 정체·하락** → 과적합(overfitting) 신호입니다. Dropout 강화, 데이터 증강, 조기 종료(Early Stopping)가 필요합니다.
- **둘 다 개선되지 않음** → 학습률이 너무 낮거나 모델 표현력이 부족한 과소적합(underfitting) 상태입니다.
- 최종 모델은 EfficientNetB3를 **2단계**로 학습했습니다. **Phase 1**은 백본을 고정(freeze)하고 분류 헤드만 학습해 빠르게 수렴시키고, **Phase 2**는 백본 상위층을 풀어(fine-tuning) 정확도를 끌어올립니다. 위 곡선은 Phase 2(fine-tuning) 구간으로, Validation 성능이 한 단계 더 상승하는 지점을 확인할 수 있습니다.
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
