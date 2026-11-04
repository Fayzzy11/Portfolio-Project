"""Round 3 (4 Nov 2026), exactly as pre-registered in PREREG_round3.md (commit 3ce4d4f)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
import engine as E
S = "2006-01-31"
world = E.BENCH.loc[S:"2026-09-30"] - 0.0012 / 12
out = {}
W0, R = E.tilted_world(use_tilt=False); out["C0 Cap-weighted, no tilt (control)"] = E.run(W0, R, 0.001, 0.0025, S)
W1, _ = E.tilted_world(0.5); out["V3-core Tilted World (tilt 0.5)"] = E.run(W1, R, 0.001, 0.0025, S)
W2, _ = E.tilted_world(1.0); out["S1 Tilted World, tilt 1.0 (sensitivity)"] = E.run(W2, R, 0.001, 0.0025, S)
out["S2 Tilted World + trend filter (info)"] = E.run(E.overlay_sma(W1), R, 0.001, 0.0025, S)
rows = []
for nm, (r, to, w) in list(out.items()) + [("B MSCI World ETF", (world, None, None))]:
    r = r.dropna(); f, d, v = E.stats(r), E.stats(r.loc[:"2015-12-31"]), E.stats(r.loc["2016-01-31":])
    rows.append(dict(name=nm, cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"], d_cagr=d["cagr"], d_sh=d["sharpe"],
                     v_cagr=v["cagr"], v_sh=v["sharpe"], te=(r - world.reindex(r.index)).std() * 12 ** .5,
                     turnover=(to.mean() * 12 if to is not None else np.nan)))
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).set_index("name").to_string(float_format=lambda x: f"{x:.3f}"))
# what the tilt does today and on average
us = W1["C_US"] / 0.5; print("US weight in country half: avg", round(us.mean(), 3), "last", round(us.iloc[-1], 3), "| cap-weight last", round((W0["C_US"] / 0.5).iloc[-1], 3))
act = (W1 - W0).abs().sum(axis=1) / 2; print("active share avg", round(act.mean(), 3))
pd.to_pickle({k: v[0] for k, v in out.items()}, os.path.join(E.D, "round3.pkl"))
