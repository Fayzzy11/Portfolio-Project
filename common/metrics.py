"""Performance metrics shared by every strategy.

All functions take daily EXCESS returns (above the risk-free rate), so the Sharpe ratio is simply
mean / standard deviation, annualised.
"""
import numpy as np
import pandas as pd

ANN = 261  # trading days per year


def nav(r: pd.Series) -> pd.Series:
    return (1 + r.fillna(0)).cumprod()


def drawdown(r: pd.Series) -> pd.Series:
    v = nav(r)
    return v / v.cummax() - 1


def sharpe(r: pd.Series) -> float:
    r = r.dropna()
    sd = r.std()
    return float(r.mean() / sd * np.sqrt(ANN)) if sd > 0 else np.nan


def sharpe_ci(sr: float, years: float, z: float = 1.96) -> tuple[float, float, float]:
    """Standard error of the annual Sharpe ratio under i.i.d. returns (Lo, 2002): sqrt((1 + SR²/2) / T)."""
    se = np.sqrt((1 + 0.5 * sr ** 2) / years)
    return se, sr - z * se, sr + z * se


def stats(r: pd.Series) -> dict:
    r = r.dropna()
    years = len(r) / ANN
    v = nav(r)
    cagr = v.iloc[-1] ** (1 / years) - 1
    vol = r.std() * np.sqrt(ANN)
    sr = sharpe(r)
    dd = drawdown(r)
    se, lo, hi = sharpe_ci(sr, years)
    neg = r[r < 0]
    sortino = r.mean() * ANN / (np.sqrt((neg ** 2).sum() / len(r)) * np.sqrt(ANN)) if len(neg) else np.nan
    m = (1 + r).resample("ME").prod() - 1
    return {
        "start": str(r.index[0].date()), "end": str(r.index[-1].date()), "years": round(years, 1),
        "annual_return": cagr, "volatility": vol, "sharpe": sr,
        "sharpe_t_stat": sr * np.sqrt(years), "sharpe_ci95_low": lo, "sharpe_ci95_high": hi,
        "sortino": sortino, "max_drawdown": dd.min(),
        "max_drawdown_date": str(dd.idxmin().date()),
        "calmar": cagr / abs(dd.min()) if dd.min() < 0 else np.nan,
        "pct_positive_months": float((m > 0).mean()),
        "best_month": float(m.max()), "worst_month": float(m.min()),
        "monthly_skew": float(m.skew()),
    }


def monthly(r: pd.Series) -> pd.Series:
    return (1 + r.fillna(0)).resample("ME").prod() - 1


def annual(r: pd.Series) -> pd.Series:
    return (1 + r.fillna(0)).resample("YE").prod() - 1
