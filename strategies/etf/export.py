"""Export the official value strategy (V4c, adopted 4 Nov 2026) and every value variant tested, for the site.
Writes site/data/etf_strategies.json (aggregated results only: no raw Bloomberg data)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
import engine as E
HERE = os.path.dirname(os.path.abspath(__file__))
S, END, MID = "2006-01-31", "2026-09-30", "2015-12-31"


def f(x):
    return float(x) if isinstance(x, (float, np.floating, int, np.integer)) and not isinstance(x, bool) else x


def nav(r): return [round(float(x), 5) for x in (1 + r).cumprod()]


def pack(r, bench, b2=None):
    b = bench.reindex(r.index)
    out = dict(dates=[d.strftime("%Y-%m") for d in r.index], nav=nav(r), bench=nav(b), bench_name=bench.name,
               stats={k: f(v) for k, v in E.stats(r, b).items() if v is not None}, bench_stats={k: f(v) for k, v in E.stats(b).items()},
               calendar={int(k): float(v) for k, v in E.calendar(r).items()}, bench_calendar={int(k): float(v) for k, v in E.calendar(b).items()},
               halves={"design": {k: f(v) for k, v in E.stats(r.loc[:MID], b.loc[:MID]).items() if v is not None},
                       "valid": {k: f(v) for k, v in E.stats(r.loc["2016-01-31":], b.loc["2016-01-31":]).items() if v is not None},
                       "bench_design": {k: f(v) for k, v in E.stats(b.loc[:MID]).items()}, "bench_valid": {k: f(v) for k, v in E.stats(b.loc["2016-01-31":]).items()}})
    if b2 is not None:
        b2 = b2.reindex(r.index)
        out.update(bench2=nav(b2), bench2_name=b2.name, bench2_stats={k: f(v) for k, v in E.stats(b2).items()},
                   bench2_calendar={int(k): float(v) for k, v in E.calendar(b2).items()})
    return out


world = E.BENCH.loc[S:END]
wv = E.world_value()
bench, bench2 = (wv.loc[S:END], world) if wv is not None else (world, None)

W, R, expo, rs = E.value_core()          # official ETF core V7 (4 Nov 2026): V4c selection + 50% de-risking
on = expo >= 1
zc, zs = E.value_v4c(timing=False)[3:5]
r, to, wn = E.run(W, R, 0.001, 0.0025, S)
res = {"value": pack(r, bench, bench2)}
v = res["value"]
v["turnover"] = float(to.mean() * 12)
v["risk_off_months"] = int((~on.loc[S:END]).sum()); v["months"] = int(len(on.loc[S:END]))
v["switches"] = int(on.loc[S:END].astype(int).diff().abs().sum())
v["invested_avg"] = float(wn.sum(axis=1).mean())
v["line_changes_per_year"] = float(((W > 0).astype(int).diff().abs().sum(axis=1) / 2).loc[S:END].mean() * 12)
last = W.iloc[-1]
nr = rs[["trend", "credit", "breadth"]].iloc[-1]
v["holdings"] = {"date": W.index[-1].strftime("%Y-%m"), "risk_on": bool(on.iloc[-1]), "exposure": float(expo.iloc[-1]),
                 "lines": [k for k, x in last.items() if x > 0],
                 "selection": [k for k, x in E.value_v4c(timing=False)[0].iloc[-1].items() if x > 0],
                 "indicators": {k: bool(nr[k]) for k in ("trend", "credit", "breadth")},
                 "fast": bool(rs["fast"].iloc[-1]), "breadth_share": float(rs["breadth_share"].iloc[-1])}

# every value version tested (rounds 1-4), same period
cands = pd.read_pickle(os.path.join(E.D, "cands.pkl")); r2 = pd.read_pickle(os.path.join(E.D, "round2.pkl"))
r3 = pd.read_pickle(os.path.join(E.D, "round3.pkl")); r4 = pd.read_pickle(os.path.join(E.D, "round4_value.pkl"))
versions = [
    ("V1 Rules (validated 30 Oct)", cands["V1 Rules (validated)"][0], "pre"),
    ("V6 Rules + market trend filter", cands["V6 Rules + market trend overlay (10m SMA)"][0], "post"),
    ("VB 50% MSCI World + 50% V6", r2["VB 50% MSCI World ETF + 50% rotation with overlay"], "pre"),
    ("V3 Cap-weighted world, value tilt", r3["V3-core Tilted World (tilt 0.5)"], "pre"),
    ("V4b Per-line trend filter", r4["V4b per-line filter"], "pre"),
    ("V4c Buffer + 100% cash trend filter", E.run(E.value_v4c()[0], R, 0.001, 0.0025, S)[0], "pre"),
    ("V5 3 sectors, 50% de-risking, fast re-entry", pd.read_pickle(os.path.join(E.D, "round5.pkl"))["V5 3 sectors, 50% cut, fast re-entry"], "pre"),
    ("V7 ETF core: V4c selection + 50% de-risking (official)", r, "pre"),
    ("V4d 12 tranches + market trend filter", r4["V4d 12 tranches + market filter"], "pre"),
    ("V4e 12 tranches + filter, bonds risk-off", r4["V4e 12 tranches + filter, bonds risk-off"], "pre"),
    ("MSCI World Net EUR", world, "bench"),
]
if wv is not None: versions.append(("MSCI World Value Net EUR", wv.loc[S:END], "bench"))
rows = []
for nm, s, kind in versions:
    s = s.loc[S:END].dropna(); a, d, vv = E.stats(s), E.stats(s.loc[:MID]), E.stats(s.loc["2016-01-31":])
    rows.append(dict(name=nm, kind=kind, cagr=f(a["cagr"]), vol=f(a["vol"]), sharpe=f(a["sharpe"]), mdd=f(a["mdd"]), design_cagr=f(d["cagr"]),
                     design_sharpe=f(d["sharpe"]), valid_cagr=f(vv["cagr"]), valid_sharpe=f(vv["sharpe"])))
res["variants"] = rows
res["signal"] = {"ic12_countries": -0.046, "ic12_sectors": -0.026}
json.dump(res, open(os.path.join(HERE, "..", "..", "site", "data", "etf_strategies.json"), "w"))
# private files for the note and the Excel (not published)
pd.to_pickle(dict(r=r, to=to, W=W, wn=wn, on=on, zc=zc, zs=zs, R=R, world=world, wv=wv), os.path.join(E.D, "v7_full.pkl"))
print("V7", round(v["stats"]["cagr"], 4), round(v["stats"]["sharpe"], 3), round(v["stats"]["mdd"], 3), "| bench", bench.name,
      "| risk-off", v["risk_off_months"], "/", v["months"], "switches", v["switches"], "| line changes/yr", round(v["line_changes_per_year"], 1), "|", v["holdings"])

# Horus Smart Beta converted to EUR (Horus AM publishes USD), for the mixed portfolio in the tracker
h = json.load(open(os.path.join(HERE, "..", "..", "site", "data", "horus_smart_beta.json")))
idx = pd.period_range(h["start"], periods=len(h["r_p3"]), freq="M").to_timestamp("M")
fx = E.col(E.MK, "EURUSD Curncy").pct_change().reindex(idx)          # USD per EUR
to_eur = lambda x: list(np.round(((1 + pd.Series(x, index=idx)) / (1 + fx) - 1).values, 6))
res["horus_eur"] = {"dates": [d.strftime("%Y-%m") for d in idx], "r": to_eur(h["r_p3"]), "b": to_eur(h["r_bench"])}
json.dump(res, open(os.path.join(HERE, "..", "..", "site", "data", "etf_strategies.json"), "w"))
print("horus_eur", res["horus_eur"]["dates"][0], res["horus_eur"]["dates"][-1], len(res["horus_eur"]["r"]))
