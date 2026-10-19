"""Run: streamlit run app.py. No API keys are needed for demo or CSV mode."""
import hashlib
import inspect
import os
from dataclasses import asdict
from datetime import date, timedelta
import pandas as pd
import streamlit as st
from technical_lab.config import Settings
from technical_lab.data import demo_history, read_csv_bundle, yahoo_fetch_many
from technical_lab.universe import reference_universe, fetch_current_constituents
from technical_lab.replay import as_of, completed_daily_bars, step_session
from technical_lab.indicators import compute_indicators
from technical_lab.signals import add_signals, confirmed_swings, swing_structure, summary_row
from technical_lab.charts import technical_chart, LAYERS
from technical_lab.learning import (LEARNING_PATH, GLOSSARY, METRIC_HELP, read_the_chart,
                                    evidence_tally, worked_numbers, quiz)
from technical_lab.theme import reading_cards, learning_step_card
from technical_lab.exports import excel_bytes
from technical_lab.observations import NAMES as OBSERVATION_NAMES, observation_mask, observation_summary, breadth_headline

st.set_page_config(page_title="Technical Analysis Lab | Mountain Path Academy",page_icon="📈",layout="wide")
from technical_lab.theme import apply_theme, header, footer

apply_theme()
header()


def yahoo_enabled():
    env=os.getenv("ENABLE_YAHOO","").lower() in {"true","1","yes"}
    try:
        return env or bool(st.secrets.get("ENABLE_YAHOO",False))
    except Exception:
        return env


@st.cache_data(show_spinner=False)
def get_demo(symbol):
    return demo_history(symbol)


@st.cache_data(ttl=900,show_spinner=False)
def get_yahoo(symbols,start,end):
    return yahoo_fetch_many(symbols,start,end)


@st.cache_data(ttl=86400,show_spinner=False)
def official_universe():
    return fetch_current_constituents()


@st.cache_data(show_spinner=False)
def parse_upload(payload):
    return read_csv_bundle(payload)


def analyze(frame, cutoff, s):
    # Single entry point shared by dashboard and screener; cutoff comes FIRST.
    truncated=as_of(frame,cutoff)
    if truncated.empty:
        return truncated
    return add_signals(compute_indicators(truncated,s),s)


with st.sidebar:
    st.header("Explore the market")
    source=st.selectbox("Data source",["Synthetic demo","Upload CSV","Yahoo Finance (personal research)"])
    universe=st.session_state.get("universe",reference_universe())
    if st.button("Refresh current Nifty 50 constituents"):
        try:
            universe=official_universe()
            st.session_state.universe=universe
            st.session_state.universe_status=f"Official list fetched {pd.Timestamp.now(tz='Asia/Kolkata'):%d %b %Y}"
        except Exception as exc:
            st.warning(f"Could not refresh the official list. {exc}")
    st.caption(st.session_state.get("universe_status","Bundled reference watchlist: verify current membership. Refresh from NSE Indices or edit data/reference_universe.csv."))
    upload=None
    uploaded_frames={}
    if source=="Upload CSV":
        upload=st.file_uploader("OHLCV CSV",type=["csv"])
        st.caption("Columns: Symbol, Date, Open, High, Low, Close; Volume optional. Use ^NSEI and ^NSEBANK for spot indices.")
        if upload is None:
            st.info("Upload the included data/sample_ohlcv.csv to try this mode.")
            st.stop()
        try:
            uploaded_frames=parse_upload(upload.getvalue())
        except Exception as exc:
            st.error(f"CSV could not be read: {exc}")
            st.stop()
        symbols=list(uploaded_frames)
        names={k:k for k in symbols}
    else:
        symbols=universe.Symbol.to_list()
        names={r.Symbol:f"{r.Name} ({r.Symbol})" for r in universe.itertuples()}
    symbol=st.selectbox("Instrument",symbols,format_func=lambda k:names[k])
    layers=st.selectbox("Chart layers",LAYERS,help="Learning one idea at a time? Show only the candles, the moving averages, the support/resistance levels or the momentum panels. 'Everything' shows the full chart.")
    average=st.selectbox("Show averages",["Both","SMA","EMA"],help="SMA = simple moving average (solid lines). EMA = exponential moving average (dotted lines), which reacts faster to recent prices.")
    chart_bars=st.slider("Visible chart bars",60,500,180,20,help="About 250 bars is one trading year; 60 bars is roughly three months.")
    with st.expander("Indicator parameters"):
        st.caption("Defaults are the textbook settings (20/50/200 averages, RSI 14, MACD 12/26/9). Change one at a time and watch what moves.")
        short=int(st.number_input("Short MA",min_value=2,max_value=100,value=20))
        fast=int(st.number_input("Intermediate MA",min_value=3,max_value=250,value=50))
        slow=int(st.number_input("Long MA",min_value=4,max_value=500,value=200))
        sr=int(st.number_input("Support/resistance lookback",min_value=2,max_value=250,value=20))
        basis=st.selectbox("Support/resistance prices",["High/Low","Close"])
        roc=int(st.number_input("ROC periods",min_value=1,max_value=100,value=12))
        rsi=int(st.number_input("RSI periods",min_value=2,max_value=100,value=14))
        mf=int(st.number_input("MACD fast",min_value=2,max_value=100,value=12))
        ms=int(st.number_input("MACD slow",min_value=3,max_value=200,value=26))
        signal=int(st.number_input("MACD signal",min_value=2,max_value=100,value=9))
        swing=int(st.number_input("Swing confirmation bars",min_value=1,max_value=10,value=3))
    try:
        settings=Settings(short,fast,slow,sr,basis,roc,rsi,mf,ms,signal,swing).validate()
    except ValueError as exc:
        st.error(str(exc));st.stop()
    if st.button("Clear market-data cache"):
        get_yahoo.clear();official_universe.clear()
        st.success("The market-data cache is cleared; rerun or change the instrument to reload.")

