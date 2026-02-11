import websocket
import json
import sqlite3
from datetime import datetime
import threading
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BinanceDataCollector:
    def __init__(self, symbol='ethusdt'):
        self.symbol = symbol.lower()
        self.db = sqlite3.connect('crypto_data.db', check_same_thread=False)
        self.lock = threading.Lock()
        self.init_database()
        self.fetch_historical_klines()  # 获取历史K线
        
    def init_database(self):
        """初始化数据库表"""
        cursor = self.db.cursor()
        
        # 交易流水表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp INTEGER,
                price REAL,
                quantity REAL,
                is_buyer_maker INTEGER,
                trade_id INTEGER
            )
        ''')
        
        # 为旧数据添加symbol列（如果不存在）
        try:
            cursor.execute('ALTER TABLE trades ADD COLUMN symbol TEXT')
        except:
            pass
        
        # 订单簿表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orderbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp INTEGER,
                bids TEXT,
                asks TEXT
            )
        ''')
        
        try:
            cursor.execute('ALTER TABLE orderbook ADD COLUMN symbol TEXT')
        except:
            pass
        
        # K线表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS klines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                interval TEXT,
                open_time INTEGER,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                close_time INTEGER,
                quote_volume REAL,
                trades_count INTEGER,
                taker_buy_volume REAL,
                taker_buy_quote_volume REAL
            )
        ''')
        
        # 为旧表添加字段
        try:
            cursor.execute('ALTER TABLE klines ADD COLUMN symbol TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE klines ADD COLUMN interval TEXT')
        except:
            pass
        
        # 24小时统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticker_24h (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp INTEGER,
                price_change REAL,
                price_change_percent REAL,
                weighted_avg_price REAL,
                last_price REAL,
                volume REAL,
                quote_volume REAL
            )
        ''')
        
        try:
            cursor.execute('ALTER TABLE ticker_24h ADD COLUMN symbol TEXT')
        except:
            pass
        
        self.db.commit()
        print("✅ Database initialized")
    
    def fetch_historical_klines(self):
        """获取历史K线数据"""
        import requests
        
        intervals = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
        limits = {
            '1m': 500,   # 最近500分钟
            '5m': 500,   # 最近2500分钟
            '15m': 500,  # 最近7500分钟
            '30m': 500,  # 最近15000分钟
            '1h': 500,   # 最近500小时
            '4h': 500,   # 最近2000小时
            '1d': 365    # 最近365天
        }
        
        print(f"\n📋 正在获取 {self.symbol.upper()} 的历史K线数据...")
        
        for interval in intervals:
            try:
                url = "https://api.binance.com/api/v3/klines"
                params = {
                    'symbol': self.symbol.upper(),
                    'interval': interval,
                    'limit': limits[interval]
                }
                
                response = requests.get(url, params=params, timeout=10, verify=False)
                
                if response.status_code == 200:
                    klines = response.json()
                    
                    with self.lock:
                        cursor = self.db.cursor()
                        count = 0
                        
                        for k in klines:
                            # k = [open_time, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_volume, taker_buy_quote_volume, ignore]
                            cursor.execute('''
                                INSERT INTO klines VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                self.symbol,
                                interval,
                                int(k[0]),      # open_time
                                float(k[1]),    # open
                                float(k[2]),    # high
                                float(k[3]),    # low
                                float(k[4]),    # close
                                float(k[5]),    # volume
                                int(k[6]),      # close_time
                                float(k[7]),    # quote_volume
                                int(k[8]),      # trades_count
                                float(k[9]),    # taker_buy_volume
                                float(k[10])    # taker_buy_quote_volume
                            ))
                            count += 1
                        
                        self.db.commit()
                    
                    print(f"  ✅ {interval:3s}: 获取 {count} 条K线")
                    time.sleep(0.5)  # 避免请求限制
                    
                else:
                    print(f"  ❌ {interval}: API错误 {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {interval}: 获取失败 - {e}")
        
        print(f"✅ 历史K线数据获取完成!\n")
    
    def collect_trades(self):
        """采集实时成交数据"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                # 聚合成交数据格式: a=聚合ID, p=价格, q=数量, T=时间, m=买方是否maker
                with self.lock:
                    cursor = self.db.cursor()
                    cursor.execute('''
                        INSERT INTO trades (symbol, timestamp, price, quantity, is_buyer_maker, trade_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        self.symbol,
                        data['T'],
                        float(data['p']),
                        float(data['q']),
                        1 if data['m'] else 0,
                        data.get('a', data.get('t', 0))  # 使用聚合ID或交易ID
                    ))
                    self.db.commit()
                print(f"[Trade] Price: ${data['p']}, Qty: {data['q']}, Buyer: {'Yes' if not data['m'] else 'No'}")
            except Exception as e:
                print(f"Trade error: {e}")
        
        def on_error(ws, error):
            print(f"Trade WebSocket Error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print("Trade WebSocket closed, reconnecting...")
            time.sleep(5)
            self.collect_trades()
        
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@aggTrade"
        ws = websocket.WebSocketApp(
            ws_url, 
            on_message=on_message, 
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever()
    
    def collect_orderbook(self):
        """采集订单簿数据（每秒一次）"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                # 深度数据格式: bids=买盘, asks=卖盘
                bids = data.get('bids', [])
                asks = data.get('asks', [])
                
                if not bids or not asks:
                    return
                    
                with self.lock:
                    cursor = self.db.cursor()
                    cursor.execute('''
                        INSERT INTO orderbook (symbol, timestamp, bids, asks)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        self.symbol,
                        int(datetime.now().timestamp() * 1000),
                        json.dumps(bids[:20]),
                        json.dumps(asks[:20])
                    ))
                    self.db.commit()
                
                # 计算买卖压力
                total_bids = sum([float(b[1]) for b in bids[:20]])
                total_asks = sum([float(a[1]) for a in asks[:20]])
                ratio = total_bids / total_asks if total_asks > 0 else 0
                print(f"[OrderBook] Bid/Ask Ratio: {ratio:.2f} (Bids: {total_bids:.2f}, Asks: {total_asks:.2f})")
            except Exception as e:
                print(f"OrderBook error: {e}")
        
        def on_error(ws, error):
            print(f"OrderBook WebSocket Error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print("OrderBook WebSocket closed, reconnecting...")
            time.sleep(5)
            self.collect_orderbook()
        
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@depth@1000ms"
        ws = websocket.WebSocketApp(
            ws_url, 
            on_message=on_message, 
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever()
    
    def collect_klines(self, interval='1m'):
        """采集K线数据"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                k = data['k']
                if k['x']:  # K线已完成
                    with self.lock:
                        cursor = self.db.cursor()
                        cursor.execute('''
                            INSERT INTO klines VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            self.symbol,
                            interval,
                            k['t'], float(k['o']), float(k['h']), float(k['l']),
                            float(k['c']), float(k['v']), k['T'], float(k['q']),
                            k['n'], float(k['V']), float(k['Q'])
                        ))
                        self.db.commit()
                    print(f"[Kline-{interval}] Close: ${k['c']}, Volume: {k['v']}, Trades: {k['n']}")
            except Exception as e:
                print(f"Kline error: {e}")
        
        def on_error(ws, error):
            print(f"Kline WebSocket Error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print("Kline WebSocket closed, reconnecting...")
            time.sleep(5)
            self.collect_klines(interval)
        
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_{interval}"
        ws = websocket.WebSocketApp(
            ws_url, 
            on_message=on_message, 
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever()
    
    def collect_ticker_24h(self):
        """采集24小时统计数据（每分钟一次）"""
        import requests
        
        while True:
            try:
                url = f"https://api.binance.com/api/v3/ticker/24hr"
                params = {'symbol': self.symbol.upper()}
                response = requests.get(url, params=params, timeout=10, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    with self.lock:
                        cursor = self.db.cursor()
                        cursor.execute('''
                            INSERT INTO ticker_24h VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            self.symbol,
                            int(datetime.now().timestamp() * 1000),
                            float(data['priceChange']),
                            float(data['priceChangePercent']),
                            float(data['weightedAvgPrice']),
                            float(data['lastPrice']),
                            float(data['volume']),
                            float(data['quoteVolume'])
                        ))
                        self.db.commit()
                    print(f"[24h Stats] Price: ${data['lastPrice']}, Change: {data['priceChangePercent']}%, Volume: {data['volume']}")
                else:
                    print(f"24h Stats API error: {response.status_code}")
                
            except Exception as e:
                print(f"24h Stats error: {e}")
            
            time.sleep(60)  # 每分钟更新一次
    
    def start_collection(self):
        """启动多线程采集"""
        print(f"🚀 Starting data collection for {self.symbol.upper()}...")
        
        # 多时间周期K线采集
        kline_intervals = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
        
        threads = [
            threading.Thread(target=self.collect_trades, daemon=True, name="Trades"),
            threading.Thread(target=self.collect_orderbook, daemon=True, name="OrderBook"),
            threading.Thread(target=self.collect_ticker_24h, daemon=True, name="24h Stats"),
        ]
        
        # 为每个时间周期创建独立的K线采集线程
        for interval in kline_intervals:
            t = threading.Thread(
                target=self.collect_klines, 
                args=(interval,),
                daemon=True, 
                name=f"Kline-{interval}"
            )
            threads.append(t)
        
        for t in threads:
            t.start()
            print(f"✅ {t.name} thread started")
        
        print("📊 Data collection running...\n")
        
        # 保持主线程运行
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            print("\n⛔ Stopping data collection...")

if __name__ == '__main__':
    collector = BinanceDataCollector('ethusdt')
    collector.start_collection()
