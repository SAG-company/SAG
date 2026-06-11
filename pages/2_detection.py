import streamlit as st

st.set_page_config(page_title="질환 탐지", page_icon="🔍", layout="wide")

st.title("🔍 질환 탐지")
st.markdown("---")

# ── 1. 이미지 업로드 ──────────────────────────
uploaded_file = st.file_uploader(
    "반려동물 사진을 업로드하세요",
    type=["jpg", "jpeg", "png"]
)
st.write("또는")
camera_image = st.camera_input("카메라로 촬영하기")

image = uploaded_file or camera_image

if image:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📷 원본 이미지")
        st.image(image, use_column_width=True)
    with col2:
        st.subheader("🔥 AI 집중 분석 부위")
        st.info("Grad-CAM 히트맵은 모델 연동 후 표시됩니다")

    st.markdown("---")

    # ── TODO: 아래 더미 데이터를 predict()로 교체 ──
    # from predict import predict
    # result = predict(image)
    # predicted_class = result["class"]
    # confidence = result["confidence"]
    # probabilities = result["probabilities"]
    predicted_class = "연동 전"
    confidence = 0.0
    probabilities = {}

    st.subheader("📋 분석 결과")
    col3, col4 = st.columns(2)
    with col3:
        st.metric("진단 결과", predicted_class)
    with col4:
        st.metric("신뢰도", f"{confidence * 100:.1f}%")

    st.info("🔧 모델 연동 후 정확한 결과가 표시됩니다 (김윤열 연동 예정)")

else:
    st.warning("👆 사진을 업로드하거나 카메라로 촬영하세요.")