if source.startswith("Yahoo") and not yahoo_enabled():
    st.info("Yahoo research mode is disabled by default. For permitted personal use, enable ENABLE_YAHOO in environment variables or Streamlit secrets. Public deployment can use the demo or data you have permission to display via CSV / a licensed adapter.")
    st.stop()

if source=="Synthetic demo":
    full=get_demo(symbol)
    st.info("SYNTHETIC DEMO · Invented prices and volumes on business-day dates through 1 October 2026. These are not actual stock or index observations.")
    source_id="demo-v1"
    source_note="Synthetic deterministic demonstration; dates are business days, not an exchange calendar."
elif source=="Upload CSV":
    full=completed_daily_bars(uploaded_frames[symbol])
    source_id=hashlib.sha256(upload.getvalue()).hexdigest()
    source_note="User-provided CSV; displayed data rights, adjustments and timestamp quality depend on its source."
else:
    start=date.today()-timedelta(days=365*5+20)
    with st.spinner("Loading daily history…"):
        try:
            frames,errors=get_yahoo((symbol,),start,date.today()+timedelta(days=1))
            if symbol not in frames:
                st.error(errors.get(symbol,"No history returned."));st.stop()
            full=completed_daily_bars(frames[symbol])
        except Exception as exc:
            st.error(f"Market-data request failed: {exc}. Try again later or use CSV/demo mode.");st.stop()
    source_id="yahoo-unadjusted"
    source_note="Yahoo via yfinance; daily, potentially delayed/revised, auto_adjust=False. Split adjustments can still affect historical values."
    st.caption("Research data, not a real-time feed. Today's incomplete daily candle is excluded before 15:40 IST. Provider access does not establish public redistribution rights.")

if full.empty:
    st.warning("No completed daily bars are available.");st.stop()
if len(full)<2:
    st.warning("At least two completed daily bars are needed.");st.stop()

# Replay is a GLOBAL cutoff for every chart, screener row and export in this run.
with st.sidebar:
    replay=st.checkbox("Historical replay",value=False,help="Hide every price after a chosen date, read the chart, write down your view, then step forward one session to see what happened.")
    if replay:
        key="replay_date_"+hashlib.sha1((source_id+symbol).encode()).hexdigest()[:12]
        minimum,maximum=full.index[0].date(),full.index[-1].date()
        if key not in st.session_state:
            st.session_state[key]=full.index[min(300,len(full)-2)].date()
        for action,direction in [("Previous session",-1),("Next session",1)]:
            if st.button(action):
                st.session_state[key]=step_session(full.index,st.session_state[key],direction)
        cutoff=st.date_input("Reveal prices through",min_value=minimum,max_value=maximum,key=key)
        st.caption("All views and downloads stop here. Current/reference constituents are used, not historical index membership.")
    else:
        cutoff=full.index[-1].date()

