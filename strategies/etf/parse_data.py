import openpyxl, pandas as pd, numpy as np, sys
from datetime import datetime
src, out = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
tk = pd.DataFrame(list(wb["Tickers"].iter_rows(min_row=2, max_col=8, values_only=True)),
                  columns=["ticker", "name", "crncy", "gics_sector", "gics_ig", "cntry_of_risk", "cntry_of_domicile", "figi"])
tk = tk.replace({r"^#N/A.*": np.nan}, regex=True); tk.to_parquet(f"{out}/sat_tickers.parquet")
def blocks(prefix):
    recs = []
    for n in [s for s in wb.sheetnames if s.startswith(prefix + "_")]:
        rows = list(wb[n].iter_rows(min_row=2, values_only=True))
        names = rows[0]
        for c in range(0, len(names), 2):
            t = names[c]
            if not t: continue
            for r in rows[2:]:
                if c + 1 < len(r) and isinstance(r[c], datetime) and isinstance(r[c + 1], (int, float)):
                    recs.append((t, pd.Timestamp(r[c]) + pd.offsets.MonthEnd(0), float(r[c + 1])))
    df = pd.DataFrame(recs, columns=["ticker", "date", "value"]).drop_duplicates(["ticker", "date"], keep="last")
    return df.pivot(index="date", columns="ticker", values="value").sort_index()
tr = blocks("TR"); cap = blocks("CAP")
tr.to_parquet(f"{out}/sat_tr_monthly.parquet"); cap.to_parquet(f"{out}/sat_cap_monthly.parquet")
F = ["SALES_REV_TURN", "EBIT", "NET_INCOME", "CF_FREE_CASH_FLOW", "TOT_COMMON_EQY", "NET_DEBT", "MINORITY_NONCONTROLLING_INTEREST", "BS_SH_OUT", "ANNOUNCEMENT_DT"]
recs = []
for n in [s for s in wb.sheetnames if s.startswith("FUND_")]:
    rows = list(wb[n].iter_rows(min_row=4, values_only=True)); t = None
    for r in rows:
        if r[1]: t = r[1]
        if t is None: continue
        for j, f in enumerate(F):
            c = 2 + 2 * j
            if c + 1 < len(r) and isinstance(r[c], datetime) and isinstance(r[c + 1], (int, float)):
                recs.append((t, pd.Timestamp(r[c]), f, float(r[c + 1])))
fd = pd.DataFrame(recs, columns=["ticker", "fy_end", "field", "value"]).drop_duplicates(["ticker", "fy_end", "field"], keep="last")
fd = fd.pivot_table(index=["ticker", "fy_end"], columns="field", values="value").reset_index()
fd["announcement_dt"] = pd.to_datetime(fd["ANNOUNCEMENT_DT"].dropna().astype("int64").astype(str), format="%Y%m%d", errors="coerce").reindex(fd.index)
fd.to_parquet(f"{out}/sat_fundamentals.parquet")
print("tickers", len(tk), "| sector missing", tk.gics_sector.isna().sum(), "| TR", tr.shape, tr.index.min().date(), tr.index.max().date(), "| CAP", cap.shape, "| fund rows", len(fd), "tickers", fd.ticker.nunique(), "fy", fd.fy_end.min().date(), fd.fy_end.max().date())
