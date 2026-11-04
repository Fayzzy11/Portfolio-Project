# Satellite — pre-registration (written 4 Nov 2026, 19:15, before any satellite result was computed)

Rules validated by Noah on 4 Nov 2026 (14:47), including the 50% de-risking applied to the satellite.
Structure: **70% ETF core V7 + 30% stock satellite**.

## Data (from the Claude Code stock-screen project, unchanged)
- Scores: `scores_fye6` — sector-relative value composite (EV/EBIT, P/B, FCF yield, EV/Sales; P/B + P/E for financials),
  fundamentals usable from fiscal-year end + 6 months and never before the announcement date (locked rule), point-in-time
  universe (Bloomberg World Large & Mid Cap, 24 developed countries, liquidity filters). 10 dates, 30 Jun 2021 → 31 Dec 2025.
- Returns: weekly total returns in EUR, net of withholding tax, unhedged (`ret_total_net`); delisted lines earn 0 after their
  last price (project convention).

## Satellite rules
1. **Eligible** at screen date t: eligible stocks of the screen whose country of risk OR GICS sector is held by the core's value
   selection at the month end of t (the 4 countries and 4 sectors, before the risk rule), with a price at t.
2. **Ranking:** sector-relative value percentile `score_pct` (ties broken by `score`).
3. **Selection:** 8 names, max 2 per GICS sector and 3 per country, 1/8 of the satellite each (3.75% of the strategy).
4. **Holding:** a held name is kept at the next screen date while it remains eligible in the universe and in the cheapest 40% of
   its sector (`score_pct` ≥ 0.60); freed slots are refilled from rule 1-3.
5. **Rebalancing:** at the 10 screen dates (semi-annual: the screen has no monthly scores), trades executed the following week.
6. **Risk rule:** the satellite's equity exposure follows the core's exposure (100% or 50%, decided at each month end, applied
   over the next month); the rest earns the euro money-market rate (€STR).
7. **Costs:** 0.15% per unit of turnover (trades and exposure changes); unhedged.
8. **Pitches:** veto/priority only in the live record from November 2026 — not in the backtest.

## Combination and tests
- Strategy = 70% core V7 + 30% satellite, rebalanced to 70/30 monthly (no extra cost charged for that rebalance; disclosed).
  Weekly satellite returns compounded into calendar months (weeks assigned by their Friday).
- Period: July 2021 → June 2026 (60 months), the only period with stock scores. Reported: satellite alone, core alone and
  70/30 strategy, against MSCI World Value Net EUR (benchmark) and MSCI World Net EUR; t-statistic of the excess return.
- No parameter of rules 1-7 will be changed after seeing the result. Any change would be a new, labelled trial.