analyzed=analyze(full,cutoff,settings)
if analyzed.empty:
    st.info("No bars at the selected cutoff.");st.stop()
latest=analyzed.iloc[-1]
actual_date=analyzed.index[-1].date()
if actual_date!=cutoff:
    st.warning(f"Requested cutoff: {cutoff}. Last available session: {actual_date}. No missing sessions have been fabricated.")
if replay:
    st.warning(f"REPLAY · prices revealed only through {actual_date}. Step forward to reveal the next session.")
if len(analyzed)<max(settings.slow_ma,200,settings.macd_slow+settings.macd_signal-1):
    st.caption("Some indicators are warming up. Missing indicator values are shown as —; they are not zero or bearish signals.")

swings=confirmed_swings(analyzed.Close,settings.swing_window)
summary=summary_row(symbol,analyzed,settings)
context=(source,source_id,str(cutoff),str(asdict(settings)),tuple(symbols))
record=st.session_state.get("screen_record",{})
screen=record.get("table",pd.DataFrame()) if record.get("context")==context else pd.DataFrame()


def fmt(value,decimals=2):
    return "—" if value is None or pd.isna(value) else f"{value:,.{decimals}f}"


columns=st.columns(5)
for col,label,value,tip in zip(columns,["Close","Daily change %",f"RSI {settings.rsi_period}",f"ROC {settings.roc_period} %","MACD histogram"],
                            [latest.Close,latest.Return_1D_Pct,latest.RSI,latest.ROC,latest.MACD_Histogram],
                            [METRIC_HELP["Close"],METRIC_HELP["Daily change %"],METRIC_HELP["RSI"],METRIC_HELP["ROC"],METRIC_HELP["MACD histogram"]]):
    col.metric(label,fmt(value),help=tip)
st.caption(f"{symbol} · Latest completed bar: {actual_date} · Daily timeframe · {len(analyzed)} revealed observations")

# A keyed tab bar keeps the selected tab across reruns, so clicking "Run screener"
# no longer throws the user back to the first tab. Older Streamlit lacks the key.
TAB_NAMES=["Start here","Chart & interpretation","Check yourself","Screener","Replay journal","Learn the calculations","Data & downloads"]
_tab_kwargs={"key":"main_tabs","on_change":"rerun"} if "key" in inspect.signature(st.tabs).parameters else {}
tab_start,tab_chart,tab_quiz,tab_screen,tab_replay,tab_learn,tab_data=st.tabs(TAB_NAMES,**_tab_kwargs)
cards=read_the_chart(analyzed,settings,swings)

with tab_start:
    st.subheader("New to technical analysis? Start here")
    st.markdown(
        "This lab lets you **see** each idea from the Mountain Path *Let Us Learn Technical Analysis* series on real-looking charts. "
        "Work through the six steps in order; each one tells you what to look at and gives you a small task.\n\n"
        "**How to use the lab in four moves:** 1) pick an instrument in the sidebar · "
        "2) use **Chart layers** to show one idea at a time · "
        "3) read **Read this chart in plain English** under the chart · "
        "4) test yourself in **Check yourself**, or practise with **Historical replay**.")
    for item in LEARNING_PATH:
        learning_step_card(item)
    with st.expander("Glossary · every term in plain words"):
        st.dataframe(pd.DataFrame(GLOSSARY.items(),columns=["Term","Meaning"]),width="stretch",hide_index=True)
    st.caption("Educational descriptions of indicator readings, not buy or sell recommendations.")

