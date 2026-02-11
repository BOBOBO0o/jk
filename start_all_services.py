"""
统一启动脚本 - 在单个容器中运行所有采集器和API服务器
适用于Zeabur等容器化部署平台
"""
import subprocess
import sys
import time
import signal

processes = []

def start_service(name, command):
    """启动一个服务"""
    print(f"[启动] {name}...")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes.append((name, process))
    return process

def signal_handler(signum, frame):
    """处理终止信号"""
    print("\n[停止] 收到终止信号，正在关闭所有服务...")
    for name, process in processes:
        print(f"[停止] {name}")
        process.terminate()
    sys.exit(0)

def main():
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("  加密货币数据采集系统 - 统一启动")
    print("=" * 60)
    print()
    
    # 启动现货数据采集器
    print("[现货数据采集]")
    start_service("ETH 现货", "python start_test.py")
    time.sleep(2)
    start_service("BTC 现货", "python start_btc.py")
    time.sleep(2)
    start_service("BNB 现货", "python start_bnb.py")
    time.sleep(2)
    start_service("SOL 现货", "python start_sol.py")
    time.sleep(2)
    
    # 启动合约数据采集器
    print("\n[合约数据采集]")
    start_service("ETH 合约", "python start_eth_futures.py")
    time.sleep(2)
    start_service("BTC 合约", "python start_btc_futures.py")
    time.sleep(2)
    start_service("BNB 合约", "python start_bnb_futures.py")
    time.sleep(2)
    start_service("SOL 合约", "python start_sol_futures.py")
    time.sleep(5)
    
    # 启动API服务器
    print("\n[API服务器]")
    api_process = start_service(
        "API服务器",
        "gunicorn -w 2 -b 0.0.0.0:5001 --timeout 120 cloud_api_server:app"
    )
    
    print("\n" + "=" * 60)
    print("✅ 所有服务已启动！")
    print("=" * 60)
    print("\n📊 运行中的服务：")
    for name, _ in processes:
        print(f"  • {name}")
    
    print("\n🌐 API地址: http://0.0.0.0:5001")
    print("📝 按 Ctrl+C 停止所有服务\n")
    
    # 监控所有进程
    try:
        while True:
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} 已退出，退出码: {process.returncode}")
            time.sleep(10)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == '__main__':
    main()
