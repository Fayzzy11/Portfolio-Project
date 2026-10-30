# Anti-bias checklist (written before interpreting the backtest)

Rule n°1 of the project: if a result looks good, check survivorship, look-ahead and units *before* any other explanation. Each line states the control, how it is implemented and the evidence.

| # | Risk | Control | Evidence | Status |
|---|---|---|---|---|
| 1 | **Survivorship** | Universe at each date = WORLD composition at that date (10 dated lists), never today's members nor the union | `src/universe.py::point_in_time_universe`; member counts fall from 3,332 to 2,248 over time, delisted tickers (`…D` suffix) are present | OK |
| 2 | Survivorship (holding period) | A held line that stops trading earns 0% after its last price; no forward-filled gains | `src/returns.py::total_returns`, test `test_total_return_is_adjusted_price_return_and_stops_after_delisting` | OK — limit: a bankruptcy with no final price would be missed (none observed in holdings) |
| 3 | **Look-ahead (accounting)** | Fiscal year usable from FYE + 6 months and not before announcement | `src/signals.py`; integration test fails if any score uses a year before availability | OK |
| 4 | Look-ahead (restatements) | Originally reported figures (`FILING_STATUS = OR`) at extraction | Extraction settings (log 26/10) | OK (to confirm at terminal) |
| 5 | Look-ahead (prices / trading) | Decisions use information up to D (cap/float/turnover snapshots at D, returns up to the last Friday ≤ D); trades at the close of the first Friday after D | `src/backtest.py` docstring and `trade_date` | OK |
| 6 | Look-ahead (classification) | GICS sector = **current** classification applied to the whole history | Known limit of the extract | Open — limited impact (few re-classifications, mainly 2023 GICS changes for payments/Visa/Mastercard moving to Financials) |
| 7 | **Units: dividends double-counted** | Event study proves `PX_LAST` already embeds dividends: TR = adjusted price return | `docs/data_quality.md` §3; benchmark replica −0.3%/yr vs MSCI World Net | **Fixed** (was +2%/yr) |
| 8 | Units: pence / sub-units | Prices in EUR at source; dividend currency inferred for GBp/ILs (only used for the withholding haircut) | `src/returns.py::clean_dividends` | OK |
| 9 | Units: millions / EUR | Fundamentals and market cap both in EUR millions; ratios of company totals only | Market cap vs price × shares: median 1.07 | OK |
| 10 | **Gross vs net dividends** | Headline uses net-of-withholding returns (MSCI net convention); gross reported as sensitivity (+0.9%/yr for EW) | `outputs/backtest/robustness.csv` | OK |
| 11 | Index provider mismatch | Universe Bloomberg World DM vs benchmark MSCI World | Replica correlation 0.996, TE 1.2% | Disclosed |
| 12 | Transaction costs | 15 bps × two-sided turnover, initial build included; no market impact | `outputs/backtest/performance_summary.csv` (before/after costs) | Disclosed (impact understated for less liquid names) |
| 13 | FX hedge cost | Carry from 3-month interbank differentials (covered interest parity), weekly re-struck hedge | `src/backtest.py` | Disclosed (no forward bid/ask, weekly re-strike idealised) |
| 14 | Data snooping in construction | Turnover buffer fixed before seeing the corrected results (target < 60%/yr); a larger buffer did better but was **not** adopted | `docs/decisions.md` C3 | OK |
| 15 | Small sample | 5 years, 10 rebalances, one regime | IC t-stat ≈ 2.1; IR not significant | Disclosed |
