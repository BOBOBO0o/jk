@echo off
chcp 65001 >nul
title 加密货币交易系统 - 主菜单

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║           🚀 多币种加密货币智能交易分析系统                         ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo  请选择启动选项:
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.
echo    【1】启动所有币种数据采集 (ETH+BTC+BNB+SOL + Web UI)
echo    【2】启动Web UI服务器
echo.
echo  ───────────────────────────────────────────────────────────────
echo.
echo    【3】只启动 ETH 数据采集
echo    【4】只启动 BTC 数据采集
echo    【5】只启动 BNB 数据采集
echo    【6】只启动 SOL 数据采集
echo.
echo  ───────────────────────────────────────────────────────────────
echo.
echo    【7】启动所有ETH相关 (现货+合约+Web)
echo    【8】启动所有BTC相关 (现货+合约+Web)
echo    【9】启动所有BNB相关 (现货+合约+Web)
echo    【0】启动所有SOL相关 (现货+合约+Web)
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.
echo    【Q】退出
echo.

set /p choice=请输入选项 (1-9, 0, Q): 

if /i "%choice%"=="1" goto all
if /i "%choice%"=="2" goto webui
if /i "%choice%"=="3" goto eth
if /i "%choice%"=="4" goto btc
if /i "%choice%"=="5" goto bnb
if /i "%choice%"=="6" goto sol
if /i "%choice%"=="7" goto eth_all
if /i "%choice%"=="8" goto btc_all
if /i "%choice%"=="9" goto bnb_all
if /i "%choice%"=="0" goto sol_all
if /i "%choice%"=="Q" goto end

echo.
echo ❌ 无效选项，请重新选择
timeout /t 2 >nul
goto menu

:all
cls
echo.
echo 🚀 启动所有数据采集器...
start "" start_separate_windows.bat
timeout /t 2 >nul
echo.
echo ✅ 所有窗口已启动
timeout /t 3 >nul
goto menu

:webui
cls
echo.
echo 🌐 启动Web UI服务器...
start "" start_webui.bat
timeout /t 2 >nul
goto menu

:eth
cls
echo.
echo 💎 启动ETH数据采集...
start "" start_eth.bat
timeout /t 2 >nul
goto menu

:btc
cls
echo.
echo ₿ 启动BTC数据采集...
start "" start_btc.bat
timeout /t 2 >nul
goto menu

:bnb
cls
echo.
echo 🔶 启动BNB数据采集...
start "" start_bnb.bat
timeout /t 2 >nul
goto menu

:sol
cls
echo.
echo ☀️ 启动SOL数据采集...
start "" start_sol.bat
timeout /t 2 >nul
goto menu

:eth_all
cls
echo.
echo 💎 启动ETH完整系统 (现货+合约+Web UI)...
start "" start_eth.bat
timeout /t 2 >nul
start "" start_webui.bat
timeout /t 2 >nul
echo.
echo ✅ ETH系统已启动
timeout /t 3 >nul
goto menu

:btc_all
cls
echo.
echo ₿ 启动BTC完整系统 (现货+合约+Web UI)...
start "" start_btc.bat
timeout /t 2 >nul
start "" start_webui.bat
timeout /t 2 >nul
echo.
echo ✅ BTC系统已启动
timeout /t 3 >nul
goto menu

:bnb_all
cls
echo.
echo 🔶 启动BNB完整系统 (现货+合约+Web UI)...
start "" start_bnb.bat
timeout /t 2 >nul
start "" start_webui.bat
timeout /t 2 >nul
echo.
echo ✅ BNB系统已启动
timeout /t 3 >nul
goto menu

:sol_all
cls
echo.
echo ☀️ 启动SOL完整系统 (现货+合约+Web UI)...
start "" start_sol.bat
timeout /t 2 >nul
start "" start_webui.bat
timeout /t 2 >nul
echo.
echo ✅ SOL系统已启动
timeout /t 3 >nul
goto menu

:end
cls
echo.
echo 👋 感谢使用！
echo.
timeout /t 2 >nul
exit
