# NOFX数据源集成说明

## 📋 概述

已成功集成NOFX API数据源，为LM模型AI分析提供更多维度的市场数据。用户可以在前端界面勾选需要的数据源和指标。

## 🆕 新增功能

### 1. NOFX数据采集器 (`nofx_collector.py`)

**核心功能：**
- ✅ **机构/散户资金流** - 区分机构和散户的资金流向
- ✅ **订单簿热力图** - 合约和现货的大单监控、支撑阻力分析
- ✅ **多周期价格数据** - 跨交易所持仓量对比

**主要方法：**
```python
from nofx_collector import NOFXCollector

collector = NOFXCollector(api_key='your_key')  # api_key可选

# 获取资金流数据
netflow = collector.get_netflow_for_symbol('btcusdt', '1h')

# 获取订单簿热力图
heatmap = collector.get_orderbook_heatmap('btcusdt', 'future')

# 综合分析
analysis = collector.analyze_symbol('btcusdt', 
                                    include_heatmap=True, 
                                    include_netflow=True)
```

### 2. AI分析器增强 (`ai_analyzer.py`)

**新增配置参数：**
```python
config = {
    'indicators': ['ema', 'macd', 'rsi', 'atr', 'boll'],  # 技术指标
    'dataSources': ['volume', 'oi-market', 'funding-market'],  # 币安数据
    'nofx': ['netflow', 'heatmap'],  # NOFX数据源
    'customPrompt': '用户自定义提示词'  # 可选
}

analyzer = AIAnalyzer(symbol='btcusdt', nofx_api_key='your_key')
data = analyzer.get_recent_data(hours=1)
analysis = analyzer.analyze_with_lm_studio(data, config=config)
```

### 3. 前端配置面板 (`multi_index_enhanced.html`)

**新增界面元素：**
- 📊 量化数据源选择（OI持仓、资金费率等）
- 📉 技术指标勾选（EMA、MACD、RSI、ATR、BOLL）
- 📰 市场信息配置（成交量、持仓量、资金费率）
- 🌐 NOFX数据源（机构/散户资金流、订单簿热力图）
- 🤖 AI自定义提示词输入框
- ⏱️ 时间周期选择器

## 🚀 使用方法

### 步骤1：启动系统

使用原有的启动脚本：
```bash
# Windows
start_separate_windows.bat

# 或直接启动Web UI
python multi_web_ui.py
```

### 步骤2：访问增强版界面

在浏览器中访问增强版页面（需要在`multi_web_ui.py`中添加路由）：
```
http://localhost:5000/enhanced
```

### 步骤3：配置分析参数

1. **选择技术指标** - 点击指标卡片激活/取消（黄色边框=已选中）
2. **选择数据源** - 勾选需要的市场数据（蓝色边框=已选中）
3. **选择NOFX数据** - 勾选机构资金流和订单簿热力图
4. **输入自定义提示词**（可选）- 例如："重点分析短线交易机会"
5. **点击币种卡片** - 选择要分析的币种
6. **点击"开始AI分析"**

### 步骤4：查看分析结果

- 系统会根据你勾选的配置动态生成提示词
- LM Studio会综合所有选中的数据进行分析
- 分析结果包括：市场情绪、交易建议、关键理由、风险提示

## 📊 NOFX数据说明

### 机构/散户资金流
```
【资金流向 - 1小时】
  机构资金流: +1,234,567.89 USDT
  散户资金流: -987,654.32 USDT
  总资金流: +246,913.57 USDT
  ⚠️ 机构流入，散户流出（机构吸筹）
```

**分析意义：**
- 机构流入 + 散户流出 = 主力吸筹，看涨信号
- 机构流出 + 散户流入 = 散户接盘，看跌信号

### 订单簿热力图
```
【合约订单簿深度】
  买盘总量: 12,345,678.90 USDT
  卖盘总量: 9,876,543.21 USDT
  买卖差值: +2,469,135.69 USDT
  大买单数量: 15个
  大卖单数量: 8个
  ✅ 买盘压力较大 (20.0%)
```

**分析意义：**
- 买盘压力大 = 支撑强，看涨
- 卖盘压力大 = 阻力强，看跌
- 大单监控 = 主力动向

## 🧪 测试

运行测试脚本验证集成：
```bash
python test_nofx_integration.py
```

测试内容：
1. ✅ NOFX API基础功能测试
2. ✅ AI分析器配置功能测试
3. ✅ 完整系统集成测试

## 📝 配置示例

### 示例1：短线交易分析
```javascript
{
  indicators: ['rsi', 'macd'],
  dataSources: ['volume'],
  nofx: ['netflow', 'heatmap'],
  customPrompt: '侧重15分钟和1小时短线交易机会，关注快速进出场点位'
}
```

### 示例2：中长线投资分析
```javascript
{
  indicators: ['ema', 'boll'],
  dataSources: ['oi-market', 'funding-market'],
  nofx: ['netflow'],
  customPrompt: '中长线投资分析，关注持仓量变化和机构资金流向'
}
```

### 示例3：完整多维度分析
```javascript
{
  indicators: ['ema', 'macd', 'rsi', 'atr', 'boll'],
  dataSources: ['volume', 'oi-market', 'funding-market'],
  nofx: ['netflow', 'heatmap'],
  customPrompt: ''  // 使用默认综合分析
}
```

## ⚙️ API密钥配置（可选）

NOFX API支持无密钥访问（有频率限制）。如需高频访问：

1. 在 `ai_analyzer.py` 初始化时传入密钥：
```python
analyzer = AIAnalyzer(symbol='btcusdt', nofx_api_key='your_api_key')
```

2. 或在环境变量中设置：
```bash
set NOFX_API_KEY=your_api_key
```

## 📈 数据更新频率

- **Binance数据**: 实时WebSocket + REST API
- **NOFX数据**: 按需获取（分析时实时调用）
- **技术指标**: 基于最近200根K线实时计算

## 🔧 故障排查

### NOFX数据获取失败
1. 检查网络连接
2. 确认API访问限制（30请求/秒）
3. 查看日志输出

### LM Studio连接失败
1. 确保LM Studio已启动
2. 确认本地服务运行在 `localhost:1234`
3. 检查模型是否已加载

### 前端配置不生效
1. 清除浏览器缓存
2. 检查JavaScript控制台错误
3. 确认后端API端点已更新

## 📁 相关文件

```
jk/
├── nofx_collector.py          # NOFX数据采集器
├── ai_analyzer.py              # 增强的AI分析器（已修改）
├── templates/
│   └── multi_index_enhanced.html  # 增强版前端界面
├── test_nofx_integration.py   # 集成测试脚本
└── NOFX_INTEGRATION.md        # 本文档
```

## 🎯 下一步

1. ✅ 测试NOFX API连接
2. ✅ 验证数据采集
3. ⏳ 在 `multi_web_ui.py` 中添加 `/enhanced` 路由
4. ⏳ 更新分析API端点以接收配置参数
5. ⏳ 启动系统并测试完整流程

---

**注意：** NOFX API为第三方服务，请遵守其使用条款和频率限制。
