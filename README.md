# ETH 加密货币智能交易系统

基于AI的以太坊交易分析系统，集成币安交易所数据和以太坊链上数据，使用本地LLM进行智能分析。

## 🌟 功能特性

- ✅ **实时数据采集**
  - 币安交易所逐笔成交数据
  - 订单簿深度数据
  - K线数据（多时间周期）
  - 24小时市场统计

- ✅ **链上数据监控**
  - 以太坊区块监控
  - 大额转账追踪（>50 ETH）
  - 交易所资金流入流出
  - Gas价格监控

- ✅ **AI智能分析**
  - 集成LM Studio本地LLM
  - 综合市场数据分析
  - 交易信号生成
  - 规则引擎备用方案

## 📋 系统要求

### 硬件
- CPU: 4核以上
- 内存: 16GB以上（运行LLM需要）
- 硬盘: 50GB以上
- 网络: 稳定的互联网连接

### 软件
- Python 3.8+
- LM Studio（用于本地LLM）
- Windows/Linux/MacOS

## 🚀 快速开始

### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

### 2. 配置LM Studio

1. 下载并安装 [LM Studio](https://lmstudio.ai/)
2. 在LM Studio中下载推荐模型：
   - Llama 3.2 3B (小显存)
   - Llama 3.1 8B (推荐)
   - Mistral 7B
3. 加载模型并启动本地服务器（默认端口1234）

### 3. 运行系统

```powershell
python main.py
```

按提示选择运行模式：
- **选项1**: 完整系统（推荐）
- **选项2**: 仅币安数据采集
- **选项3**: 仅链上数据采集
- **选项4**: 仅AI分析
- **选项5**: 查看统计

## 📁 文件说明

```
jk/
├── main.py                 # 主程序入口
├── binance_collector.py    # 币安数据采集模块
├── onchain_collector.py    # 链上数据采集模块
├── ai_analyzer.py          # AI分析模块
├── requirements.txt        # Python依赖
├── README.md              # 本文件
└── crypto_data.db         # SQLite数据库（运行后生成）
```

## 💾 数据库结构

系统使用SQLite存储数据，包含以下表：

### 币安数据表
- `trades` - 交易流水
- `orderbook` - 订单簿快照
- `klines` - K线数据
- `ticker_24h` - 24小时统计

### 链上数据表
- `large_transfers` - 大额转账
- `exchange_flow` - 交易所流入流出
- `gas_prices` - Gas价格
- `blocks` - 区块信息

## 🔧 配置说明

### 修改交易对
编辑 `main.py` 中的交易对设置：
```python
binance = BinanceDataCollector('btcusdt')  # 改为BTC
```

### 修改分析频率
编辑 `main.py` 中的时间间隔：
```python
analysis_interval = 300  # 秒，默认5分钟
```

### 配置Etherscan API（可选）
编辑 `onchain_collector.py`：
```python
self.etherscan_key = 'YOUR_API_KEY'  # 在etherscan.io免费注册
```

### 修改RPC节点
编辑 `onchain_collector.py` 中的RPC列表，可添加Infura/Alchemy节点。

## 📊 使用示例

### 完整系统运行流程

1. **启动系统**
```powershell
python main.py
# 选择 1 - 启动完整系统
```

2. **等待数据采集**
- 系统会自动采集60秒初始数据
- 可以看到实时交易、订单簿、区块信息

3. **AI分析**
- 每5分钟自动进行一次分析
- 查看AI给出的交易建议和市场分析

4. **查看统计**
- 按 Ctrl+C 停止
- 重新运行选择 5 查看数据统计

### 单独运行AI分析

如果已经采集了数据，可以单独运行分析：
```powershell
python ai_analyzer.py
```

## ⚠️ 注意事项

### 数据采集
- 首次运行需要等待数据积累
- 链上数据采集需要稳定的网络连接
- 建议至少运行1小时后再进行分析

### LM Studio
- 确保LM Studio已启动并加载模型
- 本地服务器默认端口为1234
- 如果LM Studio不可用，系统会使用规则引擎

### 风险提示
- **本系统仅供学习研究使用**
- **不构成任何投资建议**
- **加密货币投资有风险，入市需谨慎**
- **请勿使用真实资金进行自动交易**

## 🔍 故障排查

### 无法连接币安WebSocket
- 检查网络连接
- 确认币安API未被墙（可能需要代理）

### 无法连接以太坊节点
- 更换RPC节点
- 使用Infura/Alchemy等服务

### LM Studio连接失败
- 确认LM Studio已启动
- 确认本地服务器运行在1234端口
- 检查防火墙设置

### 数据库错误
- 删除 `crypto_data.db` 重新运行
- 检查硬盘空间

## 📈 未来功能

- [ ] 实时交易执行（需要币安API密钥）
- [ ] 更多技术指标计算
- [ ] Web界面可视化
- [ ] 回测功能
- [ ] 多交易对同时监控
- [ ] 风险管理模块
- [ ] 邮件/Telegram通知

## 📝 更新日志

### v1.0 (2024)
- 初始版本
- 币安数据采集
- 以太坊链上监控
- LM Studio集成
- 基础AI分析

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

如有问题，欢迎创建Issue讨论。

---

**免责声明**: 本项目仅供学习研究使用，不构成任何投资建议。加密货币投资有风险，请谨慎决策。
