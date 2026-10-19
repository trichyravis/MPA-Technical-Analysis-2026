"""The Live summary and the Filter observations list must always agree."""
from io import BytesIO
from pathlib import Path
import pandas as pd
from streamlit.testing.v1 import AppTest
from technical_lab.config import Settings
from technical_lab.data import demo_history
from technical_lab.indicators import compute_indicators
from technical_lab.signals import add_signals, summary_row, confirmed_swings
from technical_lab.universe import reference_universe
from technical_lab.observations import OBSERVATIONS, NAMES, observation_mask, observation_summary, breadth_headline
from technical_lab.exports import excel_bytes

ROOT = Path(__file__).resolve().parents[1]
S = Settings()


def scan(extra_rows=()):
    rows = []
    for symbol in reference_universe().Symbol:
        rows.append(summary_row(symbol, add_signals(compute_indicators(demo_history(symbol), S), S), S))
    rows.extend(extra_rows)
    return pd.DataFrame(rows)


def test_summary_counts_equal_filter_counts():
    screen = scan()
    summary = observation_summary(screen)
    assert summary.Observation.tolist() == NAMES
    for name in NAMES:
        shown = screen.loc[observation_mask(screen, name)]
        row = summary.loc[summary.Observation.eq(name)].iloc[0]
        assert row.Matching == len(shown), name
        listed = [] if row.Instruments == "—" else row.Instruments.split(", ")
        assert listed == shown.Symbol.tolist(), name


def test_rules_match_their_definitions():
    screen = scan()
    rsi = screen.RSI
    assert observation_mask(screen, "RSI ≥ 70").sum() == rsi.ge(70).sum()
    assert observation_mask(screen, "RSI ≤ 30").sum() == rsi.le(30).sum()
    assert observation_mask(screen, "Positive ROC").sum() == screen["ROC %"].gt(0).sum()
    regime_up = observation_mask(screen, "SMA50 above SMA200").sum()
    regime_down = observation_mask(screen, "SMA50 below SMA200").sum()
    assert regime_up + regime_down == screen["SMA50 above SMA200"].notna().sum()


def test_error_rows_and_missing_values_never_match():
    screen = scan([{"Symbol": "BROKEN.NS", "Status": "Error: no data"}])
    summary = observation_summary(screen)
    assert "BROKEN.NS" not in " ".join(summary.Instruments)
    for name in NAMES:
        assert not observation_mask(screen, name).iloc[-1], name
    assert summary.Measured.max() <= len(screen) - 1


def test_breadth_headline_and_excel_sheet():
    screen = scan()
    summary = observation_summary(screen)
    assert "above their 200-day SMA" in breadth_headline(summary)
    d = add_signals(compute_indicators(demo_history("^NSEI"), S), S)
    wb = excel_bytes(d, S, {"Source": "Demo", "Cutoff": "x"}, screen=screen,
                     swings=confirmed_swings(d.Close), summary=summary)
    sheets = pd.read_excel(BytesIO(wb), sheet_name=None)
    assert list(sheets)[:2] == ["Read Me", "Screener Summary"]
    assert len(sheets["Screener Summary"]) == len(OBSERVATIONS)


def test_app_shows_live_summary_after_scan():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
    next(b for b in app.button if b.label == "Run screener").click().run(timeout=90)
    assert not app.exception
    assert any(len(x.value) == len(OBSERVATIONS) and "Observation" in x.value for x in app.dataframe)
    box = next(x for x in app.selectbox if x.label == "Filter observations")
    assert box.options == ["All", *NAMES]
    box.set_value("Above SMA200").run(timeout=90)
    assert not app.exception
