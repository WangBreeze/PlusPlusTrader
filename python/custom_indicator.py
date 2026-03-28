"""
Python自定义指标支持模块
允许用户在Python中定义和使用自定义技术指标
"""

import json
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalType(Enum):
    """信号类型枚举"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


@dataclass
class IndicatorConfig:
    """指标配置类"""
    name: str
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_parameters: List[str] = field(default_factory=list)
    default_values: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        if not self.name:
            logger.error("Indicator name is required")
            return False
            
        # 检查必要参数
        for param in self.required_parameters:
            if param not in self.parameters:
                logger.error(f"Required parameter '{param}' is missing")
                return False
                
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "parameters": self.parameters,
            "required_parameters": self.required_parameters,
            "default_values": self.default_values
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndicatorConfig':
        """从字典创建配置"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            parameters=data.get("parameters", {}),
            required_parameters=data.get("required_parameters", []),
            default_values=data.get("default_values", {})
        )


class PythonIndicator:
    """Python自定义指标基类"""
    
    def __init__(self, config: IndicatorConfig):
        """
        初始化自定义指标
        
        Args:
            config: 指标配置
        """
        self.config = config
        self.name = config.name
        self.values = []  # 指标值序列
        self.signals = []  # 信号序列
        self.timestamps = []  # 时间戳序列
        self.is_initialized = False
        
        # 验证配置
        if not config.validate():
            raise ValueError(f"Invalid configuration for indicator '{self.name}'")
        
        # 设置参数
        self._setup_parameters()
        
    def _setup_parameters(self):
        """设置参数"""
        # 合并默认值和用户参数
        for key, default_value in self.config.default_values.items():
            if key not in self.config.parameters:
                self.config.parameters[key] = default_value
    
    def initialize(self):
        """初始化指标"""
        self.values = []
        self.signals = []
        self.timestamps = []
        self.is_initialized = True
        logger.info(f"Indicator '{self.name}' initialized")
    
    def update(self, price_data: Dict[str, Any]) -> float:
        """
        更新指标值
        
        Args:
            price_data: 价格数据，包含open, high, low, close, volume等
            
        Returns:
            计算出的指标值
        """
        if not self.is_initialized:
            self.initialize()
        
        # 提取时间戳
        timestamp = price_data.get('timestamp', len(self.timestamps))
        self.timestamps.append(timestamp)
        
        # 子类需要实现具体的计算逻辑
        value = self._calculate(price_data)
        self.values.append(value)
        
        # 生成信号
        signal = self._generate_signal(price_data, value)
        self.signals.append(signal)
        
        return value
    
    def _calculate(self, price_data: Dict[str, Any]) -> float:
        """
        计算指标值（子类必须实现）
        
        Args:
            price_data: 价格数据
            
        Returns:
            指标值
        """
        raise NotImplementedError("Subclasses must implement _calculate method")
    
    def _generate_signal(self, price_data: Dict[str, Any], value: float) -> SignalType:
        """
        生成交易信号（子类可以重写）
        
        Args:
            price_data: 价格数据
            value: 当前指标值
            
        Returns:
            交易信号
        """
        # 默认返回持有信号
        return SignalType.HOLD
    
    def get_last_value(self) -> Optional[float]:
        """获取最新的指标值"""
        if not self.values:
            return None
        return self.values[-1]
    
    def get_last_signal(self) -> Optional[SignalType]:
        """获取最新的信号"""
        if not self.signals:
            return None
        return self.signals[-1]
    
    def get_values(self, n: Optional[int] = None) -> List[float]:
        """获取指标值序列"""
        if n is None:
            return self.values.copy()
        return self.values[-n:] if self.values else []
    
    def get_signals(self, n: Optional[int] = None) -> List[SignalType]:
        """获取信号序列"""
        if n is None:
            return self.signals.copy()
        return self.signals[-n:] if self.signals else []
    
    def reset(self):
        """重置指标状态"""
        self.values = []
        self.signals = []
        self.timestamps = []
        self.is_initialized = False
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        data = {
            "indicator": self.config.to_dict(),
            "current_value": self.get_last_value(),
            "current_signal": self.get_last_signal().value if self.get_last_signal() else None,
            "value_count": len(self.values),
            "signal_count": len(self.signals)
        }
        return json.dumps(data, indent=2)
    
    def __str__(self) -> str:
        return f"PythonIndicator(name='{self.name}', values={len(self.values)}, signals={len(self.signals)})"


