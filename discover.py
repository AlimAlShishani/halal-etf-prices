import yfinance as yf
for isin in ['IE00B27YCN58', 'IE00B296QM64', 'IE00B27YCP72']:
    print('==', isin)
    try:
        for q in yf.Search(isin, max_results=20).quotes:
            sym = q.get('symbol')
            try:
                h = yf.Ticker(sym).history(period='max', auto_adjust=False)
                info = f"{len(h)} rows {h.index[0].date()}..{h.index[-1].date()} last {h['Close'].iloc[-1]:.3f}" if len(h) else 'no history'
            except Exception as e: info = f'err {e}'
            print(sym, q.get('exchange'), q.get('exchDisp'), q.get('quoteType'), '|', info)
    except Exception as e: print('search failed', e)
for sym in ['ISWD.L', 'ISUS.L', 'ISDE.L']:
    try: print(sym, yf.Ticker(sym).fast_info.get('currency'))
    except Exception as e: print(sym, 'err', e)
