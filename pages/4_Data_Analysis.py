import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Analysis | AI VET",
    page_icon="📁",
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

<div class="page-title">Data Analysis</div>
<div class="page-subtitle">
    학습 데이터의 구성, 클래스별 분포, 정상/질환 비율, 데이터 편향 가능성을 확인합니다.
    데이터 분석은 모델 신뢰도와 서비스 품질을 판단하는 핵심 근거입니다.
</div>
"""
)


col1, col2, col3, col4 = st.columns(4)

col1.metric("전체 이미지 수", "12,480")
col2.metric("강아지 이미지", "7,920")
col3.metric("고양이 이미지", "4,560")
col4.metric("질환 클래스 수", "8")

st.markdown("---")

left, right = st.columns(2, gap="large")

with left:
    st.subheader("클래스별 데이터 분포")

    class_df = pd.DataFrame(
        {
            "Class": [
                "Normal",
                "Allergy",
                "Fungal",
                "Bacterial",
                "Scabies",
                "Hotspot",
                "Alopecia",
                "Wound",
            ],
            "Count": [3200, 2100, 1600, 1800, 900, 1100, 950, 830],
        }
    )

    st.bar_chart(class_df.set_index("Class"))

with right:
    st.subheader("강아지 / 고양이 비율")

    animal_df = pd.DataFrame(
        {
            "Animal": ["Dog", "Cat"],
            "Count": [7920, 4560],
        }
    )

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(
        animal_df["Count"],
        labels=animal_df["Animal"],
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.axis("equal")

    st.pyplot(fig)

st.markdown("---")

left2, right2 = st.columns(2, gap="large")

with left2:
    st.subheader("정상 / 질환 비율")

    status_df = pd.DataFrame(
        {
            "Status": ["Normal", "Abnormal"],
            "Count": [3200, 9280],
        }
    )

    st.bar_chart(status_df.set_index("Status"))

with right2:
    st.subheader("Train / Validation / Test 분포")

    split_df = pd.DataFrame(
        {
            "Split": ["Train", "Validation", "Test"],
            "Count": [8736, 1872, 1872],
        }
    )

    st.bar_chart(split_df.set_index("Split"))

st.html(
    """
<div class="notice">
    <strong>데이터 편향 및 한계</strong><br>
    강아지 이미지가 고양이 이미지보다 많을 경우, 고양이 피부질환 분석 성능이 상대적으로 낮을 수 있습니다.
    특정 질환 클래스의 데이터 수가 부족하면 해당 질환에 대한 Recall이 낮아질 수 있습니다.
    촬영 조명, 털 길이, 피부색, 병변 위치, 이미지 해상도에 따라 모델 성능이 달라질 수 있습니다.
    실제 서비스에서는 업로드 이미지 품질 검사를 추가하는 것이 필요합니다.
</div>
"""
)