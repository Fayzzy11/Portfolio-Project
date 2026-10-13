"""Monthly routine: target positions at the latest available month end.

Usage:
    python -m strategies.trend_following.positions data/Extract_Trend_YYYYMMDD_values.xlsx 25000

Prints, for the futures version (reference) and the ETF long/cash version: signal, volatility,
target weight and euro amount for the given capital.
These are mechanical model outputs, not an investment recommendation.
"""
import sys
import warnings

import pandas as pd

from common.data import load_bloomberg_extract
from . import config as C
from . import engine as E

warnings.filterwarnings("ignore")


def main(path, capital):
    S = load_bloomberg_extract(path)
    R = E.daily_returns(S, C.FUTURES)
    me = E.month_ends(R.index)
    sig = E.signals(R, C.VARIANTS[C.REFERENCE_VARIANT], me)
    vol = E.ewma_vol(R)
    W_fut = E.weights(R, sig.iloc[-1:])
    W_etf = E.weights(R[C.ETF_UNIVERSE], sig[C.ETF_UNIVERSE].iloc[-1:], long_only=True, max_gross=C.ETF_MAX_GROSS)
    d = sig.index[-1]
    w_etf = W_etf.loc[d].reindex(R.columns).fillna(0)
    out = pd.DataFrame({
        "market": [C.LABELS[t] for t in R.columns],
        "signal": sig.loc[d].round(2).values,
        "annual_vol": vol.loc[d].round(3).values,
        "futures_weight": W_fut.loc[d].round(3).values,
        "futures_eur": (W_fut.loc[d] * capital).round(0).values,
        "etf_weight": w_etf.round(3).values,
        "etf_eur": (w_etf * capital).round(0).values,
    }, index=R.columns)
    print(f"Target positions at {d.date()} for a capital of EUR {capital:,.0f}\n")
    print(out.to_string())
    print(f"\nFutures gross leverage: {W_fut.loc[d].abs().sum():.2f}   |   ETF invested: {w_etf.sum():.0%}"
          f"   |   ETF money market: {1 - w_etf.sum():.0%}")
    return out


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else C.EXAMPLE_CAPITAL)
