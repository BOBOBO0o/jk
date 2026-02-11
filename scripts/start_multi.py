"""
多币种快速启动脚本
同时启动多个交易对的数据采集
"""
import threading
import time
from datetime import datetime
from binance_collector import BinanceDataCollector

print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🚀 多币种加密货币智能交易系统 v2.0                       ║
║                                                                  ║
║         支持: ETH, BTC, BNB, SOL, BERA                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

正在初始化系统...
""")

# 定义要监控的交易对
SYMBOLS = {
    'ethusdt': 'ETH',
    'btcusdt': 'BTC',
    'bnbusdt': 'BNB',
    'solusdt': 'SOL',
    # 'berausdt': 'BERA'  # BERA可能未上市，取消注释以启用
}

collectors = {}
threads = []

print("\n[启动数据采集]")
print("=" * 60)

for symbol, name in SYMBOLS.items():
    try:
        print(f"\n📊 初始化 {name} ({symbol.upper()}) 数据采集...")
        collector = BinanceDataCollector(symbol)
        collectors[symbol] = collector
        
        thread = threading.Thread(
            target=collector.start_collection,
            daemon=True,
            name=f"{name}-Collector"
        )
        thread.start()
        threads.append(thread)
        
        print(f"✅ {name} 采集线程已启动")
        time.sleep(2)  # 间隔启动，避免同时连接
        
    except Exception as e:
        print(f"❌ {name} 启动失败: {e}")

print("\n" + "=" * 60)
print(f"✅ 已成功启动 {len(collectors)} 个交易对的数据采集")
print("\n等待初始数据采集（30秒）...")
print("你将看到各个交易对的实时数据流")
print("=" * 60 + "\n")

# 等待30秒采集初始数据
time.sleep(30)

print("\n" + "=" * 60)
print("✅ 初始数据采集完成！")
print("\n💡 数据采集持续运行中...")
print("⌨️  按 Ctrl+C 停止系统")
print("\n📊 访问 Web界面查看数据:")
print("   运行: python multi_web_ui.py")
print("   打开: http://localhost:5000")
print("=" * 60 + "\n")

# 保持运行
try:
    for t in threads:
        t.join()
except KeyboardInterrupt:
    print("\n\n" + "=" * 60)
    print("⛔ 用户中断 - 正在关闭系统...")
    print("=" * 60)
    print(f"\n📊 系统运行统计:")
    print(f"  - 监控交易对数: {len(collectors)}")
    print(f"  - 交易对列表: {', '.join([v for v in SYMBOLS.values()])}")
    print("\n👋 感谢使用！")
    print("=" * 60)
