import streamlit as st

st.set_page_config(page_title="데이터 분석", page_icon="📊", layout="wide")

st.title("📊 데이터 분석")
st.markdown("---")

st.info("🔧 EDA 완료 후 결과가 표시됩니다 (유서하 연동 예정)")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("전체 이미지 수", "-")
with col2:
    st.metric("유증상", "-")
with col3:
    st.metric("무증상", "-")

st.markdown("---")

col4, col5 = st.columns(2)
with col4:
    st.subheader("📊 클래스 분포")
    st.empty()  # 유서하 EDA 차트 연동 후 채워질 자리

with col5:
    st.subheader("🖼️ 샘플 이미지")
    st.empty()  # 유서하 샘플 이미지 연동 후 채워질 자리