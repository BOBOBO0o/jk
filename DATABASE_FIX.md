# 数据库修复说明

## 🐛 问题描述

Web 界面显示所有币种的数据完全相同，原因是：
1. **数据库表缺少币种字段** - 所有币种的数据混在一起
2. **查询时没有区分币种** - Web UI 查询时没有过滤 symbol

## ✅ 已修复内容

### 1. 数据库结构修改 (`binance_collector.py`)

为所有数据表添加了 `symbol` 字段：

```sql
-- trades 表
ALTER TABLE trades ADD COLUMN symbol TEXT;

-- orderbook 表
ALTER TABLE orderbook ADD COLUMN symbol TEXT;

-- klines 表
ALTER TABLE klines ADD COLUMN symbol TEXT;

-- ticker_24h 表
ALTER TABLE ticker_24h ADD COLUMN symbol TEXT;
```

所有数据插入时都会记录对应的币种：
- ✅ 交易数据 - 包含 symbol
- ✅ 订单簿数据 - 包含 symbol
- ✅ K线数据 - 包含 symbol
- ✅ 24小时统计 - 包含 symbol

### 2. Web UI 查询修改 (`multi_web_ui.py`)

所有数据库查询都添加了币种过滤：

```python
# 修改前（错误）
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10

# 修改后（正确）
SELECT * FROM trades WHERE symbol = ? ORDER BY timestamp DESC LIMIT 10
```

修改的 API 端点：
- ✅ `/api/overview` - 币种概览
- ✅ `/api/symbol/<symbol>/price` - 币种价格
- ✅ `/api/symbol/<symbol>/trades` - 币种交易
- ✅ `/api/symbol/<symbol>/analysis` - 币种分析
- ✅ `/api/compare` - 币种对比

### 3. AI 分析器修改 (`ai_analyzer.py`)

所有查询都添加了币种过滤：
- ✅ 交易数据查询 - WHERE symbol = ?
- ✅ K线数据查询 - WHERE symbol = ?
- ✅ 订单簿查询 - WHERE symbol = ?
- ✅ 24小时统计查询 - WHERE symbol = ?

### 4. 新增独立窗口启动脚本

创建了 `start_separate_windows.bat`：
- ✅ 每个币种一个独立采集窗口
- ✅ ETH, BTC, BNB, SOL 各自独立
- ✅ 可以单独关闭某个币种
- ✅ 更清晰的日志输出

---

## 🚀 使用方法

### 方式一：删除旧数据库（推荐）

如果之前已经运行过系统，建议删除旧数据库重新开始：

```powershell
# 1. 停止所有正在运行的采集程序

# 2. 删除旧数据库
Remove-Item crypto_data.db

# 3. 使用独立窗口模式启动
.\start_separate_windows.bat
```

### 方式二：保留旧数据

如果想保留旧数据，系统会自动添加 symbol 列，但旧数据的 symbol 字段会是 NULL：

```powershell
# 直接启动，系统会自动更新表结构
.\start_separate_windows.bat
```

**注意**：旧数据可能导致查询不准确，建议删除。

---

## 📊 启动脚本对比

### `start_all.bat` - 统一窗口模式
- 所有币种在 1 个窗口中用多线程运行
- 日志混在一起
- 不易单独管理

### `start_separate_windows.bat` - 独立窗口模式 ⭐推荐
- 每个币种一个独立窗口
- 日志清晰分离
- 可以单独关闭某个币种
- 总共 6 个窗口：
  1. ETH 数据采集
  2. BTC 数据采集
  3. BNB 数据采集
  4. SOL 数据采集
  5. Web 界面
  6. 自动分析

---

## ⚠️ 重要提示

### 首次使用新脚本
1. **删除旧数据库** `crypto_data.db`
2. 运行 `start_separate_windows.bat`
3. 等待至少 5 分钟采集初始数据
4. 访问 http://localhost:5000 查看

### 数据采集要求
- 每个币种需要独立的数据连接
- 建议至少运行 30 分钟后再查看分析
- Web 界面会实时更新

### 窗口管理
- 关闭采集窗口会停止该币种的数据采集
- Web 界面窗口关闭后需要重启才能再次访问
- 分析窗口可以随时关闭和重启

---

## 🔍 验证修复是否成功

### 1. 检查数据库
启动采集后，运行以下命令检查：

```powershell
sqlite3 crypto_data.db "SELECT DISTINCT symbol FROM trades"
```

应该看到：
```
ethusdt
btcusdt
bnbusdt
solusdt
```

### 2. 检查 Web 界面
访问 http://localhost:5000，应该看到：
- 每个币种显示**不同的价格**
- 每个币种显示**不同的涨跌幅**
- 每个币种显示**不同的买卖比**

### 3. 检查分析
运行单币种分析：

```powershell
# 分析 BTC
python ai_analyzer.py btcusdt

# 分析 ETH
python ai_analyzer.py ethusdt
```

应该看到不同的分析结果。

---

## 🆘 故障排查

### 问题1：Web 界面仍然显示相同数据
**原因**：使用的是旧数据库
**解决**：删除 `crypto_data.db`，重新启动

### 问题2：某个币种没有数据
**原因**：该币种的采集窗口没有正常运行
**解决**：检查对应的窗口是否有错误信息

### 问题3：symbol 字段为 NULL
**原因**：使用了旧数据
**解决**：删除旧数据库或手动更新：

```sql
-- 手动为旧数据设置 symbol（不推荐）
UPDATE trades SET symbol = 'ethusdt' WHERE symbol IS NULL;
```

---

## 📝 技术细节

### 数据库 Schema 变更

**旧结构**（错误）：
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER,
    price REAL,
    ...
);
```

**新结构**（正确）：
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    symbol TEXT,  -- 新增
    timestamp INTEGER,
    price REAL,
    ...
);
```

### 查询逻辑变更

**旧查询**（错误）：
```python
cursor.execute("SELECT * FROM trades LIMIT 10")
# 返回所有币种混合的数据
```

**新查询**（正确）：
```python
cursor.execute("SELECT * FROM trades WHERE symbol = ? LIMIT 10", (symbol,))
# 只返回指定币种的数据
```

---

## ✅ 检查清单

使用修复后的系统前，确认：

- [ ] 已删除旧数据库 `crypto_data.db`
- [ ] 使用 `start_separate_windows.bat` 启动
- [ ] 看到 6 个独立窗口打开
- [ ] 每个币种窗口都在正常输出日志
- [ ] 等待至少 5 分钟数据采集
- [ ] 访问 http://localhost:5000 验证数据不同
- [ ] 运行 `multi_analyzer.py` 查看对比分析

---

**完成以上步骤后，数据显示问题应该完全解决！** 🎉
