"""Pre-committed analysis specification.

These constants are frozen before any empirical analysis and must not be changed after inspection.
"""
import os

RESEARCH_QUESTION = "Are daily returns of DBS, OCBC and UOB from 2014 to 2024 well described by a Normal distribution, and do CLT-based confidence intervals agree with bootstrap intervals for their mean, volatility and co-movement?"
TICKERS = {'DBS': 'D05.SI', 'OCBC': 'O39.SI', 'UOB': 'U11.SI'}
START = '2014-01-02'
END = '2024-12-31'
YFINANCE_END = '2025-01-01'
ALPHA = 0.05
CONFIDENCE = 0.95
B_BOOT = 10_000
B_PERM = 10_000
# Run FAST_MODE=1 to reduce Step 8 parametric bootstrap replicates for development.
# Full default is B_PARAM=1000; FAST_MODE maps to B_PARAM=100 unless B_PARAM is set explicitly.
FAST_MODE = os.getenv('FAST_MODE', '0').lower() in {'1', 'true', 'yes', 'on'}
B_PARAM = int(os.getenv('B_PARAM', '100' if FAST_MODE else '1000'))
SEED = 42
ANNUALISATION = 252
EXTREME_QUANTILE = 0.10
CALM_WINDOW = ('2017-01-01', '2019-12-31')
COVID_WINDOW = ('2020-02-01', '2020-06-30')
RATE_HIKE_WINDOW = ('2022-01-01', '2023-12-31')
BANKS = list(TICKERS)
