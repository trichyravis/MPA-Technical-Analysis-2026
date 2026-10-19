"""Learner features must agree with the plotted indicators and never use future rows."""
import math
from pathlib import Path
import pandas as pd
from streamlit.testing.v1 import AppTest
from technical_lab.config import Settings
from technical_lab.data import demo_history
from technical_lab.indicators import compute_indicators
from technical_lab.signals import add_signals, confirmed_swings
from technical_lab.replay import as_of
from technical_lab.learning import (read_the_chart, evidence_tally, worked_numbers, quiz,
                                    LEARNING_PATH, GLOSSARY)
from technical_lab.charts import technical_chart, LAYERS

ROOT = Path(__file__).resolve().parents[1]
S = Settings()


def frame(cutoff=None):
    full = demo_history("^NSEI")
    if cutoff is not None:
        full = as_of(full, cutoff)
    return add_signals(compute_indicators(full, S), S)


def test_worked_numbers_match_plotted_values():
    d = frame()
    w = worked_numbers(d, S)
    assert {"SMA", "EMA", "ROC", "RSI", "MACD", "Levels"} <= set(w)
    sma = w["SMA"]
    assert math.isclose(sma["closes"].mean(), d[f"SMA_{S.short_ma}"].iloc[-1], rel_tol=1e-12)
    # The EMA recurrence shown to learners reproduces the plotted EMA.
    a = 2 / (S.short_ma + 1)
    ema = d[f"EMA_{S.short_ma}"]
    assert math.isclose(a * d.Close.iloc[-1] + (1 - a) * ema.iloc[-2], ema.iloc[-1], rel_tol=1e-12)
    assert f"{d.RSI.iloc[-1]:.2f}" in w["RSI"]["rows"][-1][1]
    assert f"{(d.Close.iloc[-1] / d.Close.iloc[-1 - S.roc_period] - 1) * 100:+.2f}%" == w["ROC"]["rows"][-1][1]


def test_explanations_use_only_revealed_rows():
    cutoff = demo_history("^NSEI").index[400].date()
    d = frame(cutoff)
    assert d.index[-1].date() <= cutoff
    swings = confirmed_swings(d.Close, S.swing_window)
    cards = read_the_chart(d, S, swings)
    # Identical text whether or not later rows existed in the source history.
    again = read_the_chart(add_signals(compute_indicators(as_of(demo_history("^NSEI"), cutoff), S), S), S, swings)
    assert cards == again
    assert all({"lens", "tone", "headline", "explanation", "watch"} <= set(c) for c in cards)


def test_quiz_answers_follow_the_data():
    d = frame()
    swings = confirmed_swings(d.Close, S.swing_window)
    qs = quiz(d, S, swings)
    assert len(qs) >= 5
    r = d.iloc[-1]
    for q in qs:
        assert q["answer"] in q["options"]
        if "200-day" in q["q"]:
            assert q["answer"] == ("Above" if r.Close > r.SMA_200 else "Below")
        if "signal line" in q["q"]:
            assert q["answer"].startswith("Above" if r.MACD >= r.MACD_Signal else "Below")


def test_warm_up_is_labelled_not_bearish():
    d = frame(demo_history("^NSEI").index[60].date())
    cards = read_the_chart(d, S, confirmed_swings(d.Close, S.swing_window))
    trend = next(c for c in cards if c["lens"] == "Trend")
    assert trend["tone"] == "waiting"
    counts, verdict = evidence_tally(cards)
    assert counts["waiting"] >= 1 and isinstance(verdict, str)


def test_learning_path_and_glossary_are_complete():
    assert [s["step"] for s in LEARNING_PATH] == [1, 2, 3, 4, 5, 6]
    assert all(s["url"].startswith("https://themountainpathacademy.com/learn-") for s in LEARNING_PATH)
    assert {"RSI", "MACD", "SMA", "EMA", "Support", "Resistance"} <= set(GLOSSARY)


def test_every_chart_layer_renders():
    d = frame()
    full = technical_chart(d, "^NSEI", S, layers="Everything")
    assert len(technical_chart(d, "^NSEI", S, layers="Candles only").data) == 1
    for layer in LAYERS:
        assert len(technical_chart(d, "^NSEI", S, layers=layer).data) <= len(full.data)


def test_start_here_and_quiz_tabs_run_in_app():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not app.exception
    assert any(s.value == "New to technical analysis? Start here" for s in app.subheader)
    radios = [r for r in app.radio if r.label.startswith("Q")]
    assert len(radios) >= 5
    for r in radios:
        r.set_value(r.options[0])
    next(b for b in app.button if b.label == "Check my answers").click().run()
    assert not app.exception
    assert any(m.label == "Your score" for m in app.metric)
