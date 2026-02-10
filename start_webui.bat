@echo off
chcp 65001 >nul
title Web UI服务器

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║                    Web UI 服务器                                  ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo [INFO] 正在启动Web服务器...
echo.
echo 访问地址:
echo   - 基础界面: http://localhost:5000
echo   - 增强界面: http://localhost:5000/enhanced
echo.

python multi_web_ui.py

pause
