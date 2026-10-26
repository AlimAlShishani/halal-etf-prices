# Halal ETF prices

Daily prices for the Shariah-compliant ETFs followed by my paper-trading bot page.
A GitHub Action (`.github/workflows/prices.yml`) downloads them every night from Yahoo Finance into `data/`.

| File | ETF | ISIN |
|---|---|---|
| `data/world_islamic_usd.csv` | iShares MSCI World Islamic UCITS ETF (London, USD) | IE00B27YCN58 |
| `data/usa_islamic_usd.csv` | iShares MSCI USA Islamic UCITS ETF (London, USD) | IE00B296QM64 |
| `data/em_islamic_usd.csv` | iShares MSCI Emerging Markets Islamic UCITS ETF (London, USD) | IE00B27YCP72 |

Columns: `date, close, adj_close, clean, volume`. `adj_close` includes dividends; `clean` is `adj_close` with Yahoo's pence/cent mix-ups repaired (use this one). `data/gbpusd.csv` holds the exchange rate used for the repair. Prices only, for personal research. Not investment advice.
