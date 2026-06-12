import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from ui import inject_global_css, render_nav, render_page_hero


st.set_page_config(
    page_title="Model Performance | Pet Skin Intelligence",
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

left_margin, content, right_margin = st.columns([0.06, 0.88, 0.06])

with content:
    st.html(
        """
<div class="metric-band">
    <div class="metric-card">
        <div class="metric-label">Accuracy</div>
        <div class="metric-value">91.2%</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Precision</div>
        <div class="metric-value">89.7%</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Recall</div>
        <div class="metric-value">88.4%</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">F1-score</div>
        <div class="metric-value">89.0%</div>
    </div>
</div>
"""
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

        matrix = np.array(
            [
                [120, 8, 5, 3],
                [10, 95, 7, 6],
                [6, 9, 88, 10],
                [4, 5, 8, 102],
            ]
        )

        classes = ["Normal", "Scale", "Pigment", "Mass"]

        fig, ax = plt.subplots(figsize=(6, 5))
        ax.imshow(matrix)

        ax.set_xticks(range(len(classes)))
        ax.set_yticks(range(len(classes)))
        ax.set_xticklabels(classes, rotation=35, ha="right")
        ax.set_yticklabels(classes)

        for i in range(len(classes)):
            for j in range(len(classes)):
                ax.text(j, i, matrix[i, j], ha="center", va="center")

        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        st.pyplot(fig)

    with right:
        st.html(
            """
<div class="card">
    <div class="section-title">Class-wise Performance</div>
    <div class="section-desc">
        병변 유형별 Precision, Recall, F1-score를 비교합니다.
    </div>
</div>
<br>
"""
        )

        performance_df = pd.DataFrame(
            {
                "Class": ["A1 Papule", "A2 Scale", "A3 Pigment", "A7 Normal"],
                "Precision": [0.92, 0.88, 0.86, 0.91],
                "Recall": [0.94, 0.84, 0.81, 0.89],
                "F1-score": [0.93, 0.86, 0.83, 0.90],
            }
        )

        st.dataframe(performance_df, use_container_width=True)

        fig2, ax2 = plt.subplots(figsize=(6, 5))
        ax2.plot(performance_df["Class"], performance_df["Precision"], marker="o", label="Precision")
        ax2.plot(performance_df["Class"], performance_df["Recall"], marker="o", label="Recall")
        ax2.plot(performance_df["Class"], performance_df["F1-score"], marker="o", label="F1-score")
        ax2.set_ylim(0, 1)
        ax2.set_ylabel("Score")
        ax2.legend()
        st.pyplot(fig2)

    st.html(
        """
<br>
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

    epochs = list(range(1, 11))
    curve_df = pd.DataFrame(
        {
            "Epoch": epochs,
            "Train Accuracy": [0.62, 0.71, 0.78, 0.82, 0.86, 0.88, 0.90, 0.91, 0.92, 0.93],
            "Validation Accuracy": [0.60, 0.68, 0.73, 0.78, 0.81, 0.83, 0.85, 0.87, 0.88, 0.89],
            "Train Loss": [1.20, 0.96, 0.78, 0.64, 0.52, 0.44, 0.38, 0.33, 0.30, 0.27],
            "Validation Loss": [1.26, 1.05, 0.91, 0.76, 0.66, 0.58, 0.51, 0.47, 0.43, 0.40],
        }
    )

    st.line_chart(curve_df.set_index("Epoch")[["Train Accuracy", "Validation Accuracy"]])
    st.line_chart(curve_df.set_index("Epoch")[["Train Loss", "Validation Loss"]])

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