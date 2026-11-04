# Round 3 — pre-registration (written 4 Nov 2026, before any round-3 result was computed)

Levers chosen by Noah (4 Nov 2026): **MSCI-weighted value tilt** + **stock satellite**. The 10-month trend filter was NOT chosen.

## Main candidate — "Tilted World + satellite" (V3)
- **Core, 70 %: Tilted World.** Two halves of equal size, countries (14 MSCI indices) and sectors (11 MSCI World sectors).
  Inside each half: `w_i ∝ cap_i(t) × (1 + 0.5 × clip(z_i(t), −1, +1))`, renormalised to 100 %.
  `cap` = `CUR_MKT_CAP` at month end t; `z` = the validated value score (mean z-score of E/P, B/P, D/P vs the line's own 10-year history).
  A market one standard deviation cheaper than its own history is held at 1.5× its index weight, one standard deviation dearer at 0.5×.
  Monthly, signal at t applied to t+1, 0.10 % per unit of turnover, 0.25 %/yr ETF fees.
  Returns: countries = MSCI net TR (EUR); sectors = MSCI World sector net TR (`M1WO0xx`, EUR), Real Estate spliced to S&P 500 Real Estate after Oct 2023 (MSCI series frozen).
- **Satellite, 30 %:** 8 stocks from the stock-level value screen, eligible only if their country or sector is overweight in the core; max 2 per sector, 3 per country; 3.75 % each; held while in the cheapest 40 % of their sector; 0.15 % costs; unhedged. Backtest only possible over the screen's dates (Jul 2021 → Jun 2026), needs the Claude Code data.

## Tests and controls (declared now, none selectable afterwards)
| # | Portfolio | Role |
|---|---|---|
| C0 | Cap-weighted, same two halves, no tilt | Control: isolates the tilt |
| V3-core | Tilted World (tilt 0.5) | **Main core** |
| S1 | Tilted World, tilt 1.0 | Sensitivity only |
| S2 | Tilted World + 10-month trend filter | Information only (lever not chosen) |
| B | MSCI World ETF (0.12 %) | Benchmark |

Periods: full 2006-2026; design 2006-2015; validation 2016-2026. Number of trials in round 3 = 3 (V3-core, S1, S2), published.
Success criterion set by Noah (3 Nov): CAGR above the MSCI World AND lower risk (max drawdown, volatility).
