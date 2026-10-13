"""Trend-following engine (time-series momentum), monthly rebalancing.

At each month end t:
1. Signal per market: sign of the cumulative return over L months (average of the signs if several L).
2. Volatility per market: EWMA standard deviation of daily returns, annualised.
3. Raw weight: signal / volatility / number of eligible markets (every market carries the same risk).
4. Scaling: all weights are multiplied so that the portfolio's ex-ante volatility (12-month covariance)
   equals VOL_TARGET, then the gross leverage cap is applied.
5. Weights decided at the close of t are held from the next session onwards (no look-ahead).
"""
import numpy as np
import pandas as pd

from . import config as C

ANN = 261


def daily_returns(prices: dict, tickers) -> pd.DataFrame:
    px = pd.DataFrame({k: prices[k] for k in tickers}).sort_index()
    # return between two actual quotes of each market (local holidays are skipped)
    return px.apply(lambda s: s.dropna().pct_change()).reindex(px.index)


def month_ends(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    s = pd.Series(idx, index=idx)
    return pd.DatetimeIndex(s.groupby([idx.year, idx.month]).max().values)


def signals(rets: pd.DataFrame, lookbacks, me) -> pd.DataFrame:
    cum = (1 + rets.fillna(0)).cumprod()
    n_obs = rets.notna().cumsum()
    parts = []
    for L in lookbacks:
        c = cum.loc[me]
        sig = np.sign(c / c.shift(L) - 1)
        enough = n_obs.loc[me] >= (L * 21 + 21)       # enough real history to sign the trend
        parts.append(sig.where(enough))
    return sum(parts) / len(parts)                      # possible values: -1, -1/3, 1/3, 1 (or -1, 1)


def ewma_vol(rets: pd.DataFrame) -> pd.DataFrame:
    return rets.ewm(com=C.EWMA_COM, min_periods=C.EWMA_COM).std() * np.sqrt(ANN)


def weights(rets, sig, long_only=False, max_gross=C.MAX_GROSS_FUTURES) -> pd.DataFrame:
    vol = ewma_vol(rets)
    out = {}
    for d in sig.index:
        s = sig.loc[d].dropna()
        if long_only:
            s = s.clip(lower=0)
        s = s[s != 0]
        v = vol.loc[d, s.index]
        s = s[v.notna() & (v > 0)]
        w = pd.Series(0.0, index=rets.columns)
        if len(s):
            n_eligible = sig.loc[d].dropna().shape[0]     # divide by every eligible market
            raw = s / vol.loc[d, s.index] / n_eligible
            cov = rets.loc[:d].iloc[-C.COV_WINDOW:][raw.index].cov(min_periods=120).fillna(0) * ANN
            pvol = float(np.sqrt(raw.values @ cov.values @ raw.values))
            if pvol > 0:
                raw = raw * C.VOL_TARGET / pvol
            g = raw.abs().sum()
            if g > max_gross:
                raw *= max_gross / g
            w[raw.index] = raw
        out[d] = w
    return pd.DataFrame(out).T


def run_futures(rets: pd.DataFrame, lookbacks):
    me = month_ends(rets.index)
    W = weights(rets, signals(rets, lookbacks, me))
    Wd = W.reindex(rets.index).shift(1).ffill().fillna(0.0)       # held from t+1
    contrib = Wd * rets.fillna(0)
    trade_c = pd.Series({k: C.FUTURES[k][1] for k in rets.columns})
    rolls = pd.Series({k: C.FUTURES[k][2] for k in rets.columns})
    trade_cost = (W.diff().abs().fillna(W.abs()) * trade_c).sum(axis=1)
    roll_cost = (Wd.abs() * trade_c * 2 * rolls / ANN).sum(axis=1)   # round trip at every roll
    net = contrib.sum(axis=1) - roll_cost
    net.loc[trade_cost.index] -= trade_cost.values
    return _pack(net, contrib, W, Wd)


def run_etf(rets: pd.DataFrame, lookbacks):
    me = month_ends(rets.index)
    W = weights(rets, signals(rets, lookbacks, me), long_only=True, max_gross=C.ETF_MAX_GROSS)
    Wd = W.reindex(rets.index).shift(1).ffill().fillna(0.0)
    contrib = Wd * rets.fillna(0)
    trade_cost = W.diff().abs().fillna(W.abs()).sum(axis=1) * C.ETF_TRADE_COST
    ter = Wd.abs().sum(axis=1) * C.ETF_TER / ANN
    net = contrib.sum(axis=1) - ter
    net.loc[trade_cost.index] -= trade_cost.values
    return _pack(net, contrib, W, Wd)


def _pack(net, contrib, W, Wd):
    start = pd.Timestamp(C.START)
    return {
        "net": net.loc[start:C.END],
        "gross": contrib.sum(axis=1).loc[start:C.END],
        "contrib": contrib.loc[start:C.END],
        "W": W.loc[:C.END],
        "Wd": Wd.loc[start:C.END],
    }
