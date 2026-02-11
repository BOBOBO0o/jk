# -*- coding: utf-8 -*-
import sqlite3, sys, io
from datetime import datetime, timedelta
from indicators import TechnicalIndicators

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db = sqlite3.connect('crypto_data.db')
c = db.cursor()

symbols = ['btcusdt','ethusdt','solusdt','bnbusdt']

for sym in symbols:
    print(f'\n{"="*60}')
    print(f'  {sym.upper()}')
    print(f'{"="*60}')
    
    row = c.execute('SELECT close, volume, open FROM klines WHERE symbol=? AND interval="1m" ORDER BY open_time DESC LIMIT 1', (sym,)).fetchone()
    if row:
        print(f'Price: {row[0]}  1m_vol: {row[1]}')
    
    row24 = c.execute('SELECT price_change_percent, last_price, volume, quote_volume FROM ticker_24h WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
    if row24:
        print(f'24h_chg: {row24[0]}%  last: {row24[1]}  vol: {row24[2]:.2f}  quote_vol: {row24[3]:.2f}')
    
    for tf, label in [('1h','1H'), ('4h','4H'), ('1d','1D')]:
        klines = c.execute(f'SELECT open_time, open, high, low, close, volume FROM klines WHERE symbol=? AND interval="{tf}" ORDER BY open_time DESC LIMIT 200', (sym,)).fetchall()
        klines = list(reversed(klines))
        if len(klines) >= 30:
            ind = TechnicalIndicators.calculate_all_indicators(klines)
            print(f'\n--- {label} ---')
            print(f'EMA12: {ind["ema_12"]}  EMA26: {ind["ema_26"]}')
            m = ind["macd"]
            print(f'MACD: {m["macd"]}  Signal: {m["signal"]}  Hist: {m["histogram"]}  Trend: {m["trend"]}')
            print(f'RSI: {ind["rsi"]}  ATR: {ind["atr"]}')
            b = ind["bollinger"]
            print(f'BOLL: U={b["upper"]} M={b["middle"]} L={b["lower"]} Pos={b["position"]}')
    
    ts_1h = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
    ts = c.execute('''
        SELECT COUNT(*),
            SUM(CASE WHEN is_buyer_maker=0 THEN quantity ELSE 0 END),
            SUM(CASE WHEN is_buyer_maker=1 THEN quantity ELSE 0 END)
        FROM trades WHERE symbol=? AND timestamp > ?
    ''', (sym, ts_1h)).fetchone()
    if ts and ts[0] > 0:
        bv = ts[1] or 0
        sv = ts[2] or 0
        r = bv/sv if sv > 0 else 0
        print(f'\n--- Trade Flow 1H ---')
        print(f'Trades: {ts[0]}  Buy: {bv:.4f}  Sell: {sv:.4f}  B/S_ratio: {r:.3f}')
    
    print(f'\n--- Futures ---')
    try:
        oi = c.execute('SELECT open_interest, open_interest_value FROM open_interest WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
        if oi:
            print(f'OI: {oi[0]}  OI_value: ${oi[1]:,.0f}')
    except Exception:
        print('OI: N/A')
    
    try:
        fr = c.execute('SELECT funding_rate FROM funding_rate WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
        if fr:
            print(f'Funding: {fr[0]*100:.4f}%')
    except Exception:
        print('Funding: N/A')
    
    try:
        lsr = c.execute('SELECT long_short_ratio, long_account, short_account FROM long_short_ratio WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
        if lsr:
            print(f'LS_ratio: {lsr[0]}  Long: {lsr[1]:.1f}%  Short: {lsr[2]:.1f}%')
    except Exception:
        print('LS_ratio: N/A')
    
    try:
        tp = c.execute('SELECT long_position_ratio, short_position_ratio, long_account_ratio, short_account_ratio FROM top_trader_position WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
        if tp:
            print(f'TopTrader Pos L:{tp[0]:.1f}% S:{tp[1]:.1f}%  Acc L:{tp[2]:.1f}% S:{tp[3]:.1f}%')
    except Exception:
        print('TopTrader: N/A')

db.close()
