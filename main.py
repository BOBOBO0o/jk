import threading
import time
import sys
from datetime import datetime

def clear_screen():
    """清屏（跨平台）"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🚀 ETH 加密货币智能交易系统 v1.0                        ║
║                                                                  ║
║         Crypto Trading System with AI Analysis                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    print("系统启动选项：\n")
    print("1️⃣  启动完整系统（币安数据 + 链上数据 + AI分析）")
    print("2️⃣  仅启动币安数据采集")
    print("3️⃣  仅启动链上数据采集")
    print("4️⃣  仅运行AI分析（需要已有数据）")
    print("5️⃣  查看数据统计")
    print("0️⃣  退出\n")
    
    choice = input("请选择 [1-5, 0退出]: ").strip()
    
    if choice == '1':
        run_full_system()
    elif choice == '2':
        run_binance_only()
    elif choice == '3':
        run_onchain_only()
    elif choice == '4':
        run_analysis_only()
    elif choice == '5':
        show_statistics()
    elif choice == '0':
        print("👋 退出系统")
        sys.exit(0)
    else:
        print("❌ 无效选择")
        time.sleep(2)
        main()

def run_full_system():
    """启动完整系统"""
    clear_screen()
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                     🚀 启动完整系统                              ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    from binance_collector import BinanceDataCollector
    from onchain_collector import OnchainCollector
    from ai_analyzer import AIAnalyzer
    
    # 1. 启动币安数据采集
    print("\n[1/3] 启动币安数据采集...")
    binance = BinanceDataCollector('ethusdt')
    binance_thread = threading.Thread(target=binance.start_collection, daemon=True)
    binance_thread.start()
    time.sleep(2)
    
    # 2. 启动链上数据采集
    print("\n[2/3] 启动链上数据采集...")
    try:
        onchain = OnchainCollector()
        onchain_thread = threading.Thread(target=onchain.monitor_blocks, daemon=True)
        onchain_thread.start()
        time.sleep(2)
    except Exception as e:
        print(f"⚠️  链上数据采集启动失败: {e}")
        print("ℹ️  系统将继续运行，但不包含链上数据")
    
    # 3. 等待初始数据采集
    print("\n[3/3] 等待初始数据采集（60秒）...")
    for i in range(60, 0, -10):
        print(f"⏳ 剩余 {i} 秒...")
        time.sleep(10)
    
    # 4. 启动AI分析循环
    print("\n✅ 开始AI分析循环...\n")
    analyzer = AIAnalyzer()
    
    # 测试LM Studio连接
    print("🔍 检测LM Studio...")
    analyzer.test_lm_studio_connection()
    print()
    
    analysis_interval = 300  # 5分钟分析一次
    
    try:
        while True:
            analyzer.run_analysis()
            print(f"\n⏰ 下次分析将在 {analysis_interval//60} 分钟后进行...")
            print(f"💡 数据采集持续运行中...\n")
            time.sleep(analysis_interval)
    except KeyboardInterrupt:
        print("\n\n⛔ 用户中断，正在关闭系统...")
        print("👋 感谢使用！")

def run_binance_only():
    """仅运行币安数据采集"""
    clear_screen()
    print("🚀 启动币安数据采集...\n")
    
    from binance_collector import BinanceDataCollector
    
    collector = BinanceDataCollector('ethusdt')
    
    try:
        collector.start_collection()
    except KeyboardInterrupt:
        print("\n⛔ 停止数据采集")

def run_onchain_only():
    """仅运行链上数据采集"""
    clear_screen()
    print("🚀 启动链上数据采集...\n")
    
    from onchain_collector import OnchainCollector
    
    try:
        collector = OnchainCollector()
        collector.monitor_blocks()
    except KeyboardInterrupt:
        print("\n⛔ 停止链上监控")

def run_analysis_only():
    """仅运行AI分析"""
    clear_screen()
    print("🤖 AI分析模式\n")
    
    from ai_analyzer import AIAnalyzer
    
    analyzer = AIAnalyzer()
    
    print("选择分析模式：")
    print("1. 单次分析")
    print("2. 持续分析（每5分钟一次）")
    
    mode = input("\n请选择 [1-2]: ").strip()
    
    if mode == '1':
        analyzer.run_analysis()
        input("\n按回车键返回主菜单...")
        main()
    elif mode == '2':
        try:
            while True:
                analyzer.run_analysis()
                print("\n⏰ 5分钟后进行下次分析...\n")
                time.sleep(300)
        except KeyboardInterrupt:
            print("\n⛔ 停止分析")
            input("\n按回车键返回主菜单...")
            main()
    else:
        print("❌ 无效选择")
        time.sleep(2)
        main()

def show_statistics():
    """显示数据统计"""
    clear_screen()
    print("📊 数据统计\n")
    
    import sqlite3
    from datetime import timedelta
    
    try:
        db = sqlite3.connect('crypto_data.db')
        cursor = db.cursor()
        
        # 总体统计
        print("=" * 60)
        print("📈 币安交易数据")
        print("=" * 60)
        
        trades_count = cursor.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        print(f"总交易记录数: {trades_count:,}")
        
        if trades_count > 0:
            latest_trade = cursor.execute("""
                SELECT price, quantity, timestamp 
                FROM trades 
                ORDER BY timestamp DESC LIMIT 1
            """).fetchone()
            print(f"最新价格: ${latest_trade[0]:.2f}")
            print(f"最新交易时间: {datetime.fromtimestamp(latest_trade[2]/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        
        klines_count = cursor.execute("SELECT COUNT(*) FROM klines").fetchone()[0]
        print(f"K线数据: {klines_count} 条")
        
        orderbook_count = cursor.execute("SELECT COUNT(*) FROM orderbook").fetchone()[0]
        print(f"订单簿快照: {orderbook_count} 条")
        
        print("\n" + "=" * 60)
        print("⛓️  链上数据")
        print("=" * 60)
        
        blocks_count = cursor.execute("SELECT COUNT(*) FROM blocks").fetchone()[0]
        print(f"监控区块数: {blocks_count:,}")
        
        large_transfers = cursor.execute("SELECT COUNT(*), SUM(value) FROM large_transfers").fetchone()
        print(f"大额转账: {large_transfers[0]:,} 笔，总计 {large_transfers[1]:.2f} ETH")
        
        exchange_flow = cursor.execute("""
            SELECT 
                SUM(CASE WHEN flow_type='inflow' THEN amount ELSE 0 END),
                SUM(CASE WHEN flow_type='outflow' THEN amount ELSE 0 END)
            FROM exchange_flow
        """).fetchone()
        print(f"交易所总流入: {exchange_flow[0]:.2f} ETH")
        print(f"交易所总流出: {exchange_flow[1]:.2f} ETH")
        print(f"交易所净流出: {exchange_flow[1] - exchange_flow[0]:.2f} ETH")
        
        # 最近1小时统计
        timestamp_1h = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
        recent_trades = cursor.execute("""
            SELECT COUNT(*), SUM(quantity) 
            FROM trades 
            WHERE timestamp > ?
        """, (timestamp_1h,)).fetchone()
        
        print("\n" + "=" * 60)
        print("⏰ 最近1小时")
        print("=" * 60)
        print(f"交易笔数: {recent_trades[0]:,}")
        print(f"交易量: {recent_trades[1]:.2f} ETH")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 读取数据失败: {e}")
        print("ℹ️  请确保已运行数据采集")
    
    input("\n按回车键返回主菜单...")
    main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 退出系统")
        sys.exit(0)
