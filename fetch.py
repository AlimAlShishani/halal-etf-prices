"""Downloads daily prices for the halal ETFs used by the paper-trading bot page.
Runs every night on GitHub Actions and writes one CSV per listing to data/.
Columns: date, close (as quoted), adj_close (dividends reinvested), clean, volume.
`clean` is adj_close with Yahoo's unit mix-ups repaired: some London days are quoted in
US cents instead of pence (or the reverse), which looks like a fake +-40% jump. Each day is
converted with that day's GBP/USD rate to whichever unit sits closest to its neighbour."""
import os, sys, math, datetime as dt
import pandas as pd, yfinance as yf

LISTINGS = {
    'ISWD.L': 'world_islamic_usd',   # iShares MSCI World Islamic UCITS ETF, IE00B27YCN58
    'ISUS.L': 'usa_islamic_usd',     # iShares MSCI USA Islamic UCITS ETF, IE00B296QM64
    'ISDE.L': 'em_islamic_usd',      # iShares MSCI Emerging Markets Islamic UCITS ETF, IE00B27YCP72
}
TODAY = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')

def daily(ticker, adjust_cols=True):
    df = yf.Ticker(ticker).history(period='max', interval='1d', auto_adjust=False, actions=False)
    if df is None or df.empty: raise ValueError('no rows')
    idx = df.index.tz_localize(None) if df.index.tz is not None else df.index
    df.index = idx.strftime('%Y-%m-%d')
    df = df[~df.index.duplicated(keep='last')]
    return df[df.index < TODAY]                     # only finished trading days

def repair(adj, fx):
    """Walk back from the newest day; pick c, c/fx or c*fx, whichever is nearest the next day."""
    v = list(adj); n = len(v)
    if n == 0: return v
    med = sorted(v[max(0, n - 11):n - 1])[len(v[max(0, n - 11):n - 1]) // 2] if n > 1 else v[-1]
    f = fx[-1]; v[-1] = min([v[-1], v[-1] / f, v[-1] * f], key=lambda c: abs(math.log(c / med)))
    for i in range(n - 2, -1, -1):
        f = fx[i]; ref = v[i + 1]
        v[i] = min([adj[i], adj[i] / f, adj[i] * f], key=lambda c: abs(math.log(c / ref)))
    return v

os.makedirs('data', exist_ok=True)
fx_all = daily('GBPUSD=X')['Close']
failed = []
for ticker, name in LISTINGS.items():
    try:
        df = daily(ticker).dropna(subset=['Close'])
        fx = fx_all.reindex(df.index).ffill().bfill().fillna(1.3)
        clean = repair(df['Adj Close'].tolist(), fx.tolist())
        out = pd.DataFrame({'date': df.index, 'close': df['Close'].round(4).values, 'adj_close': df['Adj Close'].round(4).values,
                            'clean': [round(c, 4) for c in clean], 'volume': df['Volume'].fillna(0).astype('int64').values})
        path = f'data/{name}.csv'
        if os.path.exists(path) and len(out) < 0.9 * len(pd.read_csv(path)):
            raise ValueError(f'only {len(out)} rows, keeping the existing file')
        out.to_csv(path, index=False)
        fixed = sum(1 for a, c in zip(out.adj_close, out.clean) if abs(a / c - 1) > 0.01)
        print(f'{ticker}: {len(out)} rows, {out.date.iloc[0]} to {out.date.iloc[-1]}, repaired days: {fixed}')
    except Exception as e:
        failed.append(ticker); print(f'{ticker}: FAILED {e}', file=sys.stderr)
pd.DataFrame({'date': fx_all.index, 'gbpusd': fx_all.round(5).values}).to_csv('data/gbpusd.csv', index=False)
if len(failed) == len(LISTINGS): sys.exit(1)
