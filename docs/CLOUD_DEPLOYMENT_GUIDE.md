# 云端部署完整指南

## 📋 架构概览

```
云服务器 (7×24运行)
├── 数据采集服务 (8个进程)
│   ├── 现货数据: ETH, BTC, BNB, SOL
│   └── 合约数据: ETH, BTC, BNB, SOL
├── API服务器 (Flask)
│   ├── 端口: 5001
│   └── 提供RESTful API
└── 进程管理 (Supervisor)
    └── 自动重启、日志管理

本地客户端
├── API调用获取实时数据
├── 下载历史数据库
└── 本地分析决策
```

## 🚀 一、云服务器部署

### 1.1 服务器要求

**最低配置：**
- CPU: 2核
- 内存: 4GB
- 硬盘: 50GB SSD
- 带宽: 5Mbps
- 系统: Ubuntu 20.04 / CentOS 7+

**推荐配置：**
- CPU: 4核
- 内存: 8GB
- 硬盘: 100GB SSD
- 带宽: 10Mbps

**推荐云服务商：**
- 阿里云 ECS
- 腾讯云 CVM
- AWS EC2
- Vultr / DigitalOcean

### 1.2 系统初始化

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.8+
sudo apt install python3.8 python3-pip -y

# 安装必要工具
sudo apt install git supervisor nginx -y

