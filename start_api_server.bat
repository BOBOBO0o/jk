@echo off
chcp 65001 >nul
title API服务器 - 端口5001

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║         🌐 启动API服务器                                         ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

cd /d C:\Users\jierr\Desktop\jk

echo [启动] API服务器启动中...
echo [端口] 5001
echo [地址] http://localhost:5001
echo.
echo ✅ 可用接口：
echo   - 健康检查: http://localhost:5001/health
echo   - 数据统计: http://localhost:5001/api/stats
echo   - ETH价格: http://localhost:5001/api/price/ethusdt
echo   - 多币种: http://localhost:5001/api/multi/summary
echo.

python cloud_api_server.py

pause
