# ETF strategies: Global Value Rotation and Multi-Asset Trend

Rules fixed and validated on 30 October 2026, before the data (see the strategy pages on the site).
Data: Bloomberg extract `ETF_EXTRACT_VALUE.xlsx` (monthly, Dec 1999 – Sep 2026), not committed.

```bash
python strategies/etf/load.py data/ETF_EXTRACT_VALUE.xlsx   # parse the extract into data/etf/ (ignored by Git)
python strategies/etf/run3.py                               # rules, pre-registered variants and post-hoc research variants
python strategies/etf/export.py                             # writes site/data/etf_strategies.json
python site/build_site.py                                   # rebuilds the pages
```

Implementation notes
- Country returns: MSCI net total return indices in EUR (`NDDUxx`). Sector returns: MSCI World sector price indices in EUR
  plus 85% of the trailing dividend yield (no sector net TR index in the extract).
- MSCI World Real Estate stops updating in Oct 2023: its returns are spliced with S&P 500 Real Estate afterwards.
- Cash: 3-month Euribor until Sep 2019, €STR afterwards (EONIA not available).
- Trend sizing: inverse 12-month volatility per asset, portfolio scaled with a 36-month covariance to a 10% target, ≤ 100% invested.
- Variants V3-V7, T2-T4 and the combinations were tested after seeing the data: research only, not adopted.
