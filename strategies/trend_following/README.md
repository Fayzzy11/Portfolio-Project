# Multi-asset trend following (time-series momentum)

Full report with every calculation: `docs/trend-following/index.html`.

## In one sentence

At each month end, we check whether each of 17 markets (equity indices, government bonds, commodities,
currencies) has gone up or down over 3, 6 and 12 months; we buy what is rising and sell what is falling,
size each position so that it carries the same risk, and scale the whole portfolio to a 10% annual volatility.

## Exact rules

| Step | Rule |
|---|---|
| Universe | 17 generic futures, ratio back-adjusted (see `config.py`); WTI taken on the 2nd contract |
| Signal | s = mean of sign(3-month return), sign(6-month), sign(12-month) ∈ {−1, −1/3, +1/3, +1} |
| Volatility | σ = EWMA standard deviation of daily returns, 60-day centre of mass, × √261 |
| Raw weight | w_raw = s / σ / N (N = number of eligible markets) |
| Scaling | w = w_raw × 10% / σ_portfolio(w_raw), covariance of the last 261 days |
| Cap | sum of \|w\| ≤ 4 (futures); ≤ 1 and w ≥ 0 (ETF version) |
| Timing | computed at the close of the last business day of the month, held from the next day |
| Futures costs | weight change × market cost + roll (2 × cost × rolls per year, spread daily) |
| ETF costs | 0.10% per unit of turnover + 0.30% per year on the invested share |
| Split | design Feb 2001 – Dec 2015, validation Jan 2016 – Sep 2026 |

## Replicate

1. **Bloomberg**: `GFUT <GO>` → Generic Rolls tab → `Adjust` = **Ratio**, roll **before** expiry
   (`Days` = 5 or `With Active Futures`). Open `templates/bloomberg/Extract_Trend_Following_Bloomberg_EN.xlsx`,
   Refresh, check `Checks!C6` = "Adjusted", save a copy, paste as values, drop it into `data/`.
2. **Python**: `python -m strategies.trend_following.run data/<file>.xlsx`, then `python docs/build_report.py`.
3. **Every month**: new extract (or update), then
   `python -m strategies.trend_following.positions data/<file>.xlsx <capital>`, and place the orders
   needed to reach the target weights.
