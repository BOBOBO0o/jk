@echo off
chcp 65001 >nul
title BNB数据采集

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║                    BNB 数据采集系统                               ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo [INFO] 正在启动BNB现货数据采集...
start "BNB现货数据" cmd /k python binance_collector.py bnbusdt

timeout /t 2 >nul

echo [INFO] 正在启动BNB合约数据采集...
start "BNB合约数据" cmd /k python futures_collector.py bnbusdt

echo.
echo ✅ BNB数据采集器已启动
echo    - 现货数据窗口
echo    - 合约数据窗口
echo.
pause
