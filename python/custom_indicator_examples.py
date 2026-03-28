"""
Python自定义指标示例库
提供更多实用的自定义指标示例
"""

import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import math

# 导入基础模块
try:
    from custom_indicator import (
        PythonIndicator, IndicatorConfig, SignalType, 
        CustomIndicatorFactory, factory
    )
except ImportError:
    # 如果直接运行，使用相对导入
    from .custom_indicator import (
        PythonIndicator, IndicatorConfig, SignalType,
        CustomIndicatorFactory, factory
    )

logger = logging.getLogger(__name__)


class EnhancedMovingAverage(PythonIndicator):
    """增强型移动平均线指标"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        
        # 设置默认参数
        default_params = {
            'period': 20,
            'ma_type': 'sma',  # sma, ema, wma
            'weight_factor': 0.2  # 用于WMA的权重因子
        }
        
        for key, value in default_params.items():
            if key not in self.config.parameters:
                self.config.parameters[key] = value
        
        self.config.required_parameters = ['period', 'ma_type']
        self.config.default_values = default_params
        
        # 内部状态
        self._price_buffer = []
        self._prev_ema = None
        
    def _calculate(self, price_data: Dict[str, Any]) -> float:
        """计算移动平均"""
        close_price = price_data.get('close', 0)
        period = self.config.parameters.get('period', 20)
        ma_type = self.config.parameters.get('ma_type', 'sma')
        
        # 添加到缓冲区
        self._price_buffer.append(close_price)
        
        # 保持缓冲区大小
        if len(self._price_buffer) > period:
            self._price_buffer.pop(0)
        
        # 数据不足时返回当前价格
        if len(self._price_buffer) < period:
            return close_price
        
        # 根据类型计算移动平均
        if ma_type == 'sma':
            return self._calculate_sma()
        elif ma_type == 'ema':
            return self._calculate_ema(close_price, period)
        elif ma_type == 'wma':
            return self._calculate_wma(period)
        else:
            logger.warning(f"未知的移动平均类型: {ma_type}, 使用SMA")
            return self._calculate_sma()
    
    def _calculate_sma(self) -> float:
        """计算简单移动平均"""
        return sum(self._price_buffer) / len(self._price_buffer)
    
    def _calculate_ema(self, current_price: float, period: float) -> float:
        """计算指数移动平均"""
        alpha = 2.0 / (period + 1)
        
        if self._prev_ema is None:
            # 第一次计算使用SMA
            self._prev_ema = sum(self._price_buffer) / len(self._price_buffer)
            return self._prev_ema
        
        # EMA公式: EMA = α * current_price + (1 - α) * prev_ema
        ema = alpha * current_price + (1 - alpha) * self._prev_ema
        self._prev_ema = ema
        return ema
    
    def _calculate_wma(self, period: int) -> float:
        """计算加权移动平均"""
        weights = list(range(1, period + 1))
        total_weight = sum(weights)
        
        weighted_sum = 0
        for i, price in enumerate(self._price_buffer):
            weighted_sum += price * weights[i]
        
        return weighted_sum / total_weight
    
    def _generate_signal(self, price_data: Dict[str, Any], value: float) -> SignalType:
        """生成交易信号"""
        close_price = price_data.get('close', 0)
        
        if len(self.values) < 2:
            return SignalType.HOLD
        
        # 价格与均线关系
        prev_value = self.values[-2]
        price_above_ma = close_price > value
        prev_price_above_ma = close_price > prev_value  # 简化处理
        
        # 均线斜率
        ma_slope = value - prev_value
        
        # 综合信号生成
        if price_above_ma and ma_slope > 0:
            return SignalType.STRONG_BUY
        elif not price_above_ma and ma_slope < 0:
            return SignalType.STRONG_SELL
        elif price_above_ma:
            return SignalType.BUY
        elif not price_above_ma:
            return SignalType.SELL
        
        return SignalType.HOLD


class BollingerBands(PythonIndicator):
    """布林带指标"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        
        # 设置默认参数
        default_params = {
            'period': 20,
            'std_dev': 2.0,
            'ma_type': 'sma'
        }
        
        for key, value in default_params.items():
            if key not in self.config.parameters:
                self.config.parameters[key] = value
        
        self.config.required_parameters = ['period', 'std_dev']
        self.config.default_values = default_params
        
        # 内部状态
        self._price_buffer = []
        self._upper_band = []
        self._lower_band = []
        self._middle_band = []
        
    def _calculate(self, price_data: Dict[str, Any]) -> float:
        """计算布林带"""
        close_price = price_data.get('close', 0)
        period = self.config.parameters.get('period', 20)
        std_dev = self.config.parameters.get('std_dev', 2.0)
        ma_type = self.config.parameters.get('ma_type', 'sma')
        
        # 添加到缓冲区
        self._price_buffer.append(close_price)
        
        # 保持缓冲区大小
        if len(self._price_buffer) > period:
            self._price_buffer.pop(0)
        
        # 数据不足时返回当前价格
        if len(self._price_buffer) < period:
            self._upper_band.append(close_price)
            self._lower_band.append(close_price)
            self._middle_band.append(close_price)
            return close_price
        
        # 计算移动平均（中轨）
        if ma_type == 'sma':
            middle = sum(self._price_buffer) / len(self._price_buffer)
        elif ma_type == 'ema':
            # 简化EMA计算
            alpha = 2.0 / (period + 1)
            if len(self._middle_band) == 0:
                middle = sum(self._price_buffer) / len(self._price_buffer)
            else:
                prev_middle = self._middle_band[-1]
                middle = alpha * close_price + (1 - alpha) * prev_middle
        else:
            middle = sum(self._price_buffer) / len(self._price_buffer)
        
        # 计算标准差
        prices_array = np.array(self._price_buffer)
        std = np.std(prices_array)
        
        # 计算上下轨
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        # 保存 bands
        self._upper_band.append(upper)
        self._lower_band.append(lower)
        self._middle_band.append(middle)
        
        # 返回当前价格相对于布林带的位置（百分比）
        band_width = upper - lower
        if band_width > 0:
            position = (close_price - lower) / band_width
            return position * 100  # 返回0-100的百分比
        else:
            return 50.0  # 中性位置
    
    def _generate_signal(self, price_data: Dict[str, Any], value: float) -> SignalType:
        """生成交易信号"""
        close_price = price_data.get('close', 0)
        
        if len(self._upper_band) < 2 or len(self._lower_band) < 2:
            return SignalType.HOLD
        
        # 获取布林带值
        upper = self._upper_band[-1]
        lower = self._lower_band[-1]
        middle = self._middle_band[-1]
        
        # 布林带策略
        if close_price > upper:
            return SignalType.SELL  # 超买，卖出信号
        elif close_price < lower:
            return SignalType.BUY   # 超卖，买入信号
        elif close_price > middle and value > 60:
            return SignalType.BUY   # 价格在中轨上方且位置较高
        elif close_price < middle and value < 40:
            return SignalType.SELL  # 价格在中轨下方且位置较低
        
        return SignalType.HOLD
    
    def get_bands(self) -> Tuple[List[float], List[float], List[float]]:
        """获取布林带数据"""
        return self._upper_band, self._middle_band, self._lower_band


