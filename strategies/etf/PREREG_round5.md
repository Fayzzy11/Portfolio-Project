# Round 5 — pre-registration (written 4 Nov 2026, 14:15, before any round-5 result was computed)

Noah's brief (4 Nov 2026): sector focus only; never go fully to cash (not realistic for a real fund); cut to 50% cash when the
macro picture is tense and indicators are red; react fast to catch the rebound, even at the cost of some losses.

## Main candidate V5 — "Value sectors, half-hedged, fast re-entry"
- **Universe:** the 11 MSCI World sectors (net TR, EUR; Real Estate spliced to S&P 500 Real Estate after Oct 2023).
- **Value signal (unchanged):** mean z-score of E/P, B/P and dividend yield versus each sector's own 10-year history (5 years minimum).
- **Selection:** the 3 cheapest sectors, equal weight; a held sector stays while it is among the 5 cheapest (buffer).
- **Risk indicators (month end), each red or green:**
  1. Trend: MSCI World Net EUR below its 10-month average.
  2. Credit: Bloomberg Euro High Yield TR minus Euro Treasury 1-3y TR over 3 months < 0.
  3. Breadth: fewer than half of the 25 country and sector lines above their own 10-month average.
- **Fast re-entry signal:** MSCI World Net EUR 3-month return > 0, or index above its 5-month average.
- **Exposure:** 50% equities / 50% cash when at least 2 indicators are red AND the fast re-entry signal is off; otherwise 100% equities.
- Monthly, signals at month end applied to the next month; 0.10% per unit of turnover, 0.25%/yr ETF fees.
- **Benchmark:** MSCI World Value Net EUR; MSCI World Net EUR and V4c shown alongside.

## Sensitivities (reported, not selectable)
| # | Change | Purpose |
|---|---|---|
| S5a | 2 sectors, buffer 4 | Concentration |
| S5b | No fast re-entry (back to 100% only when fewer than 2 indicators are red) | Value of the fast leg |
| S5c | Always 100% invested | Value of the risk overlay |

## Out-of-universe check (never looked at before)
Same rule V5 applied to the 11 S&P 500 sectors (price + 85% of dividend yield, EUR), compared with the equal-weight S&P 500 sectors
and MSCI USA Net EUR. If the rule only works on the universe it was designed on, it is not credible.

Periods: 2006-2026, design 2006-2015, validation 2016-2026. Value trials so far: about 15; this round adds 1 candidate + 3 sensitivities.
