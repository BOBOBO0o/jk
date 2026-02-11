import sys
import os
import time

os.chdir(r'C:\Users\jierr\Desktop\jk')
sys.path.insert(0, r'C:\Users\jierr\Desktop\jk\src\collectors')

from futures_collector import FuturesDataCollector

print("开始启动 ETH 合约数据采集...")
collector = FuturesDataCollector('ETHUSDT')

print("\n采集间隔: 每5分钟")
print("采集数据: 持仓量、资金费率、多空比、大户持仓\n")

while True:
    try:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始采集...")
        
        collector.fetch_open_interest()
        time.sleep(1)
        
        collector.fetch_funding_rate()
        time.sleep(1)
        
        collector.fetch_long_short_ratio()
        time.sleep(1)
        
        collector.fetch_top_trader_position()
        
        print("✅ 本轮采集完成，等待5分钟...")
        time.sleep(300)  # 5分钟
        
    except KeyboardInterrupt:
        print("\n\n停止采集...")
        break
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        time.sleep(60)
