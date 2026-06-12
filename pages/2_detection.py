import random

import streamlit as st
from PIL import Image

from ui import inject_global_css, render_nav, render_page_hero


st.set_page_config(
    page_title="Detection | Pet Skin Intelligence",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
render_nav("Detection")

render_page_hero(
    eyebrow="AI Skin Detection",
    title="피부 이미지 분석",
    subtitle=(
        "강아지 또는 고양이의 피부 사진을 업로드하면 AI가 병변 유형, 정상 가능성, "
        "위험도와 보호자 행동 가이드를 제공합니다."
    ),
)

st.html('<main class="page-wrap">')

left, right = st.columns([1, 1.15], gap="large")

with left:
    st.html(
        """
<div class="card">
    <div class="section-title">Analysis Input</div>
    <div class="section-desc">
        분석 정확도를 위해 피부 부위가 선명하게 보이는 사진을 업로드하세요.
    </div>
</div>
<br>
"""
    )

    animal = st.selectbox("동물 선택", ["강아지", "고양이"])

    body_part = st.selectbox(
        "부위 선택",
        ["귀", "발", "배", "등", "얼굴", "꼬리", "항문 주변", "기타"],
    )

    symptoms = st.multiselect(
        "관찰되는 증상",
        ["붉어짐", "탈모", "각질", "딱지", "진물", "가려움", "냄새", "발 핥음", "통증"],
    )

    uploaded_file = st.file_uploader(
        "피부 사진 업로드",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

    analyze_button = st.button(
        "RUN AI ANALYSIS",
        use_container_width=True,
        type="primary",
    )

with right:
    st.html(
        """
<div class="dark-card">
    <div class="section-title" style="color:white;">AI Analysis Result</div>
    <div class="mini-text">
        입력된 이미지와 증상 정보를 기반으로 AI 분석 결과가 표시됩니다.
        결과는 병변 유형 후보, 위험도, 신뢰도, 행동 가이드로 구성됩니다.
    </div>
</div>
<br>
"""
    )

    if analyze_button and uploaded_file is not None:
        risk_level = random.choice(
            ["정상 가능성 높음", "관찰 필요", "진료 권장", "빠른 진료 권장"]
        )
        confidence = random.choice(["높음", "보통", "낮음"])

        if risk_level == "빠른 진료 권장":
            st.error(f"위험도: {risk_level}")
        elif risk_level == "진료 권장":
            st.warning(f"위험도: {risk_level}")
        elif risk_level == "관찰 필요":
            st.info(f"위험도: {risk_level}")
        else:
            st.success(f"위험도: {risk_level}")

        st.markdown("### 예측 병변 유형")

        candidates = [
            ("A2 비듬/각질 가능성", 0.42),
            ("A3 태선화/색소 가능성", 0.31),
            ("A7 무증상/정상 가능성", 0.18),
        ]

        for name, score in candidates:
            st.write(f"**{name}**")
            st.progress(score)
            st.caption(f"가능성 점수: {score * 100:.1f}%")

        st.metric("분석 신뢰도", confidence)

        st.markdown("### 보호자 행동 가이드")
        st.write(
            """
            - 증상이 2~3일 이상 지속되면 동물병원 상담을 권장합니다.
            - 진물, 악취, 출혈, 심한 탈모가 있다면 빠른 진료가 필요할 수 있습니다.
            - 사람용 연고나 약을 임의로 사용하지 마세요.
            - 같은 부위를 계속 긁거나 핥는지 관찰하세요.
            """
        )

        if animal == "고양이":
            st.warning(
                "고양이 데이터는 강아지 데이터보다 상대적으로 적어 일부 병변 유형의 분석 신뢰도가 낮을 수 있습니다."
            )

    elif analyze_button and uploaded_file is None:
        st.warning("분석할 피부 사진을 먼저 업로드해주세요.")
    else:
        st.info("왼쪽에서 분석 정보를 입력하고 이미지를 업로드하면 분석 결과가 표시됩니다.")

st.html(
    """
<div class="notice">
    <strong>Medical Notice</strong><br>
    본 결과는 질병명 확정 진단이 아니라 이미지 기반 병변 유형 분석입니다.
    정확한 원인 진단과 치료는 수의사의 진료가 필요합니다.
</div>
</main>
"""
)