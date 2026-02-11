"""
云端数据API服务器
提供RESTful API供本地客户端调用
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
import os
import gzip
import io

app = Flask(__name__)
CORS(app)  # 允许跨域访问

DB_PATH = 'crypto_data.db'

def get_db():
    """获取数据库连接"""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

# ==================== 健康检查 ====================
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'timestamp': int(datetime.now().timestamp() * 1000),
        'version': '1.0'
    })

# ==================== 数据统计 ====================
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取数据库统计信息"""
    db = get_db()
    cursor = db.cursor()
    
    stats = {}
    
    # 统计各个表的数据量
    tables = ['trades', 'orderbook', 'klines', 'ticker_24h', 
              'open_interest', 'funding_rate', 'long_short_ratio', 'top_trader_position']
    
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
            stats[table] = cursor.fetchone()['count']
        except:
            stats[table] = 0
    
    # 获取最新数据时间
    try:
        cursor.execute('SELECT MAX(timestamp) as latest FROM trades')
        latest = cursor.fetchone()['latest']
        stats['latest_data_time'] = latest
    except:
        stats['latest_data_time'] = None
    
    db.close()
    
    return jsonify({
        'status': 'success',
        'data': stats
    })

# ==================== 实时价格 ====================
@app.route('/api/price/<symbol>', methods=['GET'])
def get_latest_price(symbol):
    """获取最新价格"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT price, timestamp 
        FROM trades 
        WHERE symbol = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''', (symbol.lower(),))
    
    row = cursor.fetchone()
    db.close()
    
    if row:
        return jsonify({
            'status': 'success',
            'data': {
                'symbol': symbol,
                'price': row['price'],
                'timestamp': row['timestamp']
            }
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'No data found'
        }), 404

# ==================== 交易数据 ====================
@app.route('/api/trades/<symbol>', methods=['GET'])
def get_trades(symbol):
    """获取交易数据"""
    # 参数：limit（默认100）, start_time, end_time
    limit = request.args.get('limit', 100, type=int)
    start_time = request.args.get('start_time', type=int)
    end_time = request.args.get('end_time', type=int)
    
    db = get_db()
    cursor = db.cursor()
    
    query = 'SELECT * FROM trades WHERE symbol = ?'
    params = [symbol.lower()]
    
    if start_time:
        query += ' AND timestamp >= ?'
        params.append(start_time)
    
    if end_time:
        query += ' AND timestamp <= ?'
        params.append(end_time)
    
    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    db.close()
    
    trades = [dict(row) for row in rows]
    
    return jsonify({
        'status': 'success',
        'count': len(trades),
        'data': trades
    })

# ==================== K线数据 ====================
@app.route('/api/klines/<symbol>/<interval>', methods=['GET'])
def get_klines(symbol, interval):
    """获取K线数据"""
    limit = request.args.get('limit', 100, type=int)
    start_time = request.args.get('start_time', type=int)
    
    db = get_db()
    cursor = db.cursor()
    
    query = '''
        SELECT * FROM klines 
        WHERE symbol = ? AND interval = ?
    '''
    params = [symbol.lower(), interval]
    
    if start_time:
        query += ' AND open_time >= ?'
        params.append(start_time)
    
    query += ' ORDER BY open_time DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    db.close()
    
    klines = [dict(row) for row in rows]
    
    return jsonify({
        'status': 'success',
        'symbol': symbol,
        'interval': interval,
        'count': len(klines),
        'data': klines
    })

# ==================== 合约数据 ====================
@app.route('/api/futures/open_interest/<symbol>', methods=['GET'])
def get_open_interest(symbol):
    """获取持仓量数据"""
    limit = request.args.get('limit', 100, type=int)
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT * FROM open_interest 
        WHERE symbol = ?
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (symbol.lower(), limit))
    
    rows = cursor.fetchall()
    db.close()
    
    data = [dict(row) for row in rows]
    
    return jsonify({
        'status': 'success',
        'count': len(data),
        'data': data
    })

@app.route('/api/futures/funding_rate/<symbol>', methods=['GET'])
def get_funding_rate(symbol):
    """获取资金费率"""
    limit = request.args.get('limit', 100, type=int)
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT * FROM funding_rate 
        WHERE symbol = ?
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (symbol.lower(), limit))
    
    rows = cursor.fetchall()
    db.close()
    
    data = [dict(row) for row in rows]
    
    return jsonify({
        'status': 'success',
        'count': len(data),
        'data': data
    })

@app.route('/api/futures/long_short_ratio/<symbol>', methods=['GET'])
def get_long_short_ratio(symbol):
    """获取多空比"""
    limit = request.args.get('limit', 100, type=int)
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT * FROM long_short_ratio 
        WHERE symbol = ?
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (symbol.lower(), limit))
    
    rows = cursor.fetchall()
    db.close()
    
    data = [dict(row) for row in rows]
    
    return jsonify({
        'status': 'success',
        'count': len(data),
        'data': data
    })

# ==================== 数据下载 ====================
@app.route('/api/download/database', methods=['GET'])
def download_database():
    """下载整个数据库文件（压缩）"""
    if not os.path.exists(DB_PATH):
        return jsonify({
            'status': 'error',
            'message': 'Database not found'
        }), 404
    
    # 压缩数据库文件
    memory_file = io.BytesIO()
    with open(DB_PATH, 'rb') as f:
        with gzip.GzipFile(fileobj=memory_file, mode='wb') as gz:
            gz.write(f.read())
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/gzip',
        as_attachment=True,
        download_name=f'crypto_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db.gz'
    )

@app.route('/api/export/<table>', methods=['GET'])
def export_table(table):
    """导出指定表为JSON"""
    allowed_tables = ['trades', 'orderbook', 'klines', 'ticker_24h', 
                      'open_interest', 'funding_rate', 'long_short_ratio', 'top_trader_position']
    
    if table not in allowed_tables:
        return jsonify({
            'status': 'error',
            'message': 'Invalid table name'
        }), 400
    
    symbol = request.args.get('symbol')
    limit = request.args.get('limit', 10000, type=int)
    
    db = get_db()
    cursor = db.cursor()
    
    query = f'SELECT * FROM {table}'
    params = []
    
    if symbol:
        query += ' WHERE symbol = ?'
        params.append(symbol.lower())
    
    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    db.close()
    
    data = [dict(row) for row in rows]
    
    return jsonify({
        'status': 'success',
        'table': table,
        'count': len(data),
        'data': data
    })

# ==================== 多币种聚合 ====================
@app.route('/api/multi/prices', methods=['GET'])
def get_multi_prices():
    """获取所有币种的最新价格"""
    symbols = ['ethusdt', 'btcusdt', 'bnbusdt', 'solusdt']
    
    db = get_db()
    cursor = db.cursor()
    
    prices = {}
    for symbol in symbols:
        cursor.execute('''
            SELECT price, timestamp 
            FROM trades 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (symbol,))
        
        row = cursor.fetchone()
        if row:
            prices[symbol] = {
                'price': row['price'],
                'timestamp': row['timestamp']
            }
    
    db.close()
    
    return jsonify({
        'status': 'success',
        'data': prices
    })

@app.route('/api/multi/summary', methods=['GET'])
def get_multi_summary():
    """获取所有币种的综合数据摘要"""
    symbols = ['ethusdt', 'btcusdt', 'bnbusdt', 'solusdt']
    
    db = get_db()
    cursor = db.cursor()
    
    summary = {}
    
    for symbol in symbols:
        # 最新价格
        cursor.execute('''
            SELECT price, timestamp 
            FROM trades 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (symbol,))
        price_row = cursor.fetchone()
        
        # 24h统计
        cursor.execute('''
            SELECT * FROM ticker_24h 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (symbol,))
        ticker_row = cursor.fetchone()
        
        # 资金费率
        cursor.execute('''
            SELECT funding_rate 
            FROM funding_rate 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (symbol,))
        fr_row = cursor.fetchone()
        
        summary[symbol] = {
            'price': price_row['price'] if price_row else None,
            'price_change_percent': ticker_row['price_change_percent'] if ticker_row else None,
            'volume_24h': ticker_row['volume'] if ticker_row else None,
            'funding_rate': fr_row['funding_rate'] if fr_row else None
        }
    
    db.close()
    
    return jsonify({
        'status': 'success',
        'data': summary
    })

if __name__ == '__main__':
    # 生产环境使用 gunicorn 或 uwsgi
    # 开发环境可以直接运行
    app.run(host='0.0.0.0', port=5001, debug=False)
