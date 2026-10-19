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


TONES = {
    "positive": ("#37CDB0", "▲ Strength"),
    "negative": ("#FF6B7C", "▼ Weakness"),
    "neutral": (LIGHT_BLUE, "◆ Neutral"),
    "waiting": (MUTED, "… Warming up"),
}


def _esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def reading_cards(cards, counts, verdict):
    """Plain-English indicator cards with a strength/weakness tally."""
    tally = "".join(
        f'<span style="{NOSELECT}{_text(TONES[k][0])}font-size:13px;font-weight:700;margin-right:18px;">'
        f'{TONES[k][1]}: {counts.get(k, 0)}</span>' for k in ("positive", "negative", "neutral", "waiting"))
    head = (f'<div style="{NOSELECT}background:{CARD};border:1px solid rgba(255,215,0,.3);border-radius:14px;'
            f'padding:14px 18px;margin-bottom:12px;font-family:Arial,sans-serif;">'
            f'<div style="{NOSELECT}{_text(GOLD)}font-size:15px;font-weight:700;margin-bottom:6px;">{_esc(verdict)}</div>'
            f'<div style="{NOSELECT}">{tally}</div></div>')
    items = []
    for c in cards:
        color, label = TONES.get(c["tone"], TONES["neutral"])
        items.append(
            f'<div style="{NOSELECT}background:{CARD};border:1px solid rgba(255,255,255,.08);border-left:4px solid {color};'
            f'border-radius:12px;padding:14px 16px;font-family:Arial,sans-serif;">'
            f'<div style="{NOSELECT}display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;">'
            f'<span style="{NOSELECT}{_text(MUTED)}font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;">{_esc(c["lens"])}</span>'
            f'<span style="{NOSELECT}{_text(color)}font-size:12px;font-weight:700;">{label}</span></div>'
            f'<div style="{NOSELECT}{_text("#ffffff")}font-size:15px;font-weight:700;line-height:1.4;margin:6px 0;">{_esc(c["headline"])}</div>'
            f'<div style="{NOSELECT}{_text(TXT)}font-size:13px;line-height:1.55;">{_esc(c["explanation"])}</div>'
            f'<div style="{NOSELECT}{_text(LIGHT_BLUE)}font-size:12px;line-height:1.5;margin-top:8px;">'
            f'<span style="{NOSELECT}{_text(GOLD)}font-weight:700;">What would change this: </span>{_esc(c["watch"])}</div></div>')
    grid = (f'<div style="{NOSELECT}display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;">'
            + "".join(items) + '</div>')
    st.html(head + grid)


def learning_step_card(item):
    """One step of the six-part learning path, linking to the matching website lesson."""
    row = lambda label, text: (
        f'<div style="{NOSELECT}margin-top:8px;"><span style="{NOSELECT}{_text(GOLD)}font-size:12px;font-weight:700;'
        f'letter-spacing:1px;">{label} </span><span style="{NOSELECT}{_text(TXT)}font-size:14px;line-height:1.55;">{_esc(text)}</span></div>')
    html = (f'<div style="{NOSELECT}background:{CARD};border:1px solid rgba(255,215,0,.22);border-radius:14px;'
            f'padding:16px 18px;margin-bottom:12px;font-family:Arial,sans-serif;">'
            f'<div style="{NOSELECT}display:flex;align-items:center;gap:12px;flex-wrap:wrap;">'
            f'<span style="{NOSELECT}{_text(BLUE)}background:{GOLD};border-radius:50%;width:30px;height:30px;'
            f'display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;">{item["step"]}</span>'
            f'<span style="{NOSELECT}{_text("#ffffff")}font-size:17px;font-weight:700;">{_esc(item["title"])}</span>'
            f'<a href="{item["url"]}" target="_blank" rel="noopener noreferrer" style="{_text(GOLD)}font-size:13px;'
            f'font-weight:600;text-decoration:none;margin-left:auto;">Read the lesson ↗</a></div>'
            + row("THE IDEA", item["idea"]) + row("LOOK AT", item["look"]) + row("TRY THIS", item["try"]) + '</div>')
    st.html(html)
