---
title: Methodology
---
# Data and methodology

## Sources
- **Bloomberg terminal** (SKEMA lab, extracted 26-29 October 2026): index compositions at ten dates, weekly prices in EUR, dividend history, annual standardised fundamentals as originally reported, market cap / free float / turnover snapshots, FX, MSCI World Net EUR, €STR. Licensed data are **not** published here: the site shows methodology and aggregated results only.
- **Kenneth French Data Library** — Developed 5 factors and momentum (daily), for the factor decomposition.
- **OECD via FRED** — 3-month interbank rates by currency, for the cost of FX hedging.

## Integrity rules
1. **No survivorship:** the universe at each date is the index composition at that date, including later delisted names.
2. **No look-ahead:** a fiscal year is used from year-end + 6 months and never before its announcement; originally reported (not restated) figures; trades executed after the decision date.
3. **Units checked:** market cap vs price × shares, a benchmark replica from security returns (0.996 correlation with MSCI World Net), an event study on ex-dividend dates.
4. **Net vs gross:** returns are net of dividend withholding tax, like the benchmark.
5. **Reproducible:** one command rebuilds every number from the raw file; unit tests check the lag, returns and every portfolio constraint.
6. **Every judgement call logged** with its alternatives in a decision journal.

## Construction toolkit
Python (pandas, NumPy, SciPy/HiGHS for the integer selection, cvxpy for the optimisers, scikit-learn for Ledoit-Wolf shrinkage, statsmodels for factor regressions), python-pptx and python-docx for the documents.
