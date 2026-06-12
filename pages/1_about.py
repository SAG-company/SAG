import streamlit as st
from ui import inject_global_css, render_nav, render_page_hero


st.set_page_config(
    page_title="About | Pet Skin Intelligence",
    page_icon="ℹ️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
render_nav("About")

render_page_hero(
    eyebrow="About the Platform",
    title="AI 기반 반려동물 피부 분석 플랫폼",
    subtitle=(
        "Pet Skin Intelligence는 강아지와 고양이의 피부 사진에서 병변 유형과 이상 징후를 분석하고, "
        "보호자가 진료 필요도를 판단할 수 있도록 돕는 AI 기반 초기 선별 서비스입니다."
    ),
)

st.html('<main class="page-wrap">')

st.html(
    """
<div class="card">
    <div class="section-title">서비스 목적</div>
    <div class="section-desc">
        보호자는 반려동물이 피부를 긁거나, 털이 빠지거나, 붉은 병변이 보일 때
        병원에 바로 가야 할지 판단하기 어렵습니다. 이 서비스는 사진 기반 AI 분석을 통해
        피부 이상 가능성을 빠르게 확인하고, 보호자가 다음 행동을 결정할 수 있도록 돕습니다.
    </div>
</div>

<br>

<div class="grid-3">
    <div class="card">
        <div class="mini-title">1. 피부 사진 기반 분석</div>
        <div class="mini-text">
            업로드된 이미지에서 피부 색상, 병변 형태, 탈모, 각질, 염증 가능성 등을 분석합니다.
        </div>
    </div>

    <div class="card">
        <div class="mini-title">2. 병변 유형 분류</div>
        <div class="mini-text">
            현재 데이터 구조상 질병명을 확정하기보다 사진상 관찰되는 병변 유형을 분류합니다.
        </div>
    </div>

    <div class="card">
        <div class="mini-title">3. 진료 필요도 안내</div>
        <div class="mini-text">
            정상 가능성, 관찰 필요, 진료 권장, 빠른 진료 권장 등으로 위험도를 안내합니다.
        </div>
    </div>
</div>

<br>

<div class="card">
    <div class="section-title">현재 모델의 해석 기준</div>
    <div class="section-desc">
        본 프로젝트의 현재 라벨은 알레르기, 곰팡이, 세균성 피부염 같은 확정 질병명보다는
        구진/플라크, 비듬/각질, 태선화/색소, 농포/여드름, 미란/궤양, 결절/종괴, 무증상과 같은
        피부 병변 형태에 가깝습니다. 따라서 프론트에서도 “질병 진단”이 아니라
        “병변 유형 분석과 진료 필요도 안내”로 표현하는 것이 정확합니다.
    </div>
</div>

<div class="warning-notice">
    <strong>중요 안내</strong><br>
    AI 분석 결과는 수의사의 진단을 대체하지 않습니다. 진물, 악취, 출혈, 심한 가려움,
    급격한 탈모, 식욕 저하, 통증 반응이 있는 경우 반드시 동물병원 진료를 권장합니다.
</div>
"""
)

st.html("</main>")