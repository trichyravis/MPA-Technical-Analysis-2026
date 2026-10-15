from pathlib import Path
from io import StringIO
import re
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
CONSTITUENT_URL="https://www.niftyindices.com/IndexConstituent/ind_nifty50list.csv"
INDICES=pd.DataFrame([{"Symbol":"^NSEI","Name":"Nifty 50 index","Type":"Index"},
                      {"Symbol":"^NSEBANK","Name":"Bank Nifty index","Type":"Index"}])


def reference_universe():
    """Editable reference watchlist; not certified current/historical membership."""
    stocks=pd.read_csv(ROOT/"data"/"reference_universe.csv")
    return pd.concat([INDICES,stocks],ignore_index=True)


def fetch_current_constituents():
    response=requests.get(CONSTITUENT_URL,timeout=20,
                          headers={"User-Agent":"Mozilla/5.0","Accept":"text/csv,*/*"})
    response.raise_for_status()
    df=pd.read_csv(StringIO(response.text))
    if not {"Symbol","Company Name"}.issubset(df.columns):
        raise ValueError("Official constituent response did not contain the expected columns.")
    df=df.dropna(subset=["Symbol","Company Name"])
    symbols=df.Symbol.astype(str).str.strip()
    if len(df)!=50 or symbols.duplicated().any() or not symbols.map(lambda x:bool(re.fullmatch(r"[A-Z0-9&-]+",x))).all():
        raise ValueError("Expected 50 unique stock symbols; verify the source response.")
    stocks=pd.DataFrame({"Symbol":symbols+".NS","Name":df["Company Name"].astype(str),"Type":"Stock"})
    return pd.concat([INDICES,stocks],ignore_index=True)
