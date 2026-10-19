"""One definition of every screener observation.

The Screener's "Filter observations" list and the Live summary table are both
built from OBSERVATIONS, so a filter always shows exactly the instruments the
summary counts. Observations describe indicator states; they are not rankings
or recommendations.
"""
import pandas as pd

# name, group, column, rule, plain meaning
OBSERVATIONS = [
    ("Above SMA200", "Trend · SMA", "Above SMA200", "true",
     "Close is above its 200-day simple moving average (long-term backdrop)."),
    ("Above SMA50", "Trend · SMA", "Above SMA50", "true",
     "Close is above its 50-day simple moving average (medium-term backdrop)."),
    ("Above short EMA", "Trend · EMA", "Above short EMA", "true",
     "Close is above its short exponential moving average (default 20-day), which reacts fastest."),
    ("SMA50 above SMA200", "Crosses · regime", "SMA50 above SMA200", "true",
     "The 50-day SMA is above the 200-day SMA: the state that follows a golden cross."),
    ("SMA50 below SMA200", "Crosses · regime", "SMA50 above SMA200", "false",
     "The 50-day SMA is below the 200-day SMA: the state that follows a death cross."),
    ("Golden cross today", "Crosses · event", "Golden cross today", "true",
     "The 50-day SMA crossed above the 200-day SMA on the latest day."),
    ("Death cross today", "Crosses · event", "Death cross today", "true",
     "The 50-day SMA crossed below the 200-day SMA on the latest day."),
    ("RSI ≥ 70", "Momentum · RSI", "RSI", ">=70",
     "Strong recent gains (overbought zone). Can persist in strong uptrends."),
    ("RSI ≤ 30", "Momentum · RSI", "RSI", "<=30",
     "Strong recent losses (oversold zone). Can persist in strong downtrends."),
    ("RSI above 50", "Momentum · RSI", "RSI", ">50",
     "Average recent up-move exceeds the average recent down-move."),
    ("MACD above signal", "Momentum · MACD", "MACD above signal", "true",
     "MACD is at or above its signal line; short-term momentum is improving."),
    ("MACD cross up today", "Momentum · MACD", "MACD cross up today", "true",
     "MACD crossed above its signal line on the latest day."),
    ("MACD cross down today", "Momentum · MACD", "MACD cross down today", "true",
     "MACD crossed below its signal line on the latest day."),
    ("Positive ROC", "Momentum · ROC", "ROC %", ">0",
     "Close is higher than it was ROC-period sessions ago."),
    ("Negative ROC", "Momentum · ROC", "ROC %", "<0",
     "Close is lower than it was ROC-period sessions ago."),
    ("Breakout event", "Levels", "Breakout event", "true",
     "First close above the prior-window resistance."),
    ("Breakdown event", "Levels", "Breakdown event", "true",
     "First close below the prior-window support."),
    ("Candle setup present", "Candles", "Candle setup", "nonempty",
     "A named candlestick setup (doji, hammer, shooting star, engulfing) on the latest day."),
]

NAMES = [o[0] for o in OBSERVATIONS]
_BY_NAME = {o[0]: o for o in OBSERVATIONS}


def _usable(screen):
    """Rows that produced a reading (errors and empty histories are excluded)."""
    if screen.empty:
        return screen
    ok = ~screen.get("Status", pd.Series("", index=screen.index)).astype(str).str.startswith(("Error", "No completed"))
    return screen.loc[ok]


def observation_mask(screen, name):
    """Boolean mask over `screen` for one observation; missing values never match."""
    _, _, column, rule, _ = _BY_NAME[name]
    if column not in screen:
        return pd.Series(False, index=screen.index)
    col = screen[column]
    if rule in ("true", "false"):
        want = rule == "true"
        known = col.map(lambda v: v is not None and not (isinstance(v, float) and pd.isna(v)))
        return (known & col.map(lambda v: bool(v) == want if v is not None and not (isinstance(v, float) and pd.isna(v)) else False)).astype(bool)
    if rule == "nonempty":
        return col.map(lambda v: isinstance(v, str) and v.strip() != "").astype(bool)
    numbers = pd.to_numeric(col, errors="coerce")
    op = rule[:2] if rule[:2] in (">=", "<=") else rule[0]
    threshold = float(rule[len(op):])
    result = {">=": numbers.ge, "<=": numbers.le, ">": numbers.gt, "<": numbers.lt}[op](threshold)
    return result.fillna(False).astype(bool)


def observation_summary(screen):
    """One row per observation: how many usable instruments match, the share, and which."""
    usable = _usable(screen)
    rows = []
    for name, group, column, _, meaning in OBSERVATIONS:
        mask = observation_mask(usable, name)
        if column in usable:
            measured = usable[column].map(lambda v: not (v is None or (isinstance(v, float) and pd.isna(v)))).sum()
        else:
            measured = 0
        matched = usable.loc[mask, "Symbol"].astype(str).tolist() if "Symbol" in usable else []
        rows.append({"Group": group, "Observation": name, "Matching": int(mask.sum()),
                     "Measured": int(measured),
                     "Share": (mask.sum() / measured) if measured else None,
                     "Instruments": ", ".join(matched) if matched else "—",
                     "Meaning": meaning})
    return pd.DataFrame(rows)


def breadth_headline(summary):
    """A one-line breadth reading built from the summary table."""
    get = lambda n: summary.loc[summary.Observation.eq(n)].iloc[0]
    try:
        a200, rsi50, macd = get("Above SMA200"), get("RSI above 50"), get("MACD above signal")
    except IndexError:
        return ""
    def part(row, text):
        return f"{row.Matching} of {row.Measured} {text}" if row.Measured else ""
    bits = [part(a200, "above their 200-day SMA"), part(rsi50, "with RSI above 50"), part(macd, "with MACD above signal")]
    return " · ".join(b for b in bits if b)
