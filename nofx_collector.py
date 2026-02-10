import requests
import time
from datetime import datetime
import logging
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NOFXCollector:
    """NOFX API数据采集器"""
    
    def __init__(self, api_key=None):
        self.base_url = "https://nofxos.ai"
        self.api_key = api_key
        self.timeout = 10
        
    def _make_request(self, endpoint, params=None):
        """通用API请求方法"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        try:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"NOFX API请求失败 {endpoint}: {e}")
            return None
    
    def get_netflow_ranking(self, symbol, flow_type='top', duration='1h'):
        """
        获取资金流向排名
        flow_type: 'top' (流入) or 'low' (流出)
        """
        endpoint = f"/api/netflow/{flow_type}-ranking"
        params = {'duration': duration} if duration else {}
        return self._make_request(endpoint, params)
    
    def get_netflow_for_symbol(self, symbol, duration='1h'):
        """获取特定币种的机构和散户资金流"""
        # 从coin详情API中提取资金流数据
        data = self.get_coin_details(symbol)
        if not data:
            return None
            
        try:
            netflow_data = {
                'symbol': symbol,
                'institution_flow': data.get('netflow', {}).get('institution', {}).get(duration, 0),
                'personal_flow': data.get('netflow', {}).get('personal', {}).get(duration, 0),
                'total_flow': 0,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }
            
            # 计算总流量
            netflow_data['total_flow'] = (
                netflow_data['institution_flow'] + 
                netflow_data['personal_flow']
            )
            
            return netflow_data
        except Exception as e:
            logger.error(f"解析资金流数据失败 {symbol}: {e}")
            return None
    
    def get_orderbook_heatmap(self, symbol, market_type='future'):
        """
        获取订单簿热力图数据
        market_type: 'future' or 'spot'
        """
        endpoint = f"/api/heatmap/{market_type}/{symbol}"
        return self._make_request(endpoint)
    
    def get_heatmap_list(self):
        """获取所有币种的热力图概览"""
        endpoint = "/api/heatmap/list"
        return self._make_request(endpoint)
    
    def get_long_short_ratio(self, symbol=None):
        """获取多空比数据"""
        if symbol:
            endpoint = f"/api/long-short/{symbol}"
        else:
            endpoint = "/api/long-short/list"
        return self._make_request(endpoint)
    
    def get_funding_rate(self, symbol=None, rate_type=None):
        """
        获取资金费率
        rate_type: None (特定币种), 'top' (最高), 'low' (最低)
        """
        if symbol:
            endpoint = f"/api/funding-rate/{symbol}"
        elif rate_type:
            endpoint = f"/api/funding-rate/{rate_type}"
        else:
            endpoint = "/api/funding-rate/top"
        return self._make_request(endpoint)
    
    def get_coin_details(self, symbol):
        """获取币种综合数据（包含多时间周期价格、资金流、OI等）"""
        endpoint = f"/api/coin/{symbol}"
        return self._make_request(endpoint)
    
    def get_oi_ranking(self, ranking_type='top'):
        """
        获取OI排名
        ranking_type: 'top' (增长) or 'low' (下降)
        """
        endpoint = f"/api/oi/{ranking_type}-ranking"
        return self._make_request(endpoint)
    
    def get_oi_cap_ranking(self):
        """获取OI市值排名"""
        endpoint = "/api/oi-cap/ranking"
        return self._make_request(endpoint)
    
    def get_query_rank(self):
        """获取社区热度排名"""
        endpoint = "/api/query-rank/list"
        return self._make_request(endpoint)
    
    def get_price_ranking(self, duration='1h', sort='desc'):
        """
        获取价格涨跌排名
        duration: 1m, 5m, 15m, 30m, 1h, 4h, 8h, 12h, 24h, 2d, 3d, 5d, 7d
        sort: 'desc' (涨幅) or 'asc' (跌幅)
        """
        endpoint = "/api/price/ranking"
        params = {'duration': duration, 'sort': sort}
        return self._make_request(endpoint)
    
    def analyze_symbol(self, symbol, include_heatmap=True, include_netflow=True):
        """
        综合分析单个币种
        返回格式化的分析数据用于LM模型
        """
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'data': {}
        }
        
        # 获取综合数据
        coin_data = self.get_coin_details(symbol)
        if coin_data:
            result['data']['coin_details'] = coin_data
        
        # 资金流向
        if include_netflow:
            netflow_1h = self.get_netflow_for_symbol(symbol, '1h')
            netflow_4h = self.get_netflow_for_symbol(symbol, '4h')
            result['data']['netflow'] = {
                '1h': netflow_1h,
                '4h': netflow_4h
            }
        
        # 订单簿热力图
        if include_heatmap:
            heatmap_future = self.get_orderbook_heatmap(symbol, 'future')
            heatmap_spot = self.get_orderbook_heatmap(symbol, 'spot')
            result['data']['heatmap'] = {
                'future': heatmap_future,
                'spot': heatmap_spot
            }
        
        # 多空比
        long_short = self.get_long_short_ratio(symbol)
        if long_short:
            result['data']['long_short_ratio'] = long_short
        
        # 资金费率
        funding = self.get_funding_rate(symbol)
        if funding:
            result['data']['funding_rate'] = funding
        
        return result
    
    def format_for_llm(self, analysis_data):
        """将分析数据格式化为LLM可读的文本"""
        lines = []
        symbol = analysis_data['symbol']
        data = analysis_data.get('data', {})
        
        lines.append(f"\n=== NOFX数据源 ({symbol}) ===\n")
        
        # 资金流向
        if 'netflow' in data and data['netflow'].get('1h'):
            netflow = data['netflow']['1h']
            lines.append("【资金流向 - 1小时】")
            lines.append(f"  机构资金流: {netflow.get('institution_flow', 0):,.2f} USDT")
            lines.append(f"  散户资金流: {netflow.get('personal_flow', 0):,.2f} USDT")
            lines.append(f"  总资金流: {netflow.get('total_flow', 0):,.2f} USDT")
            
            # 判断资金流向
            inst_flow = netflow.get('institution_flow', 0)
            pers_flow = netflow.get('personal_flow', 0)
            if inst_flow > 0 and pers_flow < 0:
                lines.append("  ⚠️ 机构流入，散户流出（机构吸筹）")
            elif inst_flow < 0 and pers_flow > 0:
                lines.append("  ⚠️ 机构流出，散户流入（散户接盘）")
            lines.append("")
        
        # 订单簿热力图
        if 'heatmap' in data:
            heatmap = data['heatmap']
            if heatmap.get('future'):
                h = heatmap['future']
                lines.append("【合约订单簿深度】")
                lines.append(f"  买盘总量: {h.get('bid_volume', 0):,.2f} USDT")
                lines.append(f"  卖盘总量: {h.get('ask_volume', 0):,.2f} USDT")
                lines.append(f"  买卖差值: {h.get('delta', 0):,.2f} USDT")
                
                # 大单分析
                if h.get('large_bids'):
                    lines.append(f"  大买单数量: {len(h['large_bids'])}个")
                if h.get('large_asks'):
                    lines.append(f"  大卖单数量: {len(h['large_asks'])}个")
                
                # 买卖压力
                delta = h.get('delta', 0)
                bid_vol = h.get('bid_volume', 1)
                ask_vol = h.get('ask_volume', 1)
                if abs(delta) > 0:
                    ratio = abs(delta) / max(bid_vol, ask_vol) * 100
                    if delta > 0:
                        lines.append(f"  ✅ 买盘压力较大 ({ratio:.1f}%)")
                    else:
                        lines.append(f"  ⚠️ 卖盘压力较大 ({ratio:.1f}%)")
                lines.append("")
        
        # 多空比
        if 'long_short_ratio' in data and data['long_short_ratio']:
            ls = data['long_short_ratio']
            if isinstance(ls, dict):
                lines.append("【多空比数据】")
                lines.append(f"  多空比: {ls.get('ratio', 'N/A')}")
                if 'start_price' in ls:
                    lines.append(f"  信号触发价格: ${ls['start_price']:.4f}")
                if 'price_change' in ls:
                    lines.append(f"  价格变化: {ls['price_change']:.2f}%")
                lines.append("")
        
        # 综合数据
        if 'coin_details' in data and data['coin_details']:
            details = data['coin_details']
            
            # 价格变化
            if 'price_change' in details:
                pc = details['price_change']
                lines.append("【多周期价格变化】")
                for period in ['1h', '4h', '24h']:
                    if period in pc:
                        change = pc[period] * 100  # 转换为百分比
                        lines.append(f"  {period}: {change:+.2f}%")
                lines.append("")
            
            # OI数据
            if 'oi' in details:
                oi = details['oi']
                lines.append("【持仓量数据】")
                for exchange in ['binance', 'bybit']:
                    if exchange in oi:
                        ex_data = oi[exchange]
                        lines.append(f"  {exchange.upper()}:")
                        lines.append(f"    当前OI: {ex_data.get('oi', 0):,.0f} 张")
                        lines.append(f"    OI变化: {ex_data.get('oi_delta_percent', 0):.2f}%")
                        lines.append(f"    OI价值变化: {ex_data.get('oi_delta_value', 0):,.2f} USDT")
                lines.append("")
        
        return "\n".join(lines)


def test_nofx_api():
    """测试NOFX API"""
    collector = NOFXCollector()
    
    # 测试BTC数据
    print("正在测试NOFX API...")
    
    # 测试资金流
    print("\n1. 测试资金流数据...")
    netflow = collector.get_netflow_for_symbol('btcusdt', '1h')
    if netflow:
        print(f"✅ 资金流数据获取成功")
        print(f"   机构: {netflow.get('institution_flow', 0):,.2f} USDT")
        print(f"   散户: {netflow.get('personal_flow', 0):,.2f} USDT")
    
    # 测试热力图
    print("\n2. 测试订单簿热力图...")
    heatmap = collector.get_orderbook_heatmap('btcusdt', 'future')
    if heatmap:
        print(f"✅ 热力图数据获取成功")
        print(f"   买盘: {heatmap.get('bid_volume', 0):,.2f} USDT")
        print(f"   卖盘: {heatmap.get('ask_volume', 0):,.2f} USDT")
    
    # 综合分析
    print("\n3. 测试综合分析...")
    analysis = collector.analyze_symbol('btcusdt')
    formatted = collector.format_for_llm(analysis)
    print(formatted)


if __name__ == "__main__":
    test_nofx_api()