with tab_chart:
    st.plotly_chart(technical_chart(analyzed,symbol,settings,average,chart_bars,layers),width="stretch")
    st.subheader("Read this chart in plain English")
    counts,verdict=evidence_tally(cards)
    reading_cards(cards,counts,verdict)
    st.caption("Each card describes what one indicator shows on the latest revealed day and what would change it. "
               "Indicators often disagree; weighing them is the skill. These are descriptions, not recommendations.")
    st.markdown("#### Technical detail")
    a,b=st.columns(2)
    with a:
        st.subheader("Price structure")
        st.write(f"**Confirmed close-based swings:** {swing_structure(swings)}")
        st.write(f"**Prior-window support:** {fmt(latest.Support)}  |  **Resistance:** {fmt(latest.Resistance)}")
        st.caption(f"{settings.sr_period} previous bars using {settings.sr_basis}. These are rolling reference bounds, not guaranteed price barriers.")
        st.write(f"**Latest 50/200 event:** {summary['Latest 50/200 cross']} {summary['Cross date']}")
        st.caption("Golden/death crosses always use SMA50/SMA200, regardless of customised display averages. They are events, distinct from an ongoing regime.")
    with b:
        st.subheader("Momentum context")
        if pd.notna(latest.RSI):
            rsi_label="Above 70: recent gains dominate" if latest.RSI>=70 else "Below 30: recent losses dominate" if latest.RSI<=30 else "Between 30 and 70"
            st.write(f"**RSI:** {rsi_label}. Extremes can persist.")
        if pd.notna(latest.MACD) and pd.notna(latest.MACD_Signal):
            st.write(f"**MACD:** {'above' if latest.MACD>=0 else 'below'} zero; {'above' if latest.MACD>=latest.MACD_Signal else 'below'} its signal.")
        st.write(f"**Candle figure:** {latest.Candle_Pattern or 'No setup under the stated rules'}")
        st.caption("Figures are geometric setups with preceding-trend context; they are not automatically confirmed reversals.")
    if symbol.startswith("^"):
        st.caption("Spot index volume is not traded share volume. Volume plots and volume-based confirmation are deliberately omitted.")
    with st.expander("Confirmed swings and when they became knowable"):
        st.dataframe(swings,width="stretch",hide_index=True)
        st.caption(f"A {settings.swing_window}-bar right-hand confirmation delays availability by that many observations. Labels are never used before KnownOn. This is single-series swing structure, not complete classical Dow Theory confirmation.")

with tab_quiz:
    st.subheader("Check yourself on this chart")
    st.caption(f"{symbol} · {actual_date}. Answers are worked out from the chart you are looking at, so they change with the instrument and replay date.")
    questions=quiz(analyzed,settings,swings)
    if not questions:
        st.info("Not enough history for questions yet. Step forward in replay or choose a longer history.")
    qkey="quiz_"+hashlib.sha1((source_id+symbol+str(actual_date)).encode()).hexdigest()[:12]
    with st.form(qkey):
        picks=[st.radio(f"Q{i+1}. {q['q']}",q["options"],index=None,key=f"{qkey}_{i}") for i,q in enumerate(questions)]
        checked=st.form_submit_button("Check my answers",type="primary")
    if checked:
        score=0
        for i,(q,pick) in enumerate(zip(questions,picks)):
            if pick==q["answer"]:
                score+=1;st.success(f"Q{i+1}. Correct — {q['answer']}. {q['why']}")
            elif pick is None:
                st.info(f"Q{i+1}. Not answered. The answer is {q['answer']}. {q['why']}")
            else:
                st.error(f"Q{i+1}. Not quite — the answer is {q['answer']}. {q['why']}")
        st.metric("Your score",f"{score} / {len(questions)}")
        st.caption("Change the instrument or step the replay date forward for a fresh set of answers.")

