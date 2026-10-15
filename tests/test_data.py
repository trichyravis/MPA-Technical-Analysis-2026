import numpy as np
import pandas as pd
import pytest
from technical_lab.data import demo_history, normalize_frame, read_csv_bundle
from technical_lab.universe import reference_universe


def test_demo_is_repeatable_and_index_volume_unavailable():
    pd.testing.assert_frame_equal(demo_history('^NSEI'),demo_history('^NSEI'))
    assert demo_history('^NSEI').Volume.isna().all()
    assert demo_history('RELIANCE.NS').Volume.notna().all()
    u=reference_universe()
    assert len(u)==52 and u.Symbol.nunique()==52


def test_uploaded_daily_data_is_sorted_and_not_silently_duplicated():
    text=b'Symbol,Date,Open,High,Low,Close,Volume\nABC,2026-01-02,100,103,99,102,10\nABC,2026-01-01,99,102,98,100,20\n'
    d=read_csv_bundle(text)['ABC']
    assert d.index.is_monotonic_increasing
    with pytest.raises(ValueError,match='Duplicate'):
        read_csv_bundle(text+b'ABC,2026-01-01,99,102,98,100,20\n')


def test_invalid_ohlc_rejected():
    d=demo_history('A').iloc[:4]
    d.loc[d.index[0],'High']=d.Low.iloc[0]-1
    with pytest.raises(ValueError,match='inconsistent'):
        normalize_frame(d)


def test_csv_missing_required_headers():
    with pytest.raises(ValueError,match='CSV needs'):
        read_csv_bundle(b'Date,Close\n2026-01-01,100\n')


def test_csv_indices_do_not_acquire_invented_volume():
    text=b'Symbol,Date,Open,High,Low,Close,Volume\n^NSEI,2026-01-02,100,103,99,102,999\n'
    assert read_csv_bundle(text)['^NSEI'].Volume.isna().all()


def test_provider_rounding_in_high_low_is_tolerated():
    text=b'Symbol,Date,Open,High,Low,Close,Volume\nABC,2026-01-02,100,102.99999,99,103,10\n'
    d=read_csv_bundle(text)['ABC']
    assert d.High.iloc[0]==103
