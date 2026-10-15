"""Design adapted from trichyravis/rbi-spread-app (user-supplied reference)."""
import streamlit as st

GOLD="#FFD700"
BLUE="#003366"
MID="#004d80"
CARD="#112240"
TXT="#e6f1ff"
MUTED="#8892b0"
LIGHT_BLUE="#ADD8E6"


def apply_theme():
    st.markdown("""<style>
    .stApp{background:linear-gradient(135deg,#1a2332,#243447,#2a3f5f) fixed}
    .block-container{padding-top:1.2rem;padding-bottom:2rem;max-width:1400px}
    h1,h2,h3{color:#e6f1ff}
    .stTabs [data-baseweb="tab-list"]{gap:6px;background:rgba(17,34,64,.55);padding:6px;border-radius:12px;border:1px solid rgba(255,215,0,.18);flex-wrap:wrap}
    .stTabs [data-baseweb="tab"]{background:transparent;border-radius:8px;padding:8px 16px;font-weight:600;color:#c7d3e8}
    .stTabs [data-baseweb="tab"] *{color:#c7d3e8!important}
    .stTabs [aria-selected="true"]{background:#FFD700!important}
    .stTabs [aria-selected="true"],.stTabs [aria-selected="true"] *{color:#003366!important}
    [data-testid="stMetric"]{background:#112240;border:1px solid rgba(255,215,0,.2);border-radius:14px;padding:16px 18px;box-shadow:0 4px 18px rgba(0,0,0,.28)}
    [data-testid="stMetricValue"]{color:#FFD700}
    [data-testid="stMetricLabel"]{color:#e6f1ff}
    [data-testid="stSidebar"]{background:#112240;border-right:1px solid rgba(255,215,0,.18)}
    details{background:#112240;border:1px solid rgba(255,215,0,.18)!important;border-radius:12px!important}
    .stButton button,.stDownloadButton button{background:#112240!important;border:1px solid rgba(255,215,0,.35)!important;color:#FFD700!important}
    .stButton button p,.stDownloadButton button p{color:#FFD700!important}
    .mp-brand{background:linear-gradient(90deg,#003366,#004d80);border-radius:16px;padding:24px 26px;border:1px solid rgba(255,215,0,.3);box-shadow:0 6px 24px rgba(0,0,0,.35);margin-bottom:18px}
    .mp-brand-inner{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}
    .mp-kicker{color:#FFD700;font-size:12px;font-weight:700;letter-spacing:2px}
    .mp-title{color:#fff;font-size:29px;font-weight:800;line-height:1.2;margin:6px 0}
    .mp-subtitle{color:#ADD8E6;font-size:14px;line-height:1.6}
    .mp-author{color:#fff;font-size:14px;font-weight:700;text-align:right}
    .mp-author small{display:block;color:#b6c5da;font-size:12px;font-weight:400;margin-bottom:4px}
    .mp-brand a{color:#FFD700!important;text-decoration:none;font-size:13px}
    .mp-footer{margin-top:28px}.mp-footer-links{display:flex;flex-wrap:wrap;gap:18px;margin-top:12px}
    @media(max-width:700px){.mp-author{text-align:left}.mp-title{font-size:24px}}
    </style>""",unsafe_allow_html=True)


def header():
    st.markdown('''<div class="mp-brand"><div class="mp-brand-inner"><div>
    <div class="mp-kicker">THE MOUNTAIN PATH ACADEMY · WORLD OF FINANCE</div>
    <div class="mp-title">Nifty Technical Analysis Lab</div>
    <div class="mp-subtitle">Nifty 50 stocks · Nifty 50 index · Bank Nifty index<br>Daily charts, momentum, screening and historical replay</div>
    </div><div class="mp-author"><small>Educational Series by</small>Prof. V. Ravichandran<br>
    <a href="https://themountainpathacademy.com" target="_blank" rel="noopener noreferrer">themountainpathacademy.com ↗</a>
    </div></div></div>''',unsafe_allow_html=True)


def footer():
    st.markdown('''<div class="mp-brand mp-footer"><div class="mp-kicker">THE MOUNTAIN PATH · WORLD OF FINANCE</div>
    <div class="mp-subtitle">Bridging Theory with Practice · Excellence in Financial Education</div>
    <div class="mp-subtitle">Prof. V. Ravichandran · Visiting Professor &amp; Professor of Practice at Leading Business Schools</div>
    <div class="mp-footer-links"><a href="https://themountainpathacademy.com" target="_blank" rel="noopener noreferrer">Academy ↗</a>
    <a href="https://www.linkedin.com/in/trichyravis" target="_blank" rel="noopener noreferrer">LinkedIn ↗</a>
    <a href="https://github.com/trichyravis" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div>
    <div class="mp-subtitle" style="font-size:11px;margin-top:14px">Educational analysis only. Data source and cutoff are stated in the app. No order placement or automated investment advice.</div>
    </div>''',unsafe_allow_html=True)
