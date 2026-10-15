import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .config import Settings

NAVY="#ADD8E6"
GOLD="#FFD700"
TEAL="#37CDB0"
RED="#FF6B7C"


def technical_chart(d, symbol, settings=Settings(), average="Both", bars=180):
    v=d.tail(bars)
    volume=v.Volume.notna().any()
    titles=["Price, averages and prior-window levels",f"ROC({settings.roc_period}) %",
            f"Wilder RSI({settings.rsi_period})","MACD / signal / histogram"]
    heights=[.48,.14,.14,.24]
    if volume:
        titles.append("Traded volume");heights=[.43,.12,.12,.21,.12]
    fig=make_subplots(rows=len(titles),cols=1,shared_xaxes=True,vertical_spacing=.035,
                      row_heights=heights,subplot_titles=titles)
    fig.add_trace(go.Candlestick(x=v.index,open=v.Open,high=v.High,low=v.Low,close=v.Close,
                                increasing_line_color=TEAL,decreasing_line_color=RED,name="OHLC"),row=1,col=1)
    for j,n in enumerate([settings.short_ma,settings.fast_ma,settings.slow_ma]):
        for kind,dash in [("SMA","solid"),("EMA","dot")]:
            if average in ("Both",kind):
                fig.add_trace(go.Scatter(x=v.index,y=v[f"{kind}_{n}"],name=f"{kind} {n}",
                                         line=dict(color=[TEAL,GOLD,"#BBA5F5"][j],width=1.5,dash=dash)),row=1,col=1)
    for key,color in [("Support",TEAL),("Resistance",RED)]:
        fig.add_trace(go.Scatter(x=v.index,y=v[key],name=f"Prior {settings.sr_period}-bar {key.lower()}",
                                line=dict(color=color,dash="dash",width=1)),row=1,col=1)
    for col,label,color,shape in [("Golden_Cross","Golden cross",GOLD,"triangle-up"),
                                 ("Death_Cross","Death cross",RED,"triangle-down")]:
        events=v.loc[v[col]]
        fig.add_trace(go.Scatter(x=events.index,y=events.Close,name=label,mode="markers",
                                marker=dict(color=color,size=12,symbol=shape)),row=1,col=1)
    fig.add_trace(go.Scatter(x=v.index,y=v.ROC,name="ROC",line=dict(color=NAVY)),row=2,col=1)
    fig.add_hline(y=0,line_width=1,line_dash="dot",row=2,col=1)
    fig.add_trace(go.Scatter(x=v.index,y=v.RSI,name="RSI",line=dict(color=TEAL)),row=3,col=1)
    for y in [30,50,70]:
        fig.add_hline(y=y,line_width=1,line_dash="dot",row=3,col=1)
    fig.update_yaxes(range=[0,100],row=3,col=1)
    fig.add_trace(go.Bar(x=v.index,y=v.MACD_Histogram,name="MACD histogram",
                          marker_color=[TEAL if x>=0 else RED for x in v.MACD_Histogram.fillna(0)]),row=4,col=1)
    fig.add_trace(go.Scatter(x=v.index,y=v.MACD,name="MACD",line=dict(color=TEAL)),row=4,col=1)
    fig.add_trace(go.Scatter(x=v.index,y=v.MACD_Signal,name="Signal",line=dict(color=GOLD)),row=4,col=1)
    fig.add_hline(y=0,line_width=1,line_dash="dot",row=4,col=1)
    if volume:
        fig.add_trace(go.Bar(x=v.index,y=v.Volume,name="Volume",marker_color="#8BA7BE"),row=5,col=1)
    fig.update_layout(height=1050 if volume else 950,template="plotly_dark",hovermode="x unified",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                      title=f"{symbol} · through {d.index[-1]:%d %b %Y}",
                      xaxis_rangeslider_visible=False,
                      # Legend sits above the first subplot title instead of overlapping it.
                      legend=dict(orientation="h",yanchor="bottom",y=1.035,x=0),
                      margin=dict(l=30,r=20,t=160,b=40),font=dict(family="Arial",color=NAVY))
    fig.update_xaxes(rangeslider_visible=False,showgrid=False)
    return fig


def replay_outcome_chart(history, decision_date):
    """Use only after the learner explicitly reveals the next outcome."""
    fig=go.Figure(go.Scatter(x=history.index,y=history.Close,mode="lines",line=dict(color=TEAL),name="Close"))
    fig.add_vline(x=pd.Timestamp(decision_date).timestamp()*1000,line_dash="dash",line_color=GOLD)
    fig.update_layout(template="plotly_dark",height=300,title="Revealed outcome (after stepping forward)")
    return fig
