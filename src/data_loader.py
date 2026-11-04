from pathlib import Path
import os
import pandas as pd
import numpy as np
import yfinance as yf
from .config import TICKERS, START, YFINANCE_END, ANNUALISATION

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
INTERIM = ROOT / 'data' / 'interim'
PROCESSED = ROOT / 'data' / 'processed'
FIGURES = ROOT / 'outputs' / 'figures'
TABLES = ROOT / 'outputs' / 'tables'

EVENT_NOTES = {
    '2020-03-09': 'Global COVID-19 spread and oil-price crash (Black Monday)',
    '2020-03-12': 'COVID-19 pandemic panic with emergency global liquidity actions',
    '2020-03-16': 'COVID-19 pandemic panic and emergency Fed/MAS liquidity actions',
    '2020-03-23': 'COVID-19 sell-off floor amid emergency policy support',
    '2020-03-24': 'Global stimulus and policy-support rebound rally',
    '2020-03-25': 'Global stimulus rebound rally',
    '2020-11-09': 'Pfizer COVID-19 vaccine breakthrough rally',
    '2020-11-10': 'COVID-19 vaccine optimism continuation rally',
    '2024-08-05': 'Yen carry-trade unwind and global equity sell-off',
}

def verified_market_event(date):
    key = str(date.date()) if hasattr(date, 'date') else str(date)[:10]
    return EVENT_NOTES.get(key, 'Not independently verified: possible bank-specific market, corporate earnings, or dividend adjustment event')

def download_or_load_raw():
    for directory in (RAW, INTERIM, PROCESSED, FIGURES, TABLES):
        directory.mkdir(parents=True, exist_ok=True)
    frames = {}
    for bank, ticker in TICKERS.items():
        path = RAW / f"{ticker.replace('.', '_')}_raw.csv"
        if path.exists():
            df = pd.read_csv(path, index_col=0, parse_dates=True)
        else:
            df = yf.download(ticker, start=START, end=YFINANCE_END, auto_adjust=False,
                             progress=False, group_by='column', actions=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            df.to_csv(path)
            df = pd.read_csv(path, index_col=0, parse_dates=True)
        frames[bank] = df
    return frames

def prepare_returns():
    os.makedirs(TABLES, exist_ok=True)
    os.makedirs(INTERIM, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    frames = download_or_load_raw()
    prices = {}
    for bank, df in frames.items():
        col = 'Adj Close' if 'Adj Close' in df.columns else ('Close' if 'Close' in df else None)
        if col is None: raise RuntimeError(f'No adjusted/close column for {bank}')
        s = pd.to_numeric(df[col], errors='coerce')
        s.index = pd.to_datetime(s.index).tz_localize(None)
        prices[bank] = s.rename(bank)
    aligned = pd.concat(prices, axis=1).sort_index()
    duplicate_count = int(aligned.index.duplicated().sum())
    if duplicate_count:
        aligned = aligned[~aligned.index.duplicated(keep='first')]
    aligned = aligned.dropna(how='any')
    bad_prices = int(((aligned <= 0).sum().sum()))
    returns = np.log(aligned / aligned.shift(1)).dropna()
    sigma = returns.std(ddof=1)
    threshold = 5 * sigma
    extreme = returns.abs().gt(threshold).stack().reset_index()
    extreme.columns = ['Date', 'Bank', 'Extreme']
    extreme = extreme[extreme['Extreme']]
    extreme['Magnitude'] = [returns.loc[d, b] for d, b in zip(extreme['Date'], extreme['Bank'])]
    extreme['Verified_Market_Event'] = [verified_market_event(d) for d in extreme['Date']]
    extreme = extreme[['Date', 'Bank', 'Magnitude', 'Verified_Market_Event']].sort_values(['Date', 'Bank'])
    extreme.to_csv(TABLES/'step3_cleaning_log.csv', index=False)
    lines = ['# Cleaning log', '', f'- Aligned date range: {returns.index.min().date()} to {returns.index.max().date()}',
             f'- Duplicate dates removed: {duplicate_count}', f'- Non-positive prices: {bad_prices}',
             f'- Returns retained: {len(returns)}', '', '| Date | Bank | log return | Verified market event |', '|---|---|---:|---|']
    lines += [f"| {r.Date.date()} | {r.Bank} | {r.Magnitude:.6f} | {r.Verified_Market_Event} |" for r in extreme.itertuples()]
    (INTERIM).mkdir(parents=True, exist_ok=True)
    (INTERIM/'cleaning_log.md').write_text('\n'.join(lines) + '\n')
    PROCESSED.mkdir(parents=True, exist_ok=True)
    returns.to_csv(PROCESSED/'bank_log_returns.csv')
    return aligned, returns
