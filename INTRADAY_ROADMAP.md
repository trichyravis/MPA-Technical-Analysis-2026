# Phase two: extend the same lab to intraday data

The delivered release is **daily only**. It contains no live broker connection, auto-refresh loop or order placement. This keeps classroom calculations and replay reproducible.

## Recommended structure

1. A licensed feed or appropriately entitled broker account supplies historical intraday OHLC and authorised streaming data.
2. A separate always-running collector authenticates, reconnects, deduplicates and records timestamps. It owns credentials and rate limits.
3. A bar-building service constructs 5/15/60-minute bars, using the actual exchange calendar and session boundaries. Clearly distinguish forming and completed bars.
4. A shared store/cache holds the latest completed bars. Do not open one broker WebSocket per Streamlit visitor.
5. Streamlit reads prepared snapshots and reuses the indicator and interpretation modules. A daily/intraday selector names the interval and source freshness.

Streamlit Community Cloud can host a pilot but sleeps when inactive and has resource limits. An uninterrupted live collector needs an always-running service even if Streamlit remains the user interface.

## Changes needed in code

- Introduce `BarRequest(symbol, interval, start, end, timezone)` and a provider method for timestamped intraday data. Keep `DailyProvider` working.
- Add a separate intraday normalizer. **Do not** pass intraday timestamps through the current daily normalizer: it intentionally normalises timestamps to daily session dates and rejects duplicates.
- Preserve timezone-aware Asia/Kolkata timestamps for intraday bars. Use a trading-session calendar rather than fixed business days or midnight resampling.
- Replace the daily completion guard with per-bar completion based on interval and session close. A forming bar may be displayed but must not trigger “confirmed” daily-style signals.
- Make replay cutoff a timestamp, not just a date. Truncate before indicators, screener, charts and exports exactly as daily mode does.
- Fetch adequate intraday warm-up. A 200-bar average on 5-minute data means 200 five-minute bars, not 200 days.
- Keep spot-index volume unavailable unless an explicitly named, separately sourced proxy is chosen.
- Track feed timestamp, last trade timestamp, receipt timestamp, bar end and stale state separately.
- Obtain permission for browser display and downloads for the intended audience; an API subscription alone does not establish redistribution rights.

## Provider candidates to evaluate

- Kite Connect: historical candle endpoint and WebSocket market quotes.
  - https://kite.trade/docs/connect/v3/historical/
  - https://kite.trade/docs/connect/v3/websocket/
- NSE or an authorised market-data vendor: exchange data products and display terms.
  - https://www.nseindia.com/static/market-data/real-time-data-subscription
  - https://www.nseindia.com/static/market-data/nse-data-policy

Confirm current instrument coverage, authentication lifecycle, retention, public display/download permissions, limits and prices before choosing. Do not hard-code prices or promise tick-by-tick latency in the UI.

## Acceptance tests before launch

- A 5-minute bar containing a future tick never appears at an earlier replay timestamp.
- Out-of-order and duplicate ticks cannot double-count volume or create duplicate bars.
- Session boundaries, holidays, partial sessions and the final bar match the exchange schedule.
- Reconnect/backfill does not leave invisible gaps or revise a previously shown bar without a visible update policy.
- Expired authentication and stale feeds show a clear stale/unavailable state rather than a fabricated price.
- User sessions share cached bars without sharing private tokens.
- Chart/screener/export agree for identical symbol, timeframe and cutoff.
- The latest incomplete bar is labelled forming and excluded from confirmed events.

## Website integration

Use the same website link after this upgrade. No new Academy page structure is required. Keep the educational daily/replay views alongside a clearly named intraday view.
