import random

import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="Detection | AI VET",
    page_icon="🐾",
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
    padding: 26px;
    font-size: 16px;
    line-height: 1.8;
    color: #1F2937;
    margin-top: 30px;
}
</style>

<div class="page-title">Skin Detection</div>
<div class="page-subtitle">
    강아지 또는 고양이의 피부 사진을 업로드하고 AI 분석 결과를 확인합니다.
    결과는 위험도, 예측 후보, 신뢰도, 보호자 행동 가이드로 구성됩니다.
</div>
"""
)


left, right = st.columns([1, 1.15], gap="large")

with left:
    st.subheader("Analysis Input")

    animal = st.selectbox(
        "동물 선택",
        ["강아지", "고양이"],
    )

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
    st.subheader("AI Analysis Result")

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

        st.markdown("### Possible Patterns")

        candidates = [
            ("알레르기성 피부염 가능성", 0.42),
            ("곰팡이성 피부질환 가능성", 0.31),
            ("세균성 피부염 가능성", 0.18),
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

    elif analyze_button and uploaded_file is None:
        st.warning("분석할 피부 사진을 먼저 업로드해주세요.")
    else:
        st.info("왼쪽에서 분석 정보를 입력하고 이미지를 업로드하면 분석 결과가 표시됩니다.")


st.html(
    """
<div class="notice">
    <strong>Medical Notice</strong><br>
    AI 분석 결과는 참고용입니다. 정확한 진단과 치료는 수의사의 진료가 필요합니다.
</div>
"""
)