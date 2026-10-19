# The Mountain Path Academy · Technical Analysis Lab

A GitHub-ready Streamlit teaching application for Nifty 50 stocks, the Nifty 50 index and Bank Nifty index. It includes daily candlesticks, SMA/EMA, golden/death crosses, prior-window support/resistance, ROC, Wilder RSI, MACD, a screener, Excel downloads and historical replay.

**Author:** Prof. V. Ravichandran · [The Mountain Path Academy](https://themountainpathacademy.com)

**Design:** adapted to the dark navy, gold, tabbed style of your [RBI Spread app](https://github.com/trichyravis/rbi-spread-app). This is a separate application and repository.

## 1. Create your GitHub repository

Suggested name: **MPA-Technical-Analysis-2026**.

1. Extract the supplied ZIP.
2. Sign in to [GitHub](https://github.com/trichyravis) and create a new empty repository named `MPA-Technical-Analysis-2026`.
3. Upload **the contents inside** `technical-analysis-lab`, so `app.py`, `requirements.txt`, `technical_lab`, `data`, and `.streamlit` are at the repository root. Do not nest the whole folder one level deeper.
4. Include the hidden `.streamlit` directory: it supplies the matching theme. Also include `.github/workflows/tests.yml` for automated tests. If your browser hides dotfolders, use the Git commands below.
5. Do not upload a `.venv`, tokens, `.env`, or a real `secrets.toml`.

Using Terminal instead (after creating the empty repo):

```bash
cd "/path/to/technical-analysis-lab"
git init
git add .
git commit -m "Add Mountain Path technical analysis learning lab"
git branch -M main
git remote add origin https://github.com/trichyravis/MPA-Technical-Analysis-2026.git
git push -u origin main
```

Use your normal GitHub sign-in when asked. No credentials belong in these source files.

## 2. Deploy on Streamlit Community Cloud

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and connect your GitHub account.
2. Select **Create app**.
3. Repository: `trichyravis/MPA-Technical-Analysis-2026`.
4. Branch: `main`.
5. Main file path: **`app.py`**.
6. In Advanced settings, choose Python 3.12, 3.13 or 3.14 (the default 3.14 works).
7. Deploy. Pick an available app name, for example `MPA-Technical-Analysis-2026`.
8. Open the app. The default synthetic mode needs no data account or API key.

The final app address is assigned during deployment. Do not assume the suggested name is available until Streamlit confirms it.

## 3. Run locally on your Mac

Use Python 3.11 to 3.14:

```bash
cd "/path/to/technical-analysis-lab"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed in Terminal. Stop with **Control+C**. To reopen later, activate `.venv` and run `streamlit run app.py` again.

The dependency versions in `requirements.txt` are pinned to the versions used for validation. Upgrade them deliberately and rerun tests.

## 4. Choose the data source

### Synthetic demo: immediate, offline and reproducible

- Supports both indices and all symbols in the bundled 50-stock reference watchlist.
- Prices and stock volumes are invented. Dates are business days, not an NSE holiday calendar.
- The series ends on 1 October 2026 to keep demonstrations repeatable.
- There is no silent fallback from a failed market feed to synthetic prices.
- Index volume is blank because spot indices have no traded share volume.

### Upload CSV: use data you have permission to display

Try `data/sample_ohlcv.csv`. It contains 300 synthetic observations for each of Nifty 50, Bank Nifty and Reliance.

Required headers:

```csv
Symbol,Date,Open,High,Low,Close,Volume
RELIANCE.NS,2026-01-02,1500,1530,1490,1520,5000000
^NSEI,2026-01-02,25000,25200,24900,25100,
^NSEBANK,2026-01-02,52000,52500,51800,52300,
```

- Use ISO dates `YYYY-MM-DD`; one row per symbol per daily session.
- OHLC must be finite and positive. High/Low must contain Open/Close.
- Dates may be unsorted; the loader sorts them. Duplicate dates are rejected rather than silently overwritten.
- `Volume` is optional. Unknown volume stays missing; `^NSEI` and `^NSEBANK` always omit volume.
- Use the same adjustment convention throughout a file. Correct or explicitly handle splits and other corporate actions before importing.
- Upload only columns you intend the app to analyse. Streamlit's upload limit is 20 MB.
- Today's bar is excluded before 15:40 IST in CSV and Yahoo modes. No current, still-forming candle generates daily signals.

### Yahoo Finance: optional personal research adapter

Yahoo mode is **disabled by default**. The project can run publicly with demo data or permitted CSV data. The open-source yfinance package does not itself grant rights to redistribute Yahoo market data.

For a permitted personal/local research use:

```bash
ENABLE_YAHOO=true streamlit run app.py
```

Or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and set:

```toml
ENABLE_YAHOO = true
```

For hosted settings use Streamlit's Secrets panel. Do not commit a real secrets file.

- The adapter requests five years of **daily** history with `auto_adjust=False`.
- This is not an exchange-certified real-time feed. Quotes can be delayed, incomplete, revised, rate-limited or unavailable.
- Provider split adjustments can still revise historical prices. This is not point-in-time corporate-action data.
- The current incomplete daily bar is removed before 15:40 IST.
- Successful requests are cached for 15 minutes; the screener requests batches of ten selected instruments.
- Failures stay visible as error rows. Data is never replaced by an invented “live” price.

For a public market-data service, use a provider agreement that permits the intended display and Excel-download audience. Replace `yahoo_fetch_many` through the contract in `technical_lab/provider_contract.py`. The calculations and replay logic can stay the same.

Sources: [yfinance documentation and terms notice](https://ranaroussi.github.io/yfinance/), [NSE data policy](https://www.nseindia.com/static/market-data/nse-data-policy).

## 5. Universe: current list versus historical membership

The app includes `^NSEI` and `^NSEBANK`, plus 50 stocks in an **editable reference watchlist**. The bundled list is not certified as the current list and is not a historical constituent database.

Use **Refresh current Nifty 50 constituents** to fetch the official CSV from NSE Indices. Exactly 50 unique equity symbols are expected. On failure the app reports it and retains the explicitly labelled reference list. Alternatively update `data/reference_universe.csv` yourself.

[Official Nifty 50 constituents CSV](https://www.niftyindices.com/IndexConstituent/ind_nifty50list.csv)

Yahoo equity symbols use `.NS`. Corporate actions and symbol changes may require updates to mappings or a different provider.

Historical replay uses the selected current/reference universe. It is a learning replay, **not** a survivorship-free historical-index strategy backtest.

## 6. What the app does

| Area | Behaviour |
|---|---|
| Charts | OHLC candles, selectable SMA/EMA, support/resistance, aligned ROC, RSI and MACD panels; traded volume only when available |
| Averages | Defaults 20/50/200; custom display periods; first full-window SMA seed for EMA |
| Crossovers | Golden/death cross events always use SMA50/SMA200, regardless of custom display periods |
| Levels | Prior-window rolling High/Low or Close bounds; tested candle excluded |
| Momentum | Configurable ROC, Wilder RSI and MACD; seed rules disclosed |
| Candle figures | Transparent doji/hammer/shooting-star/engulfing setup definitions with preceding-price context |
| Price structure | Confirmed close-based swing highs/lows, with both pivot date and knowledge date |
| Screener | All selected symbols, parameters and replay cutoff shared with dashboard; partial failures visible |
| Excel | Read Me, Parameters, Metadata, OHLCV, Indicators, and optional Screener, Confirmed Swings and Replay Journal |
| Replay | Cut the input first, then calculate everything; advance by an actual available session |

There is no hidden composite buy/sell score and no order execution. Indicator agreement is not independent evidence or an established win probability.

### Support and resistance

A prior-window maximum/minimum is a reproducible reference method, not the universal definition of a supply/demand zone. Choose `High/Low` or `Close` in the sidebar. The tested candle is excluded from the level window.

### Candle rules

Doji: body ≤10% of nonzero range. Hammer: after a prior decline, lower wick ≥2× body, upper wick ≤body and body >10% of range. Shooting star mirrors the geometry after an advance. Engulfing uses opposite candle bodies and a corresponding prior move. These are setups; they do not claim that a later confirmation already occurred.

### Dow Theory boundary

“Higher highs and higher lows” here describes **one instrument's confirmed closing-price swings**. It does not claim classical Dow Theory confirmation between industrial and transportation market averages.

## For learners: guided mode

New learners should open the **Start here** tab first. It follows the six lessons of the Academy's *Let Us Learn Technical Analysis* series. Each step has **The idea**, **Look at** (where to look on the chart) and **Try this** (a small task), plus a link to the full lesson.

- **Chart layers** (sidebar) shows one idea at a time: *Candles only*, *Price & averages*, *Support & resistance* or *Momentum*. *Everything* is the original full chart.
- **Read this chart in plain English** (under the chart) explains the latest trend, swing structure, RSI, MACD, ROC, levels and candle. Each card also says what would change that reading, and a tally shows whether the indicators agree or disagree.
- **Check yourself** asks questions whose answers are worked out from the chart on screen. A fresh set appears when you change the instrument or step the replay date.
- **Learn the calculations** now shows *today's numbers, step by step* (SMA, EMA, ROC, RSI, MACD, support/resistance) using the same values the chart plots.
- **Live summary** (Screener tab): after each scan, one row per observation — SMA 50/200, short EMA, golden/death-cross state and events, RSI ≥ 70 / ≤ 30 / above 50, MACD above signal and crosses, positive/negative ROC, breakouts, breakdowns and candle setups — with how many instruments match, the share and which ones, plus a market-breadth line. It uses exactly the same rules as **Filter observations**, so counts always agree. It is also exported as the *Screener Summary* sheet in Excel.
- Hover over the **?** beside any headline number or sidebar control for a one-line explanation. A glossary sits at the bottom of **Start here**.

All learner text reads only the revealed rows, so explanations and quiz answers respect Historical replay. They describe indicator readings; they are not recommendations.

## 7. Historical replay teaching workflow

1. Select an instrument and enable **Historical replay**.
2. Set a cutoff with enough history for the indicators you want (200+ observations for SMA200).
3. Inspect the chart and write the trend, levels, scenario and invalidation in Replay journal.
4. Record the observation at that cutoff.
5. Click **Next session** to reveal the next available session.
6. Re-run the screener at the new cutoff if desired.
7. Download the visible journal and Excel snapshot before closing the session.

**Important implementation details:**

- `as_of()` truncates before all indicator/pattern calculations.
- Plot axes, the data table, screener, confirmed swings and exported prices see the truncated data only.
- A pivot needing three bars to its right becomes knowable three bars later, with `KnownOn` recorded. It is not backdated into a trading rule.
- Rewinding hides journal entries written at later dates.
- A journal belongs to the browser session and source/instrument. It is not permanently stored or emailed.
- Full histories exist on the server; replay is not a secure examination system.
- Current/reference constituents and revised historical data remain limitations. No performance claims or full trading-strategy backtest are provided.

## 8. Add a separate link to your Academy website

Once Streamlit confirms your deployed app address, replace `YOUR-DEPLOYED-APP-URL` below:

```html
<a class="open" href="YOUR-DEPLOYED-APP-URL"
   target="_blank" rel="noopener noreferrer">
  Open Technical Analysis Lab ↗
</a>
```

Place it in the Technical Analysis section of `fundamentals.html` and optionally in each article. A direct new-tab link is recommended over an iframe for easier chart interaction on phones.

This Streamlit repository is deployed on Streamlit (or a Python host), **not** Firebase Hosting. Firebase continues to host the existing Academy learning pages. Adding the final link to those pages is a separate website deployment.

## 9. Validate before deployment

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover formula examples, RSI edge cases, indicator warm-up, valid OHLC, missing index volume, crossover events, future-data mutation under replay, delayed swing availability, cutoff-safe Excel, and the Streamlit demo/replay/screener interface. No network or account is needed for tests.

## 10. Project map

```text
app.py                         Streamlit interface
technical_lab/theme.py         Reference-app navy/gold design
technical_lab/data.py          Demo, CSV and Yahoo daily adapters
technical_lab/universe.py      Indices and constituent list loading
technical_lab/indicators.py    SMA/EMA, ROC, Wilder RSI, MACD, prior levels
technical_lab/signals.py       Crossovers, candle setups, confirmed swings
technical_lab/replay.py        Data cutoff and completed-bar guard
technical_lab/charts.py        Plotly candlestick and indicator chart, with focus layers
technical_lab/learning.py      Learning path, plain-English readings, worked numbers, quiz
technical_lab/observations.py  One rule set for screener filters and the live summary
technical_lab/exports.py       Styled Excel snapshot
technical_lab/config.py        Validated indicator settings
technical_lab/provider_contract.py   Replacement daily-feed interface
INTRADAY_ROADMAP.md             Phase-two architecture and acceptance criteria
DATA_NOTES.md                  Exact methodology and limitations
.streamlit/config.toml         Matching dark theme
.github/workflows/tests.yml    GitHub test workflow
```

## Troubleshooting

- **ModuleNotFoundError:** activate the same virtual environment used to install `requirements.txt`.
- **Wrong Streamlit entry point:** ensure root `app.py`, not a nested folder, is selected.
- **Yahoo disabled:** use synthetic/CSV mode, or explicitly enable permitted research use.
- **Yahoo rate limit or empty symbol:** wait and retry, verify the current ticker, or upload permitted CSV data. No API route is guaranteed.
- **Blank early indicators:** allow sufficient warm-up. For standard MACD the first histogram is observation 34; SMA200 needs 200 closes.
- **Screener shows old results:** changing source, parameters or replay cutoff invalidates its snapshot; click Run screener again.
- **Unusual spikes:** inspect corporate actions, adjustment conventions and CSV quality before interpreting any signal.
- **Charts on phones:** use the chart toolbar/fullscreen and hide the sidebar for more space.

## Reference documentation

- [Streamlit deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
- [Streamlit secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Fidelity: ROC](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/roc)
- [Fidelity: RSI](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI)
- [Fidelity: MACD](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/macd)
