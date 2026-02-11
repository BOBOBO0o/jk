import sys
import os

os.chdir(r'C:\Users\jierr\Desktop\jk')
sys.path.insert(0, r'C:\Users\jierr\Desktop\jk\src\collectors')

from binance_collector import BinanceDataCollector

print("开始启动 BNB 数据采集...")
collector = BinanceDataCollector('bnbusdt')
collector.start_collection()
