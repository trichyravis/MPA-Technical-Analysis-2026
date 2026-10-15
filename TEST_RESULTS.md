# Validation record

Validated on 15 October 2026 using Python 3.12 and the dependency versions in requirements.txt.

Command: `python -m pytest -q`

Result: **23 passed**.

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

All tests are offline. Yahoo fetching and official NSE constituent-list refresh are implemented but were not live-verified in this environment. No real-time feed, broker login or intraday service is included in release one. The visual styling was derived from the source of the requested rbi-spread-app reference; full browser/mobile visual QA remains a deployment check.
