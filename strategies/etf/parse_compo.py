import openpyxl, pandas as pd, sys
wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
out = []
rows = list(wb["Compositions"].iter_rows(values_only=True)); dates = rows[1]
for c in range(0, len(dates), 3):
    if dates[c] is None: continue
    d = pd.to_datetime(dates[c], dayfirst=True)
    for r in rows[3:]:
        if c + 1 < len(r) and r[c] not in (None, "") and isinstance(r[c + 1], (int, float)):
            out.append((d, str(r[c]).strip() + " Equity", float(r[c + 1])))
t = list(wb["Tests"].iter_rows(values_only=True))
for col, d in ((7, "2006-06-30"), (10, "2011-12-30")):            # H-I and K-L (0-based 7 and 10)
    out = [x for x in out if x[0] != pd.Timestamp(d)]
    for r in t[3:]:
        if col + 1 < len(r) and r[col] not in (None, "") and isinstance(r[col + 1], (int, float)):
            out.append((pd.Timestamp(d), str(r[col]).strip() + " Equity", float(r[col + 1])))
df = pd.DataFrame(out, columns=["date", "ticker", "weight_pct"])
df.to_parquet(sys.argv[2]); print(df.groupby("date").agg(n=("ticker", "size"), w=("weight_pct", "sum")).to_string())
