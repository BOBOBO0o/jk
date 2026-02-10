# 技术指标更新说明

## ✅ 已完成的更新

### 1. 多时间周期 K线采集
修改了 `binance_collector.py`：
- ✅ 添加了 `interval` 字段到 klines 表
- ✅ 同时采集 7 个时间周期：**1m, 5m, 15m, 30m, 1h, 4h, 1d**
- ✅ 每个时间周期独立线程采集

### 2. 技术指标计算模块 (`indicators.py`)
创建了完整的技术指标计算库：
- ✅ **EMA** (指数移动平均线) - 12周期和26周期
- ✅ **MACD** (平滑异同移动平均线) - 包含快线、慢线、信号线、柱状图
- ✅ **RSI** (相对强弱指标) - 14周期
- ✅ **ATR** (平均真实波幅) - 14周期
- ✅ **BOLL** (布林带) - 20周期，2倍标准差

### 3. AI 分析器集成
修改了 `ai_analyzer.py`：
- ✅ 导入技术指标计算模块
- ✅ 查询200根1分钟K线用于指标计算
- ✅ 在数据中添加 `indicators` 字段
- ✅ 提示词中包含所有技术指标信息
- ✅ AI 会综合技术指标给出分析建议

---

## 🚀 如何使用

### 方式一：使用现有窗口
如果系统正在运行，需要重启才能应用更新：

```powershell
# 1. 关闭所有采集窗口（Ctrl+C 或直接关闭窗口）

# 2. 删除旧数据库（可选，如果想保留数据可跳过）
Remove-Item crypto_data.db

# 3. 重新启动
.\start_separate_windows.bat
```

### 方式二：保留旧数据
系统会自动为旧表添加 `interval` 字段，但旧K线数据不会有interval值：

```powershell
# 直接重启即可，不删除数据库
.\start_separate_windows.bat
```

---

## 📊 技术指标说明

### EMA (指数移动平均线)
- **EMA(12)**: 短期趋势
- **EMA(26)**: 长期趋势
- **金叉**: EMA(12) 上穿 EMA(26) - 看涨信号
- **死叉**: EMA(12) 下穿 EMA(26) - 看跌信号

### MACD (平滑异同移动平均线)
- **MACD线**: 快线(12) - 慢线(26)
- **信号线**: MACD的9周期EMA
- **柱状图**: MACD - 信号线
- **多头信号**: 柱状图 > 0 且 MACD > 0
- **空头信号**: 柱状图 < 0 且 MACD < 0

### RSI (相对强弱指标)
- **范围**: 0-100
- **超买**: RSI > 70 (可能回调)
- **超卖**: RSI < 30 (可能反弹)
- **中性**: 30 < RSI < 70

### ATR (平均真实波幅)
- **衡量波动性**: 值越大波动越剧烈
- **用途**: 设置止损位、判断市场活跃度

### BOLL (布林带)
- **上轨**: 中轨 + 2倍标准差
- **中轨**: 20周期SMA
- **下轨**: 中轨 - 2倍标准差
- **突破上轨**: 超买区，可能回调
- **突破下轨**: 超卖区，可能反弹
- **带宽收窄**: 波动率降低，可能即将突破

---

## 📈 多时间周期 K线

系统现在采集 7 个时间周期的 K线：

| 周期 | 说明 | 用途 |
|------|------|------|
| 1m | 1分钟 | 短线交易、实时趋势 |
| 5m | 5分钟 | 日内短线 |
| 15m | 15分钟 | 日内中线 |
| 30m | 30分钟 | 日内长线 |
| 1h | 1小时 | 短期趋势 |
| 4h | 4小时 | 中期趋势 |
| 1d | 1天 | 长期趋势 |

### 查询特定周期的K线

```python
# 查询1小时K线
cursor.execute("""
    SELECT * FROM klines 
    WHERE symbol = 'ethusdt' AND interval = '1h'
    ORDER BY open_time DESC LIMIT 100
""")
```

---

## 🔍 验证技术指标