# 创建工作目录
mkdir -p ~/crypto_collector
cd ~/crypto_collector
```

### 1.3 上传项目文件

**方式1：使用Git**
```bash
# 如果项目已托管在Git仓库
git clone your-repo-url
cd your-repo
```

**方式2：使用SCP/SFTP**
```bash
# 从本地上传
scp -r C:\Users\jierr\Desktop\jk/* user@your-server-ip:~/crypto_collector/
```

**方式3：打包上传**
```bash
# 本地打包
tar -czf crypto_collector.tar.gz jk/

# 上传到服务器
scp crypto_collector.tar.gz user@your-server-ip:~/

# 服务器解压
tar -xzf crypto_collector.tar.gz
```

### 1.4 安装依赖

```bash
cd ~/crypto_collector

# 安装Python依赖
pip3 install -r requirements.txt

# 额外安装API服务依赖
pip3 install flask flask-cors gunicorn
```

### 1.5 配置Supervisor（进程管理）

创建配置文件：
```bash
sudo nano /etc/supervisor/conf.d/crypto_collector.conf
```

添加以下内容：
```ini
[group:crypto_collectors]
programs=eth_spot,btc_spot,bnb_spot,sol_spot,eth_futures,btc_futures,bnb_futures,sol_futures,api_server

# ETH 现货采集
[program:eth_spot]
command=python3 /home/ubuntu/crypto_collector/start_test.py
directory=/home/ubuntu/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/eth_spot.err.log
stdout_logfile=/var/log/crypto/eth_spot.out.log
user=ubuntu

# BTC 现货采集
[program:btc_spot]
command=python3 /home/ubuntu/crypto_collector/start_btc.py
directory=/home/ubuntu/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/btc_spot.err.log
stdout_logfile=/var/log/crypto/btc_spot.out.log
user=ubuntu

# BNB 现货采集
[program:bnb_spot]
command=python3 /home/ubuntu/crypto_collector/start_bnb.py
directory=/home/ubuntu/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/bnb_spot.err.log
stdout_logfile=/var/log/crypto/bnb_spot.out.log
user=ubuntu

# SOL 现货采集
[program:sol_spot]
command=python3 /home/ubuntu/crypto_collector/start_sol.py
directory=/home/ubuntu/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/sol_spot.err.log
stdout_logfile=/var/log/crypto/sol_spot.out.log
user=ubuntu

# ETH 合约采集
[program:eth_futures]
command=python3 /home/ubuntu/crypto_collector/start_eth_futures.py
directory=/home/ubuntu/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/eth_futures.err.log
stdout_logfile=/var/log/crypto/eth_futures.out.log
user=ubuntu

# BTC 合约采集
[program:btc_futures]
command=python3 /home/ubuntu/crypto_collector/start_btc_futures.py
directory=/home/ubuntu/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/btc_futures.err.log
stdout_logfile=/var/log/crypto/btc_futures.out.log
user=ubuntu

# BNB 合约采集
[program:bnb_futures]
command=python3 /home/ubuntu/crypto_collector/start_bnb_futures.py
directory=/home/ubuntu/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/bnb_futures.err.log
stdout_logfile=/var/log/crypto/bnb_futures.out.log
user=ubuntu

# SOL 合约采集
[program:sol_futures]
command=python3 /home/ubuntu/crypto_collector/start_sol_futures.py
directory=/home/ubuntu/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/sol_futures.err.log
stdout_logfile=/var/log/crypto/sol_futures.out.log
user=ubuntu

# API服务器
[program:api_server]
command=gunicorn -w 4 -b 0.0.0.0:5001 cloud_api_server:app
directory=/home/ubuntu/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/api_server.err.log
stdout_logfile=/var/log/crypto/api_server.out.log
user=ubuntu
```

创建日志目录：
```bash
sudo mkdir -p /var/log/crypto
sudo chown -R ubuntu:ubuntu /var/log/crypto
```

重载配置并启动：
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start crypto_collectors:*
```

### 1.6 配置防火墙

```bash
# 开放API端口
sudo ufw allow 5001/tcp

# 开放SSH端口（如果还没开）
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable
```

### 1.7 配置Nginx反向代理（可选）

```bash
sudo nano /etc/nginx/sites-available/crypto_api
```

添加：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 或使用IP

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/crypto_api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📱 二、本地客户端使用

### 2.1 安装依赖

```bash
pip install requests
```

### 2.2 基本使用

```python
from local_api_client import CloudDataClient

# 初始化（替换为您的服务器IP）
client = CloudDataClient('http://123.45.67.89:5001')

# 健康检查
status = client.health_check()
print(status)

# 获取实时价格
price = client.get_latest_price('ethusdt')
print(f"ETH价格: ${price['data']['price']}")

# 获取K线数据
klines = client.get_klines('btcusdt', '1h', limit=24)
print(f"获取到 {klines['count']} 条K线")

# 下载完整数据库
client.download_database('local_data.db')
```

### 2.3 API接口文档

#### 健康检查
```
GET /health
响应: {"status": "ok", "timestamp": 1234567890}
```

#### 获取价格
```
GET /api/price/{symbol}
响应: {"status": "success", "data": {"symbol": "ethusdt", "price": 2500.5}}
```

#### 获取交易数据
```
GET /api/trades/{symbol}?limit=100&start_time=1234567890
响应: {"status": "success", "count": 100, "data": [...]}
```

#### 获取K线
```
GET /api/klines/{symbol}/{interval}?limit=100
响应: {"status": "success", "data": [...]}
```

#### 获取合约数据
```
GET /api/futures/open_interest/{symbol}
GET /api/futures/funding_rate/{symbol}
GET /api/futures/long_short_ratio/{symbol}
```

#### 下载数据库
```
GET /api/download/database
响应: 压缩的数据库文件
```

#### 多币种摘要
```
GET /api/multi/prices
GET /api/multi/summary
```

## 🔧 三、运维管理

### 3.1 查看服务状态

```bash
# 查看所有服务
sudo supervisorctl status

# 查看特定服务
sudo supervisorctl status eth_spot

# 查看日志
tail -f /var/log/crypto/eth_spot.out.log
```

### 3.2 重启服务

```bash
# 重启所有采集器
sudo supervisorctl restart crypto_collectors:*

# 重启单个服务
sudo supervisorctl restart eth_spot

# 重启API服务器
sudo supervisorctl restart api_server
```

### 3.3 数据库维护

```bash
# 查看数据库大小
du -h ~/crypto_collector/crypto_data.db

# 备份数据库
cp ~/crypto_collector/crypto_data.db ~/backups/crypto_data_$(date +%Y%m%d).db

# 定期清理旧数据（可选）
# 创建清理脚本，定期删除30天前的数据
```

### 3.4 定时任务

```bash
crontab -e
```

添加：
```cron
# 每天凌晨3点备份数据库
0 3 * * * cp ~/crypto_collector/crypto_data.db ~/backups/crypto_data_$(date +\%Y\%m\%d).db

# 每周日凌晨4点清理30天前的数据
0 4 * * 0 sqlite3 ~/crypto_collector/crypto_data.db "DELETE FROM trades WHERE timestamp < strftime('%s', 'now', '-30 days') * 1000;"
```

### 3.5 监控告警

安装监控脚本：
```python
# monitor.py
import requests
import time

def check_services():
    try:
        response = requests.get('http://localhost:5001/health', timeout=5)
        if response.status_code != 200:
            send_alert("API服务器异常")
    except:
        send_alert("API服务器无响应")

def send_alert(message):
    # 发送邮件或Telegram通知
    print(f"告警: {message}")

while True:
    check_services()
    time.sleep(300)  # 每5分钟检查一次
```

## 💰 四、成本估算

**阿里云ECS（2核4GB）：**
- 月付: ¥70-100/月
- 年付: ¥600-800/年

**流量费用：**
- API调用流量: ≈5GB/月
- 费用: ¥5-10/月

**总成本：**
- 约 ¥700-1000/年

## 🔒 五、安全建议

1. **使用防火墙**：只开放必要端口
2. **API认证**：添加Token认证（可选）
3. **HTTPS**：配置SSL证书（推荐）
4. **定期备份**：每天自动备份数据库
5. **监控告警**：服务异常及时通知
6. **限流保护**：防止API滥用

## 📚 六、故障排查

### 问题1：采集器无法启动
```bash
# 检查日志
tail -f /var/log/crypto/eth_spot.err.log

# 手动测试
cd ~/crypto_collector
python3 start_test.py
```

### 问题2：API无法访问
```bash
# 检查端口
netstat -tlnp | grep 5001

# 检查防火墙
sudo ufw status

# 测试本地访问
curl http://localhost:5001/health
```

### 问题3：数据库锁定
```bash
# 检查数据库
sqlite3 crypto_data.db "PRAGMA integrity_check;"

# 如果损坏，恢复备份
cp ~/backups/crypto_data_最近日期.db ~/crypto_collector/crypto_data.db
```

## ✅ 七、验证清单

部署完成后，验证以下项目：

- [ ] 8个采集器进程正常运行
- [ ] API服务器响应正常
- [ ] 数据正常写入数据库
- [ ] 本地客户端能成功调用API
- [ ] Supervisor自动重启正常
- [ ] 日志文件正常记录
- [ ] 防火墙规则配置正确
- [ ] 定时备份任务配置

---

**部署支持：** 如有问题，请查看日志文件或联系技术支持
