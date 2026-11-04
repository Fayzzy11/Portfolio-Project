"""Round 5 (4 Nov 2026), exactly as pre-registered in PREREG_round5.md (commit 3051739)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
import engine as E
S, END, MID = "2006-01-31", "2026-09-30", "2015-12-31"
rc, rs = E.country_returns(), E.sector_returns_tr()
zs = E.value_score(E.VS, E.SECTORS)
mkt = E.col(E.MK, "MSDEWIN Index")
# indicators
red_trend = mkt < mkt.rolling(10).mean()
hy = E.col(E.TREND_PLUS, "LP01TREU"); g13 = E.col(E.TREND_PLUS, "LET1TREU")
red_credit = (hy.pct_change(3) - g13.pct_change(3)) < 0
lines = pd.concat([rc, rs], axis=1); idx = (1 + lines.fillna(0)).cumprod()
breadth = (idx > idx.rolling(10).mean()).where(lines.notna()).mean(axis=1)
red_breadth = breadth < 0.5
nred = red_trend.astype(int) + red_credit.astype(int) + red_breadth.astype(int)
fast = (mkt.pct_change(3) > 0) | (mkt > mkt.rolling(5).mean())


def exposure(fast_reentry=True):
    e = {}
    for t in nred.index:
        cut = nred.loc[t] >= 2
        if fast_reentry: cut = cut and not fast.loc[t]
        e[t] = 0.5 if cut else 1.0
    return pd.Series(e)


def select(z, n, keep):
    held, out = [], {}
    for t in z.index:
        s = z.loc[t].dropna()
        if len(s) < n: out[t] = list(held); continue
        rank = s.rank(ascending=False)
        held = [h for h in held if h in rank and rank[h] <= keep]
        for c in rank.sort_values().index:
            if len(held) >= n: break
            if c not in held: held.append(c)
        out[t] = list(held)
    W = pd.DataFrame({t: {c: 1 / len(l) for c in l} for t, l in out.items()}).T.reindex(z.index).fillna(0.0)
    return W[z.notna().sum(axis=1) >= 8]


def build(n=3, keep=5, mode="fast", z=zs, rets=rs):
    W = select(z, n, keep)
    if mode == "fast": W = W.mul(exposure(True).reindex(W.index).fillna(1), axis=0)
    elif mode == "slow": W = W.mul(exposure(False).reindex(W.index).fillna(1), axis=0)
    return E.run(W, rets, 0.001, 0.0025, S)


wv = E.world_value().loc[S:END]; mw = E.BENCH.loc[S:END]
v4c = pd.read_pickle(E.D + "/v4c_full.pkl")["r"]
out = {"V5 3 sectors, 50% cut, fast re-entry": build(), "S5a 2 sectors": build(2, 4), "S5b no fast re-entry": build(mode="slow"),
       "S5c always invested": build(mode="none")}
rows = []
def row(nm, r, to=None, w=None):
    f, d, v = E.stats(r), E.stats(r.loc[:MID]), E.stats(r.loc["2016-01-31":])
    ex = r - wv.reindex(r.index)
    return dict(name=nm, cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"], d_cagr=d["cagr"], v_cagr=v["cagr"], d_sh=d["sharpe"], v_sh=v["sharpe"],
                t_vs_wv=ex.mean() / ex.std() * np.sqrt(len(ex)), ahead_years=int(((E.calendar(r) - E.calendar(wv.reindex(r.index))) > 0).sum()),
                turnover=(to.mean() * 12 if to is not None else np.nan), invested=(w.sum(axis=1).mean() if w is not None else np.nan))
for nm, (r, to, w) in out.items(): rows.append(row(nm, r, to, w))
rows += [row("V4c (official until now)", v4c), row("MSCI World Value", wv), row("MSCI World", mw)]
pd.set_option("display.width", 260)
print(pd.DataFrame(rows).set_index("name").to_string(float_format=lambda x: f"{x:.3f}"))
ex = exposure(True).loc[S:END]; print("V5: months at 50%:", int((ex < 1).sum()), "of", len(ex), "| switches", int((ex != ex.shift()).sum() - 1))
exs = exposure(False).loc[S:END]; print("S5b: months at 50%:", int((exs < 1).sum()), "| switches", int((exs != exs.shift()).sum() - 1))
spells = (ex != ex.shift()).cumsum()[ex < 1]; print("V5 half spells:", [(g.index[0].strftime("%Y-%m"), len(g)) for _, g in ex[ex < 1].groupby(spells)])
cal = pd.DataFrame({"V5": E.calendar(out["V5 3 sectors, 50% cut, fast re-entry"][0]), "S5c": E.calendar(out["S5c always invested"][0]), "V4c": E.calendar(v4c), "WV": E.calendar(wv), "MW": E.calendar(mw)})
print(cal.round(3).to_string())
# out-of-universe: S&P 500 sectors
SP = {"EN": "S5ENRS", "MT": "S5MATR", "IN": "S5INDU", "CD": "S5COND", "CS": "S5CONS", "HC": "S5HLTH", "FN": "S5FINL", "IT": "S5INFT", "TC": "S5TELS", "UT": "S5UTIL", "RE": "S5RLST"}
zsp = E.value_score(E.VS, SP)
rsp = pd.DataFrame({c: E.col(E.VS, t).pct_change() + (E.col(E.VS, t, "EQY_DVD_YLD_12M").ffill() / 100).shift(1) * 0.85 / 12 for c, t in SP.items()})
ok = rsp.notna().sum(); print("S&P sector coverage starts:", {c: rsp[c].dropna().index[0].strftime("%Y-%m") for c in rsp})
sp_v5 = build(z=zsp, rets=rsp); sp_c = build(z=zsp, rets=rsp, mode="none")
ewsp = rsp.loc[S:END].mean(axis=1) - 0.0025 / 12
usa = E.col(E.RT, "NDDUUS").pct_change().loc[S:END]
rows = [row("OOU V5 on S&P 500 sectors", sp_v5[0], sp_v5[1], sp_v5[2]), row("OOU always invested", sp_c[0], sp_c[1], sp_c[2]),
        row("Equal-weight S&P 500 sectors", ewsp), row("MSCI USA Net EUR", usa)]
print(pd.DataFrame(rows).set_index("name")[["cagr", "vol", "sharpe", "mdd", "d_cagr", "v_cagr"]].to_string(float_format=lambda x: f"{x:.3f}"))
pd.to_pickle({k: v[0] for k, v in out.items()} | {"sp_v5": sp_v5[0], "sp_c": sp_c[0], "exposure": exposure(True), "nred": nred, "fast": fast}, E.D + "/round5.pkl")
