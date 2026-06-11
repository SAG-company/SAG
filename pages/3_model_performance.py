import streamlit as st

st.set_page_config(page_title="모델 성능", page_icon="📈", layout="wide")

st.title("📈 모델 성능")
st.markdown("---")

st.info("🔧 모델 학습 완료 후 결과가 표시됩니다 (김윤열 연동 예정)")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Accuracy", "-")
with col2:
    st.metric("F1-Score", "-")
with col3:
    st.metric("ROC-AUC", "-")

st.markdown("---")

col4, col5 = st.columns(2)
with col4:
    st.subheader("📊 Confusion Matrix")
    st.empty()  # 김윤열 결과 연동 후 채워질 자리

with col5:
    st.subheader("📉 학습 곡선")
    st.empty()  # 김윤열 결과 연동 후 채워질 자리