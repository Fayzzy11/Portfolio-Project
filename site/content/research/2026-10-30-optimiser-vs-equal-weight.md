---
title: Why the optimiser lost to 1/N in a value portfolio
date: 30 Oct 2026
summary: Same 50 stocks, three weighting schemes. Minimum variance and mean-variance lagged equal weight by about 2.3 points a year — and the reason is style, not only estimation error.
---
## The experiment
At each of ten semi-annual dates the same 50 cheap stocks were weighted three ways: equally, by minimum variance (Ledoit-Wolf covariance, 250 weeks) and by classic mean-variance, all under identical constraints (0.5%-4% per name, ±10 points by sector and country).

## The result
| Weighting | Ann. return | Active vs MSCI World Net |
|---|---|---|
| Equal weight | 11.6% | −0.1% |
| Minimum variance | 9.4% | −2.3% |
| Mean-variance | 9.4% | −2.4% |
| Weights proportional to the score | 11.5% | −0.2% |

## Why
- **Style drift.** Minimum variance overweights the least volatile cheap stocks — staples, utilities, defensive health care — and adds a quality/investment tilt (RMW +0.12, CMA +0.23) with a lower beta. Over 2021-2026 the cheap *cyclicals* were the ones that paid.
- **Estimation error.** Mean-variance uses historical average returns, which are notoriously noisy; it concentrates in past winners within a value book, partly undoing the signal (DeMiguel, Garlappi & Uppal, 2009).
- **Turnover.** Optimised weights move more: 70% a year vs 57% for equal weight.

## What I take from it
Equal weight is a hard benchmark for an optimiser when the expected-return input carries little information. If I used an optimiser, I would feed it the score as the alpha (Grinold-style) and control factor exposures explicitly rather than minimising raw variance.
