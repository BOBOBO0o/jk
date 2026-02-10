"""
合约数据采集器 - 获取持仓量、资金费率、多空比等
"""
import requests
import sqlite3
import time
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FuturesDataCollector:
    def __init__(self, symbol='ETHUSDT'):
        """
        初始化合约数据采集器
        symbol: 交易对（大写），如 'ETHUSDT', 'BTCUSDT'
        """
        self.symbol = symbol.upper()
        self.db = sqlite3.connect('crypto_data.db', check_same_thread=False)
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        cursor = self.db.cursor()
        
        # 持仓量表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS open_interest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp INTEGER,
                open_interest REAL,
                open_interest_value REAL
            )
        ''')
        
        # 资金费率表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funding_rate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp INTEGER,
                funding_rate REAL,
                next_funding_time INTEGER
            )
        ''')
        
        # 多空比表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS long_short_ratio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp INTEGER,
                long_short_ratio REAL,
                long_account REAL,
                short_account REAL
            )
        ''')
        
        # 大户持仓表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_trader_position (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp INTEGER,
                long_position_ratio REAL,
                short_position_ratio REAL,
                long_account_ratio REAL,
                short_account_ratio REAL
            )
        ''')
        
        self.db.commit()
        print("✅ Futures database initialized")
    
    def fetch_open_interest(self):
        """获取持仓量"""
        try:
            url = "https://fapi.binance.com/fapi/v1/openInterest"
            params = {'symbol': self.symbol}
            
            response = requests.get(url, params=params, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                
                cursor = self.db.cursor()
                cursor.execute('''
                    INSERT INTO open_interest (symbol, timestamp, open_interest, open_interest_value)
                    VALUES (?, ?, ?, ?)
                ''', (
                    self.symbol.lower(),
                    int(datetime.now().timestamp() * 1000),
                    float(data.get('openInterest', 0)),
                    float(data.get('openInterest', 0)) * self._get_current_price()
                ))
                self.db.commit()
                
                print(f"[OI] {self.symbol}: {float(data.get('openInterest', 0)):.2f}")
                return True
            else:
                print(f"Open Interest API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Open Interest error: {e}")
            return False
    
    def fetch_funding_rate(self):
        """获取资金费率"""
        try:
            url = "https://fapi.binance.com/fapi/v1/premiumIndex"
            params = {'symbol': self.symbol}
            
            response = requests.get(url, params=params, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                
                cursor = self.db.cursor()
                cursor.execute('''
                    INSERT INTO funding_rate (symbol, timestamp, funding_rate, next_funding_time)
                    VALUES (?, ?, ?, ?)
                ''', (
                    self.symbol.lower(),
                    int(datetime.now().timestamp() * 1000),
                    float(data.get('lastFundingRate', 0)),
                    int(data.get('nextFundingTime', 0))
                ))
                self.db.commit()
                
                funding_rate_percent = float(data.get('lastFundingRate', 0)) * 100
                print(f"[FR] {self.symbol}: {funding_rate_percent:.4f}%")
                return True
            else:
                print(f"Funding Rate API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Funding Rate error: {e}")
            return False
    
    def fetch_long_short_ratio(self):
        """获取多空比（全市场账户）"""
        try:
            url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
            params = {
                'symbol': self.symbol,
                'period': '5m',
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    latest = data[0]
                    
                    cursor = self.db.cursor()
                    cursor.execute('''
                        INSERT INTO long_short_ratio (symbol, timestamp, long_short_ratio, long_account, short_account)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        self.symbol.lower(),
                        int(latest.get('timestamp', datetime.now().timestamp() * 1000)),
                        float(latest.get('longShortRatio', 1)),
                        float(latest.get('longAccount', 0)),
                        float(latest.get('shortAccount', 0))
                    ))
                    self.db.commit()
                    
                    print(f"[LSR] {self.symbol}: {float(latest.get('longShortRatio', 1)):.2f}")
                    return True
            else:
                print(f"Long/Short Ratio API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Long/Short Ratio error: {e}")
            return False
    
    def fetch_top_trader_position(self):
        """获取大户持仓比例"""
        try:
            url = "https://fapi.binance.com/futures/data/topLongShortPositionRatio"
            params = {
                'symbol': self.symbol,
                'period': '5m',
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    latest = data[0]
                    
                    cursor = self.db.cursor()
                    cursor.execute('''
                        INSERT INTO top_trader_position 
                        (symbol, timestamp, long_position_ratio, short_position_ratio, long_account_ratio, short_account_ratio)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        self.symbol.lower(),
                        int(latest.get('timestamp', datetime.now().timestamp() * 1000)),
                        float(latest.get('longPosition', 0)),
                        float(latest.get('shortPosition', 0)),
                        float(latest.get('longAccount', 0)),
                        float(latest.get('shortAccount', 0))
                    ))
                    self.db.commit()
                    
                    print(f"[TTP] {self.symbol}: Long {float(latest.get('longPosition', 0)):.2f}% | Short {float(latest.get('shortPosition', 0)):.2f}%")
                    return True
            else:
                print(f"Top Trader Position API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Top Trader Position error: {e}")
            return False
    
    def _get_current_price(self):
        """获取当前价格（用于计算持仓量价值）"""
        try:
            url = "https://fapi.binance.com/fapi/v1/ticker/price"
            params = {'symbol': self.symbol}
            response = requests.get(url, params=params, timeout=5, verify=False)
            if response.status_code == 200:
                return float(response.json().get('price', 0))
        except:
            pass
        return 0
    
    def collect_all(self):
        """采集所有合约数据"""
        print(f"\n🔄 Collecting futures data for {self.symbol}...")
        
        while True:
            try:
                self.fetch_open_interest()
                time.sleep(1)
                
                self.fetch_funding_rate()
                time.sleep(1)
                
                self.fetch_long_short_ratio()
                time.sleep(1)
                
                self.fetch_top_trader_position()
                
                # 每5分钟更新一次
                time.sleep(300)
                
            except KeyboardInterrupt:
                print("\n⛔ Stopping futures data collection...")
                break
            except Exception as e:
                print(f"❌ Collection error: {e}")
                time.sleep(60)

if __name__ == '__main__':
    import sys
    
    symbol = 'ETHUSDT'
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         📊 合约数据采集器 - {symbol:^10s}                        ║
║                                                                  ║
║         数据类型:                                                 ║
║         • 持仓量 (Open Interest)                                  ║
║         • 资金费率 (Funding Rate)                                 ║
║         • 多空比 (Long/Short Ratio)                              ║
║         • 大户持仓 (Top Trader Position)                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    collector = FuturesDataCollector(symbol)
    collector.collect_all()