class CustomIndicatorFactory:
    """自定义指标工厂"""
    
    def __init__(self):
        self._indicators = {}  # 名称 -> 指标类映射
        self._instances = {}  # 实例ID -> 指标实例映射
        self._next_id = 1
    
    def register(self, indicator_class):
        """
        注册自定义指标类
        
        Args:
            indicator_class: 指标类（必须是PythonIndicator的子类）
        """
        if not issubclass(indicator_class, PythonIndicator):
            raise TypeError(f"Indicator class must be a subclass of PythonIndicator")
        
        indicator_name = indicator_class.__name__
        self._indicators[indicator_name] = indicator_class
        logger.info(f"Registered indicator: {indicator_name}")
    
    def create(self, indicator_name: str, config: Optional[Dict[str, Any]] = None) -> str:
        """
        创建指标实例
        
        Args:
            indicator_name: 指标名称
            config: 配置参数
            
        Returns:
            实例ID
        """
        if indicator_name not in self._indicators:
            raise ValueError(f"Indicator '{indicator_name}' not registered")
        
        # 创建配置
        if config is None:
            config = {}
        
        indicator_config = IndicatorConfig(
            name=indicator_name,
            parameters=config
        )
        
        # 创建实例
        indicator_class = self._indicators[indicator_name]
        instance = indicator_class(indicator_config)
        
        # 分配ID
        instance_id = f"{indicator_name}_{self._next_id}"
        self._next_id += 1
        self._instances[instance_id] = instance
        
        logger.info(f"Created indicator instance: {instance_id}")
        return instance_id
    
    def get_instance(self, instance_id: str) -> PythonIndicator:
        """获取指标实例"""
        if instance_id not in self._instances:
            raise ValueError(f"Indicator instance '{instance_id}' not found")
        return self._instances[instance_id]
    
    def remove_instance(self, instance_id: str):
        """移除指标实例"""
        if instance_id in self._instances:
            del self._instances[instance_id]
            logger.info(f"Removed indicator instance: {instance_id}")
    
    def list_indicators(self) -> List[str]:
        """列出所有注册的指标"""
        return list(self._indicators.keys())
    
    def list_instances(self) -> List[str]:
        """列出所有实例"""
        return list(self._instances.keys())
    
    def clear_instances(self):
        """清除所有实例"""
        self._instances.clear()
        self._next_id = 1
        logger.info("Cleared all indicator instances")


# 示例：简单的移动平均线指标
class SimpleMovingAverage(PythonIndicator):
    """简单移动平均线指标"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        # 设置默认参数
        if 'period' not in self.config.parameters:
            self.config.parameters['period'] = 20
        self.config.required_parameters = ['period']
        self.config.default_values = {'period': 20}
        
        # 内部状态
        self._price_buffer = []
    
    def _calculate(self, price_data: Dict[str, Any]) -> float:
        """计算简单移动平均"""
        close_price = price_data.get('close', 0)
        period = self.config.parameters.get('period', 20)
        
        # 添加到缓冲区
        self._price_buffer.append(close_price)
        
        # 保持缓冲区大小
        if len(self._price_buffer) > period:
            self._price_buffer.pop(0)
        
        # 计算平均值
        if len(self._price_buffer) < period:
            return close_price  # 数据不足时返回当前价格
        
        return sum(self._price_buffer) / len(self._price_buffer)
    
    def _generate_signal(self, price_data: Dict[str, Any], value: float) -> SignalType:
        """生成交易信号"""
        close_price = price_data.get('close', 0)
        
        if len(self.values) < 2:
            return SignalType.HOLD
        
        # 简单的价格与均线交叉策略
        prev_value = self.values[-2]
        prev_price = close_price  # 简化处理
        
        if close_price > value and prev_price <= prev_value:
            return SignalType.BUY
        elif close_price < value and prev_price >= prev_value:
            return SignalType.SELL
        
        return SignalType.HOLD


# 示例：相对强弱指数指标
class RelativeStrengthIndex(PythonIndicator):
    """相对强弱指数指标"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        # 设置默认参数
        if 'period' not in self.config.parameters:
            self.config.parameters['period'] = 14
        self.config.required_parameters = ['period']
        self.config.default_values = {'period': 14}
        
        # 内部状态
        self._prev_close = None
        self._gains = []
        self._losses = []
    
    def _calculate(self, price_data: Dict[str, Any]) -> float:
        """计算RSI"""
        close_price = price_data.get('close', 0)
        period = self.config.parameters.get('period', 14)
        
        if self._prev_close is None:
            self._prev_close = close_price
            return 50.0  # 初始值
        
        # 计算价格变化
        change = close_price - self._prev_close
        self._prev_close = close_price
        
        # 记录收益和损失
        gain = max(change, 0)
        loss = abs(min(change, 0))
        
        self._gains.append(gain)
        self._losses.append(loss)
        
        # 保持缓冲区大小
        if len(self._gains) > period:
            self._gains.pop(0)
            self._losses.pop(0)
        
        # 计算平均收益和损失
        if len(self._gains) < period:
            return 50.0  # 数据不足时返回中性值
        
        avg_gain = sum(self._gains) / period
        avg_loss = sum(self._losses) / period
        
        # 计算RSI
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _generate_signal(self, price_data: Dict[str, Any], value: float) -> SignalType:
        """生成交易信号"""
        # RSI超买超卖策略
        if value > 70:
            return SignalType.SELL
        elif value < 30:
            return SignalType.BUY
        elif 30 <= value <= 70:
            return SignalType.HOLD
        
        return SignalType.HOLD


