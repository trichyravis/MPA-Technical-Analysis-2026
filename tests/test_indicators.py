import numpy as np
import pandas as pd
import pytest
from technical_lab.config import Settings
from technical_lab.indicators import seeded_average, rsi_wilder, compute_indicators
from technical_lab.signals import add_signals
from technical_lab.data import demo_history


def test_slide_example_sma_ema():
    p=pd.Series([100,102,101,105,107,106,110,108,112,115],dtype=float)
    out=seeded_average(p,5)
    assert out.iloc[:4].isna().all()
    assert out.iloc[4]==103
    assert out.iloc[5]==pytest.approx(104)
    assert out.iloc[-1]==pytest.approx(110.62962962962963)
    assert p.rolling(5).mean().iloc[-1]==pytest.approx(110.2)


def test_workbook_wilder_rsi_seed_and_update():
    p=pd.Series([100,101.2,100.8,102.1,103.4,102.9,104.3,105.6,105.1,106.8,108.2,107.7,109.4,110.9,110.3,112.1])
    r=rsi_wilder(p,14)
    assert r.iloc[:14].isna().all()
    assert r.iloc[14]==pytest.approx(83.66013071895418)
    assert r.iloc[15]==pytest.approx(85.49754573850953)


@pytest.mark.parametrize('values, expected',[(list(range(100,140)),100),(list(range(140,100,-1)),0),([100]*40,50)])
def test_rsi_edge_cases(values,expected):
    assert rsi_wilder(pd.Series(values,dtype=float),14).iloc[-1]==pytest.approx(expected)


def test_macd_seed_warmup_and_identity():
    d=compute_indicators(demo_history('^NSEI').iloc[:80])
    assert d.MACD.first_valid_index()==d.index[25]
    assert d.MACD_Signal.first_valid_index()==d.index[33]
    pd.testing.assert_series_equal(d.MACD-d.MACD_Signal,d.MACD_Histogram,check_names=False)


def test_roc_off_by_one():
    d=demo_history('TEST').iloc[:30]
    a=compute_indicators(d,Settings(roc_period=10))
    assert a.ROC.iloc[:10].isna().all()
    assert a.ROC.iloc[10]==pytest.approx((d.Close.iloc[10]/d.Close.iloc[0]-1)*100)


def test_prior_resistance_can_be_exceeded():
    d=demo_history('TEST').iloc[:30]
    d.loc[d.index[-1],['Open','Low','High','Close']]=[9999,9998,10001,10000]
    a=add_signals(compute_indicators(d))
    assert a.Resistance.iloc[-1]==pytest.approx(d.High.iloc[-21:-1].max())
    assert bool(a.Above_Prior_Resistance.iloc[-1])


def test_interior_gap_not_silently_smoothed():
    with pytest.raises(ValueError):
        seeded_average(pd.Series([1,2,np.nan,4,5]),2)
