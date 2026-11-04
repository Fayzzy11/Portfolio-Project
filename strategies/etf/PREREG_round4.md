# Round 4 — pre-registration (written 4 Nov 2026, 10:30, before any round-4 result was computed)

## A. Value + trend filters (Noah's brief: beat the MSCI World over the whole period, value-focused, monthly)
Story: **value decides WHAT to hold, trend decides WHEN to hold it.** The value signal is slow (years), so it should not be
churned monthly; the trend filter is fast and is the only part that needs a monthly check.

Base selection = validated rules (4 cheapest countries + 4 cheapest sectors, value z-score vs own 10-year history).
Market filter = MSCI World Net EUR above its 10-month average at month end, else the sleeve goes to the risk-off asset.

| # | Candidate | What changes vs the validated rules |
|---|---|---|
| V4b | Per-line filter | Each selected line is held only while its own index is above its 10-month average; otherwise that slot is in cash |
| V4c | Buffer + market filter | Buy the 4 cheapest; keep a held line until it drops out of the 6 cheapest (no early selling of a value bet); market filter on top |
| V4d | 12 tranches + market filter | 1/12 of the sleeve is re-formed each month and held 12 months (value horizon respected); market filter on top |
| V4e | V4d with bonds as risk-off | As V4d, but risk-off goes to euro government bonds (Bloomberg Euro Treasury TR) instead of cash |

References already known (not trials): V1 rules, V6 rules + market filter, MSCI World ETF.
Costs as before (0.10 % per unit of turnover, 0.25 %/yr ETF fees). Periods: 2006-2026, design 2006-2015, validation 2016-2026.
Success criterion (Noah): CAGR above the MSCI World ETF over 2006-2026 with a lower max drawdown. 4 trials, all published.

## B. Trend following — long/short, walk-forward choice of the "theme of the moment"
Goal (Noah): profit from up AND down moves, replicable by a private investor, pick the best theme with rolling out-of-sample.

- **Themes (40):** the 14 original markets, 15 new ones from extract #2 (Brent unavailable), 11 MSCI World sectors (net TR, EUR).
- **Short side, retail-replicable:** only through UCITS inverse (-1x daily) ETFs held long. Shortable set: US equities,
  euro-area equities, European equities, euro govt bonds, US Treasuries, gold, WTI, broad commodities.
  Modelled short return = −r − σ²/12 (daily-reset decay, σ = trailing 12-month vol) − 0.60 %/yr fee. No leverage: gross ≤ 100 %.
- **Model grid (18 models):** lookback L ∈ {3, 6, 12} months × number of positions k ∈ {3, 5, 8} × {long-only, long/short}.
  Score = L-month excess return over cash ÷ 12-month vol. Long book = top k with positive score; short book (long/short models)
  = up to k shortable themes with the most negative score. Inverse-vol weights, scaled to 10 % vol (36-month covariance), gross ≤ 100 %.
- **Walk-forward selection:** each month t, every model's net returns over the trailing W months (strictly before t+1) are compared;
  the model with the best trailing Sharpe is used for month t+1. Two trials: **W = 12** and **W = 24** months (Noah: "1/2 ans").
- Costs 0.10 % per unit of turnover, 0.30 %/yr ETF fees. Reported 2006-2026 and halves; references T1 (validated rules) and MSCI World.
