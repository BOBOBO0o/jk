# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
db = sqlite3.connect('crypto_data.db')
c = db.cursor()

tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    name = t[0]
    cnt = c.execute(f'SELECT COUNT(*) FROM [{name}]').fetchone()[0]
    cols = [d[0] for d in c.execute(f'SELECT * FROM [{name}] LIMIT 1').description] if cnt > 0 else []
    print(f'{name}: {cnt} rows | {cols}')

# 全市场24h数据对比
print('\n=== 24H TICKER ALL SYMBOLS ===')
rows = c.execute('SELECT symbol, price_change_percent, last_price, volume, quote_volume FROM ticker_24h ORDER BY timestamp DESC').fetchall()
seen = set()
for r in rows:
    if r[0] not in seen:
        seen.add(r[0])
        print(f'{r[0]:10s} chg:{r[1]:>8}%  price:{r[2]:>12}  vol:{float(r[3]):>15,.2f}  quote_vol:{float(r[4]):>18,.2f}')

# 全市场合约数据对比
print('\n=== FUTURES OVERVIEW ===')
for sym in ['btcusdt','ethusdt','solusdt','bnbusdt']:
    oi = c.execute('SELECT open_interest, open_interest_value FROM open_interest WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
    fr = c.execute('SELECT funding_rate FROM funding_rate WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
    lsr = c.execute('SELECT long_short_ratio, long_account, short_account FROM long_short_ratio WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
    
    oi_str = f'OI_val: ${oi[1]:>15,.0f}' if oi else 'OI: N/A'
    fr_str = f'Fund: {fr[0]*100:>8.4f}%' if fr else 'Fund: N/A'
    lsr_str = f'LS: {lsr[0]:>6.3f} (L:{lsr[1]:.1f}% S:{lsr[2]:.1f}%)' if lsr else 'LS: N/A'
    print(f'{sym.upper():10s} {oi_str}  {fr_str}  {lsr_str}')

# 全市场成交额占比
print('\n=== QUOTE VOLUME SHARE ===')
total_qv = 0
qvs = {}
for sym in ['btcusdt','ethusdt','solusdt','bnbusdt']:
    r = c.execute('SELECT quote_volume FROM ticker_24h WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
    if r:
        qv = float(r[0])
        qvs[sym] = qv
        total_qv += qv

for sym, qv in qvs.items():
    pct = qv / total_qv * 100 if total_qv > 0 else 0
    print(f'{sym.upper():10s} ${qv:>18,.2f}  ({pct:.1f}%)')
print(f'{"TOTAL":10s} ${total_qv:>18,.2f}')

# 资金费率汇总 - 判断全市场情绪
print('\n=== FUNDING RATE SENTIMENT ===')
neg_count = 0
for sym in ['btcusdt','ethusdt','solusdt','bnbusdt']:
    fr = c.execute('SELECT funding_rate FROM funding_rate WHERE symbol=? ORDER BY timestamp DESC LIMIT 1', (sym,)).fetchone()
    if fr and fr[0] < 0:
        neg_count += 1
print(f'Negative funding: {neg_count}/4 symbols')
if neg_count >= 3:
    print('=> Market-wide SHORT bias')
elif neg_count == 0:
    print('=> Market-wide LONG bias')
else:
    print('=> Mixed sentiment')

db.close()
