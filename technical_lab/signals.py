"""Descriptive signals, not recommendations or validated probability estimates."""
import numpy as np
import pandas as pd
from .config import Settings


def crossover(a, b):
    valid = a.notna() & b.notna() & a.shift(1).notna() & b.shift(1).notna()
    up = valid & (a > b) & (a.shift(1) <= b.shift(1))
    down = valid & (a < b) & (a.shift(1) >= b.shift(1))
    return up, down


def add_signals(frame, settings=Settings()):
    d = frame.copy()
    s = settings
    d["MA_Cross_Up"], d["MA_Cross_Down"] = crossover(d[f"SMA_{s.fast_ma}"], d[f"SMA_{s.slow_ma}"])
    d["Golden_Cross"], d["Death_Cross"] = crossover(d["SMA_50"], d["SMA_200"])
    d["MACD_Cross_Up"], d["MACD_Cross_Down"] = crossover(d["MACD"], d["MACD_Signal"])
    # A breakout event is an entry into the above-prior-bound state.
    above = d["Close"] > d["Resistance"]
    below = d["Close"] < d["Support"]
    d["Above_Prior_Resistance"] = above & d["Resistance"].notna()
    d["Below_Prior_Support"] = below & d["Support"].notna()
    d["Breakout_Event"] = d["Above_Prior_Resistance"] & ~above.shift(1, fill_value=False)
    d["Breakdown_Event"] = d["Below_Prior_Support"] & ~below.shift(1, fill_value=False)
    d["Candle_Pattern"] = candle_patterns(d)
    return d


def candle_patterns(d):
    o, h, l, c = [d[k] for k in ("Open", "High", "Low", "Close")]
    body, span = (c-o).abs(), h-l
    upper, lower = h-pd.concat([o,c],axis=1).max(axis=1), pd.concat([o,c],axis=1).min(axis=1)-l
    prior_up = c.shift(1) > c.shift(4)
    prior_down = c.shift(1) < c.shift(4)
    # Transparent geometric teaching rules, not a proprietary pattern classifier.
    doji = (span > 0) & (body <= .1*span)
    hammer = prior_down & (body > .1*span) & (lower >= 2*body) & (upper <= body)
    star = prior_up & (body > .1*span) & (upper >= 2*body) & (lower <= body)
    bull_engulf = prior_down & (c.shift(1)<o.shift(1)) & (c>o) & (o<=c.shift(1)) & (c>=o.shift(1))
    bear_engulf = prior_up & (c.shift(1)>o.shift(1)) & (c<o) & (o>=c.shift(1)) & (c<=o.shift(1))
    labels = pd.Series("",index=d.index,dtype=object)
    for condition, label in [(doji,"Doji shape"),(hammer,"Hammer setup"),(star,"Shooting-star setup"),
                             (bull_engulf,"Bullish engulfing setup"),(bear_engulf,"Bearish engulfing setup")]:
        labels.loc[condition] = label
    return labels


def confirmed_swings(close, window=3):
    """Expose a pivot at its KNOWLEDGE date (window bars later), never backdate it."""
    records = []
    for known in range(2*window, len(close)):
        pivot = known-window
        area = close.iloc[pivot-window:known+1]
        value = float(close.iloc[pivot])
        for kind, condition in [("High", value==area.max() and (area==value).sum()==1),
                                ("Low", value==area.min() and (area==value).sum()==1)]:
            if condition:
                records.append({"PivotDate":close.index[pivot],"KnownOn":close.index[known],"Kind":kind,"Price":value})
    return pd.DataFrame(records,columns=["PivotDate","KnownOn","Kind","Price"])


def swing_structure(swings):
    highs = swings.loc[swings.Kind.eq("High"),"Price"].tail(2).to_list()
    lows = swings.loc[swings.Kind.eq("Low"),"Price"].tail(2).to_list()
    if len(highs)<2 or len(lows)<2:
        return "Insufficient confirmed swings"
    if highs[1]>highs[0] and lows[1]>lows[0]:
        return "Higher highs and higher lows"
    if highs[1]<highs[0] and lows[1]<lows[0]:
        return "Lower highs and lower lows"
    return "Mixed swing structure"


def last_cross(d, up_col, down_col, up_name="Up", down_name="Down"):
    events = d.loc[d[up_col] | d[down_col]]
    if events.empty:
        return "None in available history", ""
    last = events.iloc[-1]
    return (up_name if last[up_col] else down_name), events.index[-1].strftime("%Y-%m-%d")


def summary_row(symbol, d, settings=Settings()):
    if d.empty:
        return {"Symbol":symbol,"Status":"No completed bars"}
    row = d.iloc[-1]
    cross, date = last_cross(d,"Golden_Cross","Death_Cross","Golden cross","Death cross")
    def value(k):
        v=row.get(k,np.nan)
        return None if pd.isna(v) else float(v)
    ma200=value("SMA_200")
    ma50=value("SMA_50")
    ema=value(f"EMA_{settings.short_ma}")
    macd,signal=value("MACD"),value("MACD_Signal")
    above=lambda ref:None if ref is None else bool(row.Close>ref)
    return {"Symbol":symbol,"Date":d.index[-1].strftime("%Y-%m-%d"),"Close":value("Close"),
            "Change %":value("Return_1D_Pct"),"RSI":value("RSI"),"ROC %":value("ROC"),
            "MACD hist":value("MACD_Histogram"),"Above SMA200":above(ma200),
            "Above SMA50":above(ma50),"Above short EMA":above(ema),
            "SMA50 above SMA200":None if ma50 is None or ma200 is None else bool(ma50>ma200),
            "MACD above signal":None if macd is None or signal is None else bool(macd>=signal),
            "MACD cross up today":bool(row.get("MACD_Cross_Up",False)),
            "MACD cross down today":bool(row.get("MACD_Cross_Down",False)),
            "Golden cross today":bool(row.Golden_Cross),"Death cross today":bool(row.Death_Cross),
            "Latest 50/200 cross":cross,"Cross date":date,
            "Breakout event":bool(row.Breakout_Event),"Breakdown event":bool(row.Breakdown_Event),
            "Support":value("Support"),"Resistance":value("Resistance"),
            "Volume ratio":value("Volume_Ratio"),"Candle setup":row.Candle_Pattern,
            "Status":"Ready" if ma200 is not None and value("RSI") is not None else "Warm-up incomplete"}
