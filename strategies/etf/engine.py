"""Backtests of the two ETF strategies (rules fixed and validated on 30 Oct 2026, before the data).

Value rotation: 14 countries + 11 MSCI World sectors, monthly, top 4 + top 4 on a time-series value score.
Multi-asset trend: 14 assets, monthly, long/cash on the 3/6/12-month trend blend, risk parity, 10% vol target.
"""
import numpy as np
import pandas as pd

import os
from pathlib import Path
D = os.environ.get("ETF_DATA", str(Path(__file__).resolve().parents[2] / "data" / "etf"))   # parsed extract (not committed)
VP = pd.read_pickle(f"{D}/Valo_Pays.pkl")
VS = pd.read_pickle(f"{D}/Valo_Secteurs.pkl")
RT = pd.read_pickle(f"{D}/Rendements.pkl")
MK = pd.read_pickle(f"{D}/Marche.pkl")

COUNTRIES = {"US": ("MXUS", "NDDUUS"), "JP": ("MXJP", "NDDUJN"), "GB": ("MXGB", "NDDUUK"), "FR": ("MXFR", "NDDUFR"),
             "DE": ("MXDE", "NDDUGR"), "CH": ("MXCH", "NDDUSZ"), "NL": ("MXNL", "NDDUNE"), "IT": ("MXIT", "NDDUIT"),
             "ES": ("MXES", "NDDUSP"), "SE": ("MXSE", "NDDUSW"), "DK": ("MXDK", "NDDUDE"), "CA": ("MXCA", "NDDUCA"),
             "AU": ("MXAU", "NDDUAS"), "HK": ("MXHK", "NDDUHK")}
SECTORS = {"EN": "MXWO0EN", "MT": "MXWO0MT", "IN": "MXWO0IN", "CD": "MXWO0CD", "CS": "MXWO0CS", "HC": "MXWO0HC",
           "FN": "MXWO0FN", "IT": "MXWO0IT", "TC": "MXWO0TC", "UT": "MXWO0UT", "RE": "MXWO0RE"}
TREND = {"EQ_US": "NDDUUS", "EQ_EMU": "MSDEEMUN", "EQ_JP": "NDDUJN", "EQ_EM": "NDUEEGF", "BD_UST": "LUATTRUU",
         "BD_EGB": "LEATTREU", "BD_GAGG": "LEGATRUU", "BD_UCRP": "LUACTRUU", "CM_GOLD": "XAU", "CM_SILV": "XAG",
         "CM_BCOM": "BCOMTR", "CM_WTI": "BCOMCLTR", "CM_CU": "BCOMHGTR", "CM_AGRI": "BCOMAGTR"}
WHT_SECTOR = 0.15          # withholding-tax haircut on sector dividend yields (sector indices are price-only)


def col(df, t, f="PX_LAST"):
    key = t if t.endswith(("Index", "Curncy")) else (t + (" Curncy" if t in ("XAU", "XAG") else " Index"))
    return df[(key, f)]


# ---------------------------------------------------------------- returns
def cash_monthly():
    eur3m = col(MK, "EUR003M Index")
    estr = col(MK, "ESTRON Index")
    r = eur3m.where(eur3m.index < "2019-10-31", estr.reindex(eur3m.index)).fillna(eur3m)
    return (r / 100 / 12).rename("cash")


CASH = cash_monthly()
BENCH = col(MK, "MSDEWIN Index").pct_change().rename("MSCI World Net EUR")


def country_returns():
    return pd.DataFrame({c: col(RT, tr).pct_change() for c, (_, tr) in COUNTRIES.items()})


def sector_returns():
    out = {}
    for c, t in SECTORS.items():
        px = col(VS, t)
        if c == "RE":   # MSCI World Real Estate price stops updating after Oct 2023: splice S&P 500 Real Estate
            sp = col(VS, "S5RLST Index")
            stale = px.diff().ne(0)[::-1].idxmax()
            r = px.pct_change().where(px.index <= stale, sp.pct_change())
        else:
            r = px.pct_change()
        dy = col(VS, t, "EQY_DVD_YLD_12M").ffill() / 100
        out[c] = r + dy.shift(1) * (1 - WHT_SECTOR) / 12
    return pd.DataFrame(out)


def trend_returns():
    return pd.DataFrame({a: col(RT, t).pct_change() for a, t in TREND.items()})


# ---------------------------------------------------------------- value signal
def value_score(df, tickers, window=120, min_obs=60):
    """Average of z-scores of E/P, B/P and D/P, each against the line's own trailing history."""
    scores = {}
    for code, t in tickers.items():
        t = t if isinstance(t, str) else t[0]
        pe = col(df, t, "PE_RATIO")
        ep = (1 / pe).where(pe > 0)
        bp = 1 / col(df, t, "PX_TO_BOOK_RATIO").where(lambda x: x > 0)
        dp = col(df, t, "EQY_DVD_YLD_12M") / 100
        zs = []
        for x in (ep, bp, dp):
            m = x.rolling(window, min_periods=min_obs).mean()
            s = x.rolling(window, min_periods=min_obs).std()
            zs.append((x - m) / s)
        scores[code] = pd.concat(zs, axis=1).mean(axis=1, skipna=True)
    return pd.DataFrame(scores)


