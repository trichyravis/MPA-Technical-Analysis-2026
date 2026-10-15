"""A replacement feed can implement this contract without changing indicators.

This release provides daily demo/CSV/Yahoo adapters. No live/intraday connector
or broker authentication is included. See INTRADAY_ROADMAP.md for phase two.
"""
from typing import Protocol
import pandas as pd


class DailyProvider(Protocol):
    def fetch_many(self, symbols: tuple[str, ...], start: str, end: str
                   ) -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
        """Return normalized daily OHLCV frames and explicit per-symbol errors.

        DatetimeIndex is timezone-naive Indian session date; end is exclusive.
        Frames must be sorted, unique, finite OHLC. Index volume must be NaN.
        Authenticate server-side and respect provider display/download rights.
        """
        ...
