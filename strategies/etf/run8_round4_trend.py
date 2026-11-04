"""Round 4-B (4 Nov 2026): long/short trend on 40 themes, walk-forward model choice, as pre-registered (commit 14e2336)."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
import engine as E
S, END = "2006-01-31", "2026-09-30"
NEW = {"BD_EGB13": "LET1TREU", "BD_EGB10": "LET5TREU", "BD_UST13": "LT01TRUU", "BD_UST20": "LUTLTRUU", "BD_EILB": "BEIG1T",
       "BD_TIPS": "LBUTTRUU", "BD_EHY": "LP01TREU", "EQ_EUR": "MSDEE15N", "EQ_UK": "NDDUUK", "EQ_PXJ": "NDDUPXJ",
       "EQ_WSC": "NCUDWI", "CM_NG": "BCOMNGTR", "CM_IND": "BCOMINTR", "CM_PREC": "BCOMPRTR", "CM_LIVE": "BCOMLITR"}
SHORTABLE = ["EQ_US", "EQ_EMU", "EQ_EUR", "BD_EGB", "BD_UST", "CM_GOLD", "CM_WTI", "CM_BCOM"]
L_R = pd.concat([E.trend_returns(),
                 pd.DataFrame({k: E.col(E.TREND_PLUS, v).pct_change() for k, v in NEW.items()}),
                 E.sector_returns_tr().add_prefix("SEC_")], axis=1)
cash = E.CASH.reindex(L_R.index).fillna(0)
vol = L_R.rolling(12, min_periods=12).std() * 12 ** .5
SH = pd.DataFrame({"SH_" + a: -L_R[a] - (vol[a].shift(1) ** 2) / 12 - 0.006 / 12 for a in SHORTABLE})   # inverse ETF, daily reset
R = pd.concat([L_R, SH], axis=1)


def model(L, k, ls, target=0.10, cov_win=36):
    ex = L_R.sub(cash, axis=0)
    mom = (1 + ex).rolling(L).apply(np.prod, raw=True) - 1
    score = mom / vol
    rows = {}
    for t in L_R.index:
        s = score.loc[t].dropna()
        if len(s) < 20: continue
        longs = s[s > 0].nlargest(k).index
        raw = pd.Series(0.0, index=R.columns)
        raw[longs] = 1 / vol.loc[t, longs]
        if ls:
            sh = s.reindex(SHORTABLE).dropna(); sh = sh[sh < 0].nsmallest(k).index
            raw[["SH_" + a for a in sh]] = 1 / vol.loc[t, sh].values
        act = raw[raw > 0].index
        if len(act) == 0: rows[t] = raw; continue
        hist = R.loc[:t, act].tail(cov_win).dropna()
        if len(hist) < 12: continue
        x = raw[act]; pv = float(np.sqrt(x @ (hist.cov() * 12) @ x))
        w = raw * (target / pv if pv > 0 else 0)
        if w.sum() > 1: w = w / w.sum()
        rows[t] = w
    return pd.DataFrame(rows).T.fillna(0.0)


grid = list(itertools.product([3, 6, 12], [3, 5, 8], [False, True]))
MW, MR = {}, {}
for g in grid:
    W = model(*g); r, _, _ = E.run(W, R, 0.001, 0.003, "2002-01-31")
    MW[g], MR[g] = W, r
MRdf = pd.DataFrame(MR)


def walk_forward(win):
    rows, choice = {}, {}
    for t in MRdf.index:
        h = MRdf.loc[:t].tail(win)                       # returns realised up to and including month t
        if len(h) < win: continue
        sh = h.mean() / h.std()
        best = sh.idxmax(); choice[t] = best
        rows[t] = MW[best].loc[t] if t in MW[best].index else pd.Series(0.0, index=R.columns)
    return pd.DataFrame(rows).T.fillna(0.0), pd.Series(choice)


world = E.BENCH.loc[S:END] - 0.0012 / 12
WT, RT = E.trend(); t1, _, _ = E.run(WT, RT, 0.001, 0.003, S)
res = {"T1 rules (reference)": (t1, None)}
for win in (12, 24):
    W, ch = walk_forward(win); r, to, w = E.run(W, R, 0.001, 0.003, S)
    res[f"T4-WF{win} walk-forward {win}m"] = (r, (to, w, ch))
rows = []
for nm, (r, extra) in list(res.items()) + [("MSCI World ETF", (world, None))]:
    f, d, v = E.stats(r), E.stats(r.loc[:"2015-12-31"]), E.stats(r.loc["2016-01-31":])
    row = dict(name=nm, cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"], d_sh=d["sharpe"], v_sh=v["sharpe"],
               d_cagr=d["cagr"], v_cagr=v["cagr"], corr=r.corr(world.reindex(r.index)))
    if extra:
        to, w, ch = extra
        row.update(turnover=to.mean() * 12, short_w=w.filter(like="SH_").sum(axis=1).mean(), gross=w.sum(axis=1).mean(),
                   model_changes=int((ch.loc[S:] != ch.loc[S:].shift()).sum()))
    rows.append(row)
pd.set_option("display.width", 260)
print(pd.DataFrame(rows).set_index("name").to_string(float_format=lambda x: f"{x:.3f}"))
# in-sample best fixed model (for information: what hindsight would have picked)
fx = pd.DataFrame({str(g): E.stats(MR[g].loc[S:]) for g in grid}).T[["cagr", "sharpe", "mdd"]].astype(float).sort_values("sharpe", ascending=False)
print(fx.head(5).round(3)); print("median fixed-model Sharpe", round(fx.sharpe.median(), 3))
for nm, (r, extra) in res.items():
    if extra: print(nm, "model usage:", extra[2].loc[S:].value_counts().head(5).to_dict())
cal = pd.DataFrame({k: E.calendar(v[0]) for k, v in res.items()}); cal["MSCI"] = E.calendar(world)
print(cal.loc[2006:].round(3).to_string())
pd.to_pickle({k: v[0] for k, v in res.items()}, os.path.join(E.D, "round4_trend.pkl"))
