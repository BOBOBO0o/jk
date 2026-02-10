"""
技术指标计算模块
支持: EMA, MACD, RSI, ATR, BOLL
"""
import numpy as np
from typing import List, Tuple, Dict

class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """
        计算指数移动平均线 (EMA)
        """
        if len(prices) < period:
            return []
        
        ema = []
        multiplier = 2 / (period + 1)
        
        # 初始EMA使用SMA
        sma = sum(prices[:period]) / period
        ema.append(sma)
        
        # 后续使用EMA公式
        for price in prices[period:]:
            ema_value = (price - ema[-1]) * multiplier + ema[-1]
            ema.append(ema_value)
        
        return ema
    
    @staticmethod
    def calculate_macd(prices: List[float], 
                       fast_period: int = 12, 
                       slow_period: int = 26, 
                       signal_period: int = 9) -> Dict[str, float]:
        """
        计算MACD指标
        返回: {'macd': float, 'signal': float, 'histogram': float}
        """
        if len(prices) < slow_period + signal_period:
            return {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'neutral'}
        
        # 计算快线和慢线EMA
        ema_fast = TechnicalIndicators.calculate_ema(prices, fast_period)
        ema_slow = TechnicalIndicators.calculate_ema(prices, slow_period)
        
        # MACD线 = 快线 - 慢线
        macd_line = []
        for i in range(len(ema_slow)):
            fast_idx = i + (fast_period - slow_period)
            if fast_idx < len(ema_fast):
                macd_line.append(ema_fast[fast_idx] - ema_slow[i])
        
        if len(macd_line) < signal_period:
            return {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'neutral'}
        
        # 信号线 = MACD的EMA
        signal_line = TechnicalIndicators.calculate_ema(macd_line, signal_period)
        
        # 柱状图 = MACD - 信号线
        if len(signal_line) > 0:
            macd_value = macd_line[-1]
            signal_value = signal_line[-1]
            histogram = macd_value - signal_value
            
            # 判断趋势
            if histogram > 0 and macd_value > 0:
                trend = 'bullish'  # 多头
            elif histogram < 0 and macd_value < 0:
                trend = 'bearish'  # 空头
            else:
                trend = 'neutral'  # 中性
            
            return {
                'macd': round(macd_value, 4),
                'signal': round(signal_value, 4),
                'histogram': round(histogram, 4),
                'trend': trend
            }
        
        return {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'neutral'}
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        计算相对强弱指标 (RSI)
        """
        if len(prices) < period + 1:
            return 50.0  # 默认中性值
        
        # 计算价格变化
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        # 初始平均增益和损失
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # 使用指数移动平均
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    @staticmethod
    def calculate_atr(high_prices: List[float], 
                     low_prices: List[float], 
                     close_prices: List[float], 
                     period: int = 14) -> float:
        """
        计算平均真实波幅 (ATR)
        """
        if len(high_prices) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(close_prices)):
            high_low = high_prices[i] - low_prices[i]
            high_close = abs(high_prices[i] - close_prices[i-1])
            low_close = abs(low_prices[i] - close_prices[i-1])
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        if len(true_ranges) < period:
            return 0.0
        
        # 初始ATR使用简单平均
        atr = sum(true_ranges[:period]) / period
        
        # 后续使用指数移动平均
        for i in range(period, len(true_ranges)):
            atr = (atr * (period - 1) + true_ranges[i]) / period
        
        return round(atr, 4)
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], 
                                  period: int = 20, 
                                  std_dev: float = 2.0) -> Dict[str, float]:
        """
        计算布林带 (Bollinger Bands)
        返回: {'upper': float, 'middle': float, 'lower': float, 'position': str}
        """
        if len(prices) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'width': 0, 'position': 'neutral'}
        
        # 中轨 = SMA
        middle = sum(prices[-period:]) / period
        
        # 标准差
        variance = sum([(p - middle) ** 2 for p in prices[-period:]]) / period
        std = variance ** 0.5
        
        # 上轨和下轨
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        # 带宽
        width = ((upper - lower) / middle) * 100 if middle > 0 else 0
        
        # 当前价格相对位置
        current_price = prices[-1]
        if current_price > upper:
            position = 'above_upper'  # 超买区
        elif current_price < lower:
            position = 'below_lower'  # 超卖区
        elif current_price > middle:
            position = 'above_middle'  # 中上区
        else:
            position = 'below_middle'  # 中下区
        
        return {
            'upper': round(upper, 2),
            'middle': round(middle, 2),
            'lower': round(lower, 2),
            'width': round(width, 2),
            'position': position,
            'current_price': round(current_price, 2)
        }
    
    @staticmethod
    def calculate_all_indicators(klines_data: List[Tuple]) -> Dict:
        """
        计算所有技术指标
        klines_data: [(open_time, open, high, low, close, volume), ...]
        """
        if len(klines_data) < 26:  # 至少需要26根K线（MACD慢线周期）
            return {
                'ema_12': 0,
                'ema_26': 0,
                'macd': {},
                'rsi': 50,
                'atr': 0,
                'bollinger': {},
                'available': False
            }
        
        # 提取价格数据
        close_prices = [float(k[4]) for k in klines_data]
        high_prices = [float(k[2]) for k in klines_data]
        low_prices = [float(k[3]) for k in klines_data]
        
        # 计算各项指标
        ema_12 = TechnicalIndicators.calculate_ema(close_prices, 12)
        ema_26 = TechnicalIndicators.calculate_ema(close_prices, 26)
        macd = TechnicalIndicators.calculate_macd(close_prices)
        rsi = TechnicalIndicators.calculate_rsi(close_prices)
        atr = TechnicalIndicators.calculate_atr(high_prices, low_prices, close_prices)
        bollinger = TechnicalIndicators.calculate_bollinger_bands(close_prices)
        
        return {
            'ema_12': round(ema_12[-1], 2) if ema_12 else 0,
            'ema_26': round(ema_26[-1], 2) if ema_26 else 0,
            'macd': macd,
            'rsi': rsi,
            'atr': atr,
            'bollinger': bollinger,
            'available': True
        }

if __name__ == '__main__':
    # 测试代码
    test_prices = [100 + i + (i % 5) * 2 for i in range(50)]
    
    print("测试技术指标计算:")
    print(f"价格数据: {test_prices[-10:]}")
    
    ema = TechnicalIndicators.calculate_ema(test_prices, 12)
    print(f"\nEMA(12): {ema[-1]:.2f}")
    
    macd = TechnicalIndicators.calculate_macd(test_prices)
    print(f"\nMACD: {macd}")
    
    rsi = TechnicalIndicators.calculate_rsi(test_prices)
    print(f"\nRSI(14): {rsi:.2f}")
    
    # 模拟高低价
    high_prices = [p + 2 for p in test_prices]
    low_prices = [p - 2 for p in test_prices]
    atr = TechnicalIndicators.calculate_atr(high_prices, low_prices, test_prices)
    print(f"\nATR(14): {atr:.4f}")
    
    boll = TechnicalIndicators.calculate_bollinger_bands(test_prices)
    print(f"\nBollinger Bands: {boll}")
