"""Load the Bloomberg ETF extract into tidy monthly DataFrames.

Usage: python strategies/etf/load.py data/ETF_EXTRACT_VALUE.xlsx ; python strategies/etf/load.py data/VALUE_ETF_2.xlsx   then   python strategies/etf/run3.py ; python strategies/etf/export.py
"""
import sys
import openpyxl
import pandas as pd
import numpy as np

SRC = sys.argv[1]
from pathlib import Path
OUT = str(Path(__file__).resolve().parents[2] / "data" / "etf")   # not committed: licensed data
wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)


def block(name):
    rows = list(wb[name].iter_rows(values_only=True))
    labels, tick, fld = rows[1], rows[2], rows[2]
    out = {}
    for c in range(0, len(rows[2]), 3):
        t = rows[2][c]
        if not t:
            continue
        f = rows[2][c + 1]
        d = []
        for r in rows[4:]:
            if c + 1 >= len(r):
                continue
            dt, v = r[c], r[c + 1]
            if dt is None:
                continue
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                d.append((pd.Timestamp(dt), float(v)))
        s = pd.Series(dict(d), dtype=float)
        if len(s):
            s.index = s.index + pd.offsets.MonthEnd(0)
            s = s[~s.index.duplicated(keep="last")]
        out[(t, f)] = s
    return out


import os
os.makedirs(OUT, exist_ok=True)
for name in [n for n in ["Valo_Pays", "Valo_Secteurs", "Rendements", "Marche", "Capi", "Secteurs_TR", "Trend_Plus"] if n in wb.sheetnames]:   # extract #1 and #2
    b = block(name)
    df = pd.DataFrame(b)
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["ticker", "field"])
    df = df.sort_index()
    df.to_pickle(f"{OUT}/{name}.pkl")
    cov = df.notna().sum()
    print(name, df.shape, df.index.min().date(), df.index.max().date())
    print("  short/empty:", [(t, f, n) for (t, f), n in cov.items() if n < 120][:30])
