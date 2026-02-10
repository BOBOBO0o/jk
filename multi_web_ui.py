"""
多币种Web界面 - 支持BTC、ETH、BNB、SOL、BERA
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

# 支持的交易对
SYMBOLS = {
    'ethusdt': 'ETH',
    'btcusdt': 'BTC',
    'bnbusdt': 'BNB',
    'solusdt': 'SOL',
    'berausdt': 'BERA'
}

def get_db():
    """获取数据库连接"""
    return sqlite3.connect('crypto_data.db')

def get_symbol_table_prefix(symbol):
    """获取交易对的表前缀"""
    return symbol.replace('usdt', '').lower()

@app.route('/')
def index():
    """主页"""
    return render_template('multi_index.html', symbols=SYMBOLS)

@app.route('/enhanced')
def enhanced():
    """增强版界面 - 支持AI配置"""
    return render_template('multi_index_enhanced.html', symbols=SYMBOLS)

@app.route('/api/symbols')
def get_symbols():
    """获取所有支持的交易对"""
    return jsonify(list(SYMBOLS.keys()))

@app.route('/api/overview')
def get_overview():
    """获取所有币种的概览"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        overview = []
        
        for symbol_key, symbol_name in SYMBOLS.items():
            try:
                # 获取最近10笔交易的平均价格
                recent_trades = cursor.execute(f"""
                    SELECT price, timestamp FROM trades 
                    WHERE symbol = ?
                    ORDER BY timestamp DESC LIMIT 10
                """, (symbol_key,)).fetchall()
                
                if recent_trades:
                    avg_price = sum([t[0] for t in recent_trades]) / len(recent_trades)
                    
                    # 获取24小时统计
                    ticker_24h = cursor.execute("""
                        SELECT price_change_percent, volume 
                        FROM ticker_24h 
                        WHERE symbol = ?
                        ORDER BY timestamp DESC LIMIT 1
                    """, (symbol_key,)).fetchone()
                    
                    # 计算1小时买卖比
                    timestamp_1h = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
                    buy_sell = cursor.execute("""
                        SELECT 
                            SUM(CASE WHEN is_buyer_maker=0 THEN quantity ELSE 0 END) as buy_volume,
                            SUM(CASE WHEN is_buyer_maker=1 THEN quantity ELSE 0 END) as sell_volume
                        FROM trades WHERE symbol = ? AND timestamp > ?
                    """, (symbol_key, timestamp_1h)).fetchone()
                    
                    buy_volume = buy_sell[0] if buy_sell and buy_sell[0] else 0
                    sell_volume = buy_sell[1] if buy_sell and buy_sell[1] else 0
                    buy_sell_ratio = round(buy_volume / sell_volume, 2) if sell_volume > 0 else 0
                    
                    overview.append({
                        'symbol': symbol_key,
                        'name': symbol_name,
                        'price': round(avg_price, 2),
                        'change_24h': round(ticker_24h[0], 2) if ticker_24h else 0,
                        'volume_24h': round(ticker_24h[1], 2) if ticker_24h else 0,
                        'buy_sell_ratio': buy_sell_ratio,
                        'available': True
                    })
                else:
                    overview.append({
                        'symbol': symbol_key,
                        'name': symbol_name,
                        'price': 0,
                        'change_24h': 0,
                        'volume_24h': 0,
                        'buy_sell_ratio': 0,
                        'available': False
                    })
            except Exception as e:
                print(f"Error getting data for {symbol_key}: {e}")
                overview.append({
                    'symbol': symbol_key,
                    'name': symbol_name,
                    'price': 0,
                    'change_24h': 0,
                    'volume_24h': 0,
                    'buy_sell_ratio': 0,
                    'available': False
                })
        
        db.close()
        return jsonify(overview)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/symbol/<symbol>/price')
