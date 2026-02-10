@echo off
chcp 65001 >nul
title 多币种加密货币系统启动器

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║         🚀 多币种加密货币智能交易系统 v2.0                       ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo [启动中] 正在打开各个系统窗口...
echo.

:: 1. 启动数据采集
echo [窗口 1] 📊 启动数据采集...
start "数据采集 - ETH/BTC/BNB/SOL" cmd /k "python start_multi.py"
timeout /t 2 /nobreak >nul

:: 2. 启动 Web 界面
echo [窗口 2] 🌐 启动 Web 界面...
start "Web界面 - localhost:5000" cmd /k "echo 等待数据采集启动... && timeout /t 10 /nobreak >nul && python multi_web_ui.py"
timeout /t 2 /nobreak >nul

:: 3. 启动自动分析
echo [窗口 3] 🤖 启动自动分析...
start "多币种分析 - 自动循环" cmd /k "echo 等待初始数据采集... && timeout /t 30 /nobreak >nul && echo 开始分析... && :loop && python multi_analyzer.py && echo. && echo 等待 5 分钟后重新分析... && timeout /t 300 /nobreak >nul && goto loop"

echo.
echo ═══════════════════════════════════════════════════════════════════
echo ✅ 所有窗口已启动！
echo.
echo 📌 已打开的窗口：
echo   1️⃣  数据采集窗口 - 实时采集市场数据
echo   2️⃣  Web 界面窗口 - http://localhost:5000
echo   3️⃣  分析窗口 - 每 5 分钟自动分析
echo.
echo 💡 提示：
echo   • 在各窗口按 Ctrl+C 停止对应服务
echo   • 浏览器访问 http://localhost:5000 查看数据
echo   • 关闭对应窗口即可停止该服务
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
