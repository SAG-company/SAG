import streamlit as st

st.set_page_config(page_title="Home")

st.title("🐾 AI 수의사")
st.subheader("반려동물의 피부증상, AI 수의사로 확인하세요.")
st.markdown("-----")

# 서비스 소개
st.header("Service")
st.write("AI 수의사는 반려동물의 사진을 분석하여 피부 및 구강 질환 여부를 탐지하는 서비스입니다.")


#팀 정보
st.header("Team")
col1, col2, col3 = st.columns(3)
with col1:
    st.info("유서하 \n 데이터·EDA")
with col2:
    st.info("김윤열 \n 모델링·팀리더")
with col3:
    st.info("한정욱 \n 스트림릿·시각화")

#사용법
st.header("사용법")
st.markdown("""
1. 왼쪽 사이드바에서 **질환 탐지** 메뉴를 선택합니다
2. 반려동물 사진을 업로드합니다
3. AI가 질환 여부를 자동으로 분석합니다
4. 결과를 확인하고 필요 시 동물병원을 방문합니다            
""")