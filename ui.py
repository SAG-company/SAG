import streamlit as st


def inject_global_css() -> None:
    st.html(
        """
<style>
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
    background: #F7F8FA;
}

/* =========================
   Top Navigation
========================= */

.top-nav {
    height: 78px;
    background: rgba(255, 255, 255, 0.97);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 54px;
    border-bottom: 1px solid rgba(17, 24, 39, 0.08);
    position: sticky;
    top: 0;
    z-index: 999;
    backdrop-filter: blur(10px);
    font-family: Arial, sans-serif;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
    color: #0B1633;
}

.logo-dot {
    width: 36px;
    height: 36px;
    background: #13284B;
    border-radius: 50%;
}

.brand-text {
    font-size: 22px;
    line-height: 1.0;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 38px;
    font-size: 15px;
    color: #111827;
    font-weight: 500;
}

.nav-links a {
    text-decoration: none;
    color: #111827;
    padding-bottom: 8px;
}

.nav-links a.active {
    border-bottom: 2px solid #13284B;
}

.nav-right {
    display: flex;
    align-items: center;
    gap: 18px;
    color: #111827;
    font-size: 15px;
}

/* =========================
   Page Hero
========================= */

.page-hero {
    background: linear-gradient(135deg, #08111F 0%, #13284B 100%);
    color: white;
    padding: 70px 0;
    font-family: Arial, sans-serif;
}

.page-hero-inner {
    width: min(1280px, calc(100% - 64px));
    margin: 0 auto;
}

.eyebrow {
    color: #A8C7FF;
    letter-spacing: 2.4px;
    font-size: 13px;
    text-transform: uppercase;
    font-weight: 700;
    margin-bottom: 18px;
}

.page-title {
    font-size: 56px;
    line-height: 1.1;
    font-weight: 700;
    letter-spacing: -1.2px;
    margin-bottom: 18px;
}

.page-subtitle {
    max-width: 940px;
    font-size: 18px;
    line-height: 1.85;
    color: rgba(255,255,255,0.78);
}

/* =========================
   Cards / Sections
========================= */

.section-title {
    font-size: 34px;
    font-weight: 750;
    color: #111827;
    margin-bottom: 18px;
    letter-spacing: -0.6px;
}

.section-desc {
    font-size: 17px;
    line-height: 1.8;
    color: #4B5563;
    max-width: 900px;
    margin-bottom: 28px;
}

.card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 24px;
    padding: 32px;
    box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
    box-sizing: border-box;
}

.dark-card {
    background: linear-gradient(145deg, #08111F, #13284B);
    color: white;
    border-radius: 24px;
    padding: 34px;
    box-shadow: 0 18px 42px rgba(19, 40, 75, 0.22);
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
    color: #111827;
    margin-bottom: 12px;
}

.mini-text {
    font-size: 16px;
    line-height: 1.75;
    color: #4B5563;
}

.dark-card .mini-title {
    color: white;
}

.dark-card .mini-text {
    color: rgba(255,255,255,0.75);
}

.notice {
    background: #EEF4FF;
    border-left: 6px solid #13284B;
    border-radius: 14px;
    padding: 28px 32px;
    color: #1F2937;
    font-size: 16px;
    line-height: 1.85;
    margin-top: 30px;
}

.warning-notice {
    background: #FFF8E1;
    border-left: 6px solid #F5C542;
    border-radius: 14px;
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
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    padding: 26px;
    box-shadow: 0 12px 30px rgba(17,24,39,0.05);
}

.metric-label {
    color: #6B7280;
    font-size: 14px;
    margin-bottom: 10px;
}

.metric-value {
    color: #13284B;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -0.8px;
}

/* =========================
   Home
========================= */

.home-hero {
    min-height: 780px;
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    font-family: Arial, sans-serif;
}

.home-hero-inner {
    width: min(1280px, calc(100% - 64px));
    margin: 0 auto;
}

.home-hero-text {
    max-width: 570px;
    color: white;
}

.home-title {
    font-size: 76px;
    font-weight: 750;
    line-height: 1.12;
    letter-spacing: -1.8px;
    margin-bottom: 30px;
    text-shadow: 0 4px 20px rgba(0,0,0,0.32);
}

.home-desc {
    font-size: 22px;
    line-height: 1.7;
    margin-bottom: 36px;
    text-shadow: 0 3px 14px rgba(0,0,0,0.35);
}

.btn-row {
    display: flex;
    gap: 20px;
}

.btn-primary {
    padding: 17px 48px;
    background: #13284B;
    color: white !important;
    text-decoration: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: 700;
}

.btn-secondary {
    padding: 17px 48px;
    border: 1px solid white;
    color: white !important;
    text-decoration: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: 700;
    background: rgba(255,255,255,0.08);
}

.feature-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: white;
    padding: 44px 54px;
    border-bottom: 1px solid #E5E7EB;
    font-family: Arial, sans-serif;
}

.feature {
    padding: 0 34px;
    border-right: 1px solid #E5E7EB;
}

.feature:last-child {
    border-right: none;
}

.feature-title {
    font-size: 21px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 10px;
}

.feature-desc {
    font-size: 15px;
    color: #4B5563;
    line-height: 1.65;
}

/* =========================
   Responsive
========================= */

@media (max-width: 1100px) {
    .nav-links {
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
        border-bottom: 1px solid #E5E7EB;
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
}
</style>
"""
    )


def render_nav(active: str) -> None:
    def active_class(name: str) -> str:
        return "active" if active == name else ""

    st.html(
        f"""
<div class="top-nav">
    <div class="brand">
        <div class="logo-dot"></div>
        <div class="brand-text">Pet Skin<br>Intelligence</div>
    </div>

    <div class="nav-links">
        <a class="{active_class('Home')}" href="/" target="_self">Home</a>
        <a class="{active_class('About')}" href="/About" target="_self">About</a>
        <a class="{active_class('Detection')}" href="/Detection" target="_self">Detection</a>
        <a class="{active_class('Model Performance')}" href="/Model_Performance" target="_self">Model Performance</a>
        <a class="{active_class('Data Analysis')}" href="/Data_Analysis" target="_self">Data Analysis</a>
    </div>

    <div class="nav-right">
        <span>Search</span>
        <span>|</span>
        <span>Client Login</span>
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