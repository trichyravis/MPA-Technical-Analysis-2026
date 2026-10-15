"""Mountain Path Streamlit theme.

Custom HTML is rendered with st.html (not st.markdown). Every text node carries an
inline color plus -webkit-text-fill-color, and every custom div has user-select:none,
so the brand header and footer render identically in light and dark browser modes.
"""
import streamlit as st

GOLD = "#FFD700"
BLUE = "#003366"
MID = "#004d80"
CARD = "#112240"
TXT = "#e6f1ff"
MUTED = "#8892b0"
GREEN = "#28a745"
RED = "#dc3545"
LIGHT_BLUE = "#ADD8E6"
BACKGROUND = "linear-gradient(135deg,#1a2332,#243447,#2a3f5f)"

NOSELECT = "user-select:none;-webkit-user-select:none;"


def _text(color):
    """Inline color that survives Streamlit/Safari text-fill overrides."""
    return f"color:{color};-webkit-text-fill-color:{color};"


def _link(url, label):
    return (f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
            f'style="{_text(GOLD)}text-decoration:none;font-weight:600;font-size:13px;">{label}</a>')


def apply_theme():
    # A style-only st.html call is injected into the page without taking layout space.
    st.html(f"""<style>
    .stApp{{background:{BACKGROUND} fixed}}
    .block-container{{padding-top:1.2rem;padding-bottom:2rem;max-width:1400px}}
    h1,h2,h3{{color:{TXT}}}
    .stTabs [data-baseweb="tab-list"]{{gap:6px;background:rgba(17,34,64,.55);padding:6px;border-radius:12px;border:1px solid rgba(255,215,0,.18);flex-wrap:wrap}}
    .stTabs [data-baseweb="tab"]{{background:transparent;border-radius:8px;padding:8px 16px;font-weight:600;color:#c7d3e8}}
    .stTabs [data-baseweb="tab"] *{{color:#c7d3e8!important}}
    .stTabs [aria-selected="true"]{{background:{GOLD}!important}}
    .stTabs [aria-selected="true"],.stTabs [aria-selected="true"] *{{color:{BLUE}!important;-webkit-text-fill-color:{BLUE}!important}}
    [data-testid="stMetric"]{{background:{CARD};border:1px solid rgba(255,215,0,.2);border-radius:14px;padding:16px 18px;box-shadow:0 4px 18px rgba(0,0,0,.28)}}
    [data-testid="stMetricValue"]{{color:{GOLD}}}
    [data-testid="stMetricLabel"]{{color:{TXT}}}
    [data-testid="stSidebar"]{{background:{CARD};border-right:1px solid rgba(255,215,0,.18)}}
    details{{background:{CARD};border:1px solid rgba(255,215,0,.18)!important;border-radius:12px!important}}
    .stButton button,.stDownloadButton button{{background:{CARD}!important;border:1px solid rgba(255,215,0,.35)!important;color:{GOLD}!important}}
    .stButton button p,.stDownloadButton button p{{color:{GOLD}!important}}
    </style>""")


def _card(inner, extra=""):
    return (f'<div style="{NOSELECT}background:linear-gradient(90deg,{BLUE},{MID});border-radius:16px;'
            f'padding:24px 26px;border:1px solid rgba(255,215,0,.3);box-shadow:0 6px 24px rgba(0,0,0,.35);'
            f'font-family:Arial,sans-serif;{extra}">{inner}</div>')


def header():
    left = (f'<div style="{NOSELECT}flex:1 1 420px;">'
            f'<div style="{NOSELECT}{_text(GOLD)}font-size:12px;font-weight:700;letter-spacing:2px;">'
            f'THE MOUNTAIN PATH ACADEMY · WORLD OF FINANCE</div>'
            f'<div style="{NOSELECT}{_text("#ffffff")}font-size:29px;font-weight:800;line-height:1.2;margin:6px 0;">'
            f'Nifty Technical Analysis Lab</div>'
            f'<div style="{NOSELECT}{_text(LIGHT_BLUE)}font-size:14px;line-height:1.6;">'
            f'Nifty 50 stocks · Nifty 50 index · Bank Nifty index<br>'
            f'Daily charts, momentum, screening and historical replay</div></div>')
    right = (f'<div style="{NOSELECT}flex:0 1 auto;">'
             f'<div style="{NOSELECT}{_text("#b6c5da")}font-size:12px;margin-bottom:4px;">Educational Series by</div>'
             f'<div style="{NOSELECT}{_text("#ffffff")}font-size:14px;font-weight:700;margin-bottom:4px;">'
             f'Prof. V. Ravichandran</div>'
             f'{_link("https://themountainpathacademy.com", "themountainpathacademy.com ↗")}</div>')
    st.html(_card(f'<div style="{NOSELECT}display:flex;align-items:center;justify-content:space-between;'
                  f'gap:20px;flex-wrap:wrap;">{left}{right}</div>', "margin-bottom:18px;"))


def footer():
    links = " ".join([
        _link("https://themountainpathacademy.com", "Academy ↗"),
        _link("https://www.linkedin.com/in/trichyravis", "LinkedIn ↗"),
        _link("https://github.com/trichyravis", "GitHub ↗"),
    ])
    body = (f'<div style="{NOSELECT}{_text(GOLD)}font-size:12px;font-weight:700;letter-spacing:2px;">'
            f'THE MOUNTAIN PATH · WORLD OF FINANCE</div>'
            f'<div style="{NOSELECT}{_text(LIGHT_BLUE)}font-size:14px;line-height:1.6;">'
            f'Bridging Theory with Practice · Excellence in Financial Education</div>'
            f'<div style="{NOSELECT}{_text(LIGHT_BLUE)}font-size:14px;line-height:1.6;">'
            f'Prof. V. Ravichandran · Visiting Professor &amp; Professor of Practice at Leading Business Schools</div>'
            f'<div style="{NOSELECT}display:flex;flex-wrap:wrap;gap:18px;margin-top:12px;">{links}</div>'
            f'<div style="{NOSELECT}{_text(MUTED)}font-size:11px;margin-top:14px;">'
            f'Educational analysis only. Data source and cutoff are stated in the app. '
            f'No order placement or automated investment advice.</div>')
    st.html(_card(body, "margin-top:28px;"))
