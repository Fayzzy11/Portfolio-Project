"""Round 6 (4 Nov 2026): ETF core V7, as pre-registered in PREREG_round6.md."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np, engine as E
S, END, MID = "2006-01-31", "2026-09-30", "2015-12-31"
wv = E.world_value().loc[S:END]; mw = E.BENCH.loc[S:END]
rows = []
def row(nm, r):
    f, d, v = E.stats(r), E.stats(r.loc[:MID]), E.stats(r.loc["2016-01-31":]); ex = r - wv.reindex(r.index)
    return dict(name=nm, cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"], d_cagr=d["cagr"], v_cagr=v["cagr"], d_sh=d["sharpe"], v_sh=v["sharpe"],
                ahead=int(((E.calendar(r) - E.calendar(wv.reindex(r.index))) > 0).sum()), t=ex.mean() / ex.std() * np.sqrt(len(ex)) if ex.std() > 0 else np.nan)
W, R, expo, rs = E.value_core(); r7, to, w = E.run(W, R, 0.001, 0.0025, S)
W2, _, expo2, _ = E.value_core(fast_reentry=False); r7s, _, _ = E.run(W2, R, 0.001, 0.0025, S)
r4c = pd.read_pickle(E.D + "/v4c_full.pkl")["r"]
for nm, r in (("V7 core (fast re-entry)", r7), ("V7 without fast re-entry", r7s), ("V4c (100% cash rule)", r4c), ("MSCI World Value", wv), ("MSCI World", mw)):
    rows.append(row(nm, r))
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).set_index("name").to_string(float_format=lambda x: f"{x:.3f}"))
e = expo.loc[S:END]; print("months at 50%", int((e < 1).sum()), "of", len(e), "switches", int((e != e.shift()).sum() - 1), "turnover", round(to.mean() * 12, 2))
print("calendar V7 vs WV:", {y: (round(a, 3), round(b, 3)) for y, a, b in zip(E.calendar(r7).index, E.calendar(r7), E.calendar(wv))})
