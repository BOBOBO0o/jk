@echo off
chcp 65001 >nul
title 多币种系统 - 独立窗口启动器

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║         🚀 多币种加密货币系统 - 独立窗口模式                     ║
echo ║                                                                  ║
echo ║         每个币种一个独立窗口                                     ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo [启动中] 正在为每个币种打开独立采集窗口...
echo.

:: 创建临时Python启动脚本
echo import sys > temp_collector.py
echo from binance_collector import BinanceDataCollector >> temp_collector.py
echo. >> temp_collector.py
echo if len(sys.argv) ^> 1: >> temp_collector.py
echo     symbol = sys.argv[1] >> temp_collector.py
echo     print(f"启动 {symbol.upper()} 数据采集...") >> temp_collector.py
echo     collector = BinanceDataCollector(symbol) >> temp_collector.py
echo     collector.start_collection() >> temp_collector.py

:: 1. ETH 数据采集窗口
echo [窗口 1] 📊 启动 ETH 数据采集...
start "ETH 数据采集" cmd /k "python temp_collector.py ethusdt"
timeout /t 2 /nobreak >nul

:: 2. BTC 数据采集窗口
echo [窗口 2] 📊 启动 BTC 数据采集...
start "BTC 数据采集" cmd /k "python temp_collector.py btcusdt"
timeout /t 2 /nobreak >nul

:: 3. BNB 数据采集窗口
echo [窗口 3] 📊 启动 BNB 数据采集...
start "BNB 数据采集" cmd /k "python temp_collector.py bnbusdt"
timeout /t 2 /nobreak >nul

:: 4. SOL 数据采集窗口
echo [窗口 4] 📊 启动 SOL 数据采集...
start "SOL 数据采集" cmd /k "python temp_collector.py solusdt"
timeout /t 2 /nobreak >nul

:: 9. Web 界面窗口
echo [窗口 9] 🌐 启动 Web 界面...
start "Web界面 - localhost:5000" cmd /k "echo 等待数据采集启动... && timeout /t 20 /nobreak >nul && python multi_web_ui.py"
timeout /t 2 /nobreak >nul

:: 10. 自动分析窗口
echo [窗口 10] 🤖 启动自动分析...
start "多币种分析 - 自动循环" cmd /k "echo 等待初始数据采集... && timeout /t 50 /nobreak >nul && :loop && python multi_analyzer.py && echo. && echo 等待 5 分钟后重新分析... && timeout /t 300 /nobreak >nul && goto loop"

echo.
echo ═══════════════════════════════════════════════════════════════════
echo ✅ 所有窗口已启动！
echo.
echo 📌 已打开 10 个窗口：
echo   📊 现货数据采集: ETH, BTC, BNB, SOL
echo   📈 合约数据采集: ETH, BTC, BNB, SOL
echo   🌐 Web 界面: http://localhost:5000
echo   🤖 自动分析: 每 5 分钟一次
echo.
echo 💡 提示：
echo   • 现货数据: 实时交易、订单簿、K线（7个周期）
echo   • 合约数据: 持仓量、资金费率、多空比、大户持仓
echo   • 技术指标: EMA, MACD, RSI, ATR, BOLL
echo   • 浏览器访问 http://localhost:5000 查看数据
echo   • 按 Ctrl+C 在窗口中停止对应服务
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
