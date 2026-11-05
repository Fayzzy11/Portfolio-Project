"""Export the official value strategy (70% ETF core V7 + 30% stock satellite v2, decided 4-5 Nov 2026) for the site.
Writes site/data/etf_strategies.json — aggregated results and holdings only, no raw Bloomberg series."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
import engine as E
HERE = os.path.dirname(os.path.abspath(__file__))
O = pd.read_pickle(os.path.join(E.D, "official.pkl"))
sat, core, combo = O["sat"], O["core"], O["combo"]
IDX = combo.index; S, END, MID = IDX[0], IDX[-1], "2015-12-31"
wv = E.world_value().reindex(IDX).rename("MSCI World Value Net EUR"); mw = E.BENCH.reindex(IDX).rename("MSCI World Net EUR")


def f(x): return float(x) if isinstance(x, (float, np.floating, int, np.integer)) and not isinstance(x, bool) else x
def nav(r): return [round(float(x), 5) for x in (1 + r).cumprod()]
def st(r, b=None): return {k: f(v) for k, v in E.stats(r, b).items() if v is not None}
def halves(r, b): return {"design": st(r.loc[:MID], b.loc[:MID]), "valid": st(r.loc["2016-01-31":], b.loc["2016-01-31":]),
                          "bench_design": st(b.loc[:MID]), "bench_valid": st(b.loc["2016-01-31":])}
def tstat(r, b): e = r - b; return f(e.mean() / e.std() * np.sqrt(len(e)))


v = dict(dates=[d.strftime("%Y-%m") for d in IDX], nav=nav(combo), bench=nav(wv), bench_name=wv.name, bench2=nav(mw), bench2_name=mw.name,
         stats=st(combo, wv), bench_stats=st(wv), bench2_stats=st(mw), calendar={int(k): float(x) for k, x in E.calendar(combo).items()},
         bench_calendar={int(k): float(x) for k, x in E.calendar(wv).items()}, bench2_calendar={int(k): float(x) for k, x in E.calendar(mw).items()},
         halves=halves(combo, wv), t_vs_bench=tstat(combo, wv),
         parts={"core": dict(stats=st(core.loc[IDX], wv), halves=halves(core.loc[IDX], wv), t=tstat(core.loc[IDX], wv), nav=nav(core.loc[IDX])),
                "satellite": dict(stats=st(sat.loc[IDX], wv), halves=halves(sat.loc[IDX], wv), t=tstat(sat.loc[IDX], wv), nav=nav(sat.loc[IDX]),
                                  turnover=f(O["to"].mean() * 12))})
expo = O["expo"]; rs = O["rs"]; on = expo.reindex(IDX)
v["turnover_core"] = f(O["core_to"].reindex(IDX).mean() * 12)
v["turnover"] = f(0.7 * v["turnover_core"] + 0.3 * O["to"].mean() * 12)
v["risk_off_months"] = int((expo.shift(1).reindex(IDX) < 1).sum()); v["months"] = len(IDX)
v["switches"] = int((expo.reindex(IDX) != expo.reindex(IDX).shift()).sum() - 1)
v["invested_avg"] = f(expo.shift(1).reindex(IDX).fillna(1).mean())
# portfolio decided at the last date (end of June 2026), held in July 2026
D = END
Wsel = E.value_v4c(timing=False)[0].loc[:D].iloc[-1]
nr = rs[["trend", "credit", "breadth"]].loc[:D].iloc[-1]
lg = O["logs"][max(k for k in O["logs"] if k <= D)]
def nice(n):
    up = {"BNP", "AG", "SA", "NV", "SE", "SPA", "ASA", "AB", "UK", "US", "NTT", "BASF", "ENI", "HSBC", "BP", "RWE", "ING", "AXA", "ABB", "UBS"}
    w = []
    for x in n.replace("-REG", "").split():
        u = x.upper().strip(".,")
        w.append("SpA" if u == "SPA" else "plc" if u == "PLC" else u if u in up else "-".join(y.capitalize() for y in x.split("-")))
    return " ".join(w)
PIT = {p["bbg"]: p["name"] for p in json.load(open(os.path.join(HERE, "..", "..", "site", "data", "pitches.json")))}
v["holdings"] = {"date": D.strftime("%Y-%m"), "exposure": f(expo.loc[:D].iloc[-1]), "risk_on": bool(expo.loc[:D].iloc[-1] >= 1),
                 "selection": [k for k, x in Wsel.items() if x > 0], "indicators": {k: bool(nr[k]) for k in ("trend", "credit", "breadth")},
                 "satellite": [dict(ticker=t, name=nice(r["name"]), sector=r["sector"], country=r["cty"], score_pct=f(r["score_pct"]),
                                    pitch=PIT.get(t.replace(" Equity", "")) or PIT.get(t)) for t, r in lg.iterrows()]}
res = {"value": v}
# major versions only (the changes discussed with Noah), same period
r1 = E.run(E.value_rotation()[0], E.value_rotation()[1], 0.001, 0.0025, "2006-01-31")[0]
r4c = E.run(E.value_v4c()[0], E.value_v4c()[1], 0.001, 0.0025, "2006-01-31")[0]
r5 = pd.read_pickle(os.path.join(E.D, "round5.pkl"))["V5 3 sectors, 50% cut, fast re-entry"]
versions = [("V1 Rules of 30 Oct: 4 cheapest countries + 4 sectors", r1, "30 Oct"), ("V4c + holding buffer and 100% cash trend filter", r4c, "4 Nov"),
            ("V5 3 sectors only, 50% de-risking", r5, "4 Nov"), ("V7 ETF core: V4c selection, 50% de-risking", core, "4 Nov"),
            ("Satellite: 8 cheapest stocks in the core's countries and sectors", sat, "5 Nov"),
            ("Strategy: 70% core + 30% satellite (official)", combo, "5 Nov"), ("MSCI World Value Net EUR", wv, "bench"), ("MSCI World Net EUR", mw, "bench")]
rows = []
for nm, s_, when in versions:
    s_ = s_.reindex(IDX); a, d_, vv = E.stats(s_), E.stats(s_.loc[:MID]), E.stats(s_.loc["2016-01-31":])
    rows.append(dict(name=nm, when=when, cagr=f(a["cagr"]), vol=f(a["vol"]), sharpe=f(a["sharpe"]), mdd=f(a["mdd"]),
                     design_cagr=f(d_["cagr"]), design_sharpe=f(d_["sharpe"]), valid_cagr=f(vv["cagr"]), valid_sharpe=f(vv["sharpe"])))
res["variants"] = rows
# Horus in EUR and the combination with the value strategy
h = json.load(open(os.path.join(HERE, "..", "..", "site", "data", "horus_smart_beta.json")))
hidx = pd.period_range(h["start"], periods=len(h["r_p3"]), freq="M").to_timestamp("M")
fx = E.col(E.MK, "EURUSD Curncy").pct_change().reindex(hidx)
heur = (1 + pd.Series(h["r_p3"], index=hidx)) / (1 + fx) - 1; beur = (1 + pd.Series(h["r_bench"], index=hidx)) / (1 + fx) - 1
res["horus_eur"] = {"dates": [d.strftime("%Y-%m") for d in hidx], "r": list(np.round(heur.values, 6)), "b": list(np.round(beur.values, 6))}
# Currency-hedged Horus: dollar return minus the dollar cash rate plus the euro cash rate (1-month forward hedge, covered interest parity)
ceur = E.cash_monthly().reindex(hidx)
hhed = pd.Series(h["r_p3"], index=hidx) - pd.Series(h["rf"], index=hidx) + ceur
bhed = pd.Series(h["r_bench"], index=hidx) - pd.Series(h["rf"], index=hidx) + ceur
res["horus_eur_hedged"] = {"dates": [d.strftime("%Y-%m") for d in hidx], "r": list(np.round(hhed.values, 6)), "b": list(np.round(bhed.values, 6))}
ci = IDX.intersection(hidx)


def combine(hr):
    mix = []
    for w in (1.0, 0.7, 0.5, 0.3, 0.0):
        r = w * combo.loc[ci] + (1 - w) * hr.loc[ci]; a = E.stats(r)
        mix.append(dict(value=w, cagr=f(a["cagr"]), vol=f(a["vol"]), sharpe=f(a["sharpe"]), mdd=f(a["mdd"])))
    down = mw.reindex(ci) < 0
    return {"start": ci[0].strftime("%Y-%m"), "end": ci[-1].strftime("%Y-%m"), "corr": f(combo.loc[ci].corr(hr.loc[ci])),
            "corr_bear": f(combo.loc[ci][down].corr(hr.loc[ci][down])), "mixes": mix,
            "corr_rolling_36_min": f(combo.loc[ci].rolling(36).corr(hr.loc[ci]).min()), "corr_rolling_36_max": f(combo.loc[ci].rolling(36).corr(hr.loc[ci]).max())}


res["combination"] = combine(hhed)            # headline: strategy performance only (Horus hedged into euros)
res["combination_unhedged"] = combine(heur)   # what an unhedged euro investor actually got (includes the dollar)
res["signal"] = {"ic12_countries": -0.046, "ic12_sectors": -0.026}
json.dump(res, open(os.path.join(HERE, "..", "..", "site", "data", "etf_strategies.json"), "w"))
print("official", v["dates"][0], v["dates"][-1], round(v["stats"]["cagr"], 4), round(v["stats"]["sharpe"], 3), round(v["stats"]["mdd"], 3), "t", round(v["t_vs_bench"], 2))
for k in ("combination", "combination_unhedged"):
    c = res[k]; print(k, round(c["corr"], 3), round(c["corr_bear"], 3), [(m["value"], round(m["cagr"], 4), round(m["vol"], 4), round(m["sharpe"], 2), round(m["mdd"], 3)) for m in c["mixes"]])
print("holdings", v["holdings"]["exposure"], v["holdings"]["selection"], [(x["name"], x["country"], x["pitch"]) for x in v["holdings"]["satellite"]])
