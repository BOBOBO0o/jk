@echo off
chcp 65001 >nul
title 启动所有数据采集器

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║         🚀 多币种加密货币系统 - 启动所有采集器                  ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

cd /d C:\Users\jierr\Desktop\jk

echo [1/8] 启动 ETH 现货数据采集...
start "ETH 现货" cmd /k "python start_test.py"
timeout /t 2 /nobreak >nul

echo [2/8] 启动 BTC 现货数据采集...
start "BTC 现货" cmd /k "python start_btc.py"
timeout /t 2 /nobreak >nul

echo [3/8] 启动 BNB 现货数据采集...
start "BNB 现货" cmd /k "python start_bnb.py"
timeout /t 2 /nobreak >nul

echo [4/8] 启动 SOL 现货数据采集...
start "SOL 现货" cmd /k "python start_sol.py"
timeout /t 2 /nobreak >nul

echo [5/8] 启动 ETH 合约数据采集...
start "ETH 合约" cmd /k "python start_eth_futures.py"
timeout /t 2 /nobreak >nul

echo [6/8] 启动 BTC 合约数据采集...
start "BTC 合约" cmd /k "python start_btc_futures.py"
timeout /t 2 /nobreak >nul

echo [7/8] 启动 BNB 合约数据采集...
start "BNB 合约" cmd /k "python start_bnb_futures.py"
timeout /t 2 /nobreak >nul

echo [8/8] 启动 SOL 合约数据采集...
start "SOL 合约" cmd /k "python start_sol_futures.py"
timeout /t 2 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════════
echo ✅ 所有采集器已启动！
echo.
echo 📌 已打开 8 个窗口：
echo   📊 现货数据：ETH, BTC, BNB, SOL
echo   📈 合约数据：ETH, BTC, BNB, SOL
echo.
echo 📂 采集内容：
echo   现货：实时交易、订单簿、K线(7周期)、24h统计
echo   合约：持仓量、资金费率、多空比、大户持仓(案5分钟)
echo.
echo 💡 提示：
echo   • 数据存储在 crypto_data.db 数据库中
echo   • 按 Ctrl+C 在各窗口中停止对应服务
echo   • 等待 1-2 分钟后数据开始积累
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
