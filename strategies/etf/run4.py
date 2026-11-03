"""Second round (3 Nov 2026): candidates fixed before testing, parameters from the literature, no tuning."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
import engine as E
pd.set_option("display.width", 220)
out = {}
W, R = E.value_rotation(); v1, _, _ = E.run(W, R, cost=0.001, ter=0.0025, start="2006-01-31")
v6, _, _ = E.run(E.overlay_sma(W), R, cost=0.001, ter=0.0025, start="2006-01-31")
world = E.BENCH.loc["2006-01-31":"2026-09-30"] - 0.0012 / 12          # MSCI World ETF, 0.12% TER
out["V1 Rules (validated)"] = v1
out["V6 Rules + trend overlay"] = v6
out["VA 50% MSCI World ETF + 50% rotation"] = 0.5 * world + 0.5 * v1
out["VB 50% MSCI World ETF + 50% rotation with overlay"] = 0.5 * world + 0.5 * v6
out["MSCI World Net EUR"] = E.BENCH.loc["2006-01-31":"2026-09-30"]
WT, RT = E.trend(); t1, _, _ = E.run(WT, RT, cost=0.001, ter=0.003, start="2001-01-31")
WA, _ = E.trend_class_budget(); ta, toa, wa = E.run(WA, RT, cost=0.001, ter=0.003, start="2001-01-31")
out["T1 Trend rules (validated)"] = t1
out["TA Trend, equal risk per asset class"] = ta
out["60/40 EUR"] = E.sixty_forty().loc["2001-01-31":"2026-09-30"]
out["MSCI World Net EUR (2001)"] = E.BENCH.loc["2001-01-31":"2026-09-30"]
rows = []
for nm, r in out.items():
    r = r.dropna()
    mid = "2015-12-31"
    f, d, v = E.stats(r), E.stats(r.loc[:mid]), E.stats(r.loc["2016-01-31":])
    rows.append(dict(name=nm, start=f["start"], cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"],
                     d_cagr=d["cagr"], d_sharpe=d["sharpe"], v_cagr=v["cagr"], v_sharpe=v["sharpe"],
                     corr_world=r.corr(E.BENCH.reindex(r.index))))
print(pd.DataFrame(rows).set_index("name").to_string(float_format=lambda x: f"{x:.3f}"))
print("TA avg invested", wa.loc["2001":].sum(axis=1).mean().round(2))
pd.to_pickle(out, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "etf", "round2.pkl"))
