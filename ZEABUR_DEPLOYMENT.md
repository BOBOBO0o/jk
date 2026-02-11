# Zeabur 部署指南

## 🚀 为什么选择 Zeabur？

- ✅ **简单易用** - 零配置，自动构建部署
- ✅ **成本低廉** - 比传统云服务器便宜50%+
- ✅ **自动扩展** - 根据流量自动调整资源
- ✅ **持久化存储** - 数据库文件自动保存
- ✅ **一键部署** - 连接GitHub即可

## 📋 方案选择

### 方案A：单容器部署（推荐新手）
**优点：** 简单、成本低（约$5/月）
**缺点：** 所有服务在一个容器中

### 方案B：多容器部署（推荐生产）
**优点：** 独立管理、更稳定
**缺点：** 成本较高（约$15/月）

---

## 🎯 方案A：单容器部署（5分钟完成）

### 步骤1：准备GitHub仓库

```bash
# 1. 初始化Git（如果还没有）
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit for Zeabur deployment"

# 4. 创建GitHub仓库并推送
# 在GitHub上创建新仓库：crypto-collector
git remote add origin https://github.com/your-username/crypto-collector.git
git branch -M main
git push -u origin main
```

### 步骤2：修改Dockerfile使用统一启动

编辑 `Dockerfile`，修改最后一行：
```dockerfile
# 将原来的：
# CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5001", "--timeout", "120", "cloud_api_server:app"]

# 改为：
CMD ["python", "start_all_services.py"]
```

### 步骤3：部署到Zeabur

1. 访问 [Zeabur Dashboard](https://dash.zeabur.com/)
2. 点击 **New Project**
3. 选择 **Deploy from GitHub**
4. 授权并选择您的仓库：`crypto-collector`
5. Zeabur会自动检测到Dockerfile并开始构建
6. 等待3-5分钟，构建完成

### 步骤4：配置域名（可选）

1. 在Project设置中点击 **Domains**
2. Zeabur会自动分配一个域名，如：`crypto-collector.zeabur.app`
3. 或者绑定自定义域名

### 步骤5：测试API

```bash
# 健康检查
curl https://your-app.zeabur.app/health

# 获取数据统计
curl https://your-app.zeabur.app/api/stats

# 获取ETH价格
curl https://your-app.zeabur.app/api/price/ethusdt
```

### 步骤6：本地客户端连接

```python
from local_api_client import CloudDataClient

# 使用Zeabur域名
client = CloudDataClient('https://your-app.zeabur.app')

# 测试连接
health = client.health_check()
print(health)

# 获取实时价格
price = client.get_latest_price('ethusdt')
print(f"ETH: ${price['data']['price']}")
```

---

## 🏗️ 方案B：多容器部署（高级）

### 文件准备

已准备好 `docker-compose.yml`，包含9个服务：
- 4个现货采集器
- 4个合约采集器
- 1个API服务器

### 部署步骤

1. 将 `docker-compose.yml` 推送到GitHub
2. 在Zeabur中选择 **Docker Compose** 部署
3. Zeabur会自动为每个服务创建容器
4. 配置持久化存储（Volumes）

**注意：** 多容器部署需要Zeabur Pro版本

---

## 💾 持久化存储配置

### 在Zeabur Dashboard中：

1. 进入您的服务 → **Storage**
2. 点击 **Create Volume**
3. 配置：
   - Name: `crypto-data`
   - Mount Path: `/app/crypto_data.db`
   - Size: 5GB
4. 保存并重启服务

这样数据库文件会被持久化保存，重启不会丢失数据。

---

## 🔧 环境变量配置（可选）

在Zeabur Dashboard的 **Environment Variables** 中添加：

```
PYTHONUNBUFFERED=1
API_PORT=5001
DB_PATH=/app/crypto_data.db
```

---

## 📊 监控和日志

### 查看日志
1. Zeabur Dashboard → 您的服务
2. 点击 **Logs** 标签
3. 实时查看所有输出

### 查看资源使用
1. 点击 **Metrics** 标签
2. 查看CPU、内存、网络使用情况

---

## 💰 成本估算

### 方案A（单容器）
- **计算资源：** $5/月（共享CPU + 512MB内存）
- **存储：** $1/月（5GB）
- **流量：** 免费（100GB/月）
- **总计：** 约 $6/月 或 ¥40/月

### 方案B（多容器）
- **计算资源：** $15/月（每个容器$1.5/月）
- **存储：** $1/月（5GB共享）
- **流量：** 免费（100GB/月）
- **总计：** 约 $16/月 或 ¥110/月

**对比传统云服务器（¥700-1000/年），Zeabur更便宜且更简单！**

---

## 🛠️ 常见问题

### Q1: 如何重启服务？
**A:** Zeabur Dashboard → 服务 → 右上角菜单 → **Restart**

### Q2: 如何更新代码？
**A:** 推送到GitHub后，Zeabur会自动重新构建部署

### Q3: 数据库文件在哪？
**A:** 配置了Volume后在 `/app/crypto_data.db`，可以通过API下载

### Q4: 如何下载数据库？
```python
client = CloudDataClient('https://your-app.zeabur.app')
client.download_database('local_data.db')
```

### Q5: 如何查看实时数据？
访问：`https://your-app.zeabur.app/api/stats`

### Q6: 服务崩溃了怎么办？
Zeabur会自动重启。查看日志定位问题。

---

## 📝 部署后验证清单

- [ ] 服务状态显示 "Running"
- [ ] `/health` 接口返回正常
- [ ] `/api/stats` 显示数据条数在增长
- [ ] 日志中看到数据采集信息
- [ ] 本地客户端能成功连接
- [ ] 数据库文件正常保存

---

## 🎓 完整部署流程总结

```bash
# 1. 准备代码
cd C:\Users\jierr\Desktop\jk
git init
git add .
git commit -m "Deploy to Zeabur"

# 2. 推送到GitHub
git remote add origin https://github.com/your-username/crypto-collector.git
git push -u origin main

# 3. 在Zeabur部署
# - 访问 dash.zeabur.com
# - 连接GitHub仓库
# - 自动构建部署

# 4. 配置Volume（持久化存储）
# - 在Dashboard中创建Volume
# - 挂载到 /app/crypto_data.db

# 5. 测试
curl https://your-app.zeabur.app/health

# 6. 本地使用
python -c "
from local_api_client import CloudDataClient
client = CloudDataClient('https://your-app.zeabur.app')
print(client.get_latest_price('ethusdt'))
"
```

---

## 🔗 相关链接

- **Zeabur官网：** https://zeabur.com
- **Zeabur文档：** https://zeabur.com/docs
- **定价：** https://zeabur.com/pricing
- **GitHub：** https://github.com/zeabur/zeabur

---

## 📞 支持

遇到问题？
1. 查看Zeabur日志
2. 检查本地测试是否正常
3. 参考 `docker-compose.yml` 进行本地调试

**本地测试命令：**
```bash
docker-compose up
```

---

**恭喜！您的加密货币数据采集系统现在7×24小时运行在云端了！** 🎉
