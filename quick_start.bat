@echo off
chcp 65001 >nul
title 快速启动菜单

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║         🚀 多币种加密货币系统 - 快速启动菜单                    ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo 请选择要启动的模块：
echo.
echo   [1] 📊 数据采集（多币种）
echo   [2] 🌐 Web 界面
echo   [3] 🤖 多币种分析（单次）
echo   [4] 🔄 多币种分析（自动循环，每5分钟）
echo   [5] 📈 单币种分析
echo   [6] 🚀 一键启动全部（3个窗口）
echo.
echo   [0] ❌ 退出
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
set /p choice=请输入选项 [0-6]: 

if "%choice%"=="1" goto collector
if "%choice%"=="2" goto webui
if "%choice%"=="3" goto analyze_once
if "%choice%"=="4" goto analyze_loop
if "%choice%"=="5" goto single_analyze
if "%choice%"=="6" goto start_all
if "%choice%"=="0" goto end
echo.
echo ❌ 无效选项，请重新选择
timeout /t 2 /nobreak >nul
goto menu

:collector
echo.
echo 📊 启动多币种数据采集...
start "数据采集 - 多币种" cmd /k "python start_multi.py"
goto menu_wait

:webui
echo.
echo 🌐 启动 Web 界面...
echo 💡 提示: 确保数据采集已启动
start "Web界面 - localhost:5000" cmd /k "python multi_web_ui.py"
goto menu_wait

:analyze_once
echo.
echo 🤖 运行多币种分析（单次）...
start "多币种分析" cmd /k "python multi_analyzer.py && echo. && echo 分析完成！ && pause"
goto menu_wait

:analyze_loop
echo.
echo 🔄 启动自动循环分析（每5分钟）...
start "多币种分析 - 自动循环" cmd /k "echo 开始自动分析循环... && :loop && python multi_analyzer.py && echo. && echo 等待 5 分钟后重新分析... && timeout /t 300 /nobreak && goto loop"
goto menu_wait

:single_analyze
cls
echo.
echo 📈 单币种分析
echo ═══════════════════════════════════════════════════════════════════
echo.
echo 请选择要分析的币种：
echo   [1] ETH
echo   [2] BTC
echo   [3] BNB
echo   [4] SOL
echo   [5] BERA
echo   [0] 返回主菜单
echo.
set /p coin=请输入选项 [0-5]: 

if "%coin%"=="1" set symbol=ethusdt
if "%coin%"=="2" set symbol=btcusdt
if "%coin%"=="3" set symbol=bnbusdt
if "%coin%"=="4" set symbol=solusdt
if "%coin%"=="5" set symbol=berausdt
if "%coin%"=="0" goto menu

if defined symbol (
    echo.
    echo 分析 %symbol%...
    start "单币种分析 - %symbol%" cmd /k "python ai_analyzer.py %symbol% && echo. && pause"
    set symbol=
    goto menu_wait
) else (
    echo.
    echo ❌ 无效选项
    timeout /t 2 /nobreak >nul
    goto single_analyze
)

:start_all
echo.
echo 🚀 一键启动全部系统...
echo.
echo [窗口 1] 📊 数据采集
start "数据采集 - 多币种" cmd /k "python start_multi.py"
timeout /t 3 /nobreak >nul

echo [窗口 2] 🌐 Web 界面
start "Web界面 - localhost:5000" cmd /k "echo 等待数据采集启动... && timeout /t 10 /nobreak >nul && python multi_web_ui.py"
timeout /t 3 /nobreak >nul

echo [窗口 3] 🤖 自动分析
start "多币种分析 - 自动循环" cmd /k "echo 等待初始数据... && timeout /t 30 /nobreak >nul && :loop && python multi_analyzer.py && echo. && echo 等待 5 分钟... && timeout /t 300 /nobreak >nul && goto loop"

echo.
echo ✅ 所有窗口已启动！
echo 💡 浏览器访问: http://localhost:5000
goto menu_wait

:menu_wait
echo.
echo.
echo 按任意键返回主菜单...
pause >nul
goto menu

:end
echo.
echo 👋 感谢使用！
timeout /t 2 /nobreak >nul
exit
