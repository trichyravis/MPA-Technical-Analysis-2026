from io import BytesIO
import pandas as pd
import pytest
from technical_lab.config import Settings
from technical_lab.data import demo_history
from technical_lab.indicators import compute_indicators
from technical_lab.signals import add_signals, confirmed_swings, crossover, summary_row
from technical_lab.replay import as_of, completed_daily_bars, step_session
from technical_lab.exports import excel_bytes


def pipeline(d):
    return add_signals(compute_indicators(d))


def test_future_price_mutation_cannot_change_replay():
    full=demo_history('RELIANCE.NS')
    cutoff=full.index[350]
    a=pipeline(as_of(full,cutoff))
    changed=full.copy()
    changed.loc[changed.index>cutoff,['Open','High','Low','Close']]*=100
    b=pipeline(as_of(changed,cutoff))
    pd.testing.assert_frame_equal(a,b)
    # Even a full-run causal calculation agrees at the same prefix.
    pd.testing.assert_frame_equal(a,pipeline(changed).loc[:cutoff])
    assert summary_row('RELIANCE.NS',a)==summary_row('RELIANCE.NS',b)


def test_pivot_available_only_after_right_hand_confirmation():
    p=pd.Series([1,2,5,2,1,2,3],index=pd.date_range('2026-01-01',periods=7),dtype=float)
    assert confirmed_swings(p.iloc[:4],2).empty
    pivots=confirmed_swings(p.iloc[:5],2)
    assert pivots.iloc[0].PivotDate==p.index[2]
    assert pivots.iloc[0].KnownOn==p.index[4]


def test_cross_event_does_not_repeat_in_regime():
    up,down=crossover(pd.Series([1.,2.,4.,5.]),pd.Series([3.,3.,3.,3.]))
    assert up.tolist()==[False,False,True,False]
    assert not down.any()


def test_unwarmed_signal_is_not_false_cross():
    up,down=crossover(pd.Series([float('nan'),4.,5.]),pd.Series([float('nan'),3.,3.]))
    assert not up.any() and not down.any()


def test_completed_daily_cutoff_uses_india_clock():
    d=demo_history('^NSEI').tail(5)
    now=pd.Timestamp(str(d.index[-1].date())+' 15:30',tz='Asia/Kolkata')
    assert completed_daily_bars(d,now).index[-1]<d.index[-1]
    assert completed_daily_bars(d,now+pd.Timedelta(minutes=10)).index[-1]==d.index[-1]


def test_step_session_skips_missing_dates():
    dates=pd.to_datetime(['2026-01-02','2026-01-05','2026-01-07'])
    assert str(step_session(dates,'2026-01-02'))=='2026-01-05'
    assert str(step_session(dates,'2026-01-07',-1))=='2026-01-05'


def test_replay_excel_contains_no_future_price_rows():
    full=demo_history('^NSEI')
    cutoff=full.index[300]
    d=pipeline(as_of(full,cutoff))
    workbook=excel_bytes(d,Settings(),{'Source':'Demo','Cutoff':str(cutoff.date())},swings=confirmed_swings(d.Close))
    parsed=pd.read_excel(BytesIO(workbook),sheet_name=None)
    for name in ['OHLCV','Indicators']:
        assert pd.to_datetime(parsed[name].Date).max()<=cutoff
    assert parsed['OHLCV'].Volume.isna().all()
    assert len(parsed['OHLCV'])==301
