# Satellite v2 — pre-registration (written 5 Nov 2026, before any v2 result was computed)

Noah's decisions (4 Nov 2026, 19:10-19:21): same 8-name rules, core countries/sectors, history from 2006, coherent reduced
universe, monthly scores, monthly prices. Rules 1-8 of `PREREG_satellite.md` are unchanged except where stated below.

## Universe (point-in-time, no survivorship)
- Members of Bloomberg WORLD Index at each semi-annual date (Dec 2005 → Dec 2025), country of risk in the 24 developed markets of
  the mandate, ranked by index weight: the **300 largest**, one line per issuer (largest weight kept). The list of a date applies
  until the next date. Delisted names stay in the data with their real returns (e.g. Lehman → 0).
- GICS sector: Bloomberg current GICS; for 162 delisted names Bloomberg returns none, so they were classified by hand
  (`satellite_lists/manual_gics.csv`, current GICS definitions). No liquidity filter (the 300 largest are all liquid).

## Monthly score (identical to the stock screen of 29 Oct, `src/signals.py`)
- Fundamentals: annual, original figures (`FILING_STATUS = OR`), EUR; a fiscal year is usable from fiscal-year end + 6 months and
  never before its announcement date. Market cap: Bloomberg `CUR_MKT_CAP` at the month end (EUR).
- Metrics: EV/EBIT, B/P, FCF/P, Sales/EV (non-financials, min 3 of 4); B/P, E/P (financials, min 2 of 2). Winsorised 1%/99%
  across the universe, z-scored within GICS sector, averaged; `score_pct` = rank within sector.

## Satellite (8 names, 30% of the strategy)
- Monthly at each month end: eligible if country OR sector held by the core's value selection that month (before the risk rule);
  a held name stays while still in the universe with `score_pct` ≥ 0.60; free slots filled by highest `score_pct` (ties: score),
  max 2 per sector and 3 per country; equal weight, reset monthly.
- Exposure follows the core's risk rule (100% or 50%), rest in euro money market. Costs 0.15% per unit of turnover.
- Returns: Bloomberg `TOT_RETURN_INDEX_GROSS_DVDS` monthly in EUR, unhedged, minus a flat 0.40%/yr withholding-tax haircut
  (≈15% of a ~2.7% dividend yield; no stock-level dividend data in this extract) — disclosed.

## Tests (reported whatever the result)
- Period Jan 2006 → Jun 2026; design 2006-2015, validation 2016-2026. Satellite alone, core V7 alone, 70/30 strategy (monthly
  rebalanced), vs MSCI World Value Net EUR and MSCI World Net EUR; t-statistic of excess returns; calendar years.
- For reference only: the 29 Oct 2021-2026 semi-annual satellite (different universe), not a candidate.
- No rule above will be changed after seeing the results; any change is a new, labelled trial.
