"""Learner-facing explanations built from the same causal indicator frame.

Everything here only *reads* the analysed frame (already cut at the replay date),
so explanations, worked numbers and quiz answers never use future rows.
The language is descriptive and educational: it states what the indicators show,
never what to buy or sell.
"""
import numpy as np
import pandas as pd
from .config import Settings
from .signals import swing_structure

SITE = "https://themountainpathacademy.com"

# ---------------------------------------------------------------- learning path
LEARNING_PATH = [
    {"step": 1, "title": "What is technical analysis?", "url": f"{SITE}/learn-what-is-technical-analysis",
     "idea": "Technical analysis studies price and volume history to describe trend, levels and momentum. "
             "It does not value the business; it reads how buyers and sellers have behaved.",
     "look": "Start with the candlestick panel at the top of the chart. Is the price, broadly, rising, falling or moving sideways?",
     "try": "Set Visible chart bars to 250 (about one trading year) and describe the year in one sentence."},
    {"step": 2, "title": "Dow Theory and trend structure", "url": f"{SITE}/learn-what-is-dow-theory",
     "idea": "An uptrend makes higher highs and higher lows; a downtrend makes lower highs and lower lows. "
             "A swing is only 'known' a few bars after it happens.",
     "look": "Read 'Price structure' under the chart and open 'Confirmed swings' to see when each swing became knowable.",
     "try": "Turn on Historical replay, step forward ten sessions, and note when the swing label changes."},
    {"step": 3, "title": "Candlestick charts", "url": f"{SITE}/learn-candlestick-charts",
     "idea": "Each candle shows open, high, low and close. The body is open-to-close; the wicks show the range. "
             "Green closed above its open, red below.",
     "look": "Hover over any candle to read its four prices. The 'Candle figure' line names a setup when one appears.",
     "try": "Choose Chart layers → Candles only, find a long lower wick, and explain what buyers did that day."},
    {"step": 4, "title": "Moving averages: SMA and EMA", "url": f"{SITE}/learn-moving-averages-sma-ema",
     "idea": "A moving average smooths noise. The SMA weights every day equally; the EMA weights recent days more, "
             "so it turns sooner. Price above a rising 200-day average is a common long-term uptrend description.",
     "look": "Choose Chart layers → Price & averages. Compare the 50-day and 200-day lines; a gold triangle marks a golden cross.",
     "try": "Open 'Learn the calculations' and check today's SMA against the closes listed there."},
    {"step": 5, "title": "Support and resistance", "url": f"{SITE}/learn-support-and-resistance",
     "idea": "Support is a recent floor where falls have stopped; resistance a recent ceiling. Here they are the lowest "
             "low and highest high of the previous 20 bars, so today never counts towards its own level.",
     "look": "Choose Chart layers → Support & resistance. A close above the dashed red line is a breakout event.",
     "try": "Read how far the price is from each level in 'Read this chart', then find the last breakout on the chart."},
    {"step": 6, "title": "Momentum: ROC, RSI and MACD", "url": f"{SITE}/learn-momentum-indicators-roc-rsi-macd",
     "idea": "Momentum asks how fast price is changing. RSI above 70 or below 30 marks strong recent moves (not automatic reversals). "
             "MACD above its signal line means short-term momentum is improving.",
     "look": "Choose Chart layers → Momentum and read the three lower panels together.",
     "try": "Find a day when RSI was above 70 and check whether the price kept rising afterwards. Extremes can persist."},
]

# ---------------------------------------------------------------- glossary
GLOSSARY = {
    "OHLC": "Open, High, Low, Close — the four prices that make one candle.",
    "Candle body": "The part between open and close. Green (teal) if close > open, red if close < open.",
    "Wick (shadow)": "The thin line above or below the body showing the day's high and low.",
    "SMA": "Simple moving average: the plain average of the last n closes.",
    "EMA": "Exponential moving average: an average that gives more weight to recent closes.",
    "Golden cross": "The 50-day SMA crosses above the 200-day SMA — a widely watched trend event.",
    "Death cross": "The 50-day SMA crosses below the 200-day SMA.",
    "Support": "A recent floor: here, the lowest low of the previous n bars.",
    "Resistance": "A recent ceiling: here, the highest high of the previous n bars.",
    "Breakout": "A close above prior resistance, on the first day it happens.",
    "Breakdown": "A close below prior support, on the first day it happens.",
    "ROC": "Rate of change: the percentage change in close over n periods.",
    "RSI": "Relative Strength Index (0–100): the share of recent movement that came from up-days.",
    "Overbought / oversold": "RSI above 70 / below 30. Describes a strong recent move, not a guaranteed reversal.",
    "MACD": "Moving Average Convergence Divergence: fast EMA minus slow EMA.",
    "Signal line": "A 9-period EMA of MACD.",
    "Histogram": "MACD minus its signal line; bars above zero mean MACD is above its signal.",
    "Swing high / low": "A close higher (lower) than the closes on either side of it.",
    "Warm-up": "The first bars before an indicator has enough history to be calculated.",
    "Replay": "Hiding all prices after a chosen date, so you can practise without knowing the future.",
}

