"""Downloads daily prices for the halal ETFs used by the paper-trading bot page.
Runs every night on GitHub Actions and writes one CSV per listing to data/.
Columns: date, close (as traded), adj_close (dividends reinvested), volume."""
import os, sys, pandas as pd, yfinance as yf

LISTINGS = {
    # iShares MSCI World Islamic UCITS ETF (IE00B27YCN58), London, USD
    'ISWD.L': 'world_islamic_usd',
    # iShares MSCI USA Islamic UCITS ETF (IE00B296QM64), London, USD
    'ISUS.L': 'usa_islamic_usd',
    # iShares MSCI Emerging Markets Islamic UCITS ETF (IE00B27YCP72), London, USD
    'ISDE.L': 'em_islamic_usd',
}
os.makedirs('data', exist_ok=True)
failed = []
for ticker, name in LISTINGS.items():
    try:
        df = yf.Ticker(ticker).history(period='max', interval='1d', auto_adjust=False, actions=False)
        if df is None or df.empty or 'Close' not in df: raise ValueError('no rows')
        idx = df.index.tz_localize(None) if df.index.tz is not None else df.index
        out = pd.DataFrame({'date': idx.strftime('%Y-%m-%d'),
                            'close': df['Close'].round(4).values, 'adj_close': df['Adj Close'].round(4).values,
                            'volume': df['Volume'].fillna(0).astype('int64').values})
        out = out.dropna(subset=['close']).drop_duplicates('date', keep='last')
        path = f'data/{name}.csv'
        if os.path.exists(path) and len(out) < 0.9 * len(pd.read_csv(path)):
            raise ValueError(f'only {len(out)} rows, keeping the existing file')
        out.to_csv(path, index=False)
        print(f'{ticker}: {len(out)} rows, {out.date.iloc[0]} to {out.date.iloc[-1]}')
    except Exception as e:
        failed.append(ticker); print(f'{ticker}: FAILED {e}', file=sys.stderr)
if len(failed) == len(LISTINGS): sys.exit(1)
