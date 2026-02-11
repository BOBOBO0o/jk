@echo off
chcp 65001 >nul
title SOL数据采集

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║                    SOL 数据采集系统                               ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo [INFO] 正在启动SOL现货数据采集...
start "SOL现货数据" cmd /k python binance_collector.py solusdt

timeout /t 2 >nul

echo [INFO] 正在启动SOL合约数据采集...
start "SOL合约数据" cmd /k python futures_collector.py solusdt

echo.
echo ✅ SOL数据采集器已启动
echo    - 现货数据窗口
echo    - 合约数据窗口
echo.
pause
