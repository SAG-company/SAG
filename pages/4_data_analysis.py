from pathlib import Path

import streamlit as st

from ui import inject_global_css, render_nav, render_page_hero


st.set_page_config(
    page_title="Data Analysis | AI 수의사",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
render_nav("Data Analysis")

render_page_hero(
    eyebrow="Dataset Intelligence",
    title="데이터 분석",
    subtitle=(
        "학습 데이터의 구성, 클래스별 분포, 강아지/고양이 비율, 품질 필터링 결과와 "
        "데이터 편향 가능성을 EDA 결과로 확인합니다."
    ),
)


BASE = Path(__file__).resolve().parent.parent
FIG_DIR = BASE / "outputs" / "figures"


def show_figure(filename: str, caption: str) -> None:
    """EDA 산출 이미지를 있으면 표시, 없으면 안내."""
    path = FIG_DIR / filename
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info(f"`{filename}` 이 아직 없습니다. EDA 노트북 실행 후 표시됩니다.")


left_margin, content, right_margin = st.columns([0.06, 0.88, 0.06])

with content:
    # ---------- 핵심 수치 밴드 (DATA_SPECIFICATION 기준) ----------
    st.html(
        """
<div class="metric-band">
    <div class="metric-card">
        <div class="metric-label">전체 이미지 수</div>
        <div class="metric-value">34,987</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">강아지 이미지</div>
        <div class="metric-value">31,003</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">고양이 이미지</div>
        <div class="metric-value">3,984</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">클래스 수</div>
        <div class="metric-value">7</div>
    </div>
</div>
"""
    )

    # ---------- EDA 도표 (유서하 산출물 연동) ----------
    left, right = st.columns(2, gap="large")

    with left:
        st.html(
            """
<div class="card">
    <div class="section-title">강아지 / 고양이 분포</div>
    <div class="section-desc">
        고양이 데이터는 전체의 약 11.4%로 적습니다. 모델 평가와 서비스 해석에 반드시 반영해야 합니다.
    </div>
</div>
<br>
"""
        )
        show_figure("species_dist.png", "축종(강아지/고양이) 분포")

    with right:
        st.html(
            """
<div class="card">
    <div class="section-title">클래스 · 부위 분포</div>
    <div class="section-desc">
        A1~A7 병변 유형과 촬영 부위별 이미지 수를 확인합니다. 층화 샘플링으로 균형을 맞췄습니다.
    </div>
</div>
<br>
"""
        )
        show_figure("class_region_dist.png", "클래스 · 부위 분포")

    st.html("<br>")

    left2, right2 = st.columns(2, gap="large")

    with left2:
        st.html(
            """
<div class="card">
    <div class="section-title">이미지 품질 분포</div>
    <div class="section-desc">
        밝기이상 · 저해상도 · 단색손상 등을 자동 스크리닝해 OK 이미지만 학습에 사용했습니다.
    </div>
</div>
<br>
"""
        )
        show_figure("quality_dist.png", "품질 검사 결과 분포")

    with right2:
        st.html(
            """
<div class="card">
    <div class="section-title">해상도 분포</div>
    <div class="section-desc">
        저해상도 이미지를 걸러내기 위한 해상도 분포를 확인합니다.
    </div>
</div>
<br>
"""
        )
        show_figure("resolution_dist.png", "이미지 해상도 분포")

    # ---------- 샘플 이미지 갤러리 ----------
    st.html(
        """
<br>
<div class="card">
    <div class="section-title">샘플 이미지 갤러리</div>
    <div class="section-desc">
        실제 학습 데이터 샘플과 데이터 증강(Augmentation) 결과 예시입니다.
    </div>
</div>
<br>
"""
    )

    gallery = [
        ("sample_images.png", "클래스별 샘플 이미지"),
        ("augmentation_samples.png", "데이터 증강 예시"),
    ]
    cols = st.columns(len(gallery))
    for col, (filename, caption) in zip(cols, gallery):
        with col:
            show_figure(filename, caption)

    st.html(
        """
<div class="warning-notice">
    <strong>데이터 편향 및 한계</strong><br>
    고양이 데이터는 전체 데이터 중 약 11.4%로 상대적으로 적습니다.
    또한 일부 병변 클래스에는 고양이 샘플이 포함되어 있지 않아,
    고양이 분석 결과는 병변 유형에 따라 신뢰도가 낮을 수 있습니다.
    이 문제는 augmentation만으로 완전히 해결하기 어렵고,
    고양이 원본 데이터 추가 수집이 필요합니다.
</div>
"""
    )
