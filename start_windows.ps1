# 多币种加密货币系统 - 多窗口启动脚本
# 使用方法: .\start_windows.ps1

Write-Host "
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🚀 多币种加密货币智能交易系统 v2.0                       ║
║                   多窗口启动器                                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

Write-Host "正在启动系统..." -ForegroundColor Yellow
Write-Host ""

# 获取当前目录
$currentPath = Get-Location

# 1. 启动数据采集窗口
Write-Host "📊 启动窗口 1: 多币种数据采集..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentPath'; python start_multi.py"
Start-Sleep -Seconds 2

# 2. 启动 Web 界面窗口
Write-Host "🌐 启动窗口 2: Web 界面..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentPath'; Write-Host '等待数据采集启动...' -ForegroundColor Yellow; Start-Sleep -Seconds 10; python multi_web_ui.py"
Start-Sleep -Seconds 2

# 3. 启动多币种分析窗口
Write-Host "🤖 启动窗口 3: 多币种分析..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentPath'; Write-Host '等待初始数据采集...' -ForegroundColor Yellow; Start-Sleep -Seconds 30; Write-Host '开始分析...'; while (`$true) { python multi_analyzer.py; Write-Host ''; Write-Host '等待 5 分钟后重新分析...' -ForegroundColor Cyan; Start-Sleep -Seconds 300 }"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ 所有窗口已启动！" -ForegroundColor Green
Write-Host ""
Write-Host "📌 已打开的窗口：" -ForegroundColor Yellow
Write-Host "  1️⃣  数据采集窗口 - 实时采集 ETH, BTC, BNB, SOL 数据"
Write-Host "  2️⃣  Web 界面窗口 - http://localhost:5000"
Write-Host "  3️⃣  分析窗口 - 每 5 分钟自动分析一次"
Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Cyan
Write-Host "  • 在各窗口按 Ctrl+C 停止对应服务"
Write-Host "  • 访问 http://localhost:5000 查看实时数据"
Write-Host "  • 分析窗口会自动循环分析，无需手动重启"
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键退出启动器（不会关闭已启动的窗口）..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
