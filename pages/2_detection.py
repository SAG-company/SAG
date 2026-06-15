import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from inference import (
    LESION_MAP,
    CLASS_ORDER,
    predict,
    gradcam,
    risk_score,
)
from ui import inject_global_css, render_nav, render_page_hero


st.set_page_config(
    page_title="Detection | AI 수의사",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
render_nav("Detection")

render_page_hero(
    eyebrow="AI Skin Detection",
    title="피부 이미지 분석",
    subtitle=(
        "강아지 또는 고양이의 피부 사진을 업로드하면 AI가 병변 유형, 정상 가능성, "
        "위험도와 보호자 행동 가이드를 제공합니다."
    ),
)


# =========================================================
# 시각화 헬퍼
# =========================================================

def probability_bar_chart(probs: dict) -> go.Figure:
    """7개 클래스 예측 확률을 수평 막대로 표시 (확률 오름차순 → 위로 갈수록 높음)."""
    items = [(f"{c} {LESION_MAP[c]}", probs[c]) for c in CLASS_ORDER]
    items.sort(key=lambda kv: kv[1])  # 오름차순 정렬

    labels = [name for name, _ in items]
    values = [v * 100 for _, v in items]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
            marker_color="#13284B",
        )
    )
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=30, t=10, b=10),
        xaxis_title="가능성 (%)",
        xaxis_range=[0, max(values) * 1.18 if values else 100],
        plot_bgcolor="white",
    )
    return fig


def risk_gauge(risk: str) -> go.Figure:
    """위험도 4단계를 0~100 게이지로 표시 (go.Indicator)."""
    score = risk_score(risk)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": " 점"},
            title={"text": f"위험도: {risk}"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#13284B"},
                "steps": [
                    {"range": [0, 25], "color": "#D1FAE5"},   # 정상
                    {"range": [25, 55], "color": "#FEF3C7"},  # 관찰
                    {"range": [55, 80], "color": "#FED7AA"},  # 진료
                    {"range": [80, 100], "color": "#FECACA"},  # 빠른 진료
                ],
            },
        )
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def gradcam_overlay(image: Image.Image, cam: np.ndarray) -> Image.Image:
    """원본 이미지 위에 Grad-CAM 히트맵을 반투명으로 겹친 이미지를 만든다."""
    import matplotlib.cm as cm

    base = image.convert("RGB")
    heat = Image.fromarray(np.uint8(cm.jet(cam) * 255)).convert("RGB")
    heat = heat.resize(base.size)
    return Image.blend(base, heat, alpha=0.45)


# =========================================================
# 레이아웃
# =========================================================

left_margin, content, right_margin = st.columns([0.06, 0.88, 0.06])

with content:
    left, right = st.columns([1, 1.15], gap="large")

    with left:
        st.html(
            """
<div class="card">
    <div class="section-title">Analysis Input</div>
    <div class="section-desc">
        분석 정확도를 위해 피부 부위가 선명하게 보이는 사진을 업로드하세요.
    </div>
</div>
<br>
"""
        )

        animal = st.selectbox("동물 선택", ["강아지", "고양이"])

        body_part = st.selectbox(
            "부위 선택",
            ["귀", "발", "배", "등", "얼굴", "꼬리", "항문 주변", "기타"],
        )

        symptoms = st.multiselect(
            "관찰되는 증상",
            ["붉어짐", "탈모", "각질", "딱지", "진물", "가려움", "냄새", "발 핥음", "통증"],
        )

        # 입력 방식: 파일 업로드 또는 카메라 촬영
        input_mode = st.radio(
            "입력 방식",
            ["파일 업로드", "카메라 촬영"],
            horizontal=True,
        )

        if input_mode == "파일 업로드":
            image_source = st.file_uploader(
                "피부 사진 업로드",
                type=["jpg", "jpeg", "png"],
            )
        else:
            image_source = st.camera_input("피부 사진 촬영")

        # 원본 미리보기
        if image_source is not None:
            preview = Image.open(image_source)
            st.image(preview, caption="입력 이미지", use_container_width=True)

        analyze_button = st.button(
            "RUN AI ANALYSIS",
            use_container_width=True,
            type="primary",
        )

    with right:
        st.html(
            """
<div class="dark-card">
    <div class="section-title" style="color:white;">AI Analysis Result</div>
    <div class="mini-text">
        입력된 이미지와 증상 정보를 기반으로 AI 분석 결과가 표시됩니다.
        결과는 병변 유형 후보, 위험도, 신뢰도, 행동 가이드로 구성됩니다.
    </div>
</div>
<br>
"""
        )

        if analyze_button and image_source is not None:
            image = Image.open(image_source)
            result = predict(image)

            if not result["available"]:
                st.warning(
                    "현재 학습된 모델이 연결되지 않아 예시(더미) 결과를 표시합니다. "
                    "모델 파일이 준비되면 자동으로 실제 분석으로 전환됩니다."
                )

            # 질환명 대형 표시 + 신뢰도 %
            metric_left, metric_right = st.columns(2)
            metric_left.metric(
                "예측 병변 유형",
                f"{result['top_label']} {result['top_name']}",
                help="가장 가능성이 높은 병변 유형입니다.",
            )
            metric_right.metric("분석 신뢰도", f"{result['confidence'] * 100:.1f}%")

            # 위험도 게이지
            st.plotly_chart(risk_gauge(result["risk"]), use_container_width=True)

            # 클래스별 예측 확률 막대
            st.markdown("### 클래스별 예측 확률")
            st.plotly_chart(
                probability_bar_chart(result["probs"]),
                use_container_width=True,
            )

            # Grad-CAM: 원본과 히트맵 나란히
            st.markdown("### Grad-CAM (관심 영역)")
            cam = gradcam(image)
            if cam is not None:
                cam_left, cam_right = st.columns(2)
                cam_left.image(image, caption="원본", use_container_width=True)
                cam_right.image(
                    gradcam_overlay(image, cam),
                    caption="Grad-CAM",
                    use_container_width=True,
                )
            else:
                st.info(
                    "Grad-CAM은 실제 학습 모델이 연결되면 표시됩니다. "
                    "(현재는 더미 모드)"
                )

            # 보호자 행동 가이드
            st.markdown("### 보호자 행동 가이드")
            st.write(
                """
                - 증상이 2~3일 이상 지속되면 동물병원 상담을 권장합니다.
                - 진물, 악취, 출혈, 심한 탈모가 있다면 빠른 진료가 필요할 수 있습니다.
                - 사람용 연고나 약을 임의로 사용하지 마세요.
                - 같은 부위를 계속 긁거나 핥는지 관찰하세요.
                """
            )

            if animal == "고양이":
                st.warning(
                    "고양이 데이터는 강아지 데이터보다 상대적으로 적어 일부 병변 유형의 분석 신뢰도가 낮을 수 있습니다."
                )

        elif analyze_button and image_source is None:
            st.warning("분석할 피부 사진을 먼저 업로드하거나 촬영해주세요.")
        else:
            st.info("왼쪽에서 분석 정보를 입력하고 이미지를 업로드하면 분석 결과가 표시됩니다.")

    st.html(
        """
<div class="notice">
    <strong>Medical Notice</strong><br>
    본 결과는 질병명 확정 진단이 아니라 이미지 기반 병변 유형 분석입니다.
    정확한 원인 진단과 치료는 수의사의 진료가 필요합니다.
</div>
"""
    )
