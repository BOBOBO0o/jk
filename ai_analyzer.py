import requests
import json
import sqlite3
from datetime import datetime, timedelta
from indicators import TechnicalIndicators
from nofx_collector import NOFXCollector

class AIAnalyzer:
    def __init__(self, symbol='ethusdt', lm_studio_url='http://localhost:1234/v1', nofx_api_key=None):
        """
        初始化分析器
        symbol: 交易对，如 'ethusdt', 'btcusdt', 'bnbusdt', 'solusdt', 'berausdt'
        nofx_api_key: NOFX API密钥（可选）
        """
        self.symbol = symbol.lower()
        self.symbol_name = symbol.replace('usdt', '').upper()
        self.lm_studio_url = lm_studio_url
        self.db = sqlite3.connect('crypto_data.db')
        self.nofx_collector = NOFXCollector(api_key=nofx_api_key)
        
    def test_lm_studio_connection(self):
        """测试LM Studio连接"""
        try:
            response = requests.get(f"{self.lm_studio_url}/models", timeout=5)
            if response.status_code == 200:
                print("✅ LM Studio connected successfully")
                models = response.json()
                if models.get('data'):
                    print(f"📦 Loaded model: {models['data'][0]['id']}")
                return True
            else:
                print(f"❌ LM Studio connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to LM Studio: {e}")
            print("ℹ️  Please make sure LM Studio is running and local server is started on port 1234")
            return False
    
    def get_recent_data(self, hours=1):
        """获取最近的数据"""
        cursor = self.db.cursor()
        timestamp_ms = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
        timestamp_s = timestamp_ms // 1000
        
        # 获取交易数据
        trades = cursor.execute('''
            SELECT 
                AVG(price) as avg_price, 
                SUM(quantity) as total_volume,
                SUM(CASE WHEN is_buyer_maker=0 THEN quantity ELSE 0 END) as buy_volume,
                SUM(CASE WHEN is_buyer_maker=1 THEN quantity ELSE 0 END) as sell_volume,
                COUNT(*) as trade_count
            FROM trades WHERE symbol = ? AND timestamp > ?
        ''', (self.symbol, timestamp_ms)).fetchone()
        
        # 获取K线数据（用于技术指标计算）
        # 获取足够多的K线数据（最近200根，用于EMA等计算）
        klines_for_indicators = cursor.execute('''
            SELECT open_time, open, high, low, close, volume 
            FROM klines 
            WHERE symbol = ? AND interval = '1m'
            ORDER BY open_time DESC LIMIT 200
        ''', (self.symbol,)).fetchall()
        
        # 反转顺序（从旧到新）
        klines_for_indicators = list(reversed(klines_for_indicators))
        
        # 获取最近10根K线用于显示
        recent_klines = cursor.execute('''
            SELECT close, volume FROM klines 
            WHERE symbol = ? AND interval = '1m' AND open_time > ? 
            ORDER BY open_time DESC LIMIT 10
        ''', (self.symbol, timestamp_ms)).fetchall()
        
        # 获取订单簿数据
        recent_orderbook = cursor.execute('''
            SELECT bids, asks FROM orderbook 
            WHERE symbol = ? AND timestamp > ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (self.symbol, timestamp_ms)).fetchone()
        
        # 计算订单簿压力
        orderbook_ratio = 1.0
        if recent_orderbook:
            try:
                bids = json.loads(recent_orderbook[0])
                asks = json.loads(recent_orderbook[1])
                total_bid_vol = sum([float(b[1]) for b in bids])
                total_ask_vol = sum([float(a[1]) for a in asks])
                orderbook_ratio = total_bid_vol / total_ask_vol if total_ask_vol > 0 else 1.0
            except:
                pass
        
        # 获取24小时统计
        ticker_24h = cursor.execute('''
            SELECT price_change_percent, volume, quote_volume 
            FROM ticker_24h 
            WHERE symbol = ?
            ORDER BY timestamp DESC LIMIT 1
        ''', (self.symbol,)).fetchone()
        
        # 获取链上数据（如果表存在）
        try:
            large_transfers = cursor.execute('''
                SELECT COUNT(*), COALESCE(SUM(value), 0) 
                FROM large_transfers 
                WHERE timestamp > ?
            ''', (timestamp_s,)).fetchone()
        except:
            large_transfers = (0, 0)
        
        try:
            exchange_flow = cursor.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN flow_type='inflow' THEN amount ELSE 0 END), 0) as inflow,
                    COALESCE(SUM(CASE WHEN flow_type='outflow' THEN amount ELSE 0 END), 0) as outflow
                FROM exchange_flow 
                WHERE timestamp > ?
            ''', (timestamp_s,)).fetchone()
        except:
            exchange_flow = (0, 0)
        
        try:
            gas_price = cursor.execute('''
                SELECT AVG(gas_price) 
                FROM gas_prices 
                WHERE timestamp > ?
            ''', (timestamp_s,)).fetchone()
        except:
            gas_price = (0,)
        
        # 获取合约数据
        try:
            # 持仓量
            open_interest = cursor.execute('''
                SELECT open_interest, open_interest_value
                FROM open_interest
                WHERE symbol = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (self.symbol,)).fetchone()
        except:
            open_interest = (0, 0)
        
        try:
            # 资金费率
            funding_rate = cursor.execute('''
                SELECT funding_rate
                FROM funding_rate
                WHERE symbol = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (self.symbol,)).fetchone()
        except:
            funding_rate = (0,)
        
        try:
            # 多空比
            long_short_ratio = cursor.execute('''
                SELECT long_short_ratio, long_account, short_account
                FROM long_short_ratio
                WHERE symbol = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (self.symbol,)).fetchone()
        except:
            long_short_ratio = (1, 0, 0)
        
        try:
            # 大户持仓
            top_trader = cursor.execute('''
                SELECT long_position_ratio, short_position_ratio
                FROM top_trader_position
                WHERE symbol = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (self.symbol,)).fetchone()
        except:
            top_trader = (0, 0)
        
        # 计算技术指标
        indicators = TechnicalIndicators.calculate_all_indicators(klines_for_indicators)
        
        # 计算价格趋势
        price_trend = "stable"
        if recent_klines and len(recent_klines) >= 2:
            latest_price = recent_klines[0][0]
            older_price = recent_klines[-1][0]
            if latest_price > older_price * 1.005:
                price_trend = "rising"
            elif latest_price < older_price * 0.995:
                price_trend = "falling"
        
        return {
            'avg_price': trades[0] if trades[0] else 0,
            'total_volume': trades[1] if trades[1] else 0,
            'buy_volume': trades[2] if trades[2] else 0,
            'sell_volume': trades[3] if trades[3] else 0,
            'trade_count': trades[4] if trades[4] else 0,
            'buy_sell_ratio': (trades[2] / trades[3]) if (trades[3] and trades[3] > 0) else 0,
            'orderbook_ratio': orderbook_ratio,
            'price_trend': price_trend,
            'price_change_24h': ticker_24h[0] if ticker_24h else 0,
            'volume_24h': ticker_24h[1] if ticker_24h else 0,
            'quote_volume_24h': ticker_24h[2] if ticker_24h else 0,
            'large_transfers_count': large_transfers[0] if large_transfers else 0,
            'large_transfers_total': large_transfers[1] if large_transfers else 0,
            'exchange_inflow': exchange_flow[0] if exchange_flow else 0,
            'exchange_outflow': exchange_flow[1] if exchange_flow else 0,
            'net_flow': (exchange_flow[1] - exchange_flow[0]) if exchange_flow else 0,
            'avg_gas_price': gas_price[0] if (gas_price and gas_price[0]) else 0,
            # 技术指标
            'indicators': indicators,
            # 合约数据
            'open_interest': open_interest[0] if open_interest else 0,
            'open_interest_value': open_interest[1] if open_interest else 0,
            'funding_rate': funding_rate[0] * 100 if funding_rate else 0,  # 转为百分比
            'long_short_ratio': long_short_ratio[0] if long_short_ratio else 1,
            'long_account_pct': long_short_ratio[1] if long_short_ratio else 0,
            'short_account_pct': long_short_ratio[2] if long_short_ratio else 0,
            'top_trader_long': top_trader[0] if top_trader else 0,
            'top_trader_short': top_trader[1] if top_trader else 0
        }
    
    def analyze_with_lm_studio(self, data, config=None):
        """
        使用LM Studio分析数据
        config: 用户配置，包含哪些数据源和指标需要包含
        {
            'indicators': ['ema', 'macd', 'rsi', 'atr', 'boll'],
            'dataSources': ['oi', 'funding', 'volume', 'oi-market', 'funding-market'],
            'nofx': ['netflow', 'heatmap'],
            'customPrompt': '用户自定义提示词'
        }
        """
        # 默认配置
        if config is None:
            config = {
                'indicators': ['ema', 'macd', 'rsi', 'atr', 'boll'],
                'dataSources': ['volume', 'oi-market', 'funding-market'],
                'nofx': [],
                'customPrompt': ''
            }
        
        # 获取NOFX数据（如果用户勾选）
        nofx_data = None
        nofx_text = ""
        if config.get('nofx') and len(config['nofx']) > 0:
            try:
                include_netflow = 'netflow' in config['nofx']
                include_heatmap = 'heatmap' in config['nofx']
                nofx_data = self.nofx_collector.analyze_symbol(
                    self.symbol, 
                    include_heatmap=include_heatmap,
                    include_netflow=include_netflow
                )
                nofx_text = self.nofx_collector.format_for_llm(nofx_data)
            except Exception as e:
                print(f"NOFX数据获取失败: {e}")
                nofx_text = ""
        
        # 判断市场情绪
        sentiment_signals = []
        if data['buy_sell_ratio'] > 1.2:
            sentiment_signals.append("买盘强劲")
        elif data['buy_sell_ratio'] < 0.8:
            sentiment_signals.append("卖盘压力大")
        
        if data['orderbook_ratio'] > 1.3:
            sentiment_signals.append("订单簿买盘厚")
        elif data['orderbook_ratio'] < 0.7:
            sentiment_signals.append("订单簿卖盘厚")
        
        if data['net_flow'] > 100:
            sentiment_signals.append("交易所大量流出（看涨）")
        elif data['net_flow'] < -100:
            sentiment_signals.append("交易所大量流入（看跌）")
        
        # 构建技术指标信息（根据用户配置）
        indicators = data.get('indicators', {})
        indicators_text = ""
        selected_indicators = config.get('indicators', [])
        
        if indicators.get('available') and len(selected_indicators) > 0:
            lines = ["\n📉 **技术指标**"]
            
            if 'ema' in selected_indicators:
                lines.append(f"• EMA(12): ${indicators.get('ema_12', 0):.2f} | EMA(26): ${indicators.get('ema_26', 0):.2f}")
            
            if 'macd' in selected_indicators:
                macd = indicators.get('macd', {})
                lines.append(f"• MACD: {macd.get('macd', 0):.4f} | Signal: {macd.get('signal', 0):.4f} | Histogram: {macd.get('histogram', 0):.4f}")
                lines.append(f"• MACD趋势: {macd.get('trend', 'neutral')} {'�︢多头)' if macd.get('trend') == 'bullish' else '(🔴空头)' if macd.get('trend') == 'bearish' else '(➖中性)'}")
            
            if 'rsi' in selected_indicators:
                rsi_val = indicators.get('rsi', 50)
                lines.append(f"• RSI(14): {rsi_val:.2f} {'🔥超买)' if rsi_val > 70 else '(👻超卖)' if rsi_val < 30 else '(👌正常)'}")
            
            if 'atr' in selected_indicators:
                lines.append(f"• ATR(14): {indicators.get('atr', 0):.4f} (波动性指标)")
            
            if 'boll' in selected_indicators:
                boll = indicators.get('bollinger', {})
                lines.append(f"• BOLL: Upper ${boll.get('upper', 0):.2f} | Mid ${boll.get('middle', 0):.2f} | Lower ${boll.get('lower', 0):.2f}")
                lines.append(f"• BOLL位置: {boll.get('position', 'neutral')} {'🔥超买区)' if boll.get('position') == 'above_upper' else '(👻超卖区)' if boll.get('position') == 'below_lower' else ''}")
            
            indicators_text = "\n".join(lines) + "\n"
        
        # 构建合约数据信息（根据用户配置）
        futures_text = ""
        selected_sources = config.get('dataSources', [])
        
        if data.get('open_interest', 0) > 0 and ('oi-market' in selected_sources or 'funding-market' in selected_sources):
            funding_rate = data.get('funding_rate', 0)
            lsr = data.get('long_short_ratio', 1)
            lines = ["\n📈 **合约数据**"]
            
            if 'oi-market' in selected_sources:
                lines.append(f"• 持仓量: {data.get('open_interest', 0):.2f} {self.symbol_name} (${data.get('open_interest_value', 0):,.0f})")
                lines.append(f"• 多空比: {lsr:.2f} {'�︢看多情绪较强)' if lsr > 1.2 else '(🔴看空情绪较强)' if lsr < 0.8 else '(➖中性)'}")
                lines.append(f"• 大户持仓: 多头 {data.get('top_trader_long', 0):.2f}% | 空头 {data.get('top_trader_short', 0):.2f}%")
            
            if 'funding-market' in selected_sources:
                lines.append(f"• 资金费率: {funding_rate:.4f}% {'�︢多头占优)' if funding_rate > 0.01 else '(🔴空头占优)' if funding_rate < -0.01 else '(➖中性)'}")
                lines.append(f"• 多头账户: {data.get('long_account_pct', 0):.2f}% | 空头账户: {data.get('short_account_pct', 0):.2f}%")
            
            futures_text = "\n".join(lines) + "\n"
        
        # 构建成交量文本
        volume_text = ""
        if 'volume' in selected_sources:
            volume_text = f"""
📊 **成交量分析**
• 1小时总量: {data['total_volume']:.2f} {self.symbol_name}
• 买入量: {data['buy_volume']:.2f} {self.symbol_name} ({data['buy_volume']/data['total_volume']*100 if data['total_volume'] > 0 else 0:.1f}%)
• 卖出量: {data['sell_volume']:.2f} {self.symbol_name} ({data['sell_volume']/data['total_volume']*100 if data['total_volume'] > 0 else 0:.1f}%)
• 成交笔数: {data['trade_count']:,} 笔
"""
        
        # 构建主提示词
        base_info = f"""📊 **币安交易所数据（最近1小时）**
• 平均价格: ${data['avg_price']:.2f}
• 总交易量: {data['total_volume']:.2f} {self.symbol_name}
• 买卖比: {data['buy_sell_ratio']:.2f} {'（买盘占优）' if data['buy_sell_ratio'] > 1 else '(卖盘占优)'}
• 订单簿买卖比: {data['orderbook_ratio']:.2f}
• 价格趋势: {data['price_trend']}

📈 **24小时数据**
• 24h价格变化: {data['price_change_24h']:.2f}%
• 24h交易量: {data['volume_24h']:.2f} {self.symbol_name}
• 24h成交额: ${data['quote_volume_24h']:.2f}
"""
        
        # 构建提示词
        prompt_parts = []
        
        # 如果有自定义提示词，优先使用
        if config.get('customPrompt') and config['customPrompt'].strip():
            prompt_parts.append(f"你是专业的加密货币量化分析师。用户的分析需求：{config['customPrompt']}")
        else:
            prompt_parts.append(f"你是专业的加密货币量化分析师。基于以下{self.symbol_name}市场数据，分析当前市场并给出交易建议。")
        
        prompt_parts.append(base_info)
        
        if volume_text:
            prompt_parts.append(volume_text)
        
        if indicators_text:
            prompt_parts.append(indicators_text)
        
        if futures_text:
            prompt_parts.append(futures_text)
        
        # 添加NOFX数据
        if nofx_text:
            prompt_parts.append(nofx_text)
        
        prompt_parts.append(f"🔍 **关键信号**: {', '.join(sentiment_signals) if sentiment_signals else '市场平稳'}")
        
        # 添加时间周期信息
        time_periods = config.get('timePeriods', {})
        if time_periods:
            period_text = f"""
⏱️ **时间周期配置**
• 短线周期: {time_periods.get('short', '4h')}
• 趋势周期: {time_periods.get('trend', '1D')}
"""
            prompt_parts.append(period_text)
        
        # 添加分析要求
        if not config.get('customPrompt'):
            period_hint = ""
            if time_periods:
                period_hint = f"请特别关注{time_periods.get('short', '4h')}和{time_periods.get('trend', '1D')}周期的趋势。"
            
            prompt_parts.append(f"""
请作为专业的量化交易员，综合以上数据进行深度分析：
{period_hint}

**请给出：**
1. 市场情绪判断（看多/看空/中性）
2. 交易建议（买入/卖出/观望）及建议仓位
3. 关键理由（3-4点，必须引用具体指标数值）
4. 风险提示和止损建议

要求：
- 必须综合所有维度数据，不能只看单一指标
- 分析要有逻辑性，指标互相佐证
- 给出具体的数值依据，不要空洞
- 简洁专业，250字内
""")
        
        prompt = "\n".join(prompt_parts)
        
        try:
            # 调用LM Studio API
            response = requests.post(
                f"{self.lm_studio_url}/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "你是专业的加密货币量化分析师，擅长技术分析和链上数据分析。回答要简洁、专业、直接。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                return analysis
            else:
                return f"❌ LM Studio API Error: {response.status_code}\n{response.text}"
                
        except requests.exceptions.Timeout:
            return "❌ LM Studio请求超时，模型可能正在处理中..."
        except Exception as e:
            return f"❌ LM Studio调用失败: {str(e)}"
    
    def generate_simple_signal(self, data):
        """生成简单的交易信号（当LM Studio不可用时）"""
        score = 0
        reasons = []
        
        # 买卖比分析
        if data['buy_sell_ratio'] > 1.3:
            score += 2
            reasons.append("买盘强劲(买卖比>1.3)")
        elif data['buy_sell_ratio'] < 0.7:
            score -= 2
            reasons.append("卖盘压力(买卖比<0.7)")
        
        # 订单簿分析
        if data['orderbook_ratio'] > 1.3:
            score += 1
            reasons.append("订单簿买盘厚")
        elif data['orderbook_ratio'] < 0.7:
            score -= 1
            reasons.append("订单簿卖盘厚")
        
        # 链上流动分析
        if data['net_flow'] > 100:
            score += 2
            reasons.append(f"大量流出交易所({data['net_flow']:.0f}{self.symbol_name})")
        elif data['net_flow'] < -100:
            score -= 2
            reasons.append(f"大量流入交易所({abs(data['net_flow']):.0f}{self.symbol_name})")
        
        # 价格趋势
        if data['price_trend'] == 'rising':
            score += 1
            reasons.append("价格上涨趋势")
        elif data['price_trend'] == 'falling':
            score -= 1
            reasons.append("价格下跌趋势")
        
        # 生成信号
        if score >= 3:
            signal = "🟢 买入信号"
        elif score <= -3:
            signal = "🔴 卖出信号"
        else:
            signal = "🟡 观望"
        
        return f"""
{signal} (得分: {score})

关键因素:
{chr(10).join(['• ' + r for r in reasons]) if reasons else '• 市场平稳'}

当前状态:
• 买卖比: {data['buy_sell_ratio']:.2f}
• 订单簿比: {data['orderbook_ratio']:.2f}
• 交易所净流出: {data['net_flow']:.2f} {self.symbol_name}
• 价格趋势: {data['price_trend']}
"""
    
    def run_analysis(self):
        """运行完整分析"""
        print("\n" + "="*70)
        print(f"🪙 币种: {self.symbol_name} ({self.symbol.upper()})")
        print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # 获取数据
        print("\n📊 正在获取数据...")
        data = self.get_recent_data(hours=1)
        
        # 显示原始数据摘要
        print(f"\n💹 当前价格: ${data['avg_price']:.2f}")
        print(f"📈 买卖比: {data['buy_sell_ratio']:.2f}")
        print(f"📊 订单簿比: {data['orderbook_ratio']:.2f}")
        print(f"⛓️  交易所净流出: {data['net_flow']:.2f} {self.symbol_name}")
        print(f"⛽ Gas价格: {data['avg_gas_price']:.2f} Gwei")
        
        # AI分析
        print("\n🤖 AI分析中...")
        
        # 尝试使用LM Studio
        if self.test_lm_studio_connection():
            analysis = self.analyze_with_lm_studio(data)
        else:
            print("⚠️  LM Studio不可用，使用规则引擎...")
            analysis = self.generate_simple_signal(data)
        
        print("\n" + "─"*70)
        print(analysis)
        print("─"*70)
        print("="*70 + "\n")
        
        return analysis

if __name__ == '__main__':
    import sys
    
    # 支持命令行参数指定币种
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else:
        # 默认分析ETH
        print("使用方法: python ai_analyzer.py [symbol]")
        print("示例: python ai_analyzer.py btcusdt")
        print("支持的币种: ethusdt, btcusdt, bnbusdt, solusdt, berausdt")
        print("\n未指定币种，默认分析 ETH\n")
        symbol = 'ethusdt'
    
    analyzer = AIAnalyzer(symbol=symbol)
    analyzer.run_analysis()
