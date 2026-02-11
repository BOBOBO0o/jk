"""
多币种对比分析器 - 同时分析多个交易对并给出综合建议
"""
import requests
import json
import sqlite3
from datetime import datetime, timedelta
from ai_analyzer import AIAnalyzer

class MultiAnalyzer:
    def __init__(self, symbols=['ethusdt', 'btcusdt', 'bnbusdt', 'solusdt'], lm_studio_url='http://localhost:1234/v1'):
        """
        初始化多币种分析器
        symbols: 要分析的交易对列表
        """
        self.symbols = symbols
        self.lm_studio_url = lm_studio_url
        self.analyzers = {}
        
        # 为每个交易对创建分析器
        for symbol in symbols:
            self.analyzers[symbol] = AIAnalyzer(symbol=symbol, lm_studio_url=lm_studio_url)
    
    def test_lm_studio_connection(self):
        """测试LM Studio连接"""
        try:
            response = requests.get(f"{self.lm_studio_url}/models", timeout=5)
            if response.status_code == 200:
                return True
            return False
        except:
            return False
    
    def analyze_all_symbols(self):
        """分析所有交易对"""
        results = {}
        
        print("\n" + "="*70)
        print("🔍 多币种市场分析")
        print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        for symbol in self.symbols:
            try:
                print(f"\n📊 正在分析 {symbol.replace('usdt', '').upper()}...")
                analyzer = self.analyzers[symbol]
                
                # 获取数据
                data = analyzer.get_recent_data(hours=1)
                
                # 检查是否有数据
                if data['trade_count'] == 0:
                    print(f"⚠️  {symbol.upper()} 暂无数据")
                    results[symbol] = {
                        'available': False,
                        'data': None,
                        'analysis': None
                    }
                    continue
                
                # 生成分析
                lm_available = self.test_lm_studio_connection()
                if lm_available:
                    analysis = analyzer.analyze_with_lm_studio(data)
                else:
                    analysis = analyzer.generate_simple_signal(data)
                
                results[symbol] = {
                    'available': True,
                    'data': data,
                    'analysis': analysis,
                    'symbol_name': symbol.replace('usdt', '').upper()
                }
                
                print(f"✅ {symbol.replace('usdt', '').upper()} 分析完成")
                
            except Exception as e:
                print(f"❌ {symbol.upper()} 分析失败: {e}")
                results[symbol] = {
                    'available': False,
                    'data': None,
                    'analysis': None,
                    'error': str(e)
                }
        
        return results
    
    def compare_symbols(self, results):
        """对比各币种表现"""
        print("\n" + "="*70)
        print("📊 币种对比分析")
        print("="*70)
        
        comparison = []
        
        for symbol, result in results.items():
            if not result['available']:
                continue
            
            data = result['data']
            symbol_name = result['symbol_name']
            
            # 计算综合得分
            score = 0
            
            # 买卖比权重
            if data['buy_sell_ratio'] > 1.3:
                score += 2
            elif data['buy_sell_ratio'] < 0.7:
                score -= 2
            elif data['buy_sell_ratio'] > 1.1:
                score += 1
            elif data['buy_sell_ratio'] < 0.9:
                score -= 1
            
            # 订单簿权重
            if data['orderbook_ratio'] > 1.3:
                score += 1
            elif data['orderbook_ratio'] < 0.7:
                score -= 1
            
            # 价格趋势权重
            if data['price_trend'] == 'rising':
                score += 1
            elif data['price_trend'] == 'falling':
                score -= 1
            
            # 24小时涨跌权重
            if data['price_change_24h'] > 5:
                score += 2
            elif data['price_change_24h'] > 2:
                score += 1
            elif data['price_change_24h'] < -5:
                score -= 2
            elif data['price_change_24h'] < -2:
                score -= 1
            
            comparison.append({
                'symbol': symbol,
                'symbol_name': symbol_name,
                'score': score,
                'price': data['avg_price'],
                'change_24h': data['price_change_24h'],
                'buy_sell_ratio': data['buy_sell_ratio'],
                'price_trend': data['price_trend'],
                'volume_24h': data['volume_24h']
            })
        
        # 按得分排序
        comparison.sort(key=lambda x: x['score'], reverse=True)
        
        # 显示对比结果
        print("\n排名 | 币种 | 得分 | 24h涨跌 | 买卖比 | 趋势 | 当前价格")
        print("-" * 70)
        
        for idx, item in enumerate(comparison, 1):
            emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "  "
            trend_emoji = "📈" if item['price_trend'] == 'rising' else "📉" if item['price_trend'] == 'falling' else "➡️"
            change_color = "+" if item['change_24h'] > 0 else ""
            
            print(f"{emoji} {idx}  | {item['symbol_name']:4s} | {item['score']:+3d}  | "
                  f"{change_color}{item['change_24h']:+6.2f}% | "
                  f"{item['buy_sell_ratio']:5.2f}  | {trend_emoji}   | "
                  f"${item['price']:,.2f}")
        
        return comparison
    
    def generate_portfolio_advice(self, comparison):
        """生成投资组合建议"""
        print("\n" + "="*70)
        print("💼 投资组合建议")
        print("="*70)
        
        if not comparison:
            print("\n⚠️  暂无足够数据生成建议")
            return
        
        # 分类币种
        bullish = [c for c in comparison if c['score'] >= 3]
        neutral = [c for c in comparison if -2 < c['score'] < 3]
        bearish = [c for c in comparison if c['score'] <= -2]
        
        print("\n🟢 看涨信号:")
        if bullish:
            for item in bullish:
                print(f"  • {item['symbol_name']}: 得分{item['score']:+d}, 24h{item['change_24h']:+.2f}%, 买卖比{item['buy_sell_ratio']:.2f}")
        else:
            print("  • 暂无")
        
        print("\n🟡 中性观望:")
        if neutral:
            for item in neutral:
                print(f"  • {item['symbol_name']}: 得分{item['score']:+d}, 24h{item['change_24h']:+.2f}%, 买卖比{item['buy_sell_ratio']:.2f}")
        else:
            print("  • 暂无")
        
        print("\n🔴 看跌信号:")
        if bearish:
            for item in bearish:
                print(f"  • {item['symbol_name']}: 得分{item['score']:+d}, 24h{item['change_24h']:+.2f}%, 买卖比{item['buy_sell_ratio']:.2f}")
        else:
            print("  • 暂无")
        
        # 生成建议
        print("\n📝 综合建议:")
        if bullish:
            print(f"  1. 优先关注: {', '.join([c['symbol_name'] for c in bullish[:2]])}")
            if len(bullish) > 1:
                print(f"  2. 建议配置: 重仓 {bullish[0]['symbol_name']}, 中仓 {bullish[1]['symbol_name']}")
        
        if bearish:
            print(f"  3. 规避风险: 建议减仓或观望 {', '.join([c['symbol_name'] for c in bearish])}")
        
        if not bullish and not bearish:
            print("  • 当前市场整体中性，建议观望或小仓位试探")
        
        print("\n⚠️  风险提示:")
        print("  • 本分析仅供参考，不构成投资建议")
        print("  • 加密货币市场波动剧烈，请控制仓位")
        print("  • 建议设置止损点，做好风险管理")
    
    def run_full_analysis(self):
        """运行完整的多币种分析"""
        print("\n" + "╔" + "="*68 + "╗")
        print("║" + " "*20 + "多币种智能分析系统" + " "*20 + "║")
        print("╚" + "="*68 + "╝")
        
        # 检查LM Studio
        lm_available = self.test_lm_studio_connection()
        if lm_available:
            print("\n✅ LM Studio 已连接")
        else:
            print("\n⚠️  LM Studio 未连接，将使用规则引擎")
        
        # 分析所有币种
        results = self.analyze_all_symbols()
        
        # 显示每个币种的详细分析
        print("\n" + "="*70)
        print("📋 详细分析报告")
        print("="*70)
        
        for symbol, result in results.items():
            if not result['available']:
                continue
            
            symbol_name = result['symbol_name']
            data = result['data']
            
            print(f"\n{'─'*70}")
            print(f"🪙 {symbol_name} ({symbol.upper()})")
            print(f"{'─'*70}")
            print(f"💹 当前价格: ${data['avg_price']:.2f}")
            print(f"📈 24h涨跌: {data['price_change_24h']:+.2f}%")
            print(f"📊 买卖比: {data['buy_sell_ratio']:.2f}")
            print(f"📚 订单簿比: {data['orderbook_ratio']:.2f}")
            print(f"📉 价格趋势: {data['price_trend']}")
            print(f"\n{result['analysis']}")
        
        # 对比分析
        comparison = self.compare_symbols(results)
        
        # 投资组合建议
        self.generate_portfolio_advice(comparison)
        
        print("\n" + "="*70)
        print(f"✅ 分析完成 | 时间: {datetime.now().strftime('%H:%M:%S')}")
        print("="*70 + "\n")
        
        return results, comparison

if __name__ == '__main__':
    import sys
    
    # 支持命令行参数指定币种
    if len(sys.argv) > 1:
        symbols = [s.lower() for s in sys.argv[1:]]
        print(f"分析币种: {', '.join([s.replace('usdt', '').upper() for s in symbols])}")
    else:
        # 默认分析所有主流币种
        symbols = ['ethusdt', 'btcusdt', 'bnbusdt', 'solusdt']
        print("使用方法: python multi_analyzer.py [symbol1] [symbol2] ...")
        print("示例: python multi_analyzer.py ethusdt btcusdt")
        print(f"\n未指定币种，默认分析: {', '.join([s.replace('usdt', '').upper() for s in symbols])}\n")
    
    analyzer = MultiAnalyzer(symbols=symbols)
    analyzer.run_full_analysis()
