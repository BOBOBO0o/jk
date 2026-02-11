"""
本地API客户端
用于从云端服务器获取数据
"""
import requests
import json
import gzip
import shutil
from datetime import datetime
import os

class CloudDataClient:
    def __init__(self, server_url='http://your-server-ip:5001'):
        """
        初始化客户端
        server_url: 云端服务器地址，例如 'http://123.45.67.89:5001'
        """
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self):
        """检查服务器健康状态"""
        try:
            response = self.session.get(f'{self.server_url}/health', timeout=5)
            return response.json()
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_stats(self):
        """获取数据统计信息"""
        response = self.session.get(f'{self.server_url}/api/stats')
        return response.json()
    
    def get_latest_price(self, symbol='ethusdt'):
        """获取最新价格"""
        response = self.session.get(f'{self.server_url}/api/price/{symbol}')
        return response.json()
    
    def get_trades(self, symbol='ethusdt', limit=100, start_time=None, end_time=None):
        """获取交易数据"""
        params = {'limit': limit}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        
        response = self.session.get(f'{self.server_url}/api/trades/{symbol}', params=params)
        return response.json()
    
    def get_klines(self, symbol='ethusdt', interval='1h', limit=100, start_time=None):
        """获取K线数据"""
        params = {'limit': limit}
        if start_time:
            params['start_time'] = start_time
        
        response = self.session.get(f'{self.server_url}/api/klines/{symbol}/{interval}', params=params)
        return response.json()
    
    def get_open_interest(self, symbol='ethusdt', limit=100):
        """获取持仓量"""
        response = self.session.get(f'{self.server_url}/api/futures/open_interest/{symbol}', params={'limit': limit})
        return response.json()
    
    def get_funding_rate(self, symbol='ethusdt', limit=100):
        """获取资金费率"""
        response = self.session.get(f'{self.server_url}/api/futures/funding_rate/{symbol}', params={'limit': limit})
        return response.json()
    
    def get_long_short_ratio(self, symbol='ethusdt', limit=100):
        """获取多空比"""
        response = self.session.get(f'{self.server_url}/api/futures/long_short_ratio/{symbol}', params={'limit': limit})
        return response.json()
    
    def get_multi_prices(self):
        """获取所有币种最新价格"""
        response = self.session.get(f'{self.server_url}/api/multi/prices')
        return response.json()
    
    def get_multi_summary(self):
        """获取所有币种综合摘要"""
        response = self.session.get(f'{self.server_url}/api/multi/summary')
        return response.json()
    
    def download_database(self, save_path='downloaded_data.db'):
        """下载完整数据库"""
        print("开始下载数据库...")
        response = self.session.get(f'{self.server_url}/api/download/database', stream=True)
        
        if response.status_code == 200:
            # 保存压缩文件
            gz_path = save_path + '.gz'
            with open(gz_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"下载完成，正在解压...")
            
            # 解压
            with gzip.open(gz_path, 'rb') as f_in:
                with open(save_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除压缩文件
            os.remove(gz_path)
            
            print(f"数据库已保存到: {save_path}")
            return True
        else:
            print(f"下载失败: {response.status_code}")
            return False
    
    def export_table(self, table, symbol=None, limit=10000):
        """导出指定表"""
        params = {'limit': limit}
        if symbol:
            params['symbol'] = symbol
        
        response = self.session.get(f'{self.server_url}/api/export/{table}', params=params)
        return response.json()

# ==================== 使用示例 ====================
if __name__ == '__main__':
    # 1. 初始化客户端（替换为您的服务器IP）
    client = CloudDataClient('http://123.45.67.89:5001')
    
    # 2. 健康检查
    print("=== 健康检查 ===")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # 3. 获取数据统计
    print("\n=== 数据统计 ===")
    stats = client.get_stats()
    print(json.dumps(stats, indent=2))
    
    # 4. 获取最新价格
    print("\n=== ETH 最新价格 ===")
    price = client.get_latest_price('ethusdt')
    print(json.dumps(price, indent=2))
    
    # 5. 获取多币种价格
    print("\n=== 所有币种价格 ===")
    multi_prices = client.get_multi_prices()
    print(json.dumps(multi_prices, indent=2))
    
    # 6. 获取K线数据
    print("\n=== ETH 1小时K线 (最近10根) ===")
    klines = client.get_klines('ethusdt', '1h', limit=10)
    print(f"获取到 {klines['count']} 条K线数据")
    
    # 7. 获取资金费率
    print("\n=== ETH 资金费率 ===")
    fr = client.get_funding_rate('ethusdt', limit=5)
    print(json.dumps(fr, indent=2))
    
    # 8. 下载数据库（可选）
    # print("\n=== 下载完整数据库 ===")
    # client.download_database('local_crypto_data.db')
