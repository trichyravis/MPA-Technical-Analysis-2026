# Calculation and data notes

## Timing and input

Daily observations are sorted and unique. OHLC prices are positive and finite. Missing or malformed OHLC bars are rejected. Missing Volume is allowed, without forward fill. Holiday dates are not invented by the real-data loaders. The deterministic demo deliberately uses business days rather than an exchange calendar.

In CSV and Yahoo modes a bar dated today in Asia/Kolkata is excluded before 15:40 IST. This is a conservative current-session completion guard, not proof of final provider publication. The last available session is displayed, including when it differs from the requested replay cutoff. Before the next trading session begins, daily signals necessarily refer to the preceding available daily bar.

## Indicator definitions

- SMA(n): arithmetic mean of n closing observations, first result at observation n.
- EMA(n): seed at n with its full-window SMA, then alpha=2/(n+1).
- ROC(n): `(close / close.shift(n) - 1) * 100`, first result at n+1.
- Wilder RSI(n): first n changes include zeros on non-gain/non-loss days. Seed average gain/loss by dividing by n, then alpha=1/n. First result at n+1. Stable ratio is `100*AG/(AG+AL)`. Both zero =>50 by explicitly chosen neutral convention.
- MACD: seeded fast EMA minus seeded slow EMA. Signal is a seeded EMA of available MACD values. With 12/26/9, MACD begins at observation 26 and signal/histogram at 34.
- Prior support/resistance: shift High/Low (or Close) by one observation, then take rolling min/max of n values. Not every breach is a newly entered breakout state; event and state are separately named.
- Golden/death cross: 50/200 SMA crossing based on two consecutive valid observations. Custom intermediate/long averages have separate `MA_Cross_Up/Down` flags and are not mislabeled golden/death crosses.
- RSI, ROC, EMA and MACD periods are bar counts, not calendar day counts.

No indicators are forward filled to hide their warm-up periods. Calculations use full precision and do not annualise ROC.

## Price structure and pattern context

Candle patterns use actual OHLC, not transformed Heikin-Ashi prices. The preceding context compares the previous close with the close three observations before that. Shapes are descriptive setup rules, not a completed confirmation, trade or causal claim about who traded.

A confirmed close-based swing uses an odd window with equal left/right bars. A unique maximum/minimum at the centre becomes available only when the right-hand observations exist. Both the pivot date and knowledge date are retained. No strategy-return backtest or historical index-membership reconstruction is included.

## Volume and indices

Spot Nifty 50 and Bank Nifty are calculated indices. Their `Volume` and volume ratios are always missing. Equity volume is compared with the mean of the previous 20 observations. No index future, ETF or sum-of-constituents proxy is inserted. Such proxies require a separate explicit instrument and definition.

## Screener and exports

The screener is a descriptive snapshot, not a signal ranking. Every row reports its last data date and errors remain visible. It uses the dashboard's parameters and global replay cutoff. A different last date is flagged. A cached result is invalidated by a source, universe, cutoff or parameter change.

The Excel workbook contains computed **values**, with formulas described in Read Me/Parameters. It is not a recalculating Excel model. Prices are cut off before calculations and exports. Text fields are guarded against Excel formula injection. No future price rows are included in replay exports.

## Data source and rights

Synthetic mode does not represent market performance. The sample CSV is synthetic and is included for testing. The bundled reference symbol list is editable and not asserted to be certified current or historical membership. The official list is requested only through the explicit refresh button.

Yahoo/yfinance is an optional research adapter and does not provide a public redistribution licence. `auto_adjust=False` prevents total-return automatic OHLC adjustment, but provider split-adjusted/revised history can still change past values. This is not an exchange-verified point-in-time source. Cache, timestamps, rate limits, missing symbols and corporate actions must be considered in any real deployment.

Broker/feed credentials must stay on the server, never in Git, browser JavaScript, downloadable spreadsheets or logs. No credentials are supplied by this project.

## Visual reference

Design reference: `trichyravis/rbi-spread-app`, `app.py` blob SHA `b1cd46d5064c5487e2bd8d101b2514b50432b442` and `.streamlit/config.toml` blob SHA `e6ec5512bdc2bde773a8343628087427ab704b47`, inspected 15 October 2026. The lab adapts its navy gradient, gold accents, cards, tabs, chart treatment and branded header/footer. It does not incorporate unrelated bond-market logic or data.
