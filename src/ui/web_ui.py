"""
Web用户界面 - 可视化实时数据和AI分析
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json
import threading
import time

app = Flask(__name__)
CORS(app)

def get_db():
    """获取数据库连接"""
    return sqlite3.connect('crypto_data.db')

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # 检查各个数据表的记录数
        trades_count = cursor.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        klines_count = cursor.execute("SELECT COUNT(*) FROM klines").fetchone()[0]
        orderbook_count = cursor.execute("SELECT COUNT(*) FROM orderbook").fetchone()[0]
        
        # 最新交易时间
        latest_trade = cursor.execute("""
            SELECT timestamp FROM trades ORDER BY timestamp DESC LIMIT 1
        """).fetchone()
        
        last_update = None
        if latest_trade:
            last_update = datetime.fromtimestamp(latest_trade[0]/1000).strftime('%Y-%m-%d %H:%M:%S')
        
        db.close()
        
        return jsonify({
            'status': 'running',
            'trades_count': trades_count,
            'klines_count': klines_count,
            'orderbook_count': orderbook_count,
            'last_update': last_update
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/current_price')
def get_current_price():
    """获取当前价格"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # 最近10笔交易的平均价格
        recent_trades = cursor.execute("""
            SELECT price, timestamp FROM trades 
            ORDER BY timestamp DESC LIMIT 10
        """).fetchall()
        
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
            ORDER BY timestamp DESC LIMIT 1
        """).fetchone()
        
        db.close()
        
        return jsonify({
            'current_price': round(avg_price, 2),
            'latest_time': latest_time,
            'change_24h': round(ticker_24h[0], 2) if ticker_24h else 0,
            'volume_24h': round(ticker_24h[1], 2) if ticker_24h else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/recent_trades')
def get_recent_trades():
    """获取最近的交易"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        trades = cursor.execute("""
            SELECT price, quantity, is_buyer_maker, timestamp 
            FROM trades 
            ORDER BY timestamp DESC LIMIT 50
        """).fetchall()
        
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

@app.route('/api/chart_data')
def get_chart_data():
    """获取K线图表数据"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # 获取最近100根K线
        klines = cursor.execute("""
            SELECT open_time, open, high, low, close, volume 
            FROM klines 
            ORDER BY open_time DESC LIMIT 100
        """).fetchall()
        
        db.close()
        
        # 反转顺序（从旧到新）
        klines = list(reversed(klines))
        
        chart_data = {
            'times': [datetime.fromtimestamp(k[0]/1000).strftime('%H:%M') for k in klines],
            'prices': [round(k[4], 2) for k in klines],  # close价格
            'volumes': [round(k[5], 2) for k in klines]
        }
        
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/market_stats')
def get_market_stats():
    """获取市场统计"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # 最近1小时的买卖压力
        timestamp_1h = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
        
        buy_sell = cursor.execute("""
            SELECT 
                SUM(CASE WHEN is_buyer_maker=0 THEN quantity ELSE 0 END) as buy_volume,
                SUM(CASE WHEN is_buyer_maker=1 THEN quantity ELSE 0 END) as sell_volume
            FROM trades WHERE timestamp > ?
        """, (timestamp_1h,)).fetchone()
        
        buy_volume = buy_sell[0] if buy_sell[0] else 0
        sell_volume = buy_sell[1] if buy_sell[1] else 0
        buy_sell_ratio = round(buy_volume / sell_volume, 2) if sell_volume > 0 else 0
        
        # 最新订单簿
        orderbook = cursor.execute("""
            SELECT bids, asks FROM orderbook 
            ORDER BY timestamp DESC LIMIT 1
        """).fetchone()
        
        orderbook_ratio = 1.0
        if orderbook:
            try:
                bids = json.loads(orderbook[0])
                asks = json.loads(orderbook[1])
                total_bids = sum([float(b[1]) for b in bids[:20]])
                total_asks = sum([float(a[1]) for a in asks[:20]])
                orderbook_ratio = round(total_bids / total_asks, 2) if total_asks > 0 else 1.0
            except:
                pass
        
        db.close()
        
        return jsonify({
            'buy_volume': round(buy_volume, 2),
            'sell_volume': round(sell_volume, 2),
            'buy_sell_ratio': buy_sell_ratio,
            'orderbook_ratio': orderbook_ratio
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/ai_analysis')
def get_ai_analysis():
    """获取AI分析结果"""
    try:
        from ai_analyzer import AIAnalyzer
        
        analyzer = AIAnalyzer()
        data = analyzer.get_recent_data(hours=1)
        
        # 检查LM Studio
        lm_available = analyzer.test_lm_studio_connection()
        
        if lm_available:
            analysis = analyzer.analyze_with_lm_studio(data)
        else:
            analysis = analyzer.generate_simple_signal(data)
        
        return jsonify({
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
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🌐 ETH 交易系统 Web界面                                  ║
║                                                                  ║
║         访问地址: http://localhost:5000                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=False, host='0.0.0.0', port=5000)
