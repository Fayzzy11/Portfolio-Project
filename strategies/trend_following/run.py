"""Run the full backtest and write every result to results/.

Usage (from the project root):
    python -m strategies.trend_following.run data/Extract_Trend_YYYYMMDD_values.xlsx
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from common.data import load_bloomberg_extract, excess_returns
from common import metrics as M
from . import config as C
from . import engine as E

warnings.filterwarnings("ignore")
OUT = Path(__file__).parent / "results"
PERIODS = {"full": (C.START, C.END), "design": (C.START, C.SPLIT), "validation": ("2016-01-01", C.END)}
CRISES = {
    "Global financial crisis": ("2007-10-09", "2009-03-09"),
    "European debt crisis": ("2011-05-02", "2011-10-03"),
    "China / oil": ("2015-08-01", "2016-02-11"),
    "Late-2018 sell-off": ("2018-10-01", "2018-12-24"),
    "Covid crash": ("2020-02-19", "2020-03-23"),
    "2022 (inflation, rate hikes)": ("2022-01-01", "2022-12-31"),
}
VALUE = "MSCI World Value (EUR)"
WORLD = "MSCI World (EUR)"
COMBO = "70/30 value/trend"
COMBO_ETF = "70/30 value/ETF"


def clean(x):
    """Make results JSON-serialisable (NaN -> null, numpy -> Python, 6 decimals)."""
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else round(float(x), 6)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, pd.Timestamp):
        return str(x.date())
    return x


def main(path):
    S = load_bloomberg_extract(path)
    rf = S[C.RF_EUR]
    value_eur = (S[C.VALUE_PROXY] / S[C.EURUSD].reindex(S[C.VALUE_PROXY].index).ffill()).dropna()
    bench = {
        VALUE: excess_returns(value_eur, rf).loc[C.START:C.END],
        WORLD: excess_returns(S[C.WORLD], rf).loc[C.START:C.END],
    }
    R = E.daily_returns(S, C.FUTURES)

    runs = {name: E.run_futures(R, L) for name, L in C.VARIANTS.items()}
    runs[C.ETF_VARIANT] = E.run_etf(R[C.ETF_UNIVERSE], C.VARIANTS[C.REFERENCE_VARIANT])
    ref, etf = C.REFERENCE_VARIANT, C.ETF_VARIANT
    series = {k: v["net"] for k, v in runs.items()} | bench
    val = bench[VALUE]

    res = {"meta": {"start": C.START, "end": C.END, "split": C.SPLIT, "reference": ref, "etf": etf,
                    "vol_target": C.VOL_TARGET, "n_markets": len(C.FUTURES), "n_markets_etf": len(C.ETF_UNIVERSE)}}

    # 1. statistics by period
    res["stats"] = {p: {k: M.stats(s.loc[a:b]) for k, s in series.items()} for p, (a, b) in PERIODS.items()}

    # 2. calendar-year returns
    combo = 0.7 * val + 0.3 * runs[ref]["net"].reindex(val.index).fillna(0)
    combo_etf = 0.7 * val + 0.3 * runs[etf]["net"].reindex(val.index).fillna(0)
    all_series = series | {COMBO: combo, COMBO_ETF: combo_etf}
    yearly = pd.DataFrame({k: M.annual(s) for k, s in all_series.items()})
    res["annual"] = {"years": [str(i.year) for i in yearly.index],
                     "series": {k: yearly[k].tolist() for k in yearly}}

    # 3. cumulative value and drawdowns (month end)
    nav_df = pd.DataFrame({k: M.nav(M.monthly(s)) * 100 for k, s in all_series.items()})
    res["nav"] = {"dates": [str(d.date()) for d in nav_df.index], "series": {k: nav_df[k].tolist() for k in nav_df}}
    dd_df = nav_df / nav_df.cummax() - 1
    res["drawdown"] = {"dates": res["nav"]["dates"], "series": {k: dd_df[k].tolist() for k in dd_df}}

    # 4. correlations
    mon = pd.DataFrame({k: M.monthly(s) for k, s in series.items()}).dropna()
    res["monthly_correlation"] = {p: mon.loc[a:b].corr().to_dict() for p, (a, b) in PERIODS.items()}
    roll_corr = {k: mon[k].rolling(36).corr(mon[VALUE]) for k in [ref, etf]}
    roll_sr = {k: mon[k].rolling(36).mean() / mon[k].rolling(36).std() * np.sqrt(12) for k in [ref, etf, VALUE]}
    res["rolling_36m"] = {"dates": [str(d.date()) for d in mon.index],
                          "correlation": {k: v.tolist() for k, v in roll_corr.items()},
                          "sharpe": {k: v.tolist() for k, v in roll_sr.items()}}

    # 5. conditional behaviour: when value does badly / well
    v = mon[VALUE]
    q10, q90 = v.quantile(0.10), v.quantile(0.90)
    res["conditional"] = {k: {
        "beta_vs_value": np.cov(mon[k], v)[0, 1] / v.var(),
        "avg_ret_value_worst_10pct": mon[k][v <= q10].mean(),
        "avg_ret_value_best_10pct": mon[k][v >= q90].mean(),
        "avg_ret_value_down": mon[k][v < 0].mean(),
        "avg_ret_value_up": mon[k][v > 0].mean(),
        "value_avg_worst_10pct": v[v <= q10].mean(),
        "corr_value_down": mon[k][v < 0].corr(v[v < 0]),
        "corr_value_up": mon[k][v > 0].corr(v[v > 0]),
        "n_months": int(len(mon)),
    } for k in [ref, etf]}

    # 6. crises
    res["crises"] = {c: {k: float((1 + s.loc[a:b]).prod() - 1) for k, s in series.items()} | {"period": f"{a} → {b}"}
                     for c, (a, b) in CRISES.items()}

    # 7. attribution by asset class and by market
    attrib = {}
    for k in [ref, etf]:
        contrib, Wd = runs[k]["contrib"], runs[k]["Wd"]
        markets = {t: {
            "label": C.LABELS[t], "asset_class": C.FUTURES[t][0],
            "annual_contribution": contrib[t].mean() * M.ANN,
            "contribution_sharpe": M.sharpe(contrib[t]) if contrib[t].std() > 0 else None,
            "avg_abs_weight": Wd[t].abs().mean(),
            "pct_time_long": float((Wd[t] > 0).mean()),
            "pct_time_short": float((Wd[t] < 0).mean()),
        } for t in contrib.columns}
        classes = {}
        for cl in sorted({C.FUTURES[t][0] for t in contrib.columns}):
            cc = contrib[[t for t in contrib.columns if C.FUTURES[t][0] == cl]].sum(axis=1)
            classes[cl] = {"annual_contribution": cc.mean() * M.ANN, "sharpe": M.sharpe(cc),
                           "annual_contribution_validation": cc.loc["2016":].mean() * M.ANN}
        attrib[k] = {"markets": markets, "classes": classes,
                     "avg_gross_leverage": Wd.abs().sum(axis=1).mean(),
                     "avg_net_leverage": Wd.sum(axis=1).mean(),
                     "annual_costs": (runs[k]["gross"] - runs[k]["net"]).mean() * M.ANN,
                     "annual_turnover": runs[k]["W"].diff().abs().sum(axis=1).mean() * 12}
    res["attribution"] = attrib

    # 8. cost sensitivity (reference version)
    g = runs[ref]["gross"]
    cost = g - runs[ref]["net"]
    res["cost_sensitivity"] = {f"x{m}": {p: M.sharpe((g - m * cost).loc[a:b]) for p, (a, b) in PERIODS.items()}
                               for m in [0, 1, 2, 3]}

    # 9. value / trend combinations
    comb = {}
    for k in [ref, etf]:
        t = runs[k]["net"].reindex(val.index).fillna(0)
        rows = []
        for wv in np.arange(0, 1.01, 0.1):
            c = wv * val + (1 - wv) * t
            row = {"value_weight": round(float(wv), 1)}
            for p, (a, b) in PERIODS.items():
                st = M.stats(c.loc[a:b])
                row[p] = {x: st[x] for x in ["annual_return", "volatility", "sharpe", "max_drawdown"]}
            rows.append(row)
        comb[k] = rows
    res["combinations"] = comb

    # 10. latest target positions — illustrates the monthly routine
    vol = E.ewma_vol(R)
    me = E.month_ends(R.index)
    last = {}
    for k in [ref, etf]:
        W = runs[k]["W"]
        d = W.index[-1]
        sig_ref = E.signals(R, C.VARIANTS[ref], me).loc[d]
        last[k] = {"date": str(d.date()), "positions": {
            t: {"label": C.LABELS[t], "asset_class": C.FUTURES[t][0], "weight": W.loc[d, t],
                "signal": sig_ref.get(t), "ewma_vol": vol.loc[d, t]} for t in W.columns}}
    res["latest_positions"] = last

    # 11. worked example at the last rebalancing (reference version)
    d = runs[ref]["W"].index[-1]
    parts = {L: E.signals(R, [L], me).loc[d] for L in [3, 6, 12]}
    blend = E.signals(R, C.VARIANTS[ref], me).loc[d]
    n_eligible = int(blend.dropna().shape[0])
    raw = (blend / vol.loc[d] / n_eligible).dropna()
    cov = R.loc[:d].iloc[-C.COV_WINDOW:][raw.index].cov(min_periods=120).fillna(0) * M.ANN
    pvol = float(np.sqrt(raw.values @ cov.values @ raw.values))
    res["worked_example"] = {
        "date": str(d.date()), "n_markets": n_eligible, "raw_ex_ante_vol": pvol,
        "scale_factor": C.VOL_TARGET / pvol, "final_gross_leverage": float(runs[ref]["W"].loc[d].abs().sum()),
        "markets": {t: {"label": C.LABELS[t], "s3": parts[3].get(t), "s6": parts[6].get(t), "s12": parts[12].get(t),
                        "signal": blend[t], "vol": vol.loc[d, t], "raw_weight": raw[t],
                        "final_weight": runs[ref]["W"].loc[d, t]} for t in raw.index}}

    # 12. contract size vs target positions
    fx = {"USD": S[C.EURUSD].iloc[-1], "GBP": S[C.EURGBP].iloc[-1], "EUR": 1.0}
    Wd_ref = runs[ref]["Wd"]
    recent = Wd_ref.loc[Wd_ref.index[-1] - pd.DateOffset(months=24):].abs().mean()
    ctr = {}
    for t, (name, mult, fac, ccy) in C.CONTRACTS.items():
        notional = mult if ccy == "EUR_FIXED" else S[t].iloc[-1] * fac * mult / fx[ccy]
        target = recent[t] * C.EXAMPLE_CAPITAL
        ctr[t] = {"label": C.LABELS[t], "contract": name, "notional_eur": notional,
                  "target_position_eur": target, "ratio": notional / target if target > 0 else None}
    res["contracts"] = {"capital": C.EXAMPLE_CAPITAL, "eurusd": fx["USD"], "markets": ctr}

    # 13. data inventory
    res["data_inventory"] = {t: {"start": str(S[t].index[0].date()), "end": str(S[t].index[-1].date()),
                                 "n_points": int(len(S[t]))} for t in S}

    OUT.mkdir(exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(clean(res), ensure_ascii=False, indent=1))
    pd.DataFrame({k: M.monthly(v["net"]) for k, v in runs.items()}).to_csv(
        OUT / "strategy_monthly_returns.csv", float_format="%.6f")
    print("Results written to", OUT)
    return res


if __name__ == "__main__":
    main(sys.argv[1])
