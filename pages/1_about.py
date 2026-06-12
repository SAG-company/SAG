import streamlit as st


st.set_page_config(
    page_title="About | AI VET",
    page_icon="ℹ️",
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
    margin-bottom: 14px;
}

.page-subtitle {
    font-size: 18px;
    line-height: 1.8;
    color: #4B5563;
    max-width: 900px;
    margin-bottom: 44px;
}

.section-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 24px;
    padding: 36px;
    box-shadow: 0 14px 34px rgba(17,24,39,0.06);
    margin-bottom: 28px;
}

.card-title {
    font-size: 28px;
    font-weight: 800;
    color: #13284B;
    margin-bottom: 14px;
}

.card-text {
    font-size: 17px;
    line-height: 1.85;
    color: #374151;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}

.mini-card {
    background: #F7F8FA;
    border: 1px solid #E5E7EB;
    border-radius: 18px;
    padding: 28px;
}

.mini-title {
    font-size: 21px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 12px;
}

.mini-text {
    font-size: 16px;
    line-height: 1.7;
    color: #4B5563;
}

.notice {
    background: #EEF4FF;
    border-left: 6px solid #13284B;
    border-radius: 14px;
    padding: 30px;
    font-size: 17px;
    line-height: 1.85;
    color: #1F2937;
}

@media (max-width: 1000px) {
    .grid {
        grid-template-columns: 1fr;
    }
}
</style>

<div class="page-title">About Pet Skin Intelligence</div>

<div class="page-subtitle">
    Pet Skin Intelligence는 강아지와 고양이의 피부 사진을 기반으로
    피부 이상 징후, 가능한 질환 패턴, 진료 필요도를 분석하는 AI 기반 초기 선별 서비스입니다.
</div>

<div class="section-card">
    <div class="card-title">서비스 목적</div>
    <div class="card-text">
        보호자는 반려동물이 피부를 긁거나, 털이 빠지거나, 붉은 병변이 보일 때
        병원에 바로 가야 할지 판단하기 어렵습니다. 이 서비스는 사진 기반 AI 분석을 통해
        피부 이상 가능성을 빠르게 확인하고, 보호자가 다음 행동을 결정할 수 있도록 돕습니다.
    </div>
</div>

<div class="grid">
    <div class="mini-card">
        <div class="mini-title">1. 사진 기반 분석</div>
        <div class="mini-text">
            사용자가 업로드한 피부 사진에서 색상, 병변 형태, 탈모, 염증 가능성을 분석합니다.
        </div>
    </div>

    <div class="mini-card">
        <div class="mini-title">2. 위험도 분류</div>
        <div class="mini-text">
            결과를 단순 병명으로 제시하지 않고 정상 가능성, 관찰 필요, 진료 권장 등으로 분류합니다.
        </div>
    </div>

    <div class="mini-card">
        <div class="mini-title">3. 행동 가이드</div>
        <div class="mini-text">
            병원 방문이 필요한 증상, 보호자가 관찰해야 할 항목, 주의사항을 함께 제공합니다.
        </div>
    </div>
</div>

<br>

<div class="section-card">
    <div class="card-title">분석 가능한 주요 증상</div>
    <div class="card-text">
        붉어짐, 탈모, 각질, 딱지, 진물, 가려움, 냄새, 발 핥음, 귀 주변 이상, 피부 변색 등
        외형적으로 확인 가능한 피부 증상을 중심으로 분석합니다.
    </div>
</div>

<div class="notice">
    <strong>중요 안내</strong><br>
    본 서비스는 수의사의 진단을 대체하지 않습니다.
    AI 분석 결과는 참고용이며, 진물, 악취, 출혈, 심한 가려움, 급격한 탈모, 식욕 저하,
    통증 반응 등이 있는 경우 반드시 동물병원 진료를 권장합니다.
</div>
"""
)