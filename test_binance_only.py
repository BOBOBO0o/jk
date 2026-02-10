"""
测试仅使用Binance数据的AI分析器配置功能
"""
from ai_analyzer import AIAnalyzer

def test_configurations():
    """测试不同的配置"""
    
    print("=" * 60)
    print("🚀 测试AI分析器配置功能（仅Binance数据）")
    print("=" * 60)
    
    # 初始化分析器
    analyzer = AIAnalyzer(symbol='btcusdt')
    
    # 测试LM Studio连接
    print("\n检查LM Studio连接...")
    lm_connected = analyzer.test_lm_studio_connection()
    
    if not lm_connected:
        print("\n⚠️ LM Studio未连接")
        print("提示：请启动LM Studio并加载模型")
        return
    
    # 获取数据
    print("\n📊 获取BTC市场数据...")
    data = analyzer.get_recent_data(hours=1)
    print(f"✅ 数据获取成功")
    print(f"   当前价格: ${data['avg_price']:.2f}")
    print(f"   买卖比: {data['buy_sell_ratio']:.2f}")
    print(f"   24h涨跌: {data['price_change_24h']:.2f}%")
    
    # 技术指标
    indicators = data.get('indicators', {})
    if indicators.get('available'):
        print(f"   RSI: {indicators.get('rsi', 0):.2f}")
        macd = indicators.get('macd', {})
        print(f"   MACD趋势: {macd.get('trend', 'N/A')}")
    
    # 合约数据
    print(f"   持仓量: {data.get('open_interest', 0):.2f}")
    print(f"   资金费率: {data.get('funding_rate', 0):.4f}%")
    print(f"   多空比: {data.get('long_short_ratio', 1):.2f}")
    
    # 测试配置
    test_cases = [
        {
            'name': '🔧 配置1: 仅技术指标',
            'config': {
                'indicators': ['ema', 'macd', 'rsi'],
                'dataSources': [],
                'nofx': [],
                'customPrompt': ''
            }
        },
        {
            'name': '🔧 配置2: 技术指标 + 成交量',
            'config': {
                'indicators': ['rsi', 'macd'],
                'dataSources': ['volume'],
                'nofx': [],
                'customPrompt': ''
            }
        },
        {
            'name': '🔧 配置3: 完整配置（无NOFX）',
            'config': {
                'indicators': ['ema', 'macd', 'rsi', 'atr', 'boll'],
                'dataSources': ['volume', 'oi-market', 'funding-market'],
                'nofx': [],
                'customPrompt': ''
            }
        },
        {
            'name': '🔧 配置4: 自定义提示词 - 短线交易',
            'config': {
                'indicators': ['rsi', 'macd'],
                'dataSources': ['volume'],
                'nofx': [],
                'customPrompt': '重点分析1小时内的短线交易机会，给出具体的进场价位和止损点位'
            }
        },
        {
            'name': '🔧 配置5: 自定义提示词 - 中长线持仓',
            'config': {
                'indicators': ['ema', 'boll'],
                'dataSources': ['oi-market', 'funding-market'],
                'nofx': [],
                'customPrompt': '分析适合持仓2-3天的中线机会，关注合约持仓和资金费率变化'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"{test_case['name']}")
        print(f"{'='*60}")
        
        config = test_case['config']
        print(f"📋 配置详情:")
        print(f"   技术指标: {config['indicators']}")
        print(f"   数据源: {config['dataSources'] if config['dataSources'] else '无'}")
        if config['customPrompt']:
            print(f"   自定义提示: {config['customPrompt'][:60]}...")
        
        try:
            print(f"\n🤖 正在分析...")
            analysis = analyzer.analyze_with_lm_studio(data, config=config)
            
            print(f"✅ 分析完成 (长度: {len(analysis)} 字符)")
            print(f"\n📝 分析结果:")
            print("-" * 60)
            print(analysis)
            print("-" * 60)
            
            # 等待用户确认继续
            if i < len(test_cases):
                input(f"\n按Enter继续下一个测试...")
                
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("✅ 所有测试完成")
    print(f"{'='*60}")
    print("\n💡 总结:")
    print("   ✓ 系统支持灵活的配置选项")
    print("   ✓ 用户可自定义技术指标组合")
    print("   ✓ 用户可自定义分析维度")
    print("   ✓ 用户可输入自定义AI提示词")
    print("   ✓ LM模型根据配置动态生成分析")


if __name__ == "__main__":
    test_configurations()