def momentum(ret, months=12, skip=0):
    return (1 + ret).rolling(months).apply(np.prod, raw=True).shift(skip) - 1


# ---------------------------------------------------------------- portfolio engine
def run(weights, rets, cost=0.001, ter=0.0, start=None, end="2026-09-30"):
    """weights: index = decision month end t, applied to returns of month t+1."""
    w = weights.reindex(columns=rets.columns).fillna(0.0)
    w_next = w.shift(1)                      # weights decided at t, held over month t+1
    gross = (w_next * rets.reindex(w_next.index)).sum(axis=1, min_count=1)
    invested = w_next.sum(axis=1)
    cash_w = 1 - invested
    cash = CASH.reindex(w_next.index).fillna(0)
    # turnover vs drifted weights
    drift = (w_next * (1 + rets.reindex(w_next.index).fillna(0)))
    drift = drift.div((1 + gross.fillna(0)), axis=0)
    turnover = (w - drift.shift(0)).abs().sum(axis=1).shift(1).fillna(w.abs().sum(axis=1).shift(1))
    net = gross + cash_w * cash - turnover * cost - invested * ter / 12
    net = net.loc[start:end].dropna()
    return net, turnover.loc[net.index], w_next.loc[net.index]


def stats(r, bench=None, rf=None):
    rf = (CASH if rf is None else rf).reindex(r.index).fillna(0)
    n = len(r)
    nav = (1 + r).cumprod()
    cagr = nav.iloc[-1] ** (12 / n) - 1
    vol = r.std() * 12 ** .5
    sharpe = (cagr - ((1 + rf.mean()) ** 12 - 1)) / vol
    dd = nav / nav.cummax() - 1
    out = dict(start=r.index[0].strftime("%Y-%m"), end=r.index[-1].strftime("%Y-%m"), years=n / 12, cagr=cagr, vol=vol,
               sharpe=sharpe, mdd=dd.min(), mdd_date=dd.idxmin().strftime("%Y-%m"), calmar=cagr / -dd.min(),
               pos_months=(r > 0).mean(), worst_month=r.min(), best_month=r.max())
    if bench is not None:
        b = bench.reindex(r.index)
        a = r - b
        te = a.std() * 12 ** .5
        bn = (1 + b).cumprod()
        bc = bn.iloc[-1] ** (12 / n) - 1
        out.update(bench_cagr=bc, active=cagr - bc, te=te, ir=(cagr - bc) / te, beta=np.cov(r, b)[0, 1] / b.var(),
                   corr=r.corr(b), up_years=None)
    return out


def calendar(r):
    return (1 + r).groupby(r.index.year).prod() - 1


# ---------------------------------------------------------------- strategies
def value_rotation(n_c=4, n_s=4, mom_filter=False, sleeves="both", score_fn=None):
    rc, rs = country_returns(), sector_returns()
    sc = value_score(VP, {k: v[0] for k, v in COUNTRIES.items()})
    ss = value_score(VS, SECTORS)
    if score_fn:
        sc, ss = score_fn(sc, rc), score_fn(ss, rs)
    valid = (sc.notna().sum(axis=1) >= 10) & (ss.notna().sum(axis=1) >= 8)
    if mom_filter:   # only lines whose 12-month return is positive are eligible; empty slots stay in cash
        sc = sc.where(momentum(rc) > 0)
        ss = ss.where(momentum(rs) > 0)
    rets = pd.concat([rc.add_prefix("C_"), rs.add_prefix("S_")], axis=1)
    rows = {}
    for t in sc.index:
        w = {}
        parts = []
        if sleeves in ("both", "countries"):
            parts.append((sc.loc[t].dropna().nlargest(n_c).index, "C_"))
        if sleeves in ("both", "sectors"):
            parts.append((ss.loc[t].dropna().nlargest(n_s).index, "S_"))
        k = len(parts)
        for (names, p), n in zip(parts, [x for x, keep in ((n_c, sleeves in ("both", "countries")), (n_s, sleeves in ("both", "sectors"))) if keep]):
            for nm in names:
                w[p + nm] = (1 / k) / n
        rows[t] = w
    W = pd.DataFrame(rows).T.fillna(0.0)
    W = W.reindex(sc.index).fillna(0.0)[valid]
    return W, rets


