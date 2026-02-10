"""
快速启动脚本 - 直接启动完整系统
"""
import threading
import time
from datetime import datetime

print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🚀 ETH 加密货币智能交易系统 v1.0                        ║
║                                                                  ║
║         自动启动模式 - 完整系统                                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

正在初始化系统...
""")

from binance_collector import BinanceDataCollector
from onchain_collector import OnchainCollector
from ai_analyzer import AIAnalyzer

# 1. 启动币安数据采集
print("\n[1/3] 🚀 启动币安数据采集...")
print("-" * 60)
binance = BinanceDataCollector('ethusdt')
binance_thread = threading.Thread(target=binance.start_collection, daemon=True)
binance_thread.start()
time.sleep(3)

# 2. 启动链上数据采集
print("\n[2/3] ⛓️  启动链上数据采集...")
print("-" * 60)
onchain_started = False
try:
    onchain = OnchainCollector()
    onchain_thread = threading.Thread(target=onchain.monitor_blocks, daemon=True)
    onchain_thread.start()
    onchain_started = True
    time.sleep(3)
except Exception as e:
    print(f"⚠️  链上数据采集启动失败: {e}")
    print("ℹ️  系统将继续运行，但不包含链上数据")
    print()

# 3. 等待初始数据采集
print("\n[3/3] ⏳ 等待初始数据采集...")
print("-" * 60)
print("正在收集数据，请等待60秒...")
print("你将看到实时的交易数据、订单簿和K线信息\n")

for i in range(60, 0, -10):
    print(f"⏰ 还需等待 {i} 秒...")
    time.sleep(10)

# 4. 启动AI分析循环
print("\n" + "="*70)
print("✅ 数据采集完成！开始AI分析...")
print("="*70)

analyzer = AIAnalyzer()

# 检测LM Studio
print("\n🔍 检测LM Studio...")
lm_available = analyzer.test_lm_studio_connection()
if not lm_available:
    print("⚠️  LM Studio未运行，将使用规则引擎进行分析")
print()

analysis_interval = 300  # 5分钟

try:
    analysis_count = 0
    while True:
        analysis_count += 1
        print(f"\n{'='*70}")
        print(f"📊 第 {analysis_count} 次分析")
        print(f"{'='*70}")
        
        analyzer.run_analysis()
        
        print(f"\n💡 数据采集持续运行中...")
        print(f"⏰ 下次分析将在 {analysis_interval//60} 分钟后进行")
        print(f"⌨️  按 Ctrl+C 停止系统\n")
        
        time.sleep(analysis_interval)
        
except KeyboardInterrupt:
    print("\n\n" + "="*70)
    print("⛔ 用户中断 - 正在关闭系统...")
    print("="*70)
    print("\n📊 系统运行统计:")
    print(f"  - 完成分析次数: {analysis_count}")
    print(f"  - 币安数据采集: ✅ 运行中")
    if onchain_started:
        print(f"  - 链上数据采集: ✅ 运行中")
    else:
        print(f"  - 链上数据采集: ❌ 未启动")
    print("\n👋 感谢使用！")
    print("="*70)