METRIC_HELP = {
    "Close": "The last completed day's closing price.",
    "Daily change %": "Percentage change from the previous close to the latest close.",
    "RSI": "Relative Strength Index, 0–100. Above 70: recent gains dominate. Below 30: recent losses dominate. 50 is balanced.",
    "ROC": "Rate of change: % change in close over the chosen number of periods. Above 0 = higher than then.",
    "MACD histogram": "MACD minus its signal line. Above 0: short-term momentum is improving; below 0: weakening.",
}


def _ok(v):
    return v is not None and not (isinstance(v, float) and np.isnan(v)) and not pd.isna(v)


def _pct(a, b):
    return (a / b - 1) * 100


# ---------------------------------------------------------------- read the chart
def read_the_chart(d, settings=Settings(), swings=None):
    """Return plain-English cards for the latest bar.

    Each card: lens, tone ('positive' | 'negative' | 'neutral' | 'waiting'),
    headline, explanation, watch (what would change the reading).
    """
    if d.empty:
        return []
    s = settings
    r = d.iloc[-1]
    close = float(r.Close)
    cards = []

    # Trend: price versus the 50- and 200-day SMA
    s50, s200 = r.get("SMA_50"), r.get("SMA_200")
    if _ok(s50) and _ok(s200):
        above50, above200 = close > s50, close > s200
        if above50 and above200:
            tone, head = "positive", "Price is above both its 50-day and 200-day averages"
        elif not above50 and not above200:
            tone, head = "negative", "Price is below both its 50-day and 200-day averages"
        else:
            tone, head = "neutral", ("Price is above the 200-day but below the 50-day average" if above200
                                     else "Price is above the 50-day but below the 200-day average")
        slope = d["SMA_200"].iloc[-1] - d["SMA_200"].iloc[-21] if len(d) > 21 and _ok(d["SMA_200"].iloc[-21]) else np.nan
        slope_txt = ("" if not _ok(slope) else
                     f" The 200-day average has {'risen' if slope > 0 else 'fallen'} over the last 20 sessions.")
        cards.append({"lens": "Trend", "tone": tone, "headline": head,
                      "explanation": f"Close {close:,.2f} vs SMA 50 {s50:,.2f} ({_pct(close, s50):+.1f}%) and "
                                     f"SMA 200 {s200:,.2f} ({_pct(close, s200):+.1f}%).{slope_txt} "
                                     "Long-term averages describe the backdrop; they react slowly by design.",
                      "watch": "A close back across the 200-day average, or a new 50/200 cross, would change this reading."})
    else:
        cards.append({"lens": "Trend", "tone": "waiting", "headline": "Not enough history for the 200-day average yet",
                      "explanation": "The 200-day SMA needs 200 completed closes. Missing values are not bearish — they are simply not calculated yet.",
                      "watch": "Step forward in replay, or use a longer history."})

    # Structure: swings
    if swings is not None:
        text = swing_structure(swings)
        tone = {"Higher highs and higher lows": "positive", "Lower highs and lower lows": "negative"}.get(text, "neutral")
        if text == "Insufficient confirmed swings":
            tone = "waiting"
        cards.append({"lens": "Structure (Dow)", "tone": tone, "headline": text,
                      "explanation": "Compares the last two confirmed swing highs and swing lows. "
                                     f"A swing is confirmed only {s.swing_window} bars after it happens, so this reading lags by design.",
                      "watch": "The next confirmed swing high or low can change the pattern."})

    # Momentum: RSI
    rsi = r.get("RSI")
    if _ok(rsi):
        if rsi >= 70:
            tone, head = "positive", f"RSI {rsi:.1f}: strong recent gains (overbought zone)"
            ex = "Recent up-moves have dominated. In strong uptrends RSI can stay above 70 for weeks; it is not an automatic sell signal."
        elif rsi <= 30:
            tone, head = "negative", f"RSI {rsi:.1f}: strong recent losses (oversold zone)"
            ex = "Recent down-moves have dominated. In strong downtrends RSI can stay below 30 for weeks; it is not an automatic buy signal."
        elif rsi >= 50:
            tone, head = "positive", f"RSI {rsi:.1f}: gains slightly outweigh losses"
            ex = "Above 50 means the average recent up-move exceeds the average recent down-move."
        else:
            tone, head = "negative", f"RSI {rsi:.1f}: losses slightly outweigh gains"
            ex = "Below 50 means the average recent down-move exceeds the average recent up-move."
        cards.append({"lens": f"Momentum · RSI {s.rsi_period}", "tone": tone, "headline": head, "explanation": ex,
                      "watch": "A move through 50 shows the balance of up- and down-days shifting."})

    # MACD
    m, sig, hist = r.get("MACD"), r.get("MACD_Signal"), r.get("MACD_Histogram")
    if _ok(m) and _ok(sig):
        prev = d["MACD_Histogram"].iloc[-2] if len(d) > 1 else np.nan
        rising = _ok(prev) and hist > prev
        tone = "positive" if m >= sig else "negative"
        head = f"MACD is {'above' if m >= sig else 'below'} its signal line and {'above' if m >= 0 else 'below'} zero"
        ex = (f"MACD {m:,.2f} vs signal {sig:,.2f}; histogram {hist:+,.2f}, "
              f"{'growing' if rising else 'shrinking'} versus yesterday. "
              "Above zero means the fast EMA is above the slow EMA.")
        cards.append({"lens": f"Momentum · MACD {s.macd_fast}/{s.macd_slow}/{s.macd_signal}", "tone": tone,
                      "headline": head, "explanation": ex,
                      "watch": "A histogram crossing zero marks MACD crossing its signal line."})

    # ROC
    roc = r.get("ROC")
    if _ok(roc):
        cards.append({"lens": f"Momentum · ROC {s.roc_period}", "tone": "positive" if roc > 0 else "negative",
                      "headline": f"Price is {abs(roc):.1f}% {'higher' if roc > 0 else 'lower'} than {s.roc_period} sessions ago",
                      "explanation": "ROC simply compares today's close with the close n sessions earlier.",
                      "watch": "ROC crossing zero means the price is back to where it was n sessions ago."})

    # Levels
    sup, res = r.get("Support"), r.get("Resistance")
    if _ok(sup) and _ok(res):
        to_res, to_sup = _pct(res, close), _pct(close, sup)
        if close > res:
            tone, head = "positive", f"Closed above prior {s.sr_period}-bar resistance ({res:,.2f})"
        elif close < sup:
            tone, head = "negative", f"Closed below prior {s.sr_period}-bar support ({sup:,.2f})"
        else:
            tone = "neutral"
            head = f"Trading inside its {s.sr_period}-bar range: {to_sup:.1f}% above support, {to_res:.1f}% below resistance"
        cards.append({"lens": "Levels", "tone": tone, "headline": head,
                      "explanation": f"Support {sup:,.2f} and resistance {res:,.2f} are the lowest and highest "
                                     f"{'prices' if s.sr_basis == 'High/Low' else 'closes'} of the previous {s.sr_period} bars, excluding today.",
                      "watch": "A close outside the range is a breakout or breakdown event."})

    # Candle
    pattern = r.get("Candle_Pattern") or ""
    body = abs(r.Close - r.Open)
    span = r.High - r.Low
    colour = "green (closed above its open)" if r.Close > r.Open else "red (closed below its open)" if r.Close < r.Open else "flat"
    share = f"{body / span * 100:.0f}% of the day's range" if span > 0 else "no range"
    cards.append({"lens": "Today's candle", "tone": "neutral",
                  "headline": pattern if pattern else f"A {colour.split(' ')[0]} candle with no named setup",
                  "explanation": f"The candle is {colour}; its body is {share}. "
                                 "Named setups are geometric shapes after a prior move; they need later confirmation.",
                  "watch": "Look at the next candle: does it confirm or reject the shape?"})
    return cards


