# 加密货币数据采集系统

一个专业的7×24小时加密货币数据采集与分析系统，支持本地部署和云端部署（Zeabur）。

## ✨ 特性

- 🔄 **实时数据采集** - 8个采集器持续运行
  - 4个现货数据采集器（ETH/BTC/BNB/SOL）
  - 4个合约数据采集器（持仓量、资金费率、多空比）
  
- 🌐 **RESTful API** - 完整的API服务
  - 实时价格查询
  - 历史K线数据
  - 合约数据查询
  - 数据库下载

- ☁️ **云端部署** - 支持多种部署方式
  - Zeabur一键部署（推荐）
  - Docker/Docker Compose
  - 传统Linux服务器

- 📊 **数据分析** - 技术指标计算
  - EMA, MACD, RSI, ATR, BOLL
  - 多币种对比分析
  - AI智能分析（可选）

## 🚀 快速开始

### 本地运行

```powershell
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动所有采集器
.\start_all.bat

# 3. 等待数据采集（1-2分钟）
# 数据将保存到 crypto_data.db
```

### 云端部署（Zeabur - 推荐）

```bash
# 1. 推送到GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/crypto-collector.git
git push -u origin main

# 2. 访问 Zeabur Dashboard
# https://dash.zeabur.com

# 3. 连接GitHub仓库，自动部署
# 详细步骤见: ZEABUR_QUICK_START.md
```

## 📦 项目结构

```
crypto-collector/
├── src/                    # 源代码
│   ├── collectors/         # 数据采集器
│   ├── analyzers/          # 数据分析器
│   ├── indicators/         # 技术指标
│   └── ui/                 # Web界面
├── scripts/                # 启动脚本
├── docs/                   # 文档
├── tests/                  # 测试文件
├── Dockerfile              # Docker配置
├── docker-compose.yml      # 多容器编排
├── cloud_api_server.py     # API服务器
├── local_api_client.py     # 本地客户端
└── start_all.bat           # 一键启动
```

## 📖 文档

- **[快速开始 - Zeabur部署](ZEABUR_QUICK_START.md)** ⭐ 推荐！5分钟上线
- **[Zeabur详细部署指南](ZEABUR_DEPLOYMENT.md)** - 完整部署文档
- **[传统云服务器部署](docs/CLOUD_DEPLOYMENT_GUIDE.md)** - Linux服务器部署
- **[系统使用指南](docs/README.md)** - 功能说明
- **[启动脚本指南](docs/STARTUP_GUIDE.md)** - 本地运行

## 💻 本地开发

### 启动数据采集

```powershell
# 启动所有采集器（8个窗口）
.\start_all.bat

# 或单独启动
python start_test.py        # ETH现货
python start_eth_futures.py # ETH合约
```

### 启动API服务器

```powershell
.\start_api_server.bat
# 访问: http://localhost:5001/health
```

## 🌐 API使用

### Python客户端

```python
from local_api_client import CloudDataClient

# 连接到云端服务器
client = CloudDataClient('https://your-app.zeabur.app')

# 获取实时价格
price = client.get_latest_price('ethusdt')
print(f"ETH: ${price['data']['price']}")

# 获取K线数据
klines = client.get_klines('btcusdt', '1h', limit=100)

# 下载完整数据库
client.download_database('local_data.db')
```

### HTTP API

```bash
# 健康检查
GET /health

# 获取价格
GET /api/price/ethusdt

# 获取K线
GET /api/klines/ethusdt/1h?limit=100

# 获取资金费率
GET /api/futures/funding_rate/ethusdt

# 多币种摘要
GET /api/multi/summary
```

## 💰 成本对比

| 方案 | 月成本 | 部署难度 | 维护成本 |
|------|--------|----------|----------|
| **Zeabur** | ¥40 | ⭐ 简单 | ⭐ 低 |
| 传统云服务器 | ¥70-100 | ⭐⭐⭐⭐ 复杂 | ⭐⭐⭐ 高 |
| 本地运行 | ¥0 | ⭐⭐ 中等 | ⭐⭐⭐⭐ 很高 |

**推荐使用Zeabur部署 - 最简单、最便宜、最省心！**

## 🛠️ 技术栈

- **Python 3.8+**
- **WebSocket** - 实时数据流
- **SQLite** - 数据存储
- **Flask** - API服务器
- **Docker** - 容器化部署
- **Zeabur** - 云端托管

## 📊 采集的数据

### 现货数据
- 实时交易流
- 订单簿深度
- K线数据（7个周期：1m/5m/15m/30m/1h/4h/1d）
- 24小时统计

### 合约数据（每5分钟）
- 持仓量（Open Interest）
- 资金费率（Funding Rate）
- 多空比（Long/Short Ratio）
- 大户持仓比例

## ⚠️ 免责声明

**本项目仅供学习研究使用，不构成任何投资建议。**

加密货币投资有风险，请谨慎决策。请勿使用真实资金进行自动交易。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请创建 Issue 讨论。

---

**现在就部署到云端，让数据7×24小时为您工作！** 🚀

查看 [ZEABUR_QUICK_START.md](ZEABUR_QUICK_START.md) 开始部署。