def get_symbol_price(symbol):
    """获取指定交易对的价格"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # 最近10笔交易的平均价格
        recent_trades = cursor.execute("""
            SELECT price, timestamp FROM trades 
            WHERE symbol = ?
            ORDER BY timestamp DESC LIMIT 10
        """, (symbol,)).fetchall()
        
        if recent_trades:
            avg_price = sum([t[0] for t in recent_trades]) / len(recent_trades)
            latest_time = datetime.fromtimestamp(recent_trades[0][1]/1000).strftime('%H:%M:%S')
        else:
            avg_price = 0
            latest_time = 'N/A'
        
        # 24小时统计
        ticker_24h = cursor.execute("""
            SELECT price_change_percent, volume, last_price 
            FROM ticker_24h 
            WHERE symbol = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (symbol,)).fetchone()
        
        db.close()
        
        return jsonify({
            'symbol': symbol,
            'current_price': round(avg_price, 2),
            'latest_time': latest_time,
            'change_24h': round(ticker_24h[0], 2) if ticker_24h else 0,
            'volume_24h': round(ticker_24h[1], 2) if ticker_24h else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/symbol/<symbol>/trades')
def get_symbol_trades(symbol):
    """获取指定交易对的最近交易"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        trades = cursor.execute("""
            SELECT price, quantity, is_buyer_maker, timestamp 
            FROM trades 
            WHERE symbol = ?
            ORDER BY timestamp DESC LIMIT 50
        """, (symbol,)).fetchall()
        
        db.close()
        
        trades_list = []
        for t in trades:
            trades_list.append({
                'price': round(t[0], 2),
                'quantity': round(t[1], 4),
                'side': 'BUY' if t[2] == 0 else 'SELL',
                'time': datetime.fromtimestamp(t[3]/1000).strftime('%H:%M:%S')
            })
        
        return jsonify(trades_list)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/symbol/<symbol>/analysis', methods=['GET', 'POST'])
def get_symbol_analysis(symbol):
    """获取指定交易对的AI分析（支持配置）"""
    try:
        from ai_analyzer import AIAnalyzer
        
        analyzer = AIAnalyzer(symbol=symbol)
        data = analyzer.get_recent_data(hours=1)
        
        lm_available = analyzer.test_lm_studio_connection()
        
        # 获取用户配置（如果是POST请求）
        config = None
        if request.method == 'POST' and request.is_json:
            config = request.get_json()
            print(f"收到配置: {config}")
        
        if lm_available:
            analysis = analyzer.analyze_with_lm_studio(data, config=config)
        else:
            analysis = analyzer.generate_simple_signal(data)
        
        return jsonify({
            'symbol': symbol,
            'analysis': analysis,
            'data': {
                'avg_price': round(data['avg_price'], 2),
                'buy_sell_ratio': round(data['buy_sell_ratio'], 2),
                'orderbook_ratio': round(data['orderbook_ratio'], 2),
                'price_trend': data['price_trend']
            },
            'lm_studio_active': lm_available,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        import traceback
        print(f"分析错误: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)})

@app.route('/api/compare')
def compare_symbols():
    """对比所有交易对"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        comparison = []
        timestamp_1h = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
        
        for symbol_key, symbol_name in SYMBOLS.items():
            try:
                # 获取价格变化
                recent_price = cursor.execute("""
                    SELECT price FROM trades WHERE symbol = ? ORDER BY timestamp DESC LIMIT 1
                """, (symbol_key,)).fetchone()
                
                old_price = cursor.execute("""
                    SELECT price FROM trades WHERE symbol = ? AND timestamp < ? ORDER BY timestamp DESC LIMIT 1
                """, (symbol_key, timestamp_1h)).fetchone()
                
                if recent_price and old_price:
                    price_change = ((recent_price[0] - old_price[0]) / old_price[0]) * 100
                else:
                    price_change = 0
                
                comparison.append({
                    'symbol': symbol_name,
                    'price_change_1h': round(price_change, 2)
                })
            except:
                pass
        
        db.close()
        return jsonify(comparison)
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🌐 多币种交易系统 Web界面                                 ║
║                                                                  ║
║         支持: ETH, BTC, BNB, SOL, BERA                           ║
║         访问地址: http://localhost:5000                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=False, host='0.0.0.0', port=5000)
