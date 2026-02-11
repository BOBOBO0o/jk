#!/bin/bash

###############################################################################
# 加密货币数据采集系统 - 云端自动部署脚本
# 适用于 Ubuntu 20.04 / Debian 11
###############################################################################

set -e  # 遇到错误立即退出

echo "=================================================="
echo "  加密货币数据采集系统 - 云端部署"
echo "=================================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 获取当前用户（排除root）
CURRENT_USER=${SUDO_USER:-$USER}
HOME_DIR="/home/$CURRENT_USER"
INSTALL_DIR="$HOME_DIR/crypto_collector"

echo "📋 安装信息："
echo "   用户: $CURRENT_USER"
echo "   安装目录: $INSTALL_DIR"
echo ""

# 1. 更新系统
echo "📦 [1/8] 更新系统..."
apt update -y
apt upgrade -y

# 2. 安装Python和依赖
echo "🐍 [2/8] 安装Python和依赖..."
apt install -y python3 python3-pip python3-venv git supervisor nginx

# 3. 创建工作目录
echo "📁 [3/8] 创建工作目录..."
mkdir -p $INSTALL_DIR
mkdir -p $HOME_DIR/backups
chown -R $CURRENT_USER:$CURRENT_USER $INSTALL_DIR
chown -R $CURRENT_USER:$CURRENT_USER $HOME_DIR/backups

# 4. 安装Python包
echo "📚 [4/8] 安装Python依赖..."
pip3 install websocket-client requests flask flask-cors gunicorn urllib3

# 5. 创建日志目录
echo "📝 [5/8] 创建日志目录..."
mkdir -p /var/log/crypto
chown -R $CURRENT_USER:$CURRENT_USER /var/log/crypto

# 6. 配置Supervisor
echo "⚙️ [6/8] 配置Supervisor..."
cat > /etc/supervisor/conf.d/crypto_collector.conf << 'EOF'
[group:crypto_collectors]
programs=eth_spot,btc_spot,bnb_spot,sol_spot,eth_futures,btc_futures,bnb_futures,sol_futures,api_server

[program:eth_spot]
command=python3 start_test.py
directory=/home/CURRENT_USER/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/eth_spot.err.log
stdout_logfile=/var/log/crypto/eth_spot.out.log
user=CURRENT_USER
environment=PYTHONUNBUFFERED=1

[program:btc_spot]
command=python3 start_btc.py
directory=/home/CURRENT_USER/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/btc_spot.err.log
stdout_logfile=/var/log/crypto/btc_spot.out.log
user=CURRENT_USER
environment=PYTHONUNBUFFERED=1

[program:bnb_spot]
command=python3 start_bnb.py
directory=/home/CURRENT_USER/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/bnb_spot.err.log
stdout_logfile=/var/log/crypto/bnb_spot.out.log
user=CURRENT_USER
environment=PYTHONUNBUFFERED=1

[program:sol_spot]
command=python3 start_sol.py
directory=/home/CURRENT_USER/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/sol_spot.err.log
stdout_logfile=/var/log/crypto/sol_spot.out.log
user=CURRENT_USER
environment=PYTHONUNBUFFERED=1

[program:eth_futures]
command=python3 start_eth_futures.py
directory=/home/CURRENT_USER/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/eth_futures.err.log
stdout_logfile=/var/log/crypto/eth_futures.out.log
user=CURRENT_USER
environment=PYTHONUNBUFFERED=1

[program:btc_futures]
command=python3 start_btc_futures.py
directory=/home/CURRENT_USER/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/btc_futures.err.log
stdout_logfile=/var/log/crypto/btc_futures.out.log
user=CURRENT_USER
environment=PYTHONUNBUFFERED=1

[program:bnb_futures]
command=python3 start_bnb_futures.py
directory=/home/CURRENT_USER/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/bnb_futures.err.log
stdout_logfile=/var/log/crypto/bnb_futures.out.log
user=CURRENT_USER
environment=PYTHONUNBUFFERED=1

[program:sol_futures]
command=python3 start_sol_futures.py
directory=/home/CURRENT_USER/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/sol_futures.err.log
stdout_logfile=/var/log/crypto/sol_futures.out.log
user=CURRENT_USER
environment=PYTHONUNBUFFERED=1

[program:api_server]
command=gunicorn -w 4 -b 0.0.0.0:5001 cloud_api_server:app
directory=/home/CURRENT_USER/crypto_collector
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto/api_server.err.log
stdout_logfile=/var/log/crypto/api_server.out.log
user=CURRENT_USER
environment=PYTHONUNBUFFERED=1
EOF

# 替换用户名
sed -i "s/CURRENT_USER/$CURRENT_USER/g" /etc/supervisor/conf.d/crypto_collector.conf

# 7. 配置定时备份
echo "💾 [7/8] 配置定时备份..."
(crontab -u $CURRENT_USER -l 2>/dev/null; echo "0 3 * * * cp $INSTALL_DIR/crypto_data.db $HOME_DIR/backups/crypto_data_\$(date +\\%Y\\%m\\%d).db") | crontab -u $CURRENT_USER -

# 8. 配置防火墙
echo "🔥 [8/8] 配置防火墙..."
ufw allow 5001/tcp
ufw allow 22/tcp
echo "y" | ufw enable || true

echo ""
echo "=================================================="
echo "✅ 部署完成！"
echo "=================================================="
echo ""
echo "📋 下一步操作："
echo ""
echo "1. 上传项目文件到: $INSTALL_DIR"
echo "   scp -r jk/* $CURRENT_USER@$(hostname -I | awk '{print $1}'):$INSTALL_DIR/"
echo ""
echo "2. 启动所有服务："
echo "   sudo supervisorctl reread"
echo "   sudo supervisorctl update"
echo "   sudo supervisorctl start crypto_collectors:*"
echo ""
echo "3. 查看服务状态："
echo "   sudo supervisorctl status"
echo ""
echo "4. 测试API："
echo "   curl http://localhost:5001/health"
echo ""
echo "5. 本地访问（替换为您的服务器IP）："
echo "   http://$(hostname -I | awk '{print $1}'):5001/health"
echo ""
echo "=================================================="
echo "📚 详细文档: docs/CLOUD_DEPLOYMENT_GUIDE.md"
echo "=================================================="
