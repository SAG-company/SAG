import base64
from pathlib import Path

import streamlit as st


def image_to_base64(path: str) -> str:
    image_path = Path(path)

    if not image_path.exists():
        return ""

    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode()


def inject_global_css() -> None:
    st.html(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* =========================
   Pfizer-inspired palette
   (밝은 일렉트릭 블루 + 시안 액센트 + 넉넉한 여백)
========================= */
:root {
    --pf-blue: #0a47ed;          /* primary action / link */
    --pf-blue-strong: #0833b8;   /* hover */
    --pf-blue-deep: #001E62;     /* hero / 강조 */
    --pf-blue-mid: #0b3bc4;      /* gradient mid */
    --pf-cyan: #00b5e2;          /* accent (the "twist") */
    --pf-tint: #eef3ff;          /* 연한 블루 배경 */
    --ink: #14152b;              /* heading near-black */
    --text: #3f4654;            /* body */
    --muted: #6b7280;
    --bg: #ffffff;
    --bg-soft: #f5f7fc;
    --border: #e6eaf2;
    --radius: 16px;
    --radius-sm: 12px;
    --shadow: 0 10px 30px rgba(20, 30, 80, 0.07);
    --shadow-lift: 0 18px 44px rgba(10, 71, 237, 0.16);
    --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
}

header, footer, #MainMenu {
    visibility: hidden;
}

.block-container {
    padding-top: 0rem;
    padding-left: 0rem;
    padding-right: 0rem;
    max-width: 100%;
}

.stApp {
    background: var(--bg-soft);
    font-family: var(--font);
}

html, body, [class*="css"] {
    font-family: var(--font);
}

/* =========================
   Top Navigation
========================= */

.top-nav {
    height: 80px;
    background: rgba(255, 255, 255, 0.92);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 54px;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 999;
    backdrop-filter: saturate(160%) blur(12px);
    font-family: var(--font);
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
    color: var(--pf-blue-deep);
    min-width: 180px;
}

.brand-logo {
    height: 50px;
    width: auto;
    object-fit: contain;
    display: block;
}

.logo-dot {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, var(--pf-blue), var(--pf-cyan));
    border-radius: 50%;
}

.brand-text {
    font-size: 22px;
    line-height: 1.0;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--pf-blue-deep);
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 36px;
    font-size: 15px;
    color: var(--ink);
    font-weight: 600;
}

.nav-links a {
    text-decoration: none;
    color: var(--ink);
    padding-bottom: 6px;
    border-bottom: 2px solid transparent;
    transition: color .18s ease, border-color .18s ease;
}

.nav-links a:hover {
    color: var(--pf-blue);
}

.nav-links a.active {
    color: var(--pf-blue);
    border-bottom: 2px solid var(--pf-blue);
}

.nav-right {
    display: flex;
    align-items: center;
    gap: 16px;
    color: var(--muted);
    font-size: 14px;
    font-weight: 600;
}

.nav-right .login-btn {
    background: var(--pf-blue);
    color: #fff;
    padding: 9px 20px;
    border-radius: 999px;
    font-weight: 700;
    transition: background .18s ease, transform .18s ease;
}

.nav-right .login-btn:hover {
    background: var(--pf-blue-strong);
    transform: translateY(-1px);
}

/* =========================
   Page Hero
========================= */

.page-hero {
    background: linear-gradient(120deg, var(--pf-blue-deep) 0%, var(--pf-blue-mid) 60%, var(--pf-blue) 100%);
    color: white;
    padding: 86px 0;
    font-family: var(--font);
    position: relative;
    overflow: hidden;
}

.page-hero::after {
    content: "";
    position: absolute;
    right: -120px;
    top: -120px;
    width: 420px;
    height: 420px;
    background: radial-gradient(circle, rgba(0,181,226,0.45), transparent 65%);
    border-radius: 50%;
    pointer-events: none;
}

.page-hero-inner {
    width: min(1280px, calc(100% - 64px));
    margin: 0 auto;
    position: relative;
    z-index: 1;
}

