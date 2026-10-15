"""Daily data adapters. Demo always works offline; Yahoo is an optional research source.

For a public licensed feed, implement fetch_many(symbols, start, end), returning
{symbol: normalized_frame}, {symbol: error}. Keep credentials on the server.
"""
from hashlib import sha256
from io import BytesIO
import numpy as np
import pandas as pd

OHLC=["Open","High","Low","Close"]


def normalize_frame(frame, is_index=False):
    d=frame.copy()
    d.columns=[str(c).strip().title() for c in d.columns]
    if "Date" in d.columns:
        d.index=pd.to_datetime(d.pop("Date"),errors="raise")
    if not isinstance(d.index,pd.DatetimeIndex):
        raise ValueError("A Date column or DatetimeIndex is required.")
    if d.index.tz is not None:
        d.index=d.index.tz_convert("Asia/Kolkata").tz_localize(None)
    d.index=d.index.normalize()
    d.index.name="Date"
    if not set(OHLC).issubset(d.columns):
        raise ValueError("Required columns: Date, Open, High, Low, Close; Volume optional.")
    if d.index.hasnans or d.index.duplicated().any():
        raise ValueError("Duplicate or missing daily dates found. Aggregate intraday data first.")
    for k in OHLC:
        d[k]=pd.to_numeric(d[k],errors="raise")
    if not np.isfinite(d[OHLC].to_numpy()).all() or (d[OHLC]<=0).any().any():
        raise ValueError("OHLC prices must be finite and positive; no missing bars accepted.")
    if ((d.High<d[["Open","Close","Low"]].max(axis=1)) | (d.Low>d[["Open","Close","High"]].min(axis=1))).any():
        raise ValueError("OHLC values are inconsistent: check each bar's high and low.")
    d["Volume"]=pd.to_numeric(d.get("Volume",pd.Series(np.nan,index=d.index)),errors="coerce")
    if (d.Volume.dropna()<0).any():
        raise ValueError("Volume cannot be negative.")
    if np.isinf(d.Volume.dropna()).any():
        raise ValueError("Volume must be finite when supplied.")
    if is_index:
        d["Volume"]=np.nan  # A calculated spot index has no traded share volume.
    return d[OHLC+["Volume"]].sort_index()


def demo_history(symbol, periods=850):
    """Stable, reproducible synthetic business-day series, NOT exchange sessions."""
    seed=int.from_bytes(sha256(symbol.encode()).digest()[:8],"little")
    rng=np.random.default_rng(seed)
    dates=pd.bdate_range(end="2026-10-01",periods=periods)
    t=np.arange(periods)
    daily=.00025+.0012*np.sin(t/80)+rng.normal(0,.012,periods)
    base=24000 if symbol=="^NSEI" else 52000 if symbol=="^NSEBANK" else 300+seed%2500
    close=base*np.exp(np.cumsum(daily));previous=np.r_[base,close[:-1]]
    op=previous*np.exp(rng.normal(0,.003,periods));spread=rng.uniform(.002,.018,periods)
    high=np.maximum(op,close)*(1+spread);low=np.minimum(op,close)*(1-spread)
    volume=rng.integers(150000,9000000,periods).astype(float)
    d=pd.DataFrame({"Open":op,"High":high,"Low":low,"Close":close,"Volume":volume},index=dates)
    return normalize_frame(d,is_index=symbol.startswith("^"))


def read_csv_bundle(payload):
    d=pd.read_csv(BytesIO(payload))
    d.columns=[str(k).strip().title() for k in d.columns]
    if not {"Date","Symbol",*OHLC}.issubset(d.columns):
        raise ValueError("CSV needs Symbol, Date, Open, High, Low, Close (Volume optional).")
    if d.Symbol.isna().any():
        raise ValueError("Every CSV row needs a symbol.")
    frames={}
    for symbol, group in d.groupby("Symbol",sort=True):
        symbol=str(symbol).strip()
        if not symbol:
            raise ValueError("Blank symbol in CSV.")
        frames[symbol]=normalize_frame(group.drop(columns="Symbol"),is_index=symbol.startswith("^"))
    if not frames:
        raise ValueError("The CSV contains no bars.")
    return frames


def yahoo_fetch_many(symbols, start, end):
    """end is exclusive. Opt-in is enforced by the UI, not by silently falling back.

    Yahoo prices can be delayed, revised, split-adjusted or unavailable. No live SLA.
    Disable auto_adjust to avoid dividend-total-return OHLC, but provider historical
    split adjustments still mean this is not a point-in-time corporate-action feed.
    """
    import yfinance as yf
    frames,errors={},{}
    if not symbols:
        return frames,errors
    raw=yf.download(list(symbols),start=str(start),end=str(end),interval="1d",
                    auto_adjust=False,actions=False,group_by="ticker",threads=False,progress=False,timeout=20)
    for symbol in symbols:
        try:
            if raw.empty:
                raise ValueError("Provider returned no prices.")
            if isinstance(raw.columns,pd.MultiIndex):
                if symbol in raw.columns.get_level_values(0):
                    part=raw[symbol]
                elif symbol in raw.columns.get_level_values(1):
                    part=raw.xs(symbol,axis=1,level=1)
                else:
                    raise ValueError("Symbol missing in provider response.")
            else:
                part=raw
            # Bulk downloads union session dates; drop all-empty per-symbol OHLC rows.
            part=part.dropna(subset=OHLC,how="all")
            if part.empty:
                raise ValueError("No history for this symbol.")
            frames[symbol]=normalize_frame(part,is_index=symbol.startswith("^"))
        except Exception as exc:
            errors[symbol]=str(exc)
    return frames,errors
