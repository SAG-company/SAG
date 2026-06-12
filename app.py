import base64
from pathlib import Path
import streamlit as st


st.set_page_config(
    page_title="AI 수의사",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def get_base64_image(image_path: str) -> str:
    path = Path(image_path)

    if not path.exists():
        return ""

    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


hero_image_base64 = get_base64_image("assets/app.png")

if hero_image_base64:
    hero_background = (
        "linear-gradient(rgba(8,18,35,0.25), rgba(8,18,35,0.35)), "
        f"url('data:image/png;base64,{hero_image_base64}')"
    )
else:
    hero_background = (
        "linear-gradient(rgba(8,18,35,0.55), rgba(8,18,35,0.65)), "
        "url('https://images.unsplash.com/photo-1601758228041-f3b2795255f1')"
    )


html = f"""
<style>
header {{
    visibility: hidden;
}}

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

.block-container {{
    padding-top: 0rem;
    padding-left: 0rem;
    padding-right: 0rem;
    padding-bottom: 0rem;
    max-width: 100%;
}}

.stApp {{
    background: #F7F8FA;
}}

.top-nav {{
    height: 78px;
    background: rgba(255, 255, 255, 0.97);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 46px;
    border-bottom: 1px solid rgba(17, 24, 39, 0.08);
    position: sticky;
    top: 0;
    z-index: 999;
    backdrop-filter: blur(10px);
    font-family: Arial, sans-serif;
}}

.brand {{
    display: flex;
    align-items: center;
    gap: 14px;
    color: #0B1633;
}}

.paw {{
    width: 34px;
    height: 34px;
    background: #13284B;
    border-radius: 50%;
    position: relative;
}}

.paw::before {{
    content: "";
    position: absolute;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #13284B;
    left: -5px;
    top: -7px;
    box-shadow:
        13px -6px 0 #13284B,
        25px 0px 0 #13284B,
        4px 21px 0 #13284B;
}}

.brand-text {{
    font-size: 22px;
    line-height: 1.0;
    font-weight: 700;
    letter-spacing: -0.4px;
}}

.nav-links {{
    display: flex;
    align-items: center;
    gap: 46px;
    font-size: 16px;
    color: #111827;
    font-weight: 500;
}}

.nav-links a {{
    text-decoration: none;
    color: #111827;
    padding-bottom: 8px;
}}

.nav-links a.active {{
    border-bottom: 2px solid #13284B;
}}

.nav-right {{
    display: flex;
    align-items: center;
    gap: 22px;
    color: #111827;
    font-size: 15px;
}}

.search-icon {{
    width: 18px;
    height: 18px;
    border: 3px solid #111827;
    border-radius: 50%;
    position: relative;
    display: inline-block;
}}

.search-icon::after {{
    content: "";
    width: 10px;
    height: 3px;
    background: #111827;
    position: absolute;
    right: -8px;
    bottom: -4px;
    transform: rotate(45deg);
    border-radius: 2px;
}}

.divider {{
    height: 30px;
    width: 1px;
    background: #111827;
    opacity: 0.55;
}}

.hero {{
    min-height: 790px;
    background-image: {hero_background};
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    font-family: Arial, sans-serif;
    color: white;
}}

.hero-content {{
    margin-left: 6.2%;
    max-width: 560px;
    margin-top: 60px;
}}

.hero-title {{
    font-size: 76px;
    line-height: 1.16;
    font-weight: 600;
    letter-spacing: -1.8px;
    margin-bottom: 34px;
    text-shadow: 0 4px 20px rgba(0,0,0,0.25);
}}

.hero-desc {{
    font-size: 22px;
    line-height: 1.7;
    font-weight: 400;
    color: rgba(255, 255, 255, 0.94);
    margin-bottom: 36px;
    text-shadow: 0 2px 14px rgba(0,0,0,0.28);
}}

.hero-buttons {{
    display: flex;
    gap: 22px;
    align-items: center;
}}

.primary-btn {{
    display: inline-block;
    padding: 18px 52px;
    background: #13284B;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-size: 19px;
    font-weight: 600;
    border: 1px solid #13284B;
}}

.secondary-btn {{
    display: inline-block;
    padding: 18px 52px;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-size: 19px;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.9);
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(6px);
}}

.feature-strip {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: #FFFFFF;
    padding: 42px 54px;
    border-bottom: 1px solid #E5E7EB;
    font-family: Arial, sans-serif;
}}

.feature-card {{
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 0 36px;
    border-right: 1px solid #E5E7EB;
}}

.feature-card:last-child {{
    border-right: none;
}}

.feature-icon {{
    width: 56px;
    height: 56px;
    border: 3px solid #13284B;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #13284B;
    font-size: 28px;
    flex-shrink: 0;
}}

.feature-title {{
    font-size: 21px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 8px;
}}

.feature-desc {{
    font-size: 15px;
    line-height: 1.6;
    color: #374151;
}}

.section {{
    padding: 92px 90px;
    background: #F7F8FA;
    font-family: Arial, sans-serif;
}}

.section.white {{
    background: #FFFFFF;
}}

.section-title {{
    font-size: 42px;
    font-weight: 600;
    color: #111827;
    text-align: center;
    margin-bottom: 18px;
    letter-spacing: -0.8px;
}}

.section-subtitle {{
    font-size: 18px;
    color: #4B5563;
    text-align: center;
    max-width: 860px;
    margin: 0 auto 52px auto;
    line-height: 1.8;
}}

.steps {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 28px;
    max-width: 1180px;
    margin: 0 auto;
}}

.step-card {{
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    padding: 38px 34px;
    min-height: 230px;
    box-shadow: 0 12px 34px rgba(17, 24, 39, 0.06);
}}

.step-num {{
    font-size: 15px;
    font-weight: 700;
    color: #13284B;
    letter-spacing: 1px;
    margin-bottom: 18px;
}}

.step-title {{
    font-size: 25px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 16px;
}}

.step-desc {{
    font-size: 16px;
    line-height: 1.75;
    color: #4B5563;
}}

.symptom-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    max-width: 1060px;
    margin: 0 auto;
}}

.symptom {{
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 999px;
    padding: 20px 24px;
    text-align: center;
    font-size: 17px;
    font-weight: 600;
    color: #13284B;
    box-shadow: 0 8px 24px rgba(17,24,39,0.05);
}}

.notice-box {{
    max-width: 1080px;
    margin: 0 auto;
    background: #EEF4FF;
    border-left: 6px solid #13284B;
    border-radius: 12px;
    padding: 34px 38px;
    color: #1F2937;
    font-size: 17px;
    line-height: 1.85;
}}

.notice-box strong {{
    font-size: 21px;
    display: block;
    margin-bottom: 8px;
    color: #111827;
}}

@media (max-width: 1100px) {{
    .nav-links {{
        display: none;
    }}

    .hero-title {{
        font-size: 54px;
    }}

    .hero-desc {{
        font-size: 18px;
    }}

    .feature-strip {{
        grid-template-columns: repeat(2, 1fr);
        row-gap: 36px;
    }}

    .feature-card {{
        border-right: none;
    }}

    .steps {{
        grid-template-columns: 1fr;
    }}

    .symptom-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 700px) {{
    .top-nav {{
        padding: 0 22px;
    }}

    .brand-text {{
        font-size: 18px;
    }}

    .nav-right {{
        display: none;
    }}

    .hero {{
        min-height: 720px;
    }}

    .hero-content {{
        margin-left: 28px;
        margin-right: 28px;
    }}

    .hero-title {{
        font-size: 43px;
    }}

    .hero-buttons {{
        flex-direction: column;
        align-items: stretch;
    }}

    .primary-btn,
    .secondary-btn {{
        text-align: center;
    }}

    .feature-strip {{
        grid-template-columns: 1fr;
        padding: 36px 26px;
    }}

    .feature-card {{
        padding: 24px 0;
        border-bottom: 1px solid #E5E7EB;
    }}

    .section {{
        padding: 68px 28px;
    }}

    .symptom-grid {{
        grid-template-columns: 1fr;
    }}
}}
</style>

<div class="top-nav">
    <div class="brand">
        <div class="paw"></div>
        <div class="brand-text">AI VET</div>
    </div>

    <div class="nav-links">
        <a href="/" class="active" target="_self">Home</a>
        <a href="/Detection" target="_self">Detection</a>
        <a href="/Model_Performance" target="_self">Model Performance</a>
        <a href="/Data_Analysis" target="_self">Data Analysis</a>
    </div>

    <div class="nav-right">
        <span class="search-icon"></span>
        <span class="divider"></span>
        <span>Client Login</span>
    </div>
</div>

<section class="hero">
    <div class="hero-content">
        <div class="hero-title">AI VET</div>
        <div class="hero-desc">
            강아지와 고양이의 피부 사진을 기반으로<br>
            AI가 피부 이상 징후와 가능한 질환,<br>
            진료 필요도를 분석합니다.
        </div>

        <div class="hero-buttons">
            <a class="primary-btn" href="/Detection" target="_self">분석 시작하기</a>
            <a class="secondary-btn" href="#service">서비스 소개 보기</a>
        </div>
    </div>
</section>

<section class="feature-strip">
    <div class="feature-card">
        <div class="feature-icon">▱</div>
        <div>
            <div class="feature-title">피부 이미지 분석</div>
            <div class="feature-desc">고해상도 AI 모델이 피부 병변을 정밀하게 분석합니다.</div>
        </div>
    </div>

    <div class="feature-card">
        <div class="feature-icon">▾</div>
        <div>
            <div class="feature-title">위험도 안내</div>
            <div class="feature-desc">위험도를 4단계로 분류하여 진료 필요도를 안내합니다.</div>
        </div>
    </div>

    <div class="feature-card">
        <div class="feature-icon">▥</div>
        <div>
            <div class="feature-title">모델 투명성</div>
            <div class="feature-desc">모델 성능 지표와 한계를 투명하게 공개합니다.</div>
        </div>
    </div>

    <div class="feature-card">
        <div class="feature-icon">◔</div>
        <div>
            <div class="feature-title">데이터 분석</div>
            <div class="feature-desc">데이터 분포와 편향을 분석하여 서비스 품질을 개선합니다.</div>
        </div>
    </div>
</section>

<section class="section" id="service">
    <div class="section-title">How It Works</div>
    <div class="section-subtitle">
        보호자가 복잡한 의학 지식 없이도 사진 업로드부터 위험도 확인까지
        자연스럽게 따라갈 수 있도록 3단계 분석 흐름으로 설계했습니다.
    </div>

    <div class="steps">
        <div class="step-card">
            <div class="step-num">STEP 01</div>
            <div class="step-title">피부 사진 업로드</div>
            <div class="step-desc">
                강아지 또는 고양이의 피부 부위가 잘 보이도록 사진을 업로드합니다.
                동물 종류, 부위, 관찰 증상을 함께 입력합니다.
            </div>
        </div>

        <div class="step-card">
            <div class="step-num">STEP 02</div>
            <div class="step-title">AI 피부 패턴 분석</div>
            <div class="step-desc">
                AI 모델이 이미지 속 피부 색상, 병변 형태, 털 빠짐, 염증 가능성 등을
                기반으로 이상 징후를 분석합니다.
            </div>
        </div>

        <div class="step-card">
            <div class="step-num">STEP 03</div>
            <div class="step-title">위험도와 행동 가이드</div>
            <div class="step-desc">
                분석 결과를 위험도, 예측 후보, 신뢰도, 보호자 행동 가이드로 정리해
                다음 판단을 도와줍니다.
            </div>
        </div>
    </div>
</section>

<section class="section white">
    <div class="section-title">분석 가능한 증상</div>
    <div class="section-subtitle">
        현재 서비스는 반려동물 피부 사진에서 관찰 가능한 주요 외형 증상을 중심으로 분석합니다.
    </div>

    <div class="symptom-grid">
        <div class="symptom">붉어짐</div>
        <div class="symptom">탈모</div>
        <div class="symptom">각질</div>
        <div class="symptom">딱지</div>
        <div class="symptom">진물</div>
        <div class="symptom">가려움</div>
        <div class="symptom">냄새</div>
        <div class="symptom">발 핥음</div>
    </div>
</section>

<section class="section">
    <div class="section-title">AI 주의사항</div>
    <div class="section-subtitle">
        이 서비스는 수의사의 진료를 대체하지 않습니다. 보호자의 초기 판단을 돕는 참고 도구입니다.
    </div>

    <div class="notice-box">
        <strong>중요 안내</strong>
        AI 분석 결과는 업로드된 사진과 입력 정보에 기반한 참고용 결과입니다.
        진물, 악취, 출혈, 심한 가려움, 급격한 탈모, 식욕 저하, 통증 반응이 있는 경우
        반드시 동물병원 진료를 권장합니다.
    </div>
</section>
"""

st.html(html)