class MACDIndicator(PythonIndicator):
    """MACD指标"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        
        # 设置默认参数
        default_params = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
        
        for key, value in default_params.items():
            if key not in self.config.parameters:
                self.config.parameters[key] = value
        
        self.config.required_parameters = ['fast_period', 'slow_period', 'signal_period']
        self.config.default_values = default_params
        
        # 内部状态
        self._fast_ema = None
        self._slow_ema = None
        self._signal_ema = None
        self._macd_line = []
        self._signal_line = []
        self._histogram = []
        
    def _calculate(self, price_data: Dict[str, Any]) -> float:
        """计算MACD"""
        close_price = price_data.get('close', 0)
        fast_period = self.config.parameters.get('fast_period', 12)
        slow_period = self.config.parameters.get('slow_period', 26)
        signal_period = self.config.parameters.get('signal_period', 9)
        
        # 计算快速EMA
        fast_alpha = 2.0 / (fast_period + 1)
        if self._fast_ema is None:
            self._fast_ema = close_price
        else:
            self._fast_ema = fast_alpha * close_price + (1 - fast_alpha) * self._fast_ema
        
        # 计算慢速EMA
        slow_alpha = 2.0 / (slow_period + 1)
        if self._slow_ema is None:
            self._slow_ema = close_price
        else:
            self._slow_ema = slow_alpha * close_price + (1 - slow_alpha) * self._slow_ema
        
        # 计算MACD线
        macd = self._fast_ema - self._slow_ema
        self._macd_line.append(macd)
        
        # 计算信号线
        signal_alpha = 2.0 / (signal_period + 1)
        if self._signal_ema is None:
            self._signal_ema = macd
        else:
            self._signal_ema = signal_alpha * macd + (1 - signal_alpha) * self._signal_ema
        
        self._signal_line.append(self._signal_ema)
        
        # 计算柱状图
        histogram = macd - self._signal_ema
        self._histogram.append(histogram)
        
        # 返回MACD值
        return macd
    
    def _generate_signal(self, price_data: Dict[str, Any], value: float) -> SignalType:
        """生成交易信号"""
        if len(self._macd_line) < 2 or len(self._signal_line) < 2:
            return SignalType.HOLD
        
        # 获取当前和之前的MACD、信号线值
        macd = self._macd_line[-1]
        prev_macd = self._macd_line[-2] if len(self._macd_line) > 1 else macd
        signal = self._signal_line[-1]
        prev_signal = self._signal_line[-2] if len(self._signal_line) > 1 else signal
        
        # MACD交叉策略
        if macd > signal and prev_macd <= prev_signal:
            return SignalType.BUY  # MACD上穿信号线，买入
        elif macd < signal and prev_macd >= prev_signal:
            return SignalType.SELL  # MACD下穿信号线，卖出
        
        # 零轴策略
        if macd > 0 and prev_macd <= 0:
            return SignalType.BUY  # MACD上穿零轴，买入
        elif macd < 0 and prev_macd >= 0:
            return SignalType.SELL  # MACD下穿零轴，卖出
        
        # 柱状图策略
        histogram = self._histogram[-1] if self._histogram else 0
        prev_histogram = self._histogram[-2] if len(self._histogram) > 1 else histogram
        
        if histogram > 0 and prev_histogram <= 0:
            return SignalType.BUY  # 柱状图转正，买入
        elif histogram < 0 and prev_histogram >= 0:
            return SignalType.SELL  # 柱状图转负，卖出
        
        return SignalType.HOLD
    
    def get_macd_data(self) -> Tuple[List[float], List[float], List[float]]:
        """获取MACD数据"""
        return self._macd_line, self._signal_line, self._histogram


class VolumeWeightedAveragePrice(PythonIndicator):
    """成交量加权平均价格指标"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        
        # 设置默认参数
        default_params = {
            'period': 20
        }
        
        for key, value in default_params.items():
            if key not in self.config.parameters:
                self.config.parameters[key] = value
        
        self.config.required_parameters = ['period']
        self.config.default_values = default_params
        
        # 内部状态
        self._price_volume_buffer = []  # (price, volume) 元组列表
        self._cumulative_vwap = []
        
    def _calculate(self, price_data: Dict[str, Any]) -> float:
        """计算VWAP"""
        close_price = price_data.get('close', 0)
        volume = price_data.get('volume', 0)
        period = self.config.parameters.get('period', 20)
        
        # 典型价格（高+低+收）/3
        high = price_data.get('high', close_price)
        low = price_data.get('low', close_price)
        typical_price = (high + low + close_price) / 3
        
        # 添加到缓冲区
        self._price_volume_buffer.append((typical_price, volume))
        
        # 保持缓冲区大小
        if len(self._price_volume_buffer) > period:
            self._price_volume_buffer.pop(0)
        
        # 计算VWAP
        if not self._price_volume_buffer:
            vwap = close_price
        else:
            total_price_volume = sum(price * vol for price, vol in self._price_volume_buffer)
            total_volume = sum(vol for _, vol in self._price_volume_buffer)
            
            if total_volume > 0:
                vwap = total_price_volume / total_volume
            else:
                vwap = close_price
        
        self._cumulative_vwap.append(vwap)
        return vwap
    
    def _generate_signal(self, price_data: Dict[str, Any], value: float) -> SignalType:
        """生成交易信号"""
        close_price = price_data.get('close', 0)
        
        if len(self._cumulative_vwap) < 2:
            return SignalType.HOLD
        
        # VWAP策略
        prev_vwap = self._cumulative_vwap[-2]
        vwap_trend = value - prev_vwap
        
        if close_price > value and vwap_trend > 0:
            return SignalType.BUY  # 价格在VWAP上方且VWAP上升
        elif close_price < value and vwap_trend < 0:
            return SignalType.SELL  # 价格在VWAP下方且VWAP下降
        elif close_price > value:
            return SignalType.BUY  # 价格在VWAP上方
        elif close_price < value:
            return SignalType.SELL  # 价格在VWAP下方
        
        return SignalType.HOLD