.eyebrow {
    color: var(--pf-cyan);
    letter-spacing: 2.6px;
    font-size: 13px;
    text-transform: uppercase;
    font-weight: 800;
    margin-bottom: 18px;
}

.page-title {
    font-size: 58px;
    line-height: 1.08;
    font-weight: 800;
    letter-spacing: -1.4px;
    margin-bottom: 20px;
}

.page-subtitle {
    max-width: 940px;
    font-size: 18px;
    line-height: 1.85;
    color: rgba(255,255,255,0.82);
}

/* =========================
   Cards / Sections
========================= */

.section-title {
    font-size: 34px;
    font-weight: 800;
    color: var(--ink);
    margin-bottom: 18px;
    letter-spacing: -0.7px;
}

.section-desc {
    font-size: 17px;
    line-height: 1.8;
    color: var(--text);
    max-width: 900px;
    margin-bottom: 28px;
}

.card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 32px;
    box-shadow: var(--shadow);
    box-sizing: border-box;
    transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lift);
    border-color: rgba(10, 71, 237, 0.28);
}

.dark-card {
    background: linear-gradient(140deg, var(--pf-blue-deep), var(--pf-blue-mid));
    color: white;
    border-radius: var(--radius);
    padding: 34px;
    box-shadow: 0 18px 42px rgba(0, 30, 98, 0.28);
    box-sizing: border-box;
}

.grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}

.grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
}

.mini-title {
    font-size: 22px;
    font-weight: 800;
    color: var(--ink);
    margin-bottom: 12px;
    letter-spacing: -0.3px;
}

.mini-text {
    font-size: 16px;
    line-height: 1.75;
    color: var(--text);
}

.dark-card .mini-title {
    color: white;
}

.dark-card .mini-text {
    color: rgba(255,255,255,0.8);
}

.notice {
    background: var(--pf-tint);
    border-left: 6px solid var(--pf-blue);
    border-radius: var(--radius-sm);
    padding: 28px 32px;
    color: #1F2937;
    font-size: 16px;
    line-height: 1.85;
    margin-top: 30px;
}

.warning-notice {
    background: #FFF8E1;
    border-left: 6px solid #F5C542;
    border-radius: var(--radius-sm);
    padding: 28px 32px;
    color: #1F2937;
    font-size: 16px;
    line-height: 1.85;
    margin-top: 30px;
}

/* =========================
   Metrics
========================= */

.metric-band {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 34px;
}

.metric-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 26px;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
    transition: transform .2s ease, box-shadow .2s ease;
}

.metric-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 4px;
    background: linear-gradient(180deg, var(--pf-blue), var(--pf-cyan));
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lift);
}

.metric-label {
    color: var(--muted);
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 10px;
}

.metric-value {
    color: var(--pf-blue);
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -0.8px;
}

/* =========================
   Home
========================= */

.home-hero {
    min-height: 760px;
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    font-family: var(--font);
    position: relative;
}

.home-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(100deg, rgba(0,30,98,0.78) 0%, rgba(10,59,196,0.45) 48%, rgba(0,30,98,0.10) 100%);
    pointer-events: none;
}

.home-hero-inner {
    width: min(1280px, calc(100% - 64px));
    margin: 0 auto;
    position: relative;
    z-index: 2;
}

.home-hero-text {
    max-width: 600px;
    color: white;
}

.home-title {
    font-size: 76px;
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -2px;
    margin-bottom: 28px;
    text-shadow: 0 4px 22px rgba(0,0,0,0.28);
}

.home-desc {
    font-size: 22px;
    line-height: 1.7;
    margin-bottom: 36px;
    color: rgba(255,255,255,0.92);
    text-shadow: 0 3px 14px rgba(0,0,0,0.3);
}

.btn-row {
    display: flex;
    gap: 18px;
}

.btn-primary {
    padding: 16px 44px;
    background: var(--pf-blue);
    color: white !important;
    text-decoration: none;
    border-radius: 999px;
    font-size: 17px;
    font-weight: 700;
    box-shadow: 0 10px 26px rgba(10, 71, 237, 0.4);
    transition: background .18s ease, transform .18s ease, box-shadow .18s ease;
}

