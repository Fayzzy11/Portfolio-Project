"""Strategy parameters, all fixed BEFORE looking at any result (2 October 2026).

Do not change these values to "improve" a backtest: every after-the-fact change is one more trial,
which makes the resulting Sharpe ratio less reliable (selection bias / data snooping).
"""

# --- Futures universe (reference version, 17 markets) -------------------------------------------
# Bloomberg ticker: (asset class, trading cost as a fraction of notional, number of rolls per year)
# Costs are conservative assumptions (half-spread + approximate IBKR commission), not measurements.
FUTURES = {
    "ES1 Index": ("Equities", 0.0002, 4),
    "VG1 Index": ("Equities", 0.0002, 4),
    "NK1 Index": ("Equities", 0.0003, 4),
    "MES1 Index": ("Equities", 0.0004, 4),
    "TY1 Comdty": ("Rates", 0.0001, 4),
    "US1 Comdty": ("Rates", 0.0001, 4),
    "RX1 Comdty": ("Rates", 0.0001, 4),
    "G 1 Comdty": ("Rates", 0.0002, 4),
    "GC1 Comdty": ("Commodities", 0.0003, 6),
    "SI1 Comdty": ("Commodities", 0.0005, 5),
    # WTI: 2nd generic, because the 1st one is held until expiry (negative price on 20 April 2020)
    "CL2 Comdty": ("Commodities", 0.0004, 12),
    "HG1 Comdty": ("Commodities", 0.0005, 5),
    "C 1 Comdty": ("Commodities", 0.0006, 5),
    "EC1 Curncy": ("Currencies", 0.0001, 4),
    "JY1 Curncy": ("Currencies", 0.0001, 4),
    "BP1 Curncy": ("Currencies", 0.0001, 4),
    "AD1 Curncy": ("Currencies", 0.0002, 4),
}

LABELS = {
    "ES1 Index": "S&P 500", "VG1 Index": "Euro Stoxx 50", "NK1 Index": "Nikkei 225",
    "MES1 Index": "MSCI Emerging Markets", "TY1 Comdty": "US 10-year", "US1 Comdty": "US 30-year",
    "RX1 Comdty": "German Bund 10-year", "G 1 Comdty": "UK Gilt 10-year", "GC1 Comdty": "Gold",
    "SI1 Comdty": "Silver", "CL2 Comdty": "WTI crude oil", "HG1 Comdty": "Copper",
    "C 1 Comdty": "Corn", "EC1 Curncy": "EUR/USD", "JY1 Curncy": "JPY/USD",
    "BP1 Curncy": "GBP/USD", "AD1 Curncy": "AUD/USD",
}

# --- Engine --------------------------------------------------------------------------------------
VOL_TARGET = 0.10          # target annual portfolio volatility
EWMA_COM = 60              # centre of mass (days) of each market's EWMA volatility (Moskowitz et al., 2012)
COV_WINDOW = 261           # window (days) of the covariance matrix used to scale the portfolio
MAX_GROSS_FUTURES = 4.0    # maximum gross leverage (sum of |weights|) for the futures version
START = "2001-02-01"       # common start date (the 12-month signal needs 12 months of history)
SPLIT = "2015-12-31"       # end of the design period; validation afterwards, untouched
END = "2026-09-30"

VARIANTS = {
    "TSMOM 3m": [3],
    "TSMOM 6m": [6],
    "TSMOM 12m": [12],
    "TSMOM blend 3/6/12m": [3, 6, 12],
}
REFERENCE_VARIANT = "TSMOM blend 3/6/12m"   # chosen for robustness, not for its result
ETF_VARIANT = "ETF long/cash version"

# --- Investable ETF version (fixed on 13 October 2026, before computing it) ----------------------
# Long or cash only, no leverage, no currencies (no simple currency ETF for a European investor).
# Futures excess returns are used as a proxy for ETF/ETC excess returns.
ETF_UNIVERSE = [k for k, v in FUTURES.items() if v[0] != "Currencies"]
ETF_MAX_GROSS = 1.0        # at most 100% of capital invested, the rest in a money-market fund
ETF_TRADE_COST = 0.0010    # 0.10% per unit of turnover (spread + commission)
ETF_TER = 0.0030           # 0.30% per year management fee on the invested share

# --- Equity references (proxy for the value strategy of the portfolio project) -------------------
VALUE_PROXY = "M1WO000V Index"   # MSCI World Value Net TR, in USD -> converted to EUR
WORLD = "MSDEWIN Index"          # MSCI World Net TR, in EUR
EURUSD = "EURUSD Curncy"
EURGBP = "EURGBP Curncy"
RF_EUR = "EUR003M Index"         # 3-month Euribor, EUR risk-free rate

# --- Smallest available contracts (assumptions to check on the exchange website / at IBKR) -------
# ticker: (contract, multiplier, price factor, currency)  ->  notional = price × factor × multiplier
# price factor: 0.01 when Bloomberg quotes in cents or in % of face value.
CONTRACTS = {
    "ES1 Index": ("Micro E-mini S&P 500 (CME)", 5, 1, "USD"),
    "VG1 Index": ("Euro Stoxx 50, standard (Eurex)", 10, 1, "EUR"),
    "TY1 Comdty": ("US 10-year Note, standard (CBOT)", 100_000, 0.01, "USD"),
    "RX1 Comdty": ("Euro-Bund, standard (Eurex)", 100_000, 0.01, "EUR"),
    "G 1 Comdty": ("Long Gilt, standard (ICE)", 100_000, 0.01, "GBP"),
    "GC1 Comdty": ("Micro Gold, 10 oz (COMEX)", 10, 1, "USD"),
    "SI1 Comdty": ("Micro Silver, 1,000 oz (COMEX)", 1_000, 1, "USD"),
    "CL2 Comdty": ("Micro WTI, 100 barrels (NYMEX)", 100, 1, "USD"),
    "HG1 Comdty": ("Micro Copper, 2,500 lb (COMEX)", 2_500, 0.01, "USD"),
    "C 1 Comdty": ("Mini Corn, 1,000 bushels (CBOT)", 1_000, 0.01, "USD"),
    "EC1 Curncy": ("Micro EUR/USD, €12,500 (CME)", 12_500, 1, "EUR_FIXED"),
    "BP1 Curncy": ("Micro GBP/USD, £6,250 (CME)", 6_250, 0.01, "USD"),
    "AD1 Curncy": ("Micro AUD/USD, AUD 10,000 (CME)", 10_000, 0.01, "USD"),
}
EXAMPLE_CAPITAL = 25_000   # € — top of the range given by Noah (€5,000 to €25,000)
