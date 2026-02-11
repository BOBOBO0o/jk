import sys
import os

# 设置工作目录
os.chdir(r'C:\Users\jierr\Desktop\jk')

# 添加源码路径
sys.path.insert(0, r'C:\Users\jierr\Desktop\jk\src\collectors')

print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path[:3])

try:
    from binance_collector import BinanceDataCollector
    print("\n✅ 成功导入 BinanceDataCollector")
    
    print("\n开始启动 ETH 数据采集...")
    collector = BinanceDataCollector('ethusdt')
    print("✅ 采集器初始化成功")
    
    collector.start_collection()
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
