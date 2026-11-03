"""Round 3 preview (3 Nov 2026): value + momentum, small pre-declared grid.
Selection on 2006-2015 only; 2016-2026 reported as out-of-sample. Every trial is printed (no hidden tries)."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
import engine as E
rc, rs = E.country_returns(), E.sector_returns()
vc = E.value_score(E.VP, {k: v[0] for k, v in E.COUNTRIES.items()})
vs = E.value_score(E.VS, E.SECTORS)
def mom(r): return E.momentum(r, 12, skip=1)            # 12-1 momentum (Jegadeesh-Titman / Asness et al.)
world = E.BENCH.loc["2006-01-31":"2026-09-30"] - 0.0012 / 12
rows = []
for wm, n, ov, core in itertools.product([0.0, 0.5], [3, 4], [False, True], [0.0, 0.5]):
    sc = E.xs_z(vc) * (1 - wm) + E.xs_z(mom(rc)).reindex_like(vc) * wm
    ss = E.xs_z(vs) * (1 - wm) + E.xs_z(mom(rs)).reindex_like(vs) * wm
    W, R = E.value_rotation_custom(sc, ss, rc, rs, n=n)
    if ov: W = E.overlay_sma(W)
    r, to, _ = E.run(W, R, cost=0.001, ter=0.0025, start="2006-01-31")
    r = (1 - core) * r + core * world.reindex(r.index)
    f, d, v = E.stats(r), E.stats(r.loc[:"2015-12-31"]), E.stats(r.loc["2016-01-31":])
    rows.append(dict(mom_w=wm, n=n, overlay=ov, core=core, cagr=f["cagr"], vol=f["vol"], sharpe=f["sharpe"], mdd=f["mdd"],
                     d_sharpe=d["sharpe"], v_sharpe=v["sharpe"], v_cagr=v["cagr"], turnover=to.mean() * 12 * (1 - core)))
b = world; fb, db, vb = E.stats(b), E.stats(b.loc[:"2015-12-31"]), E.stats(b.loc["2016-01-31":])
df = pd.DataFrame(rows).sort_values("d_sharpe", ascending=False)
pd.set_option("display.width", 220)
print(df.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("MSCI World ETF", {k: round(x, 3) for k, x in [("cagr", fb["cagr"]), ("sharpe", fb["sharpe"]), ("mdd", fb["mdd"]), ("d", db["sharpe"]), ("v", vb["sharpe"]), ("v_cagr", vb["cagr"])]})
# rank IC of 12-1 momentum vs next-12m return, to check the story holds at this level
for nm, r in (("countries", rc), ("sectors", rs)):
    fwd = (1 + r).rolling(12).apply(np.prod, raw=True).shift(-12) - 1
    m = mom(r)
    ic = pd.Series({t: m.loc[t].corr(fwd.loc[t], method="spearman") for t in m.index if m.loc[t].notna().sum() > 5 and fwd.loc[t].notna().sum() > 5})
    print("IC momentum 12m", nm, round(ic.loc["2006":].mean(), 3))
