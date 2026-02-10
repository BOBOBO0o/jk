import sys 
from binance_collector import BinanceDataCollector 
 
if len(sys.argv) > 1: 
    symbol = sys.argv[1] 
    print(f"启动 {symbol.upper()} 数据采集...") 
    collector = BinanceDataCollector(symbol) 
    collector.start_collection() 