# 全局指标工厂实例
factory = CustomIndicatorFactory()

# 注册内置指标
factory.register(SimpleMovingAverage)
factory.register(RelativeStrengthIndex)


def create_custom_indicator(indicator_name: str, **kwargs) -> str:
    """
    快速创建自定义指标实例
    
    Args:
        indicator_name: 指标名称
        **kwargs: 配置参数
        
    Returns:
        实例ID
    """
    return factory.create(indicator_name, kwargs)


def update_indicator(instance_id: str, price_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新指标并获取结果
    
    Args:
        instance_id: 实例ID
        price_data: 价格数据
        
    Returns:
        更新结果
    """
    indicator = factory.get_instance(instance_id)
    value = indicator.update(price_data)
    signal = indicator.get_last_signal()
    
    return {
        'value': value,
        'signal': signal.value if signal else None,
        'indicator_name': indicator.name,
        'timestamp': price_data.get('timestamp', len(indicator.timestamps) - 1)
    }


def get_indicator_info(instance_id: str) -> Dict[str, Any]:
    """获取指标信息"""
    indicator = factory.get_instance(instance_id)
    return json.loads(indicator.to_json())


# 使用示例
if __name__ == "__main__":
    print("=== Python自定义指标系统测试 ===")
    
    # 创建SMA指标
    sma_id = create_custom_indicator("SimpleMovingAverage", period=10)
    print(f"创建SMA指标: {sma_id}")
    
    # 创建RSI指标
    rsi_id = create_custom_indicator("RelativeStrengthIndex", period=14)
    print(f"创建RSI指标: {rsi_id}")
    
    # 模拟价格数据
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 112, 111, 113, 115]
    
    print("\n=== 更新指标 ===")
    for i, price in enumerate(prices):
        price_data = {
            'open': price - 1,
            'high': price + 1,
            'low': price - 2,
            'close': price,
            'volume': 1000,
            'timestamp': i
        }
        
        # 更新SMA
        sma_result = update_indicator(sma_id, price_data)
        print(f"时间 {i}: 价格={price}, SMA={sma_result['value']:.2f}, 信号={sma_result['signal']}")
        
        # 更新RSI
        rsi_result = update_indicator(rsi_id, price_data)
        print(f"时间 {i}: RSI={rsi_result['value']:.2f}, 信号={rsi_result['signal']}")
    
    print("\n=== 指标信息 ===")
    print("SMA信息:", json.dumps(get_indicator_info(sma_id), indent=2))
    print("RSI信息:", json.dumps(get_indicator_info(rsi_id), indent=2))
    
    print("\n=== 系统状态 ===")
    print("注册的指标:", factory.list_indicators())
    print("活跃的实例:", factory.list_instances())