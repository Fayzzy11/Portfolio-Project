# Strategies Lab — Noah Doose

A lab of systematic investment strategies, backtested on Bloomberg data.
Each strategy lives in its own folder with its frozen parameters, its code, its results and a report page
published on the project website (`docs/`, GitHub Pages).

| Strategy | Status | Report |
|---|---|---|
| Multi-asset trend following | Backtest complete (data to 30 Sep 2026) | `docs/trend-following/index.html` (French version: `docs/trend-following/fr/`) |
| Global value equities (portfolio project) | In progress | coming soon |

## Structure

```
common/                     shared code: loading Bloomberg extracts, performance metrics
strategies/
  trend_following/
    config.py               EVERY parameter, fixed before seeing results
    engine.py               signals, volatility, weights, costs
    run.py                  full backtest -> results/results.json
    positions.py            monthly routine: this month's target positions
    results/                aggregated results (no raw data)
templates/bloomberg/        Excel extraction templates (BDH/BDP formulas + checks), English and French
data/                       frozen extracts (excluded from Git)
docs/                       GitHub Pages website (one page per strategy)
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# put the frozen extract in data/, then:
python -m strategies.trend_following.run data/Extract_Trend_20261013_values.xlsx
python -m strategies.trend_following.positions data/Extract_Trend_20261013_values.xlsx 25000
python docs/build_report.py                              # rebuilds the report pages
```

## Adding a strategy

1. Copy `strategies/trend_following/` to `strategies/<name>/`.
2. Write `config.py` **before** running any backtest (assumptions, universe, costs, design/validation split).
3. Adapt `engine.py`, run `run.py`, publish the page in `docs/<name>/`, then add it to the table above
   and to `docs/index.html`.

## Lab rules

- Parameters are fixed before results; every variant tested is shown, not only the best one.
- A design period, then a validation period, with no changes in between.
- No look-ahead: a decision taken at the close of day t applies from day t+1.
- Transaction costs are always included.
- Results describe the past; they are not investment advice.

## Data licence

Raw Bloomberg data is never committed (`.gitignore`). The report pages contain monthly series derived from
MSCI indices; check the licence terms before making the repository public, or remove those series.
