@echo off
chcp 65001 >nul
title BTC数据采集

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║                    BTC 数据采集系统                               ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo [INFO] 正在启动BTC现货数据采集...
start "BTC现货数据" cmd /k python binance_collector.py btcusdt

timeout /t 2 >nul

echo [INFO] 正在启动BTC合约数据采集...
start "BTC合约数据" cmd /k python futures_collector.py btcusdt

echo.
echo ✅ BTC数据采集器已启动
echo    - 现货数据窗口
echo    - 合约数据窗口
echo.
pause