class CustomCompositeIndicator(PythonIndicator):
    """自定义复合指标示例"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        
        # 设置默认参数
        default_params = {
            'rsi_period': 14,
            'bb_period': 20,
            'bb_std': 2.0,
            'weight_rsi': 0.4,
            'weight_bb': 0.4,
            'weight_price': 0.2
        }
        
        for key, value in default_params.items():
            if key not in self.config.parameters:
                self.config.parameters[key] = value
        
        self.config.required_parameters = ['rsi_period', 'bb_period', 'bb_std']
        self.config.default_values = default_params
        
        # 内部状态
        self._price_buffer = []
        self._gain_buffer = []
        self._loss_buffer = []
        self._bb_buffer = []
        
    def _calculate(self, price_data: Dict[str, Any]) -> float:
        """计算复合指标"""
        close_price = price_data.get('close', 0)
        rsi_period = self.config.parameters.get('rsi_period', 14)
        bb_period = self.config.parameters.get('bb_period', 20)
        bb_std = self.config.parameters.get('bb_std', 2.0)
        
        # 1. 计算RSI分量
        rsi_value = self._calculate_rsi_component(close_price, rsi_period)
        
        # 2. 计算布林带分量
        bb_value = self._calculate_bb_component(close_price, bb_period, bb_std)
        
        # 3. 价格动量分量
        price_momentum = self._calculate_price_momentum(close_price)
        
        # 4. 加权合成
        weight_rsi = self.config.parameters.get('weight_rsi', 0.4)
        weight_bb = self.config.parameters.get('weight_bb', 0.4)
        weight_price = self.config.parameters.get('weight_price', 0.2)
        
        composite = (
            rsi_value * weight_rsi +
            bb_value * weight_bb +
            price_momentum * weight_price
        )
        
        return composite
    
    def _calculate_rsi_component(self, close_price: float, period: int) -> float:
        """计算RSI分量"""
        if not self._price_buffer:
            self._price_buffer.append(close_price)
            return 50.0  # 中性值
        
        # 计算价格变化
        prev_price = self._price_buffer[-1]
        change = close_price - prev_price
        self._price_buffer.append(close_price)
        
        # 保持缓冲区大小
        if len(self._price_buffer) > period * 2:
            self._price_buffer.pop(0)
        
        # 记录收益和损失
        gain = max(change, 0)
        loss = abs(min(change, 0))
        
        self._gain_buffer.append(gain)
        self._loss_buffer.append(loss)
        
        # 保持缓冲区大小
        if len(self._gain_buffer) > period:
            self._gain_buffer.pop(0)
            self._loss_buffer.pop(0)
        
        # 计算RSI
        if len(self._gain_buffer) < period:
            return 50.0
        
        avg_gain = sum(self._gain_buffer) / period
        avg_loss = sum(self._loss_buffer) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 归一化到0-1范围
        return rsi / 100.0
    
    def _calculate_bb_component(self, close_price: float, period: int, std_dev: float) -> float:
        """计算布林带分量"""
        self._bb_buffer.append(close_price)
        
        # 保持缓冲区大小
        if len(self._bb_buffer) > period:
            self._bb_buffer.pop(0)
        
        if len(self._bb_buffer) < period:
            return 0.5  # 中性值
        
        # 计算均值和标准差
        prices_array = np.array(self._bb_buffer)
        mean = np.mean(prices_array)
        std = np.std(prices_array)
        
        # 计算布林带位置
        upper = mean + (std * std_dev)
        lower = mean - (std * std_dev)
        
        if upper - lower > 0:
            position = (close_price - lower) / (upper - lower)
            return position  # 0-1范围
        else:
            return 0.5
    
    def _calculate_price_momentum(self, close_price: float) -> float:
        """计算价格动量分量"""
        if len(self._price_buffer) < 5:
            return 0.5
        
        # 计算短期动量
        short_period = min(5, len(self._price_buffer))
        recent_prices = self._price_buffer[-short_period:]
        
        if len(recent_prices) < 2:
            return 0.5
        
        # 价格变化率
        price_change = (close_price - recent_prices[0]) / recent_prices[0]
        
        # 归一化到0-1范围（假设变化率在-10%到+10%之间）
        normalized = (price_change + 0.1) / 0.2
        return max(0.0, min(1.0, normalized))
    
    def _generate_signal(self, price_data: Dict[str, Any], value: float) -> SignalType:
        """生成交易信号"""
        # 复合指标策略
        if value > 0.7:
            return SignalType.STRONG_SELL
        elif value > 0.6:
            return SignalType.SELL
        elif value < 0.3:
            return SignalType.STRONG_BUY
        elif value < 0.4:
            return SignalType.BUY
        
        return SignalType.HOLD


# 注册所有示例指标到全局工厂
factory.register(EnhancedMovingAverage)
factory.register(BollingerBands)
factory.register(MACDIndicator)
factory.register(VolumeWeightedAveragePrice)
factory.register(CustomCompositeIndicator)


def create_demo_indicators() -> Dict[str, str]:
    """创建所有示例指标并返回实例ID映射"""
    instances = {}
    
    # 创建增强移动平均
    ema_config = {
        'period': 20,
        'ma_type': 'ema'
    }
    ema_id = factory.create("EnhancedMovingAverage", ema_config)
    instances['EnhancedMovingAverage'] = ema_id
    
    # 创建布林带
    bb_config = {
        'period': 20,
        'std_dev': 2.0
    }
    bb_id = factory.create("BollingerBands", bb_config)
    instances['BollingerBands'] = bb_id
    
    # 创建MACD
    macd_config = {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9
    }
    macd_id = factory.create("MACDIndicator", macd_config)
    instances['MACDIndicator'] = macd_id
    
    # 创建VWAP
    vwap_config = {
        'period': 20
    }
    vwap_id = factory.create("VolumeWeightedAveragePrice", vwap_config)
    instances['VolumeWeightedAveragePrice'] = vwap_id
    
    # 创建复合指标
    composite_config = {
        'rsi_period': 14,
        'bb_period': 20,
        'bb_std': 2.0,
        'weight_rsi': 0.4,
        'weight_bb': 0.4,
        'weight_price': 0.2
    }
    composite_id = factory.create("CustomCompositeIndicator", composite_config)
    instances['CustomCompositeIndicator'] = composite_id
    
    return instances


def run_demo():
    """运行示例演示"""
    print("=== Python自定义指标示例库演示 ===\n")
    
    # 创建示例指标
    print("1. 创建示例指标...")
    instances = create_demo_indicators()
    
    for name, instance_id in instances.items():
        print(f"   创建 {name}: {instance_id}")
    
    print("\n2. 模拟价格数据更新...")
    
    # 模拟价格数据
    prices = [100 + i * 2 + np.random.normal(0, 1) for i in range(50)]
    volumes = [1000 + np.random.randint(-200, 200) for _ in range(50)]
    
    results = {}
    
    for i, (price, volume) in enumerate(zip(prices, volumes)):
        price_data = {
            'open': price - 0.5,
            'high': price + 1.0,
            'low': price - 1.0,
            'close': price,
            'volume': volume,
            'timestamp': i
        }
        
        # 更新所有指标
        for name, instance_id in instances.items():
            indicator = factory.get_instance(instance_id)
            value = indicator.update(price_data)
            signal = indicator.get_last_signal()
            
            if name not in results:
                results[name] = []
            
            results[name].append({
                'time': i,
                'value': value,
                'signal': signal.value if signal else 'hold'
            })
        
        # 每10个时间点打印一次
        if i % 10 == 0:
            print(f"\n   时间 {i}:")
            for name in ['EnhancedMovingAverage', 'BollingerBands', 'MACDIndicator']:
                if name in results and results[name]:
                    latest = results[name][-1]
                    print(f"     {name}: {latest['value']:.2f} ({latest['signal']})")
    
    print("\n3. 指标性能统计...")
    for name, instance_id in instances.items():
        indicator = factory.get_instance(instance_id)
        values = indicator.get_values()
        signals = indicator.get_signals()
        
        if values:
            print(f"\n   {name}:")
            print(f"     最后值: {values[-1]:.4f}")
            print(f"     值数量: {len(values)}")
            print(f"     信号数量: {len(signals)}")
            
            # 信号统计
            signal_counts = {}
            for signal in signals:
                signal_str = signal.value
                signal_counts[signal_str] = signal_counts.get(signal_str, 0) + 1
            
            print(f"     信号分布: {signal_counts}")
    
    print("\n4. 清理实例...")
    for instance_id in instances.values():
        factory.remove_instance(instance_id)
    
    print("   清理完成!")
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    run_demo()