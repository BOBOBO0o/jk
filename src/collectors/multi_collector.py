"""
多币种数据采集器 - 同时监控多个交易对
"""
import threading
import time
from binance_collector import BinanceDataCollector

class MultiCollector:
    def __init__(self, symbols=['ethusdt', 'btcusdt', 'bnbusdt', 'solusdt', 'berausdt']):
        """
        初始化多币种采集器
        symbols: 交易对列表
        """
        self.symbols = symbols
        self.collectors = {}
        
    def start_collection(self):
        """启动所有交易对的数据采集"""
        print("🚀 启动多币种数据采集系统")
        print("=" * 60)
        
        threads = []
        
        for symbol in self.symbols:
            print(f"\n📊 初始化 {symbol.upper()} 数据采集...")
            try:
                collector = BinanceDataCollector(symbol)
                self.collectors[symbol] = collector
                
                # 为每个交易对创建独立线程
                thread = threading.Thread(
                    target=collector.start_collection, 
                    daemon=True,
                    name=f"{symbol.upper()}-Collector"
                )
                thread.start()
                threads.append(thread)
                
                print(f"✅ {symbol.upper()} 采集线程已启动")
                time.sleep(1)  # 避免同时启动太多连接
                
            except Exception as e:
                print(f"❌ {symbol.upper()} 启动失败: {e}")
        
        print("\n" + "=" * 60)
        print(f"✅ 已启动 {len(self.collectors)} 个交易对的数据采集")
        print("💡 数据持续采集中... 按 Ctrl+C 停止")
        print("=" * 60 + "\n")
        
        # 保持主线程运行
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            print("\n\n⛔ 停止多币种数据采集...")
            print(f"📊 已采集 {len(self.collectors)} 个交易对的数据")

if __name__ == '__main__':
    # 定义要监控的交易对
    symbols = ['ethusdt', 'btcusdt', 'bnbusdt', 'solusdt']
    
    # 检查BERA是否在币安上市
    print("ℹ️  注意: BERA 可能尚未在币安上市，将尝试连接...")
    symbols.append('berausdt')
    
    collector = MultiCollector(symbols)
    collector.start_collection()