with tab_screen:
    st.subheader("Daily screener")
    choices=st.multiselect("Instruments to scan",symbols,default=symbols,format_func=lambda k:names[k])
    st.caption("Scan uses the same parameters and replay cutoff as the chart. Online scans request only your selections, in batches of ten. Partial failures remain visible.")
    if st.button("Run screener",type="primary"):
        scan_frames={};errors={}
        if source=="Synthetic demo":
            scan_frames={s:get_demo(s) for s in choices}
        elif source=="Upload CSV":
            scan_frames={s:completed_daily_bars(uploaded_frames[s]) for s in choices}
        else:
            start=date.today()-timedelta(days=365*5+20)
            progress=st.progress(0)
            for offset in range(0,len(choices),10):
                batch=tuple(choices[offset:offset+10])
                try:
                    found,failed=get_yahoo(batch,start,date.today()+timedelta(days=1))
                    scan_frames.update({s:completed_daily_bars(d) for s,d in found.items()});errors.update(failed)
                except Exception as exc:
                    errors.update({s:str(exc) for s in batch})
                progress.progress(min(1,(offset+10)/max(1,len(choices))))
            progress.empty()
        rows=[]
        for s in choices:
            try:
                if s not in scan_frames:
                    raise ValueError(errors.get(s,"No data returned"))
                view=analyze(scan_frames[s],cutoff,settings)
                row=summary_row(s,view,settings)
                if not view.empty and view.index[-1].date()!=actual_date:
                    row["Status"]="Different last date: inspect freshness"
                rows.append(row)
            except Exception as exc:
                rows.append({"Symbol":s,"Status":"Error: "+str(exc)})
        screen=pd.DataFrame(rows)
        st.session_state.screen_record={"context":context,"table":screen}
    if not screen.empty:
        summary_table=observation_summary(screen)
        st.markdown(f"#### Live summary · {len(screen)} instruments · through {actual_date}")
        headline=breadth_headline(summary_table)
        if headline:
            st.caption("Market breadth: "+headline+".")
        st.dataframe(summary_table,width="stretch",hide_index=True,
                     column_config={
                         "Matching":st.column_config.NumberColumn("Matching",help="Instruments showing this observation"),
                         "Measured":st.column_config.NumberColumn("Measured",help="Instruments with enough history to calculate it"),
                         "Share":st.column_config.ProgressColumn("Share of measured",format="percent",min_value=0,max_value=1),
                         "Instruments":st.column_config.TextColumn("Instruments",width="large"),
                         "Meaning":st.column_config.TextColumn("What it means",width="large")})
        st.caption("Each row uses exactly the same rule as the matching option in Filter observations below, so the counts agree. "
                   "It refreshes every time you run the screener, and in replay it reflects the replay date.")
        filter_name=st.selectbox("Filter observations",["All",*OBSERVATION_NAMES])
        filtered=screen if filter_name=="All" else screen.loc[observation_mask(screen,filter_name)]
        st.dataframe(filtered,width="stretch",hide_index=True)
        st.caption(f"{len(filtered)} displayed / {len(screen)} scanned. These are observations, not ranked buy/sell recommendations. Excel includes the full unfiltered scan and status rows.")
    else:
        st.info("Run the screener to calculate this snapshot.")

with tab_replay:
    st.subheader("Practise without future price rows")
    if not replay:
        st.info("Enable Historical replay in the sidebar, choose a cutoff, record an observation, then use Next session.")
    journal_key="journal_"+hashlib.sha1((source_id+symbol).encode()).hexdigest()[:12]
    if journal_key not in st.session_state:
        st.session_state[journal_key]=[]
    with st.form("observation_form"):
        observation=st.text_area("What do you observe? State the trend, levels and what would invalidate your view.",max_chars=2000)
        submitted=st.form_submit_button("Record observation at this cutoff")
    if submitted and observation.strip():
        st.session_state[journal_key].append({"Date":str(actual_date),"Symbol":symbol,"Close":float(latest.Close),"Observation":observation.strip()})
        st.success("Recorded for this browser session. Download the journal to retain it.")
    journal=pd.DataFrame(st.session_state[journal_key])
    if not journal.empty:
        # Rewinding also hides notes written at later cutoffs.
        journal=journal.loc[pd.to_datetime(journal.Date).dt.date<=actual_date]
        st.dataframe(journal,width="stretch",hide_index=True)
        st.download_button("Download visible journal CSV",journal.to_csv(index=False).encode(),file_name=f"{symbol}_journal_{actual_date}.csv",mime="text/csv")
    st.caption("Replay cuts data before all computations and exports. Full input histories remain on the server. This is a teaching replay, not an examination-security system or a point-in-time investment backtest. Current/reference membership and provider-revised historical prices can cause survivorship or revision bias.")