def evidence_tally(cards):
    counts = {"positive": 0, "negative": 0, "neutral": 0, "waiting": 0}
    for c in cards:
        counts[c["tone"]] = counts.get(c["tone"], 0) + 1
    p, n = counts["positive"], counts["negative"]
    if p + n == 0:
        verdict = "Not enough calculated readings yet."
    elif p >= n + 2:
        verdict = "Most readings describe strength."
    elif n >= p + 2:
        verdict = "Most readings describe weakness."
    else:
        verdict = "Readings are mixed — the indicators disagree."
    return counts, verdict


# ---------------------------------------------------------------- worked numbers
def worked_numbers(d, settings=Settings()):
    """Step-by-step calculations for the latest bar, using only revealed rows."""
    s = settings
    c = d["Close"]
    out = {}
    n = s.short_ma
    if len(c) >= n:
        window = c.tail(n)
        out["SMA"] = {"title": f"SMA {n}: average of the last {n} closes",
                      "rows": [("Sum of the last %d closes" % n, f"{window.sum():,.2f}"),
                               ("Divide by %d" % n, f"{window.sum():,.2f} ÷ {n}"),
                               ("SMA %d" % n, f"{window.mean():,.2f}")],
                      "check": d[f"SMA_{n}"].iloc[-1],
                      "closes": window}
    ema = d.get(f"EMA_{n}")
    if ema is not None and len(ema) > 1 and _ok(ema.iloc[-1]) and _ok(ema.iloc[-2]):
        a = 2 / (n + 1)
        out["EMA"] = {"title": f"EMA {n}: today's close blended with yesterday's EMA",
                      "rows": [("Smoothing factor α = 2 ÷ (n + 1)", f"2 ÷ {n + 1} = {a:.4f}"),
                               ("α × today's close", f"{a:.4f} × {c.iloc[-1]:,.2f} = {a * c.iloc[-1]:,.2f}"),
                               ("(1 − α) × yesterday's EMA", f"{1 - a:.4f} × {ema.iloc[-2]:,.2f} = {(1 - a) * ema.iloc[-2]:,.2f}"),
                               ("EMA %d" % n, f"{a * c.iloc[-1] + (1 - a) * ema.iloc[-2]:,.2f}")],
                      "check": ema.iloc[-1]}
    k = s.roc_period
    if len(c) > k:
        out["ROC"] = {"title": f"ROC {k}: change over {k} sessions",
                      "rows": [("Today's close", f"{c.iloc[-1]:,.2f}"),
                               (f"Close {k} sessions ago ({c.index[-1 - k]:%d %b %Y})", f"{c.iloc[-1 - k]:,.2f}"),
                               ("(Today ÷ then − 1) × 100", f"({c.iloc[-1]:,.2f} ÷ {c.iloc[-1 - k]:,.2f} − 1) × 100"),
                               ("ROC", f"{(c.iloc[-1] / c.iloc[-1 - k] - 1) * 100:+.2f}%")],
                      "check": d["ROC"].iloc[-1]}
    rsi = d["RSI"].iloc[-1]
    if _ok(rsi):
        changes = c.diff()
        alpha = 1 / s.rsi_period
        from .indicators import seeded_average
        ag = seeded_average(changes.clip(lower=0), s.rsi_period, alpha=alpha).iloc[-1]
        al = seeded_average((-changes).clip(lower=0), s.rsi_period, alpha=alpha).iloc[-1]
        out["RSI"] = {"title": f"RSI {s.rsi_period} (Wilder): share of recent movement from up-days",
                      "rows": [("Average gain (Wilder-smoothed)", f"{ag:,.4f}"),
                               ("Average loss (Wilder-smoothed)", f"{al:,.4f}"),
                               ("RSI = 100 × gain ÷ (gain + loss)", f"100 × {ag:,.4f} ÷ {ag + al:,.4f}"),
                               ("RSI", f"{rsi:.2f}")],
                      "check": rsi}
    m = d["MACD"].iloc[-1]
    if _ok(m) and _ok(d["MACD_Signal"].iloc[-1]):
        from .indicators import seeded_average
        fast = seeded_average(c, s.macd_fast).iloc[-1]
        slow = seeded_average(c, s.macd_slow).iloc[-1]
        sig = d["MACD_Signal"].iloc[-1]
        out["MACD"] = {"title": f"MACD {s.macd_fast}/{s.macd_slow}/{s.macd_signal}",
                       "rows": [(f"EMA {s.macd_fast} (fast)", f"{fast:,.2f}"),
                                (f"EMA {s.macd_slow} (slow)", f"{slow:,.2f}"),
                                ("MACD = fast − slow", f"{fast:,.2f} − {slow:,.2f} = {m:,.2f}"),
                                (f"Signal = EMA {s.macd_signal} of MACD", f"{sig:,.2f}"),
                                ("Histogram = MACD − signal", f"{m:,.2f} − {sig:,.2f} = {m - sig:+,.2f}")],
                       "check": d["MACD_Histogram"].iloc[-1]}
    sup, res = d["Support"].iloc[-1], d["Resistance"].iloc[-1]
    if _ok(sup) and _ok(res):
        prior = d.iloc[-1 - s.sr_period:-1]
        lo = prior["Low"] if s.sr_basis == "High/Low" else prior["Close"]
        hi = prior["High"] if s.sr_basis == "High/Low" else prior["Close"]
        out["Levels"] = {"title": f"Support and resistance: previous {s.sr_period} bars, excluding today",
                         "rows": [("Window", f"{prior.index[0]:%d %b %Y} to {prior.index[-1]:%d %b %Y}"),
                                  (f"Lowest {'low' if s.sr_basis == 'High/Low' else 'close'} → support", f"{lo.min():,.2f} on {lo.idxmin():%d %b %Y}"),
                                  (f"Highest {'high' if s.sr_basis == 'High/Low' else 'close'} → resistance", f"{hi.max():,.2f} on {hi.idxmax():%d %b %Y}")],
                         "check": res}
    return out