.btn-primary:hover {
    background: var(--pf-blue-strong);
    transform: translateY(-2px);
    box-shadow: 0 14px 32px rgba(10, 71, 237, 0.5);
}

.btn-secondary {
    padding: 16px 44px;
    border: 1.5px solid rgba(255,255,255,0.9);
    color: white !important;
    text-decoration: none;
    border-radius: 999px;
    font-size: 17px;
    font-weight: 700;
    background: rgba(255,255,255,0.06);
    transition: background .18s ease, transform .18s ease;
}

.btn-secondary:hover {
    background: rgba(255,255,255,0.18);
    transform: translateY(-2px);
}

.feature-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: white;
    padding: 46px 54px;
    border-bottom: 1px solid var(--border);
    font-family: var(--font);
}

.feature {
    padding: 4px 34px;
    border-right: 1px solid var(--border);
    position: relative;
}

.feature::before {
    content: "";
    position: absolute;
    left: 34px;
    top: 6px;
    width: 34px;
    height: 4px;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--pf-blue), var(--pf-cyan));
}

.feature:last-child {
    border-right: none;
}

.feature-title {
    font-size: 21px;
    font-weight: 800;
    color: var(--ink);
    margin-bottom: 10px;
    margin-top: 20px;
    letter-spacing: -0.3px;
}

.feature-desc {
    font-size: 15px;
    color: var(--text);
    line-height: 1.65;
}

/* =========================
   Streamlit 위젯 톤 맞추기
========================= */

.stButton > button {
    border-radius: 999px;
    font-weight: 700;
    border: 1px solid var(--pf-blue);
}

.stButton > button:hover {
    border-color: var(--pf-blue-strong);
    color: var(--pf-blue-strong);
}

/* =========================
   Responsive
========================= */

@media (max-width: 1100px) {
    .nav-links {
        display: none;
    }

    .nav-right {
        display: none;
    }

    .grid-3,
    .grid-4,
    .metric-band,
    .feature-strip {
        grid-template-columns: 1fr;
    }

    .feature {
        border-right: none;
        border-bottom: 1px solid var(--border);
        padding-bottom: 24px;
    }

    .page-hero-inner,
    .home-hero-inner {
        width: min(100% - 40px, 1280px);
    }

    .page-title {
        font-size: 42px;
    }

    .home-title {
        font-size: 48px;
    }

    .home-desc {
        font-size: 18px;
    }

    .btn-row {
        flex-direction: column;
        align-items: flex-start;
    }

    .brand-logo {
        height: 42px;
    }
}
</style>
"""
    )


def render_nav(active: str) -> None:
    def active_class(name: str) -> str:
        return "active" if active == name else ""

    logo_base64 = image_to_base64("assets/sag_logo.png")

    if logo_base64:
        logo_html = (
            f'<img class="brand-logo" '
            f'src="data:image/png;base64,{logo_base64}" '
            f'alt="SAG Logo">'
        )
    else:
        logo_html = """
        <div class="logo-dot"></div>
        <div class="brand-text">SAG</div>
        """

    st.html(
        f"""
<div class="top-nav">
    <div class="brand">
        {logo_html}
    </div>

    <div class="nav-links">
        <a class="{active_class('Home')}" href="/" target="_self">Home</a>
        <a class="{active_class('About')}" href="/about" target="_self">About</a>
        <a class="{active_class('Detection')}" href="/detection" target="_self">Detection</a>
        <a class="{active_class('Model Performance')}" href="/model_performance" target="_self">Model Performance</a>
        <a class="{active_class('Data Analysis')}" href="/data_analysis" target="_self">Data Analysis</a>
    </div>

    <div class="nav-right">
        <span>Search</span>
        <a class="login-btn" href="#" target="_self">Client Login</a>
    </div>
</div>
"""
    )


def render_page_hero(eyebrow: str, title: str, subtitle: str) -> None:
    st.html(
        f"""
<section class="page-hero">
    <div class="page-hero-inner">
        <div class="eyebrow">{eyebrow}</div>
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
    </div>
</section>
"""
    )