with tab_learn:
    st.subheader("Formula first, interpretation second")
    st.markdown("""
**SMA(n)** = mean of the latest n closes.  
**EMA(n)** = α × close + (1 − α) × previous EMA; α = 2/(n+1). First EMA uses the first n-close SMA.  
**ROC(n)** = (close / close n intervals ago − 1) × 100. Requires n+1 closes.  
**Wilder RSI(n)**: seed gains/losses from n changes, then update each average with α=1/n. RSI = 100 × average gain / (average gain + average loss). Gain-only=100; loss-only=0; all-flat=50 by convention.  
**MACD** = fast EMA − slow EMA. **Signal** = seeded EMA of MACD. **Histogram** = MACD − signal. With 12/26/9 and these seeds, the first full histogram appears at observation 34.  
**Support/resistance** = minimum/maximum of the previous n bars, excluding the tested bar. Select High/Low or Close.  
**Golden/death cross** = a new crossing of SMA50 and SMA200. An above-average state is not a new event every day.
""")
    st.markdown(f"#### Today's numbers, step by step · {symbol} · {actual_date}")
    st.caption("The same formulas applied to the latest revealed day. Each result matches the value the app plots.")
    worked=worked_numbers(analyzed,settings)
    if not worked:
        st.info("Indicators are still warming up for this date.")
    for name,block in worked.items():
        with st.expander(block["title"],expanded=(name=="SMA")):
            st.table(pd.DataFrame(block["rows"],columns=["Step","Value"]))
            if name=="SMA":
                closes=block["closes"].rename("Close").to_frame()
                closes.index=closes.index.strftime("%d %b %Y")
                st.caption(f"The {len(closes)} closes being averaged:")
                st.dataframe(closes.T,width="stretch")
    with st.expander("Exact candle rules"):
        st.write("Doji: body ≤ 10% of nonzero range. Hammer: prior close below its value three intervals earlier, lower wick ≥ 2× body, upper wick ≤ body, body > 10% of range. Shooting star mirrors this after an advance. Engulfing: opposite-colour second body contains the previous body after a corresponding prior move. Endpoint equality qualifies. Setups need an independently stated confirmation rule.")
    st.markdown("""
- [What Is Technical Analysis?](https://themountainpathacademy.com/learn-what-is-technical-analysis)
- [Dow Theory](https://themountainpathacademy.com/learn-what-is-dow-theory)
- [Candlestick Charts](https://themountainpathacademy.com/learn-candlestick-charts)
- [SMA and EMA](https://themountainpathacademy.com/learn-moving-averages-sma-ema)
- [Support and Resistance](https://themountainpathacademy.com/learn-support-and-resistance)
- [ROC, RSI and MACD](https://themountainpathacademy.com/learn-momentum-indicators-roc-rsi-macd)
""")

with tab_data:
    st.subheader("Inspect and download this snapshot")
    st.caption(source_note)
    st.dataframe(analyzed.tail(80),width="stretch")
    visible_journal=pd.DataFrame(st.session_state.get(journal_key,[]))
    if not visible_journal.empty:
        visible_journal=visible_journal.loc[pd.to_datetime(visible_journal.Date).dt.date<=actual_date]
    metadata={"Symbol":symbol,"Source":source_note,"Cutoff":str(cutoff),"Last bar":str(actual_date),
              "Replay":str(replay),"Timeframe":"Daily","Observation count":len(analyzed),
              "Export generated IST":str(pd.Timestamp.now(tz="Asia/Kolkata")),
              "Universe":st.session_state.get("universe_status","Bundled reference, not historical membership")}
    workbook=excel_bytes(analyzed,settings,metadata,screen=screen,swings=swings,journal=visible_journal,
                         summary=observation_summary(screen) if not screen.empty else None)
    st.download_button("Download Excel workbook",workbook,file_name=f"{symbol.replace('^','')}_technical_analysis_{actual_date}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Download revealed indicators CSV",analyzed.to_csv().encode(),file_name=f"{symbol}_indicators_{actual_date}.csv",mime="text/csv")
    st.caption("The Excel workbook includes OHLCV, calculated values, parameters, metadata, confirmed swings, and the current screener/journal if available. Values are exported as a reproducible snapshot; Excel cells are not a recalculating indicator model.")

footer()
