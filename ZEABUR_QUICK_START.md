# Zeabur 快速部署 - 5分钟上线

## ✅ 部署前检查清单

- [ ] 已有GitHub账号
- [ ] 已有Zeabur账号（免费注册：https://dash.zeabur.com）
- [ ] 本地代码已准备好
- [ ] 测试过本地采集器正常运行

---

## 🚀 三步部署

### 第一步：推送到GitHub（2分钟）

```powershell
# 在项目目录执行
cd C:\Users\jierr\Desktop\jk

# 初始化Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Deploy to Zeabur"

# 在GitHub创建新仓库，然后推送
git remote add origin https://github.com/YOUR_USERNAME/crypto-collector.git
git branch -M main
git push -u origin main
```

### 第二步：Zeabur一键部署（2分钟）

1. 访问 https://dash.zeabur.com
2. 点击 **New Project**
3. 选择 **Deploy from GitHub**
4. 选择仓库：`crypto-collector`
5. 等待自动构建（3-5分钟）

### 第三步：配置并测试（1分钟）

1. **生成域名**
   - 点击服务 → **Generate Domain**
   - 获得：`https://your-app.zeabur.app`

2. **测试API**
   ```powershell
   # 健康检查
   curl https://your-app.zeabur.app/health
   
   # 查看数据统计
   curl https://your-app.zeabur.app/api/stats
   ```

3. **本地连接**
   ```python
   from local_api_client import CloudDataClient
   
   client = CloudDataClient('https://your-app.zeabur.app')
   price = client.get_latest_price('ethusdt')
   print(f"ETH: ${price['data']['price']}")
   ```

---

## 💾 配置持久化存储（重要！）

部署后立即配置，防止数据丢失：

1. Zeabur Dashboard → 您的服务
2. 点击 **Storage** 标签
3. **Create Volume**
   - Name: `crypto-data`
   - Mount Path: `/app/crypto_data.db`
   - Size: `5GB`
4. **Restart** 服务

---

## 📋 部署完成验证

```powershell
# 1. 健康检查
curl https://your-app.zeabur.app/health
# 期望输出：{"status":"ok","timestamp":...}

# 2. 查看统计
curl https://your-app.zeabur.app/api/stats
# 期望看到：trades, klines等数据量在增长

# 3. 获取价格
curl https://your-app.zeabur.app/api/price/ethusdt
# 期望输出：{"status":"success","data":{"price":...}}

# 4. 本地客户端测试
python local_api_client.py
```

---

## 💰 费用说明

**免费额度：**
- 每月$5免费额度
- 适合测试和小规模使用

**付费计划（单容器）：**
- $5/月：512MB内存 + 共享CPU
- $10/月：1GB内存 + 1核CPU（推荐）
- 存储：$1/月/5GB

**月度成本估算：**
- 开发/测试：免费
- 生产环境：$6-11/月（约¥40-75/月）

---

## 🔧 常用操作

### 查看日志
```
Zeabur Dashboard → 服务 → Logs
```

### 重启服务
```
Zeabur Dashboard → 服务 → ⋯ → Restart
```

### 更新代码
```powershell
git add .
git commit -m "Update"
git push

# Zeabur会自动重新部署
```

### 下载数据库
```python
client = CloudDataClient('https://your-app.zeabur.app')
client.download_database('backup.db')
```

---

## ⚠️ 重要提示

1. **必须配置Volume** - 否则重启会丢失数据
2. **定期备份** - 使用API下载数据库
3. **监控日志** - 及时发现问题
4. **控制成本** - 关注Zeabur账单

---

## 🎯 下一步

✅ 部署完成后，您可以：

1. **本地开发**
   ```python
   # 实时获取云端数据
   client = CloudDataClient('https://your-app.zeabur.app')
   klines = client.get_klines('btcusdt', '1h', limit=100)
   # 进行本地分析...
   ```

2. **定期下载数据**
   ```python
   # 每天下载一次完整数据库
   import schedule
   schedule.every().day.at("03:00").do(
       lambda: client.download_database('daily_backup.db')
   )
   ```

3. **集成到您的策略**
   ```python
   # 实时监控 + 本地决策
   while True:
       summary = client.get_multi_summary()
       # 您的交易策略...
       time.sleep(60)
   ```

---

## 📚 完整文档

- **详细部署指南：** `ZEABUR_DEPLOYMENT.md`
- **API文档：** 查看 `cloud_api_server.py` 中的接口
- **本地客户端：** `local_api_client.py`

---

## 🎉 完成！

您的加密货币数据采集系统现在：
- ✅ 7×24小时运行在云端
- ✅ 自动采集8个数据源
- ✅ 通过API随时访问
- ✅ 成本只需 $6/月

**开始使用：**
```python
from local_api_client import CloudDataClient
client = CloudDataClient('https://your-app.zeabur.app')
print(client.get_multi_summary())
```

祝您交易顺利！📈
