"""
测试NOFX数据集成和AI分析器
"""
import sys
from ai_analyzer import AIAnalyzer

def test_basic_nofx():
    """测试基础NOFX数据获取"""
    print("=" * 60)
    print("测试 1: NOFX API基础功能")
    print("=" * 60)
    
    from nofx_collector import NOFXCollector
    collector = NOFXCollector()
    
    # 测试资金流
    print("\n1. 测试BTC资金流数据...")
    netflow = collector.get_netflow_for_symbol('btcusdt', '1h')
    if netflow:
        print("✅ 资金流数据获取成功")
        print(f"   机构流: {netflow.get('institution_flow', 0):,.2f} USDT")
        print(f"   散户流: {netflow.get('personal_flow', 0):,.2f} USDT")
        print(f"   总流量: {netflow.get('total_flow', 0):,.2f} USDT")
    else:
        print("❌ 资金流数据获取失败")
    
    # 测试热力图
    print("\n2. 测试BTC订单簿热力图...")
    heatmap = collector.get_orderbook_heatmap('btcusdt', 'future')
    if heatmap:
        print("✅ 热力图数据获取成功")
        print(f"   买盘量: {heatmap.get('bid_volume', 0):,.2f} USDT")
        print(f"   卖盘量: {heatmap.get('ask_volume', 0):,.2f} USDT")
        print(f"   买卖差: {heatmap.get('delta', 0):,.2f} USDT")
    else:
        print("❌ 热力图数据获取失败")
    
    # 测试综合分析
    print("\n3. 测试综合数据分析...")
    analysis = collector.analyze_symbol('btcusdt', include_heatmap=True, include_netflow=True)
    if analysis and analysis.get('data'):
        print("✅ 综合分析数据获取成功")
        formatted = collector.format_for_llm(analysis)
        print("\n格式化输出预览：")
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
    else:
        print("❌ 综合分析失败")


def test_ai_analyzer_with_config():
    """测试带配置的AI分析器"""
    print("\n" + "=" * 60)
    print("测试 2: AI分析器配置功能")
    print("=" * 60)
    
    analyzer = AIAnalyzer(symbol='btcusdt')
    
    # 测试不同的配置
    configs = [
        {
            'name': '只有技术指标',
            'config': {
                'indicators': ['ema', 'macd', 'rsi'],
                'dataSources': [],
                'nofx': [],
                'customPrompt': ''
            }
        },
        {
            'name': '技术指标 + 合约数据',
            'config': {
                'indicators': ['ema', 'macd', 'rsi'],
                'dataSources': ['oi-market', 'funding-market'],
                'nofx': [],
                'customPrompt': ''
            }
        },
        {
            'name': '完整配置(包含NOFX)',
            'config': {
                'indicators': ['ema', 'macd', 'rsi', 'atr', 'boll'],
                'dataSources': ['volume', 'oi-market', 'funding-market'],
                'nofx': ['netflow', 'heatmap'],
                'customPrompt': ''
            }
        },
        {
            'name': '自定义提示词',
            'config': {
                'indicators': ['rsi'],
                'dataSources': ['volume'],
                'nofx': ['netflow'],
                'customPrompt': '重点分析短线交易机会，关注1小时内的价格波动和资金流向'
            }
        }
    ]
    
    print("\n获取市场数据...")
    data = analyzer.get_recent_data(hours=1)
    print(f"✅ 数据获取成功")
    print(f"   平均价格: ${data['avg_price']:.2f}")
    print(f"   买卖比: {data['buy_sell_ratio']:.2f}")
    print(f"   技术指标: {'可用' if data.get('indicators', {}).get('available') else '不可用'}")
    
    # 测试LM Studio连接
    print("\n检查LM Studio连接...")
    lm_connected = analyzer.test_lm_studio_connection()
    
    if not lm_connected:
        print("\n⚠️ LM Studio未连接，跳过AI分析测试")
        print("提示：请启动LM Studio并加载模型，然后重新运行测试")
        return
    
    # 测试各种配置
    for test_case in configs:
        print(f"\n--- 测试配置: {test_case['name']} ---")
        print(f"技术指标: {test_case['config']['indicators']}")
        print(f"数据源: {test_case['config']['dataSources']}")
        print(f"NOFX: {test_case['config']['nofx']}")
        if test_case['config']['customPrompt']:
            print(f"自定义提示: {test_case['config']['customPrompt'][:50]}...")
        
        try:
            analysis = analyzer.analyze_with_lm_studio(data, config=test_case['config'])
            print(f"✅ 分析完成")
            print(f"分析结果长度: {len(analysis)} 字符")
            print(f"前150字: {analysis[:150]}...")
        except Exception as e:
            print(f"❌ 分析失败: {e}")


def test_full_integration():
    """测试完整集成"""
    print("\n" + "=" * 60)
    print("测试 3: 完整系统集成")
    print("=" * 60)
    
    # 测试多个币种
    symbols = ['btcusdt', 'ethusdt', 'bnbusdt']
    
    for symbol in symbols:
        print(f"\n--- 测试 {symbol.upper()} ---")
        analyzer = AIAnalyzer(symbol=symbol)
        
        # 获取数据
        data = analyzer.get_recent_data(hours=1)
        print(f"✅ {symbol}: 价格 ${data['avg_price']:.2f}, 买卖比 {data['buy_sell_ratio']:.2f}")
        
        # 使用完整配置
        config = {
            'indicators': ['ema', 'macd', 'rsi'],
            'dataSources': ['volume', 'oi-market', 'funding-market'],
            'nofx': ['netflow', 'heatmap'],
            'customPrompt': ''
        }
        
        # 测试NOFX数据获取
        try:
            from nofx_collector import NOFXCollector
            nofx = NOFXCollector()
            nofx_analysis = nofx.analyze_symbol(symbol, include_heatmap=True, include_netflow=True)
            has_nofx = bool(nofx_analysis and nofx_analysis.get('data'))
            print(f"   NOFX数据: {'✅ 可用' if has_nofx else '❌ 不可用'}")
        except Exception as e:
            print(f"   NOFX数据: ❌ 错误 - {e}")


if __name__ == "__main__":
    print("\n🚀 开始NOFX集成测试\n")
    
    # 测试1: NOFX基础功能
    try:
        test_basic_nofx()
    except Exception as e:
        print(f"\n❌ 测试1失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试2: AI分析器配置
    try:
        test_ai_analyzer_with_config()
    except Exception as e:
        print(f"\n❌ 测试2失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试3: 完整集成
    try:
        test_full_integration()
    except Exception as e:
        print(f"\n❌ 测试3失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
