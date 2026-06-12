import base64
from pathlib import Path

import streamlit as st

from ui import inject_global_css, render_nav


st.set_page_config(
    page_title="AI 수의사",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def image_to_base64(path: str) -> str:
    image_path = Path(path)

    if not image_path.exists():
        return ""

    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode()


inject_global_css()
render_nav("Home")

hero_base64 = image_to_base64("assets/hero_pet_skin.png")

if hero_base64:
    hero_background = (
        "linear-gradient(rgba(0,0,0,0.05), rgba(0,0,0,0.08)), "
        f"url('data:image/png;base64,{hero_base64}')"
    )
else:
    hero_background = "linear-gradient(135deg, #08111F, #13284B)"


st.html(
    f"""
<section class="home-hero" style="background-image: {hero_background};">
    <div class="home-hero-inner">
        <div class="home-hero-text">
            <div class="home-title">AI 수의사</div>
            <div class="home-desc">
                강아지와 고양이의 피부 사진을 기반으로<br>
                AI가 피부 이상 징후와 가능한 병변 유형,<br>
                진료 필요도를 분석합니다.
            </div>

            <div class="btn-row">
                <a class="btn-primary" href="/Detection" target="_self">분석 시작하기</a>
                <a class="btn-secondary" href="/About" target="_self">서비스 소개</a>
            </div>
        </div>
    </div>
</section>

<section class="feature-strip">
    <div class="feature">
        <div class="feature-title">피부 이미지 분석</div>
        <div class="feature-desc">
            강아지와 고양이의 피부 이미지를 업로드하고 AI 분석 결과를 확인합니다.
        </div>
    </div>

    <div class="feature">
        <div class="feature-title">위험도 안내</div>
        <div class="feature-desc">
            정상 가능성, 관찰 필요, 진료 권장, 빠른 진료 권장으로 분류합니다.
        </div>
    </div>

    <div class="feature">
        <div class="feature-title">모델 투명성</div>
        <div class="feature-desc">
            Accuracy, Precision, Recall, F1-score 등 주요 성능 지표를 제공합니다.
        </div>
    </div>

    <div class="feature">
        <div class="feature-title">데이터 분석</div>
        <div class="feature-desc">
            데이터 분포와 편향을 분석하여 서비스 신뢰도를 높입니다.
        </div>
    </div>
</section>
"""
)