# ---------------------------------------------------------------- quiz
def quiz(d, settings=Settings(), swings=None):
    """Questions whose answers are computed from the revealed data."""
    if d.empty:
        return []
    r = d.iloc[-1]
    s = settings
    qs = []
    if _ok(r.get("SMA_200")):
        ans = "Above" if r.Close > r.SMA_200 else "Below"
        qs.append({"q": "Is the latest close above or below its 200-day SMA?", "options": ["Above", "Below"], "answer": ans,
                   "why": f"Close {r.Close:,.2f} vs SMA 200 {r.SMA_200:,.2f}. Check the purple solid line on the price panel."})
    if _ok(r.get("RSI")):
        ans = "Above 70" if r.RSI >= 70 else "Below 30" if r.RSI <= 30 else "Between 30 and 70"
        qs.append({"q": f"Where is RSI {s.rsi_period} right now?", "options": ["Above 70", "Between 30 and 70", "Below 30"], "answer": ans,
                   "why": f"RSI is {r.RSI:.1f}. Read it on the RSI panel against the dotted 30, 50 and 70 lines."})
    if _ok(r.get("MACD")) and _ok(r.get("MACD_Signal")):
        ans = "Above its signal line" if r.MACD >= r.MACD_Signal else "Below its signal line"
        qs.append({"q": "Is MACD above or below its signal line?", "options": ["Above its signal line", "Below its signal line"], "answer": ans,
                   "why": f"MACD {r.MACD:,.2f} vs signal {r.MACD_Signal:,.2f}; the histogram is {'positive' if r.MACD >= r.MACD_Signal else 'negative'}."})
    if _ok(r.get("ROC")):
        ans = "Higher" if r.ROC > 0 else "Lower"
        qs.append({"q": f"Is today's close higher or lower than {s.roc_period} sessions ago?", "options": ["Higher", "Lower"], "answer": ans,
                   "why": f"ROC {s.roc_period} is {r.ROC:+.2f}% — {'positive' if r.ROC > 0 else 'negative'} means {ans.lower()}."})
    if _ok(r.get("Support")) and _ok(r.get("Resistance")):
        ans = ("Above resistance" if r.Close > r.Resistance else "Below support" if r.Close < r.Support else "Between support and resistance")
        qs.append({"q": f"Where did today close relative to the prior {s.sr_period}-bar range?",
                   "options": ["Above resistance", "Between support and resistance", "Below support"], "answer": ans,
                   "why": f"Support {r.Support:,.2f}, resistance {r.Resistance:,.2f}, close {r.Close:,.2f}."})
    if r.Close != r.Open:
        ans = "Green (close above open)" if r.Close > r.Open else "Red (close below open)"
        qs.append({"q": "What colour is today's candle?", "options": ["Green (close above open)", "Red (close below open)"], "answer": ans,
                   "why": f"Open {r.Open:,.2f}, close {r.Close:,.2f}."})
    if swings is not None:
        text = swing_structure(swings)
        if text != "Insufficient confirmed swings":
            qs.append({"q": "Which describes the latest confirmed swing structure?",
                       "options": ["Higher highs and higher lows", "Lower highs and lower lows", "Mixed swing structure"], "answer": text,
                       "why": "Compare the last two confirmed swing highs and the last two confirmed swing lows (see 'Confirmed swings')."})
    return qs
