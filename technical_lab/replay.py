import pandas as pd


def as_of(frame, cutoff):
    """Always call BEFORE analysis. No charts, exports or screeners may use future rows."""
    cutoff = pd.Timestamp(cutoff).normalize()
    return frame.loc[frame.index.normalize() <= cutoff].copy()


def step_session(dates, current, direction=1):
    dates = pd.DatetimeIndex(dates).normalize().unique().sort_values()
    if len(dates)==0:
        raise ValueError("No sessions available")
    current = pd.Timestamp(current).normalize()
    if direction > 0:
        candidates = dates[dates>current]
        return (candidates[0] if len(candidates) else dates[-1]).date()
    candidates = dates[dates<current]
    return (candidates[-1] if len(candidates) else dates[0]).date()


def completed_daily_bars(frame, now=None):
    """Conservative daily cutoff: today's India bar allowed only after 15:40 IST.

    Provider dates determine sessions; this does not manufacture bars on holidays.
    It is a completion guard, not a claim about quote freshness or final revisions.
    """
    now = pd.Timestamp.now(tz="Asia/Kolkata") if now is None else pd.Timestamp(now)
    if now.tzinfo is None:
        now=now.tz_localize("Asia/Kolkata")
    now=now.tz_convert("Asia/Kolkata")
    date=now.normalize().tz_localize(None)
    include_today = now.hour*60+now.minute >= 15*60+40
    mask=frame.index.normalize()<=date if include_today else frame.index.normalize()<date
    return frame.loc[mask].copy()
