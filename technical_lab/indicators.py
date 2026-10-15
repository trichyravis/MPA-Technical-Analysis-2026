"""Causal calculations: every row depends only on that row and earlier rows.

EMA seed = first full-window SMA. Wilder RSI seed = n changes / n,
then alpha=1/n recurrence. All-flat RSI=50; gain-only=100; loss-only=0.
Input must contain finite, contiguous OHLC observations, sorted ascending.
"""
import numpy as np
import pandas as pd
from .config import Settings


def seeded_average(series, period, alpha=None):
    if period < 1:
        raise ValueError("period must be positive")
    alpha = 2.0 / (period + 1) if alpha is None else float(alpha)
    result = pd.Series(np.nan, index=series.index, dtype=float)
    positions = np.flatnonzero(series.notna().to_numpy())
    if len(positions) < period:
        return result
    # Only leading warm-up gaps are supported. Never silently bridge missing bars.
    if not np.all(np.diff(positions) == 1):
        raise ValueError("Interior gaps must be cleaned before smoothing.")
    # Work on plain NumPy arrays: per-element .iloc access made the 52-instrument
    # screener roughly 30x slower than necessary.
    values = series.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    seed_pos = int(positions[period - 1])
    previous = float(values[positions[:period]].mean())
    out[seed_pos] = previous
    for i in positions[period:]:
        previous = alpha * values[i] + (1 - alpha) * previous
        out[i] = previous
    result[:] = out
    return result


def rsi_wilder(close, period=14):
    changes = close.diff()
    gains = changes.clip(lower=0)
    losses = (-changes).clip(lower=0)
    ag = seeded_average(gains, period, alpha=1 / period)
    al = seeded_average(losses, period, alpha=1 / period)
    total = ag + al
    result = 100 * ag / total.replace(0, np.nan)
    return result.mask(total.eq(0), 50.0)


def compute_indicators(frame, settings=Settings()):
    s = settings.validate()
    d = frame.copy()
    c = d["Close"]
    for n in sorted({s.short_ma, s.fast_ma, s.slow_ma, 50, 200}):
        d[f"SMA_{n}"] = c.rolling(n, min_periods=n).mean()
        d[f"EMA_{n}"] = seeded_average(c, n)
    d["ROC"] = (c / c.shift(s.roc_period) - 1) * 100
    d["RSI"] = rsi_wilder(c, s.rsi_period)
    d["MACD"] = seeded_average(c, s.macd_fast) - seeded_average(c, s.macd_slow)
    d["MACD_Signal"] = seeded_average(d["MACD"], s.macd_signal)
    d["MACD_Histogram"] = d["MACD"] - d["MACD_Signal"]
    low = d["Low"] if s.sr_basis == "High/Low" else c
    high = d["High"] if s.sr_basis == "High/Low" else c
    # EXCLUDE the tested bar, so strict breakouts can occur without self-inclusion.
    d["Support"] = low.shift(1).rolling(s.sr_period, min_periods=s.sr_period).min()
    d["Resistance"] = high.shift(1).rolling(s.sr_period, min_periods=s.sr_period).max()
    volume = d.get("Volume", pd.Series(np.nan, index=d.index))
    d["Volume_Mean20_Prior"] = volume.shift(1).rolling(20, min_periods=20).mean()
    d["Volume_Ratio"] = volume / d["Volume_Mean20_Prior"].replace(0, np.nan)
    d["Return_1D_Pct"] = c.pct_change(fill_method=None) * 100
    return d
