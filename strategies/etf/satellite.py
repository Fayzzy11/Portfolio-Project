"""Stock satellite (30%) of the value strategy, exactly as pre-registered in PREREG_satellite.md (commit eded958)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
import engine as E
SD = os.path.join(E.D, "..", "screen")
SC = pd.read_parquet(os.path.join(SD, "scores_fye6.parquet"))
RW = pd.read_parquet(os.path.join(SD, "ret_total_net.parquet")).sort_index()
MKW = pd.read_parquet(os.path.join(SD, "market.parquet")).sort_index()
SECTOR_NAME = {"EN": "Energy", "MT": "Materials", "IN": "Industrials", "CD": "Consumer Discretionary", "CS": "Consumer Staples",
               "HC": "Health Care", "FN": "Financials", "IT": "Information Technology", "TC": "Communication Services",
               "UT": "Utilities", "RE": "Real Estate"}
N, MAX_SEC, MAX_CTY, KEEP_PCT, COST = 8, 2, 3, 0.60, 0.0015
END_W = pd.Timestamp("2026-06-30")


def core_selection():
    W = E.value_v4c(timing=False)[0]
    return W


def select(t, held, Wcore):
    me = (t + pd.offsets.MonthEnd(0))
    row = Wcore.loc[:me].iloc[-1]
    ctys = {c[2:] for c, x in row.items() if x > 0 and c.startswith("C_")}
    secs = {SECTOR_NAME[c[2:]] for c, x in row.items() if x > 0 and c.startswith("S_")}
    s = SC[(SC["date"] == t) & SC["eligible"].fillna(False).astype(bool)].copy()
    wk = RW.index[RW.index <= t][-1]
    priced = RW.loc[wk].notna() | RW.loc[:wk].tail(4).notna().any()
    s = s[s["ticker"].map(lambda x: bool(priced.get(x, False)))]
    s = s.sort_values(["score_pct", "score"], ascending=False)
    keep = [h for h in held if h in set(s["ticker"]) and float(s.loc[s["ticker"] == h, "score_pct"].iloc[0]) >= KEEP_PCT]
    info = s.set_index("ticker")
    out = list(keep)
    cnt_s = info.loc[out, "gics_sector_name"].value_counts().to_dict() if out else {}
    cnt_c = info.loc[out, "cntry_of_risk"].value_counts().to_dict() if out else {}
    elig = s[s["cntry_of_risk"].isin(ctys) | s["gics_sector_name"].isin(secs)]
    for _, x in elig.iterrows():
        if len(out) >= N: break
        if x["ticker"] in out: continue
        if cnt_s.get(x["gics_sector_name"], 0) >= MAX_SEC or cnt_c.get(x["cntry_of_risk"], 0) >= MAX_CTY: continue
        out.append(x["ticker"]); cnt_s[x["gics_sector_name"]] = cnt_s.get(x["gics_sector_name"], 0) + 1
        cnt_c[x["cntry_of_risk"]] = cnt_c.get(x["cntry_of_risk"], 0) + 1
    return out, info.loc[out, ["name", "gics_sector_name", "cntry_of_risk", "score_pct", "score"]], (sorted(ctys), sorted(secs))


def run_satellite(apply_risk=True):
    Wcore = core_selection()
    expo_m = E.value_core()[2]                       # decided at month end m, applies to month m+1
    dates = sorted(SC["date"].unique())
    held, sel_log = [], {}
    for t in dates:
        held, info, core = select(pd.Timestamp(t), held, Wcore)
        sel_log[pd.Timestamp(t)] = (held, info, core)
    weeks = RW.index[(RW.index > dates[0]) & (RW.index <= END_W)]
    estr = MKW["ESTRON"].ffill() / 100 / 52
    rets, turns, expos = [], [], []
    w = pd.Series(dtype=float); cur_hold = None; cur_exp = None
    for wk in weeks:
        reb = [d for d in sel_log if d < wk]
        hold = sel_log[reb[-1]][0]
        prev_me = (wk - pd.offsets.MonthBegin(1)) - pd.offsets.MonthEnd(0) if wk.day > 0 else wk
        me = (wk.to_period("M").to_timestamp("M") - pd.offsets.MonthEnd(1))
        x = float(expo_m.loc[:me].iloc[-1]) if apply_risk else 1.0
        turn = 0.0
        if hold != cur_hold or x != cur_exp:
            target = pd.Series(x / len(hold), index=hold)
            allk = target.index.union(w.index)
            turn = (target.reindex(allk).fillna(0) - w.reindex(allk).fillna(0)).abs().sum()
            w = target; cur_hold, cur_exp = hold, x
        r = RW.loc[wk, w.index].fillna(0.0)
        cash_w = 1 - w.sum()
        gross = float((w * r).sum() + cash_w * estr.reindex([wk]).fillna(0).iloc[0])
        net = gross - turn * COST
        w = w * (1 + r) / (1 + gross)                 # drift
        rets.append(net); turns.append(turn); expos.append(x)
    out = pd.DataFrame({"r": rets, "turnover": turns, "expo": expos}, index=weeks)
    return out, sel_log


def to_monthly(rw):
    return (1 + rw).groupby(rw.index.to_period("M")).prod().sub(1).rename(lambda p: p.to_timestamp("M"))


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    sat, log = run_satellite()
    satm = to_monthly(sat["r"])
    S, END = "2021-07-31", "2026-06-30"
    satm = satm.loc[S:END]
    Wc, Rc, expo, rs = E.value_core(); core, _, _ = E.run(Wc, Rc, 0.001, 0.0025, "2006-01-31")
    core = core.loc[S:END]
    combo = 0.7 * core + 0.3 * satm.reindex(core.index)
    wv = E.world_value().loc[S:END]; mw = E.BENCH.loc[S:END]
    sat_norisk, _ = run_satellite(apply_risk=False); satn = to_monthly(sat_norisk["r"]).loc[S:END]
    rows = []
    for nm, r in (("Satellite (30%, with risk rule)", satm), ("Satellite without risk rule", satn), ("Core V7 (ETF)", core),
                  ("Strategy 70/30", combo), ("MSCI World Value", wv), ("MSCI World", mw)):
        f = E.stats(r); ex = r - wv.reindex(r.index); exm = r - mw.reindex(r.index)
        rows.append(dict(name=nm, cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"],
                         ex_wv=ex.mean() * 12, t_wv=ex.mean() / ex.std() * np.sqrt(len(ex)) if ex.std() > 0 else np.nan,
                         ex_mw=exm.mean() * 12, t_mw=exm.mean() / exm.std() * np.sqrt(len(exm)) if exm.std() > 0 else np.nan))
    print(pd.DataFrame(rows).set_index("name").to_string(float_format=lambda x: f"{x:.3f}"))
    print("satellite turnover/yr", round(sat["turnover"].sum() / (len(sat) / 52), 2), "| avg exposure", round(sat["expo"].mean(), 2))
    cal = pd.DataFrame({"sat": E.calendar(satm), "core": E.calendar(core), "combo": E.calendar(combo), "WV": E.calendar(wv), "MW": E.calendar(mw)}); print(cal.round(3))
    for t, (h, info, core_sel) in log.items():
        print(t.date(), "core:", core_sel[0], core_sel[1]); print("   ", [(r["name"][:22], r["gics_sector_name"][:12], r["cntry_of_risk"], round(r["score_pct"], 2)) for _, r in info.iterrows()])
    pd.to_pickle(dict(sat=sat, satm=satm, satn=satn, core=core, combo=combo, log=log), os.path.join(E.D, "satellite.pkl"))
