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
    path = FIG_DIR / filename
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info(f"`{filename}` 이 아직 없습니다. EDA 노트북 실행 후 표시됩니다.")


left_margin, content, right_margin = st.columns([0.06, 0.88, 0.06])

with content:

    # ---------- 핵심 수치 밴드 ----------
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

    st.html("<br>")

    # =========================================================
    # 강아지 / 고양이 분포 + 해석
    # =========================================================
    st.html(
        """
<div class="card">
    <div class="section-title">강아지 / 고양이 분포</div>
    <div class="section-desc">전체 데이터셋의 축종별 구성 비율을 확인합니다.</div>
</div>
<br>
"""
    )

    sp_chart, sp_text = st.columns([3, 2], gap="large")

    with sp_chart:
        show_figure("species_dist.png", "축종(강아지/고양이) 분포")

    with sp_text:
        st.markdown("#### 해석")
        st.markdown(
            """
- 강아지 **88.6%** (31,003장), 고양이 **11.4%** (3,984장)으로 강한 불균형이 존재합니다.
- 고양이 데이터 비율이 낮아 고양이 병변 클래스별 학습 샘플이 부족하고, 일부 클래스에는 고양이 이미지가 아예 없습니다.
- 이 불균형은 데이터 증강만으로 완전히 해소하기 어렵습니다. 고양이 원본 이미지 추가 수집이 가장 효과적인 해결책입니다.
- 서비스 운영 시 **고양이 분석 결과는 병변 유형에 따라 신뢰도가 낮을 수 있음**을 보호자에게 안내해야 합니다.
"""
        )

    st.html("<br>")

    # =========================================================
    # 클래스 · 부위 분포 + 해석
    # =========================================================
    st.html(
        """
<div class="card">
    <div class="section-title">클래스 · 부위 분포</div>
    <div class="section-desc">A1~A7 병변 유형과 촬영 부위별 이미지 수를 확인합니다.</div>
</div>
<br>
"""
    )

    cr_chart, cr_text = st.columns([3, 2], gap="large")

    with cr_chart:
        show_figure("class_region_dist.png", "클래스 · 부위 분포")

    with cr_text:
        st.markdown("#### 해석")
        st.markdown(
            """
- 7개 병변 유형(A1~A7)은 **층화 샘플링**으로 클래스 간 균형을 맞췄습니다. 클래스 불균형으로 인한 편향 가능성은 낮습니다.
- 일부 병변 유형은 특정 부위(예: 귀, 발)에 집중되어 있습니다. 모델이 병변이 아닌 부위 패턴을 학습할 위험이 있습니다.
- **A7(무증상)** 클래스는 정상 피부이므로 다양한 부위 이미지가 포함되어 있어 분포가 넓게 나타납니다.
- 특정 부위에 편중된 클래스는 해당 부위 외 이미지 추가 수집을 고려해야 합니다.
"""
        )

    st.html("<br>")

    # =========================================================
    # 이미지 품질 분포 + 해석
    # =========================================================
    st.html(
        """
<div class="card">
    <div class="section-title">이미지 품질 분포</div>
    <div class="section-desc">자동 품질 스크리닝 결과로, OK 이미지만 학습에 사용했습니다.</div>
</div>
<br>
"""
    )

    qt_chart, qt_text = st.columns([3, 2], gap="large")

    with qt_chart:
        show_figure("quality_dist.png", "품질 검사 결과 분포")

    with qt_text:
        st.markdown("#### 해석")
        st.markdown(
            """
품질 스크리닝은 세 가지 기준으로 자동 필터링했습니다.

- **밝기 이상**: 과노출·저노출로 병변 식별이 불가능한 이미지 제거
- **저해상도**: 224px 미만 이미지 제거 (모델 입력 크기 기준)
- **단색 손상**: 특정 채널이 거의 없는 손상 이미지 제거

OK 비율이 높을수록 원본 데이터 품질이 균일하다는 의미입니다. 필터링된 이미지가 많을 경우 수집 환경 개선이 필요합니다.
"""
        )

    st.html("<br>")

    # =========================================================
    # 해상도 분포 + 해석
    # =========================================================
    st.html(
        """
<div class="card">
    <div class="section-title">해상도 분포</div>
    <div class="section-desc">학습 데이터의 이미지 해상도 분포를 확인합니다.</div>
</div>
<br>
"""
    )

    rs_chart, rs_text = st.columns([3, 2], gap="large")

    with rs_chart:
        show_figure("resolution_dist.png", "이미지 해상도 분포")

    with rs_text:
        st.markdown("#### 해석")
        st.markdown(
            """
- 대부분의 이미지가 **224×224 이상** 해상도를 가집니다. 모델 입력 크기(224px)에 충분한 품질입니다.
- 해상도가 과도하게 높은 이미지(4K 이상)는 리사이즈 과정에서 세부 정보가 손실될 수 있습니다.
- 해상도 분포가 넓게 퍼져 있을수록 리사이즈 후 이미지 품질 편차가 커집니다.
- 해상도 분포가 특정 구간에 집중되어 있다면 수집 장비(스마트폰 카메라 등)가 균일하다는 신호입니다.
"""
        )

    st.html("<br>")

    # =========================================================
    # 샘플 이미지 갤러리
    # =========================================================
    st.html(
        """
<div class="card">
    <div class="section-title">샘플 이미지 갤러리</div>
    <div class="section-desc">실제 학습 데이터 샘플과 데이터 증강(Augmentation) 결과 예시입니다.</div>
</div>
<br>
"""
    )

    gallery_left, gallery_right = st.columns(2, gap="large")

    with gallery_left:
        show_figure("sample_images.png", "클래스별 샘플 이미지")
        st.markdown(
            """
**클래스별 대표 샘플**입니다. A1~A7 각 병변의 시각적 특징을 확인할 수 있습니다.
A1(구진/플라크)과 A2(비듬/각질)는 육안으로도 유사해 보이며, 모델이 혼동하는 주요 원인입니다.
"""
        )

    with gallery_right:
        show_figure("augmentation_samples.png", "데이터 증강 예시")
        st.markdown(
            """
**데이터 증강(Augmentation)** 은 동일 이미지에 회전·반전·밝기 변환 등을 적용해 학습 데이터를 다양화합니다.
과도한 증강은 오히려 원본 특징을 왜곡할 수 있어 적절한 강도 조절이 중요합니다.
"""
        )

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