def trend(target_vol=0.10, lookbacks=(3, 6, 12), vol_win=12, cov_win=36, max_gross=1.0, long_only=True):
    R = trend_returns()
    cash = CASH.reindex(R.index).fillna(0)
    ex = R.sub(cash, axis=0)
    sig = sum(np.sign((1 + ex).rolling(L).apply(np.prod, raw=True) - 1) for L in lookbacks) / len(lookbacks)
    pos = sig.clip(lower=0) if long_only else sig
    vol = R.rolling(vol_win, min_periods=vol_win).std() * 12 ** .5
    rows = {}
    for t in R.index:
        p, v = pos.loc[t], vol.loc[t]
        if p.isna().all() or v.isna().all():
            continue
        raw = (p / v).replace([np.inf, -np.inf], np.nan).fillna(0)
        if raw.abs().sum() == 0:
            rows[t] = raw * 0
            continue
        hist = R.loc[:t].dropna(how="all").tail(cov_win).dropna(axis=1, thresh=vol_win)
        common = [c for c in raw.index if c in hist.columns and raw[c] != 0]
        cov = hist[common].cov(min_periods=vol_win) * 12
        x = raw[common]
        pv = float(np.sqrt(x @ cov @ x)) if len(common) else 0
        k = target_vol / pv if pv > 0 else 0
        w = raw * k
        g = w.abs().sum()
        if g > max_gross:
            w = w * max_gross / g
        rows[t] = w
    W = pd.DataFrame(rows).T.fillna(0.0)
    return W, R


def sixty_forty():
    r = 0.6 * BENCH + 0.4 * col(RT, "LEGATRUU").pct_change()
    return r.rename("60/40 EUR")


def xs_value(df, tickers):
    """Cross-sectional value: each month, z-score of E/P, B/P, D/P across the lines (cheap vs peers today)."""
    parts = []
    for f in ("PE_RATIO", "PX_TO_BOOK_RATIO", "EQY_DVD_YLD_12M"):
        X = pd.DataFrame({c: col(df, t if isinstance(t, str) else t[0], f) for c, t in tickers.items()})
        X = (1 / X.where(X > 0)) if f != "EQY_DVD_YLD_12M" else X
        parts.append(X.sub(X.mean(axis=1), axis=0).div(X.std(axis=1), axis=0))
    return sum(p.fillna(0) for p in parts) / 3


def xs_z(X):
    return X.sub(X.mean(axis=1), axis=0).div(X.std(axis=1), axis=0)


def value_rotation_custom(sc, ss, rc, rs, n=4):
    rets = pd.concat([rc.add_prefix("C_"), rs.add_prefix("S_")], axis=1)
    rows = {}
    for t in sc.index:
        w = {}
        for S, p in ((sc, "C_"), (ss, "S_")):
            a = S.loc[t].dropna()
            for nm in a.nlargest(n).index:
                w[p + nm] = 0.5 / n
        rows[t] = w
    W = pd.DataFrame(rows).T.reindex(sc.index).fillna(0.0)
    return W[(sc.notna().sum(axis=1) >= 10) & (ss.notna().sum(axis=1) >= 8)], rets


def overlay_sma(W, months=10):
    """Market trend overlay: hold the strategy only while MSCI World Net EUR is above its 10-month average."""
    idx = col(MK, "MSDEWIN Index")
    on = (idx > idx.rolling(months).mean()).reindex(W.index).fillna(True)
    return W.mul(on.astype(float), axis=0)


ASSET_CLASS = {"EQ": "Equities", "BD": "Bonds", "CM": "Commodities"}


def trend_class_budget(target_vol=0.10, lookbacks=(3, 6, 12), vol_win=12, cov_win=36, max_gross=1.0):
    """Trend with an equal risk budget per asset class (1/3 equities, 1/3 bonds, 1/3 commodities),
    inverse volatility inside each class. Unused budget (class in downtrend) stays in cash."""
    R = trend_returns()
    cash = CASH.reindex(R.index).fillna(0)
    ex = R.sub(cash, axis=0)
    sig = sum(np.sign((1 + ex).rolling(L).apply(np.prod, raw=True) - 1) for L in lookbacks) / len(lookbacks)
    pos = sig.clip(lower=0)
    vol = R.rolling(vol_win, min_periods=vol_win).std() * 12 ** .5
    classes = {c: [a for a in R.columns if a.startswith(c)] for c in ASSET_CLASS}
    rows = {}
    for t in R.index:
        p, v = pos.loc[t], vol.loc[t]
        if v.isna().all():
            continue
        raw = pd.Series(0.0, index=R.columns)
        for c, names in classes.items():
            iv = (1 / v[names]).replace([np.inf, -np.inf], np.nan).fillna(0)
            if iv.sum() == 0:
                continue
            raw[names] = (iv / iv.sum() * p[names].fillna(0)) / len(classes)   # class budget scaled by signal
        if raw.sum() == 0:
            rows[t] = raw
            continue
        hist = R.loc[:t].dropna(how="all").tail(cov_win).dropna(axis=1, thresh=vol_win)
        common = [c for c in raw.index if c in hist.columns and raw[c] != 0]
        cov = hist[common].cov(min_periods=vol_win) * 12
        x = raw[common]
        pv = float(np.sqrt(x @ cov @ x))
        w = raw * (target_vol / pv if pv > 0 else 0)
        if w.sum() > max_gross:
            w = w * max_gross / w.sum()
        rows[t] = w
    return pd.DataFrame(rows).T.fillna(0.0), R
