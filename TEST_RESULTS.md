# Validation record

Validated on 15 October 2026 using Python 3.13 with streamlit 1.66, pandas 3.0, numpy 2.5, plotly 7.1 and yfinance 1.7 (ranges in requirements.txt).

Command: `python -m pytest -q`

Result: **23 passed**.

Earlier release: the original pins (streamlit 1.37.1, pandas 2.2.2, numpy 1.26.4) also passed on Python 3.12, but they have no wheels for Python 3.13/3.14, so a Streamlit Community Cloud deployment on its default Python failed while building pandas/pillow from source. The requirements now use version ranges that install on Python 3.11–3.14.

Coverage includes:

- Slide/workbook SMA, EMA and Wilder RSI examples.
- Rising, falling and all-flat RSI histories.
- Correct MACD/signal/histogram warm-up and arithmetic identity.
- ROC's n+1 observation requirement.
- Prior-window resistance that can actually be exceeded.
- Golden/death crossing events without repeated signals in an existing regime.
- No false crossings caused by warm-up gaps.
- Confirmed pivots exposed only after right-hand observations.
- Replay results unchanged after modifying future prices.
- Price rows in replay Excel files end at the cutoff.
- Indian-session completed-daily-bar cutoff.
- CSV validation and missing index volume.
- Streamlit demo page, replay controls, next-session step and 52-instrument screener.

All tests are offline. Yahoo fetching and the official NSE constituent-list refresh are implemented but not live-verified in CI. No real-time feed, broker login or intraday service is included in release one.
