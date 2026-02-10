@echo off
chcp 65001 >nul
title ETH数据采集

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║                    ETH 数据采集系统                               ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo [INFO] 正在启动ETH现货数据采集...
start "ETH现货数据" cmd /k python binance_collector.py ethusdt

timeout /t 2 >nul

echo [INFO] 正在启动ETH合约数据采集...
start "ETH合约数据" cmd /k python futures_collector.py ethusdt

echo.
echo ✅ ETH数据采集器已启动
echo    - 现货数据窗口
echo    - 合约数据窗口
echo.
pause
