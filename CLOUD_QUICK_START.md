# 云端部署快速参考

## 🚀 三步部署到云端

### 第一步：准备服务器
```bash
# 购买云服务器（推荐配置：2核4GB）
# 阿里云/腾讯云/AWS 都可以

# SSH登录服务器
ssh user@your-server-ip
```

### 第二步：一键安装脚本
```bash
# 下载并运行自动部署脚本
curl -o deploy.sh https://your-repo/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh
```

### 第三步：本地调用
```python
from local_api_client import CloudDataClient

client = CloudDataClient('http://your-server-ip:5001')
price = client.get_latest_price('ethusdt')
print(f"ETH: ${price['data']['price']}")
```

---

## 📦 完整文件清单

**云端部署需要：**
1. `cloud_api_server.py` - API服务器
2. `start_*.py` - 8个采集器启动脚本
3. `src/collectors/` - 采集器源码
4. `requirements.txt` - Python依赖

**本地使用需要：**
1. `local_api_client.py` - API客户端
2. 您的分析脚本

---

## 🔑 核心API接口

### 实时数据
```python
# 获取最新价格
client.get_latest_price('ethusdt')

# 获取所有币种价格
client.get_multi_prices()

# 获取综合摘要
client.get_multi_summary()
```

### 历史数据
```python
# 获取K线
client.get_klines('btcusdt', '1h', limit=100)

# 获取交易记录
client.get_trades('ethusdt', limit=1000)

# 获取资金费率
client.get_funding_rate('ethusdt')
```

### 数据下载
```python
# 下载完整数据库
client.download_database('local_data.db')
```

---

## 💡 使用场景示例

### 场景1：实时监控
```python
import time

while True:
    summary = client.get_multi_summary()
    for symbol, data in summary['data'].items():
        print(f"{symbol}: ${data['price']} ({data['price_change_percent']}%)")
    time.sleep(60)
```

### 场景2：数据分析
```python
# 下载数据到本地
client.download_database('analysis_data.db')

# 本地分析
import sqlite3
db = sqlite3.connect('analysis_data.db')
cursor = db.cursor()
cursor.execute('SELECT * FROM klines WHERE symbol = "ethusdt" AND interval = "1h"')
data = cursor.fetchall()
# 进行技术分析...
```

### 场景3：定时报告
```python
import schedule

def daily_report():
    summary = client.get_multi_summary()
    # 生成报告
    # 发送邮件/Telegram
    pass

schedule.every().day.at("09:00").do(daily_report)
```

---

## 🛠️ 常用命令

### 云端服务器
```bash
# 查看所有服务状态
sudo supervisorctl status

# 重启所有服务
sudo supervisorctl restart crypto_collectors:*

# 查看实时日志
tail -f /var/log/crypto/eth_spot.out.log

# 查看数据库大小
du -h ~/crypto_collector/crypto_data.db
```

### 本地测试
```bash
# 启动本地API服务器（测试用）
python cloud_api_server.py

# 测试客户端连接
python local_api_client.py

# 启动所有采集器
.\start_all.bat
```

---

## 📊 成本与收益

**投入：**
- 云服务器：¥700-1000/年
- 时间成本：2-3小时部署

**收益：**
- ✅ 7×24小时不间断数据采集
- ✅ 随时随地获取最新数据
- ✅ 历史数据完整保存
- ✅ 本地电脑无需常开
- ✅ 多设备共享数据

---

## 🔐 安全检查清单

部署前检查：
- [ ] 修改SSH默认端口
- [ ] 禁用root登录
- [ ] 配置防火墙规则
- [ ] 设置强密码
- [ ] 配置定时备份

部署后验证：
- [ ] API健康检查正常
- [ ] 数据正常写入
- [ ] 日志文件正常
- [ ] 自动重启功能正常
- [ ] 本地客户端能连接

---

## 📞 支持

**详细文档：** `docs/CLOUD_DEPLOYMENT_GUIDE.md`

**快速测试：**
1. 本地启动API: `.\start_api_server.bat`
2. 浏览器访问: http://localhost:5001/health
3. 测试客户端: `python local_api_client.py`
