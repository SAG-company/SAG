import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Model Performance | AI VET",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.html(
    """
<style>
header, footer, #MainMenu {
    visibility: hidden;
}

.block-container {
    padding-top: 2.5rem;
    padding-left: 4.5rem;
    padding-right: 4.5rem;
    max-width: 100%;
}

.page-title {
    font-size: 52px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 12px;
}

.page-subtitle {
    font-size: 18px;
    line-height: 1.8;
    color: #4B5563;
    max-width: 940px;
    margin-bottom: 40px;
}

.notice {
    background: #EEF4FF;
    border-left: 6px solid #13284B;
    border-radius: 14px;
    padding: 28px;
    font-size: 16px;
    line-height: 1.8;
    color: #1F2937;
    margin-top: 30px;
}
</style>

<div class="page-title">Model Performance</div>
<div class="page-subtitle">
    AI 피부 분석 모델의 성능 지표를 확인합니다.
    정확도뿐 아니라 Precision, Recall, F1-score, Confusion Matrix를 함께 확인해야 합니다.
</div>
"""
)


col1, col2, col3, col4 = st.columns(4)

col1.metric("Accuracy", "91.2%")
col2.metric("Precision", "89.7%")
col3.metric("Recall", "88.4%")
col4.metric("F1-score", "89.0%")

st.markdown("---")

left, right = st.columns(2, gap="large")

with left:
    st.subheader("Confusion Matrix")

    matrix = np.array(
        [
            [120, 8, 5, 3],
            [10, 95, 7, 6],
            [6, 9, 88, 10],
            [4, 5, 8, 102],
        ]
    )

    classes = ["Normal", "Allergy", "Fungal", "Bacterial"]

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
    st.subheader("Class-wise Performance")

    performance_df = pd.DataFrame(
        {
            "Class": ["Normal", "Allergy", "Fungal", "Bacterial"],
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

st.markdown("---")

st.subheader("Loss / Accuracy Curve")

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
<div class="notice">
    <strong>모델 한계 설명</strong><br>
    본 모델은 학습 데이터와 유사한 촬영 조건에서 더 안정적으로 작동합니다.
    어두운 사진, 흔들린 사진, 병변 부위가 작게 보이는 사진, 털에 가려진 사진에서는
    분석 신뢰도가 낮아질 수 있습니다. 또한 특정 질환 클래스의 데이터가 부족한 경우
    해당 질환에 대한 예측 성능이 제한될 수 있습니다.
</div>
"""
)