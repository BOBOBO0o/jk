import sys
import os

os.chdir(r'C:\Users\jierr\Desktop\jk')
sys.path.insert(0, r'C:\Users\jierr\Desktop\jk\src\collectors')

from binance_collector import BinanceDataCollector

print("开始启动 SOL 数据采集...")
collector = BinanceDataCollector('solusdt')
collector.start_collection()
