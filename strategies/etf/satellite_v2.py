"""Satellite v2 (monthly, 2006-2026, top-300 developed universe), exactly as pre-registered in PREREG_satellite_v2.md (e51b8a5)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import engine as E
SD = os.path.join(E.D, "..", "screen")
DM = ["US","CA","GB","IE","FR","DE","NL","BE","LU","AT","CH","IT","ES","PT","FI","SE","NO","DK","JP","AU","NZ","HK","SG","IL"]
SECTOR_NAME = {"EN": "Energy", "MT": "Materials", "IN": "Industrials", "CD": "Consumer Discretionary", "CS": "Consumer Staples",
               "HC": "Health Care", "FN": "Financials", "IT": "Information Technology", "TC": "Communication Services",
               "UT": "Utilities", "RE": "Real Estate"}
N, MAX_SEC, MAX_CTY, KEEP, COST, WHT = 8, 2, 3, 0.60, 0.0015, 0.004
NONFIN, FIN = ["ebit_ev", "b_p", "fcf_p", "s_ev"], ["b_p", "e_p"]

tk = pd.read_parquet(f"{SD}/sat_tickers_clean.parquet").set_index("ticker")
TR = pd.read_parquet(f"{SD}/sat_tr_monthly.parquet"); CAP = pd.read_parquet(f"{SD}/sat_cap_monthly.parquet")
RET = TR.pct_change(fill_method=None)


def universe():
    a = pd.read_parquet(f"{SD}/superset_2005_2020.parquet")[["date", "ticker", "weight_pct"]]
    b = pd.read_parquet(f"{SD}/top300_2021_2025.parquet")[["date", "ticker", "weight_pct"]]
    u = pd.concat([a, b]); u["date"] = pd.to_datetime(u["date"])
    u["cty"] = u.ticker.map(tk["cntry_of_risk"]); u["sector"] = u.ticker.map(tk["gics_sector"]); u["name"] = u.ticker.map(tk["name"])
    u = u[u.cty.isin(DM) & u.sector.notna()]
    u = u.sort_values("weight_pct", ascending=False).drop_duplicates(["date", "name"])
    u["r"] = u.groupby("date").weight_pct.rank(ascending=False, method="first")
    return u[u.r <= 300]


def fundamentals():
    f = pd.read_parquet(f"{SD}/sat_fundamentals.parquet")
    old = pd.read_parquet("/home/claude/work/cc_zip/portfolio-project/data/interim/fundamentals.parquet")
    old = old[~old.ticker.isin(f.ticker)]
    f = pd.concat([f, old], ignore_index=True)
    fye6 = f["fy_end"] + pd.DateOffset(months=6)
    f["avail"] = pd.concat([fye6, f["announcement_dt"].where(f["announcement_dt"].notna(), fye6)], axis=1).max(axis=1)
    return f


def wins(s):
    if s.notna().sum() < 3: return s
    a, b = s.quantile([0.01, 0.99]); return s.clip(a, b)


def zs(s):
    sd = s.std(); return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def score_month(m, u_m, F):
    f = F[F.avail <= m].sort_values("fy_end").groupby("ticker").tail(1).set_index("ticker")
    x = u_m.set_index("ticker").join(f, how="left")
    mcap = CAP.loc[m].reindex(x.index); mcap = mcap.where(mcap > 0)
    ev = (mcap + x["NET_DEBT"] + x["MINORITY_NONCONTROLLING_INTEREST"].fillna(0)).where(lambda v: v > 0)
    x["ebit_ev"] = x["EBIT"] / ev; x["s_ev"] = x["SALES_REV_TURN"].where(x["SALES_REV_TURN"] > 0) / ev
    x["b_p"] = x["TOT_COMMON_EQY"] / mcap; x["fcf_p"] = x["CF_FREE_CASH_FLOW"] / mcap; x["e_p"] = x["NET_INCOME"] / mcap
    for k in set(NONFIN + FIN):
        x[k + "_z"] = x.groupby("sector")[k].transform(lambda s: zs(wins(s)) if False else s)
        x[k + "_w"] = wins(x[k]); x[k + "_z"] = x.groupby("sector")[k + "_w"].transform(zs)
    zn, zf = x[[k + "_z" for k in NONFIN]], x[[k + "_z" for k in FIN]]
    cn = zn.mean(axis=1).where(zn.notna().sum(axis=1) >= 3); cf = zf.mean(axis=1).where(zf.notna().sum(axis=1) >= 2)
    x["score"] = np.where(x["sector"] == "Financials", cf, cn)
    x["score_pct"] = x.groupby("sector")["score"].rank(pct=True)
    return x


def run(S="2006-01-31", END="2026-06-30"):
    U = universe(); F = fundamentals()
    udates = sorted(U.date.unique())
    Wcore = E.value_v4c(timing=False)[0]; expo = E.value_core()[2]
    months = TR.loc[S:END].index
    held, rows, logs, cov = [], {}, {}, {}
    for m in months[:-1]:
        ud = max(d for d in udates if d <= m)
        u_m = U[U.date == ud][["ticker", "sector", "cty", "name"]]
        u_m = u_m[u_m.ticker.map(lambda t: pd.notna(TR.at[m, t]) if t in TR.columns else False)]
        x = score_month(m, u_m, F)
        cov[m] = (len(x), int(x.score.notna().sum()))
        row = Wcore.loc[:m].iloc[-1]
        ctys = {c[2:] for c, v in row.items() if v > 0 and c.startswith("C_")}
        secs = {SECTOR_NAME[c[2:]] for c, v in row.items() if v > 0 and c.startswith("S_")}
        s = x[x.score.notna()].sort_values(["score_pct", "score"], ascending=False)
        keep = [h for h in held if h in s.index and s.at[h, "score_pct"] >= KEEP]
        out = list(keep); cs = s.loc[out, "sector"].value_counts().to_dict(); cc = s.loc[out, "cty"].value_counts().to_dict()
        for t, r in s[s.cty.isin(ctys) | s.sector.isin(secs)].iterrows():
            if len(out) >= N: break
            if t in out or cs.get(r.sector, 0) >= MAX_SEC or cc.get(r.cty, 0) >= MAX_CTY: continue
            out.append(t); cs[r.sector] = cs.get(r.sector, 0) + 1; cc[r.cty] = cc.get(r.cty, 0) + 1
        held = out
        e = float(expo.loc[:m].iloc[-1])
        rows[m] = pd.Series(e / len(out), index=out) if out else pd.Series(dtype=float)
        logs[m] = s.loc[out, ["name", "sector", "cty", "score_pct"]].assign(expo=e)
    W = pd.DataFrame(rows).T.fillna(0.0)
    r, to, wn = E.run(W, RET.reindex(columns=W.columns), COST, WHT, S, END)
    return r, to, wn, logs, cov


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    S, END, MID = "2006-01-31", "2026-06-30", "2015-12-31"
    sat, to, wn, logs, cov = run(S, END)
    Wc, Rc, ex, rs = E.value_core(); core, _, _ = E.run(Wc, Rc, 0.001, 0.0025, S, END)
    idx = sat.index.intersection(core.index)
    sat, core = sat.loc[idx], core.loc[idx]
    combo = 0.7 * core + 0.3 * sat
    wv = E.world_value().reindex(idx); mw = E.BENCH.reindex(idx)
    rows = []
    for nm, r in (("Satellite v2 (8 names)", sat), ("Core V7", core), ("Strategy 70/30", combo), ("MSCI World Value", wv), ("MSCI World", mw)):
        f, d, v = E.stats(r), E.stats(r.loc[:MID]), E.stats(r.loc["2016-01-31":]); e = r - wv
        rows.append(dict(name=nm, start=f["start"], end=f["end"], cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"],
                         cagr_06_15=d["cagr"], cagr_16_26=v["cagr"], t_vs_wv=(e.mean() / e.std() * np.sqrt(len(e))) if e.std() > 0 else np.nan,
                         ahead_yrs=int((E.calendar(r) > E.calendar(wv)).sum())))
    print(pd.DataFrame(rows).set_index("name").to_string(float_format=lambda x: f"{x:.3f}"))
    print("satellite turnover/yr", round(to.mean() * 12, 2), "| scored names per month min/median:", min(v[1] for v in cov.values()), int(np.median([v[1] for v in cov.values()])))
    cal = pd.DataFrame({"sat": E.calendar(sat), "core": E.calendar(core), "combo": E.calendar(combo), "WV": E.calendar(wv), "MW": E.calendar(mw)})
    print(cal.round(3).to_string())
    hold_counts = pd.Series([t for l in logs.values() for t in l["name"]]).value_counts()
    print("most held:", hold_counts.head(12).to_dict())
    pd.to_pickle(dict(sat=sat, core=core, combo=combo, to=to, wn=wn, logs=logs, cov=cov), os.path.join(E.D, "satellite_v2.pkl"))
