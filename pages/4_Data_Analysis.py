import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from ui import inject_global_css, render_nav, render_page_hero


st.set_page_config(
    page_title="Data Analysis | AI 수의사",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
render_nav("Data Analysis")

render_page_hero(
    eyebrow="Dataset Intelligence",
    title="데이터 분석",
    subtitle=(
        "학습 데이터의 구성, 클래스별 분포, 강아지/고양이 비율, 정상/질환 비율, "
        "Train/Validation/Test 분포와 데이터 편향 가능성을 확인합니다."
    ),
)

left_margin, content, right_margin = st.columns([0.06, 0.88, 0.06])

with content:
    st.html(
        """
<div class="metric-band">
    <div class="metric-card">
        <div class="metric-label">전체 이미지 수</div>
        <div class="metric-value">34,987</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">강아지 이미지</div>
        <div class="metric-value">31,003</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">고양이 이미지</div>
        <div class="metric-value">3,984</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">클래스 수</div>
        <div class="metric-value">7</div>
    </div>
</div>
"""
    )

    left, right = st.columns(2, gap="large")

    with left:
        st.html(
            """
<div class="card">
    <div class="section-title">클래스별 데이터 분포</div>
    <div class="section-desc">
        A1~A7 병변 유형별 이미지 수를 확인합니다. 현재 전체 병변 클래스는 비교적 균형적으로 구성되어 있습니다.
    </div>
</div>
<br>
"""
        )

        class_df = pd.DataFrame(
            {
                "Class": ["A1", "A2", "A3", "A4", "A5", "A6", "A7"],
                "Count": [4998, 4999, 4998, 4995, 5000, 4999, 4998],
            }
        )

        st.bar_chart(class_df.set_index("Class"))

    with right:
        st.html(
            """
<div class="card">
    <div class="section-title">강아지 / 고양이 비율</div>
    <div class="section-desc">
        전체 데이터 중 고양이 데이터는 상대적으로 적습니다. 이 점은 서비스 해석과 모델 평가에 반드시 반영해야 합니다.
    </div>
</div>
<br>
"""
        )

        animal_df = pd.DataFrame(
            {
                "Animal": ["Dog", "Cat"],
                "Count": [31003, 3984],
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

    st.html("<br>")

    left2, right2 = st.columns(2, gap="large")

    with left2:
        st.html(
            """
<div class="card">
    <div class="section-title">정상 / 질환 비율</div>
    <div class="section-desc">
        무증상 클래스 A7과 유증상 병변 클래스 A1~A6의 비율을 확인합니다.
    </div>
</div>
<br>
"""
        )

        status_df = pd.DataFrame(
            {
                "Status": ["Symptomatic", "Normal"],
                "Count": [29989, 4998],
            }
        )

        st.bar_chart(status_df.set_index("Status"))

    with right2:
        st.html(
            """
<div class="card">
    <div class="section-title">Train / Validation / Test</div>
    <div class="section-desc">
        학습, 검증, 테스트 데이터가 약 70:15:15 비율로 나뉘어 있습니다.
    </div>
</div>
<br>
"""
        )

        split_df = pd.DataFrame(
            {
                "Split": ["Train", "Validation", "Test"],
                "Count": [24492, 5249, 5246],
            }
        )

        st.bar_chart(split_df.set_index("Split"))

    st.html(
        """
<div class="warning-notice">
    <strong>데이터 편향 및 한계</strong><br>
    고양이 데이터는 전체 데이터 중 약 11.39%로 상대적으로 적습니다.
    또한 일부 병변 클래스에는 고양이 샘플이 포함되어 있지 않아,
    고양이 분석 결과는 병변 유형에 따라 신뢰도가 낮을 수 있습니다.
    이 문제는 augmentation만으로 완전히 해결하기 어렵고,
    고양이 원본 데이터 추가 수집이 필요합니다.
</div>
"""
    )