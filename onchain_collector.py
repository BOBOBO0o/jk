from web3 import Web3
import sqlite3
import time
import requests
from datetime import datetime

class OnchainCollector:
    def __init__(self):
        # 使用免费的公共RPC节点（可替换为Infura/Alchemy）
        rpc_urls = [
            'https://eth.llamarpc.com',
            'https://rpc.ankr.com/eth',
            'https://ethereum.publicnode.com'
        ]
        
        self.w3 = None
        for url in rpc_urls:
            try:
                w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 60}))
                if w3.is_connected():
                    self.w3 = w3
                    print(f"✅ Connected to Ethereum node: {url}")
                    break
            except Exception as e:
                print(f"Failed to connect to {url}: {e}")
        
        if not self.w3:
            raise Exception("❌ Could not connect to any Ethereum node")
        
        # Etherscan API (免费，需要注册获取key)
        self.etherscan_key = 'YourFreeEtherscanAPIKey'  # 替换为您的key
        
        self.db = sqlite3.connect('crypto_data.db', check_same_thread=False)
        self.init_database()
        
        # 主要交易所冷钱包地址
        self.exchanges = {
            'Binance 1': '0x28C6c06298d514Db089934071355E5743bf21d60',
            'Binance 2': '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549',
            'Binance 3': '0xDFd5293D8e347dFe59E90eFd55b2956a1343963d',
            'Binance 4': '0x56Eddb7aa87536c09CCc2793473599fD21A8b17F',
            'Binance 5': '0x9696f59E4d72E237BE84fFD425DCaD154Bf96976',
            'Binance 6': '0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67',
            'Binance 7': '0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8',
            'Binance 8': '0xF977814e90dA44bFA03b6295A0616a897441aceC',
            'Coinbase 1': '0x71660c4005BA85c37ccec55d0C4493E66Fe775d3',
            'Coinbase 2': '0x503828976D22510aad0201ac7EC88293211D23Da',
            'Coinbase 3': '0xddfAbCdc4D8FfC6d5beaf154f18B778f892A0740',
            'Kraken 1': '0x2910543Af39abA0Cd09dBb2D50200b3E800A63D2',
            'Kraken 2': '0x0A869d79a7052C7f1b55a8EbAbbEa3420F0D1E13',
            'Bitfinex 1': '0x876EabF441B2EE5B5b0554Fd502a8E0600950cFa',
        }
        
    def init_database(self):
        cursor = self.db.cursor()
        
        # 大额转账表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS large_transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                block_number INTEGER,
                tx_hash TEXT UNIQUE,
                from_addr TEXT,
                to_addr TEXT,
                value REAL,
                gas_price REAL,
                gas_used INTEGER
            )
        ''')
        
        # 交易所流入流出表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_flow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                exchange TEXT,
                flow_type TEXT,
                amount REAL,
                tx_hash TEXT
            )
        ''')
        
        # Gas价格表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gas_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                gas_price REAL,
                block_number INTEGER,
                transaction_count INTEGER
            )
        ''')
        
        # 区块信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                block_number INTEGER UNIQUE,
                transaction_count INTEGER,
                gas_used INTEGER,
                gas_limit INTEGER
            )
        ''')
        
        self.db.commit()
        print("✅ Onchain database initialized")
    
    def monitor_blocks(self):
        """监控新区块"""
        print("🔍 Starting block monitoring...")
        
        try:
            last_block = self.w3.eth.block_number - 1  # 从前一个区块开始
            print(f"Starting from block: {last_block}")
        except Exception as e:
            print(f"Error getting block number: {e}")
            return
        
        consecutive_errors = 0
        max_errors = 5
        
        while True:
            try:
                current_block = self.w3.eth.block_number
                
                if current_block > last_block:
                    for block_num in range(last_block + 1, current_block + 1):
                        try:
                            self.process_block(block_num)
                            last_block = block_num
                            consecutive_errors = 0  # 重置错误计数
                        except Exception as e:
                            print(f"Error processing block {block_num}: {e}")
                            consecutive_errors += 1
                            if consecutive_errors >= max_errors:
                                print(f"Too many consecutive errors, waiting 60 seconds...")
                                time.sleep(60)
                                consecutive_errors = 0
                            break
                
                time.sleep(12)  # 以太坊平均出块时间
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                consecutive_errors += 1
                if consecutive_errors >= max_errors:
                    print(f"Too many errors, waiting 60 seconds...")
                    time.sleep(60)
                    consecutive_errors = 0
                else:
                    time.sleep(5)
    
    def process_block(self, block_number):
        """处理单个区块"""
        try:
            block = self.w3.eth.get_block(block_number, full_transactions=True)
        except Exception as e:
            print(f"Error fetching block {block_number}: {e}")
            return
        
        cursor = self.db.cursor()
        
        # 保存区块信息
        cursor.execute('''
            INSERT OR IGNORE INTO blocks (timestamp, block_number, transaction_count, gas_used, gas_limit)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            block['timestamp'],
            block_number,
            len(block.transactions),
            block['gasUsed'],
            block['gasLimit']
        ))
        
        if not block.transactions:
            self.db.commit()
            return
        
        # 计算平均Gas价格
        total_gas_price = 0
        for tx in block.transactions:
            if 'gasPrice' in tx and tx['gasPrice']:
                total_gas_price += tx['gasPrice']
        
        avg_gas = total_gas_price / len(block.transactions) if block.transactions else 0
        
        cursor.execute('''
            INSERT INTO gas_prices (timestamp, gas_price, block_number, transaction_count)
            VALUES (?, ?, ?, ?)
        ''', (
            block['timestamp'],
            float(self.w3.from_wei(avg_gas, 'gwei')) if avg_gas > 0 else 0,
            block_number,
            len(block.transactions)
        ))
        
        print(f"[Block {block_number}] Txs: {len(block.transactions)}, Gas: {self.w3.from_wei(avg_gas, 'gwei'):.2f} Gwei")
        
        # 处理交易
        for tx in block.transactions:
            try:
                self.process_transaction(tx, block['timestamp'])
            except Exception as e:
                print(f"Error processing tx {tx['hash'].hex()}: {e}")
        
        self.db.commit()
    
    def process_transaction(self, tx, block_timestamp):
        """处理单笔交易"""
        cursor = self.db.cursor()
        
        if tx['value'] == 0:
            return
        
        value_eth = float(self.w3.from_wei(tx['value'], 'ether'))
        
        # 记录大额转账 (>50 ETH)
        if value_eth > 50:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx['hash'])
                gas_used = receipt['gasUsed']
            except:
                gas_used = 0
            
            cursor.execute('''
                INSERT OR IGNORE INTO large_transfers 
                (timestamp, block_number, tx_hash, from_addr, to_addr, value, gas_price, gas_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                block_timestamp,
                tx['blockNumber'],
                tx['hash'].hex(),
                tx['from'],
                tx['to'] if tx['to'] else 'Contract Creation',
                value_eth,
                float(self.w3.from_wei(tx['gasPrice'], 'gwei')) if 'gasPrice' in tx else 0,
                gas_used
            ))
            print(f"  💰 Large Transfer: {value_eth:.2f} ETH from {tx['from'][:10]}... to {tx['to'][:10] if tx['to'] else 'Contract'}...")
        
        # 检查交易所流入流出
        if tx['to']:
            from_addr = tx['from'].lower()
            to_addr = tx['to'].lower()
            
            for exchange_name, exchange_addr in self.exchanges.items():
                exchange_addr_lower = exchange_addr.lower()
                
                # 流入交易所
                if to_addr == exchange_addr_lower:
                    cursor.execute('''
                        INSERT INTO exchange_flow (timestamp, exchange, flow_type, amount, tx_hash)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (block_timestamp, exchange_name, 'inflow', value_eth, tx['hash'].hex()))
                    print(f"  📥 {exchange_name} Inflow: {value_eth:.2f} ETH")
                
                # 流出交易所
                elif from_addr == exchange_addr_lower:
                    cursor.execute('''
                        INSERT INTO exchange_flow (timestamp, exchange, flow_type, amount, tx_hash)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (block_timestamp, exchange_name, 'outflow', value_eth, tx['hash'].hex()))
                    print(f"  📤 {exchange_name} Outflow: {value_eth:.2f} ETH")
    
    def get_exchange_balances(self):
        """获取交易所余额（可选功能）"""
        print("\n💼 Exchange Balances:")
        for name, addr in self.exchanges.items():
            try:
                balance = self.w3.eth.get_balance(addr)
                balance_eth = self.w3.from_wei(balance, 'ether')
                print(f"  {name}: {balance_eth:,.2f} ETH")
            except Exception as e:
                print(f"  {name}: Error - {e}")
        print()

if __name__ == '__main__':
    collector = OnchainCollector()
    
    # 显示交易所余额
    collector.get_exchange_balances()
    
    # 开始监控区块
    collector.monitor_blocks()
