"""Round 4-A (4 Nov 2026): value + trend filters, exactly as pre-registered in PREREG_round4.md (commit 14e2336)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
import engine as E
S, END = "2006-01-31", "2026-09-30"
rc, rs = E.country_returns(), E.sector_returns_tr()
zc = E.value_score(E.VP, {k: v[0] for k, v in E.COUNTRIES.items()})
zs = E.value_score(E.VS, E.SECTORS)
valid = (zc.notna().sum(axis=1) >= 10) & (zs.notna().sum(axis=1) >= 8)
bond = E.col(E.RT, "LEATTREU").pct_change().rename("BOND")
R = pd.concat([rc.add_prefix("C_"), rs.add_prefix("S_"), bond], axis=1)
idx = (1 + R.fillna(0)).cumprod()
above = idx > idx.rolling(10).mean()                       # each line vs its own 10-month average
mkt = E.col(E.MK, "MSDEWIN Index"); mkt_on = (mkt > mkt.rolling(10).mean())


def picks(z, n=4, keep=None):
    """Monthly holdings; with keep, a held line stays until it falls out of the `keep` cheapest."""
    held, out = [], {}
    for t in z.index:
        s = z.loc[t].dropna()
        if len(s) < n:
            out[t] = held; continue
        rank = s.rank(ascending=False)
        if keep:
            held = [h for h in held if h in rank and rank[h] <= keep]
            for c in rank.sort_values().index:
                if len(held) >= n: break
                if c not in held: held.append(c)
        else:
            held = list(s.nlargest(n).index)
        out[t] = list(held)
    return out


def weights(pc, ps):
    rows = {}
    for t in zc.index:
        w = {}
        for p, lst in (("C_", pc.get(t, [])), ("S_", ps.get(t, []))):
            for c in lst: w[p + c] = 0.5 / len(lst)
        rows[t] = w
    return pd.DataFrame(rows).T.reindex(zc.index).fillna(0.0)[valid]


def market_filter(W, riskoff="cash"):
    on = mkt_on.reindex(W.index).fillna(True).astype(float)
    W = W.mul(on, axis=0)
    if riskoff == "bonds":
        W["BOND"] = 1 - on
    return W


def tranches(W, n=12):
    """Average of the last n monthly formations: each formation is held n months."""
    return W.rolling(n, min_periods=1).mean()


base = weights(picks(zc), picks(zs))
buf = weights(picks(zc, keep=6), picks(zs, keep=6))
out = {
    "V1 rules (reference)": base,
    "V6 rules + market filter (reference)": market_filter(base),
    "V4b per-line filter": base.where(above.reindex(base.index).reindex(columns=base.columns).fillna(True), 0.0),
    "V4c buffer + market filter": market_filter(buf),
    "V4d 12 tranches + market filter": market_filter(tranches(base)),
    "V4e 12 tranches + filter, bonds risk-off": market_filter(tranches(base), "bonds"),
}
world = E.BENCH.loc[S:END] - 0.0012 / 12
rows, series = [], {}
for nm, W in out.items():
    r, to, w = E.run(W, R, 0.001, 0.0025, S)
    series[nm] = r
    f, d, v = E.stats(r), E.stats(r.loc[:"2015-12-31"]), E.stats(r.loc["2016-01-31":])
    rows.append(dict(name=nm, cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"], d_cagr=d["cagr"], v_cagr=v["cagr"],
                     d_sh=d["sharpe"], v_sh=v["sharpe"], turnover=to.mean() * 12, invested=w.drop(columns="BOND", errors="ignore").sum(axis=1).mean()))
f, d, v = E.stats(world), E.stats(world.loc[:"2015-12-31"]), E.stats(world.loc["2016-01-31":])
rows.append(dict(name="MSCI World ETF", cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"], d_cagr=d["cagr"], v_cagr=v["cagr"], d_sh=d["sharpe"], v_sh=v["sharpe"]))
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).set_index("name").to_string(float_format=lambda x: f"{x:.3f}"))
# how the market filter behaves
on = mkt_on.loc[S:END]
sw = on.astype(int).diff().abs().sum()
print("market filter: months risk-off", int((~on).sum()), "of", len(on), "| switches", int(sw))
spells = (on != on.shift()).cumsum()[~on]; print("risk-off spells:", [(g.index[0].strftime("%Y-%m"), len(g)) for _, g in on[~on].groupby(spells)])
print("calendar MSCI vs V6 vs V4d:")
cal = pd.DataFrame({k: E.calendar(series[k]) for k in ["V6 rules + market filter (reference)", "V4d 12 tranches + market filter"]}); cal["MSCI"] = E.calendar(world)
print(cal.loc[2006:].round(3).to_string())
pd.to_pickle(series, os.path.join(E.D, "round4_value.pkl"))