### 1. 测试技术指标计算
```powershell
python indicators.py
```

应该看到测试输出：
```
测试技术指标计算:
EMA(12): xxx.xx
MACD: {'macd': x.xxxx, 'signal': x.xxxx, ...}
RSI(14): xx.xx
ATR(14): x.xxxx
Bollinger Bands: {...}
```

### 2. 检查K线数据
等待系统运行10分钟后：

```powershell
python -c "import sqlite3; db = sqlite3.connect('crypto_data.db'); cursor = db.cursor(); result = cursor.execute('SELECT symbol, interval, COUNT(*) FROM klines GROUP BY symbol, interval').fetchall(); [print(f'{s} - {i}: {c} 条') for s, i, c in result]"
```

应该看到：
```
ethusdt - 1m: 10 条
ethusdt - 5m: 2 条
ethusdt - 15m: 1 条
...
btcusdt - 1m: 10 条
```

### 3. 运行带技术指标的分析
```powershell
python ai_analyzer.py ethusdt
```

应该在输出中看到技术指标部分。

---

## 💡 分析示例

运行分析后，会看到类似输出：

```
======================================================================
🪙 币种: ETH (ETHUSDT)
⏰ 分析时间: 2024-XX-XX XX:XX:XX
======================================================================

📊 正在获取数据...

💹 当前价格: $2500.00
📈 买卖比: 1.25
📊 订单簿比: 1.15
⛓️  交易所净流出: 150.50 ETH
⛽ Gas价格: 25.00 Gwei

🤖 AI分析中...
✅ LM Studio connected successfully

----------------------------------------------------------------------
市场情绪：看多

技术面分析：
• MACD(0.0234)处于多头趋势，柱状图为正
• RSI(65.5)位于正常区间偏强
• 价格在布林带中轨上方，趋势向上
• EMA(12)>EMA(26)，短期趋势良好

交易建议：适量买入/持有
关键理由：
1. 技术指标显示多头格局
2. 买盘强劲，买卖比>1.2
3. 交易所净流出，惜售情绪浓厚

风险提示：RSI接近超买，注意回调风险
----------------------------------------------------------------------
```

---

## ⚠️ 注意事项

### K线数据积累
- **1分钟K线**: 立即可用
- **5分钟K线**: 需要5分钟后第一根
- **15分钟K线**: 需要15分钟后第一根
- **1小时K线**: 需要1小时后第一根
- **4小时K线**: 需要4小时后第一根
- **1天K线**: 需要1天后第一根

### 技术指标计算要求
- **EMA(12)**: 至少需要12根K线
- **EMA(26)**: 至少需要26根K线
- **MACD**: 至少需要35根K线 (26+9)
- **RSI**: 至少需要15根K线 (14+1)
- **ATR**: 至少需要15根K线 (14+1)
- **BOLL**: 至少需要20根K线

**建议**: 系统运行至少 **30分钟**后再进行分析，以获得准确的技术指标。

---

## 📝 技术细节

### 数据库Schema变更

**klines表新增字段**：
```sql
CREATE TABLE klines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,           -- 新增
    interval TEXT,         -- 新增
    open_time INTEGER,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    close_time INTEGER,
    quote_volume REAL,
    trades_count INTEGER,
    taker_buy_volume REAL,
    taker_buy_quote_volume REAL
);
```

### 数据采集线程
每个币种现在有 **10个线程**：
1. 交易数据
2. 订单簿
3. 24小时统计
4-10. K线 (1m, 5m, 15m, 30m, 1h, 4h, 1d)

---

## ✅ 检查清单

更新后确认：
- [ ] 停止所有旧的采集窗口
- [ ] 运行 `.\start_separate_windows.bat`
- [ ] 看到每个币种窗口输出 K线数据（不同周期）
- [ ] 等待至少30分钟数据积累
- [ ] 运行 `python ai_analyzer.py ethusdt`
- [ ] 验证输出中包含技术指标信息
- [ ] 检查多时间周期K线数据

---

**完成以上步骤后，技术指标功能就完全可用了！** 🎉
