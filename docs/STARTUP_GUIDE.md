# 🚀 启动脚本使用指南

## 📋 快速启动

### 主菜单（推荐）
双击运行：
```
start_menu.bat
```
提供交互式菜单，可以选择启动任何组件。

---

## 🎯 单币种启动脚本

### ETH 以太坊
```bash
start_eth.bat
```
**启动内容：**
- ETH现货数据采集（交易、订单簿、K线）
- ETH合约数据采集（持仓量、资金费率、多空比）

### BTC 比特币
```bash
start_btc.bat
```
**启动内容：**
- BTC现货数据采集
- BTC合约数据采集

### BNB 币安币
```bash
start_bnb.bat
```
**启动内容：**
- BNB现货数据采集
- BNB合约数据采集

### SOL Solana
```bash
start_sol.bat
```
**启动内容：**
- SOL现货数据采集
- SOL合约数据采集

---

## 🌐 Web界面

### 启动Web UI
```bash
start_webui.bat
```
**访问地址：**
- 基础界面: http://localhost:5000
- 增强界面: http://localhost:5000/enhanced

**功能：**
- 实时价格监控
- 多币种对比
- AI分析配置
- 技术指标选择

---

## 🔥 完整系统启动

### 启动所有币种
```bash
start_separate_windows.bat
```
**启动内容：**
- 4个现货数据采集窗口（ETH/BTC/BNB/SOL）
- 4个合约数据采集窗口
- 1个Web UI服务器
- 1个自动分析器（可选）

**总共：10个窗口**

---

## 📊 启动选项对比

| 脚本 | ETH | BTC | BNB | SOL | Web UI | 窗口数 |
|------|-----|-----|-----|-----|--------|--------|
| `start_menu.bat` | ✓ | ✓ | ✓ | ✓ | ✓ | 交互菜单 |
| `start_eth.bat` | ✓ | ✗ | ✗ | ✗ | ✗ | 2 |
| `start_btc.bat` | ✗ | ✓ | ✗ | ✗ | ✗ | 2 |
| `start_bnb.bat` | ✗ | ✗ | ✓ | ✗ | ✗ | 2 |
| `start_sol.bat` | ✗ | ✗ | ✗ | ✓ | ✗ | 2 |
| `start_webui.bat` | ✗ | ✗ | ✗ | ✗ | ✓ | 1 |
| `start_separate_windows.bat` | ✓ | ✓ | ✓ | ✓ | ✓ | 10 |

---

## 💡 使用场景

### 场景1：只关注比特币
```bash
start_btc.bat      # 启动BTC数据采集
start_webui.bat    # 启动Web界面查看
```

### 场景2：对比多个币种
```bash
start_separate_windows.bat  # 启动所有币种
# 访问 http://localhost:5000/enhanced
```

### 场景3：测试单个币种
```bash
start_eth.bat      # 只测试ETH数据
```

### 场景4：轻量级监控
```bash
start_webui.bat    # 只启动Web界面
# 使用已有的数据库数据
```

---

## ⚙️ 自定义启动

### 修改币种
编辑对应的 `.bat` 文件，修改币种参数：
```batch
python binance_collector.py ethusdt
改为
python binance_collector.py 你的币种
```

### 添加新币种
复制 `start_eth.bat`，重命名并修改其中的币种名称。

---

## 🛑 停止服务

### 方法1：关闭窗口
直接关闭对应的命令行窗口

### 方法2：Ctrl+C
在窗口中按 `Ctrl+C` 停止

### 方法3：任务管理器
如果窗口无响应，使用任务管理器结束 Python 进程

---

## 📝 常见问题

### Q: 启动后没有数据？
**A:** 等待1-2分钟，系统需要时间连接Binance并开始采集数据。

### Q: Web UI无法访问？
**A:** 
1. 确认 `start_webui.bat` 正在运行
2. 检查端口5000是否被占用
3. 尝试访问 http://127.0.0.1:5000

### Q: 数据采集器报错？
**A:**
1. 检查网络连接
2. 确认Binance API可访问
3. 查看窗口中的错误信息

### Q: 可以同时启动多个相同币种吗？
**A:** 不建议。同一币种的数据采集器不应重复启动。

### Q: 数据存储在哪里？
**A:** 所有数据存储在 `crypto_data.db` SQLite数据库中。

---

## 🔧 技术说明

### 现货数据采集
- WebSocket实时连接
- 7个K线周期（1m/5m/15m/30m/1h/4h/1d）
- 订单簿深度（20档）
- 实时交易流

### 合约数据采集
- REST API轮询（每5分钟）
- 持仓量（Open Interest）
- 资金费率（Funding Rate）
- 多空比（Long/Short Ratio）
- 大户持仓（Top Trader Position）

### Web服务器
- Flask框架
- 端口：5000
- 支持CORS跨域请求

---

## 📚 相关文档

- [README.md](README.md) - 项目总览
- [NOFX_INTEGRATION.md](NOFX_INTEGRATION.md) - NOFX数据源集成
- [MULTI_ANALYSIS_GUIDE.md](MULTI_ANALYSIS_GUIDE.md) - 多币种分析指南

---

**提示：** 建议使用 `start_menu.bat` 主菜单，提供最佳的交互体验。
