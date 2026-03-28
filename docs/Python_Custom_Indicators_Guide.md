# Python自定义指标开发指南

## 概述

PlusPlusTrader的Python自定义指标系统允许用户在Python中轻松定义和使用自己的技术指标。通过这个系统，你可以：

1. **快速原型开发**：在Python中快速实现和测试新的交易想法
2. **灵活组合**：创建复杂的复合指标和策略
3. **无缝集成**：Python指标可以直接在C++核心中使用
4. **易于维护**：Python代码更易于编写、测试和调试

## 系统架构

```
┌─────────────────────────────────────────────┐
│              C++ 核心引擎                   │
│  ┌─────────────────────────────────────┐  │
│  │      PythonIndicatorBridge          │  │
│  │  (C++ ↔ Python 桥接接口)            │  │
│  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────┐
│            Python 自定义指标系统             │
│  ┌─────────────────────────────────────┐  │
│  │      PythonIndicator 基类           │  │
│  │  (所有自定义指标的基类)              │  │
│  └─────────────────────────────────────┘  │
│  ┌─────────────────────────────────────┐  │
│  │      CustomIndicatorFactory         │  │
│  │  (指标工厂和生命周期管理)            │  │
│  └─────────────────────────────────────┘  │
│  ┌─────────────────────────────────────┐  │
│  │      示例指标库                      │  │
│  │  (SMA, RSI, MACD, 布林带等)         │  │
│  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## 快速开始

### 1. 创建简单的自定义指标

```python
from custom_indicator import PythonIndicator, IndicatorConfig, SignalType

class MySimpleIndicator(PythonIndicator):
    """简单的自定义指标示例"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        
        # 设置默认参数
        self.config.parameters.setdefault('period', 10)
        self.config.required_parameters = ['period']
        
        # 初始化内部状态
        self._price_buffer = []
    
    def _calculate(self, price_data: dict) -> float:
        """计算指标值"""
        close_price = price_data.get('close', 0)
        period = self.config.parameters.get('period', 10)
        
        # 添加到缓冲区
        self._price_buffer.append(close_price)
        
        # 保持缓冲区大小
        if len(self._price_buffer) > period:
            self._price_buffer.pop(0)
        
        # 计算简单移动平均
        if not self._price_buffer:
            return close_price
        
        return sum(self._price_buffer) / len(self._price_buffer)
    
    def _generate_signal(self, price_data: dict, value: float) -> SignalType:
        """生成交易信号"""
        close_price = price_data.get('close', 0)
        
        if len(self.values) < 2:
            return SignalType.HOLD
        
        # 简单的价格与指标交叉策略
        prev_value = self.values[-2]
        
        if close_price > value and close_price <= prev_value:
            return SignalType.BUY
        elif close_price < value and close_price >= prev_value:
            return SignalType.SELL
        
        return SignalType.HOLD
```

### 2. 使用指标

```python
from custom_indicator import factory

# 创建指标实例
config = {'period': 20}
instance_id = factory.create("MySimpleIndicator", config)

# 获取指标实例
indicator = factory.get_instance(instance_id)

# 更新指标
price_data = {
    'open': 100.0,
    'high': 102.0,
    'low': 98.0,
    'close': 101.0,
    'volume': 1000,
    'timestamp': 1
}

value = indicator.update(price_data)
signal = indicator.get_last_signal()

print(f"指标值: {value}")
print(f"信号: {signal}")
```

### 3. 在C++中使用Python指标

```cpp
#include "custom/PythonIndicatorBridge.h"
#include "indicators/PriceData.h"

using namespace pplustrader;
using namespace pplustrader::custom;

int main() {
    // 初始化Python环境
    PythonIndicatorBridge& bridge = PythonIndicatorBridge::getInstance();
    bridge.initialize();
    
    // 创建Python指标实例
    std::string config = "{\"period\": 20}";
    std::string instance_id = bridge.createIndicator("MySimpleIndicator", config);
    
    // 创建包装器
    PythonWrappedIndicator indicator(bridge, instance_id, "MyIndicator");
    
    // 更新指标
    PriceData price_data;
    price_data.open = 100.0;
    price_data.high = 102.0;
    price_data.low = 98.0;
    price_data.close = 101.0;
    price_data.volume = 1000;
    price_data.timestamp = 1;
    
    double value = indicator.calculate(price_data);
    Signal signal = indicator.generateSignal(price_data, value);
    
    std::cout << "指标值: " << value << std::endl;
    std::cout << "信号: " << static_cast<int>(signal) << std::endl;
    
    return 0;
}
```

## 核心概念

### 1. PythonIndicator基类

所有自定义指标都必须继承自`PythonIndicator`基类，并实现以下方法：

- `_calculate(price_data)`: 计算指标值（必须实现）
- `_generate_signal(price_data, value)`: 生成交易信号（可选重写）

### 2. 价格数据结构

`price_data`参数是一个字典，包含以下字段：

| 字段 | 类型 | 描述 |
|------|------|------|
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `volume` | float | 成交量 |
| `timestamp` | int | 时间戳 |

### 3. 信号类型

系统支持以下信号类型：

| 信号 | 描述 |
|------|------|
| `SignalType.BUY` | 买入信号 |
| `SignalType.SELL` | 卖出信号 |
| `SignalType.HOLD` | 持有信号 |
| `SignalType.STRONG_BUY` | 强烈买入信号 |
| `SignalType.STRONG_SELL` | 强烈卖出信号 |

### 4. 配置管理

每个指标都有自己的配置，可以通过`IndicatorConfig`类管理：

```python
config = IndicatorConfig(
    name="MyIndicator",
    description="我的自定义指标",
    version="1.0.0",
    author="Your Name",
    parameters={'period': 20, 'factor': 2.0},
    required_parameters=['period'],
    default_values={'period': 10, 'factor': 1.5}
)
```

## 高级功能

### 1. 错误处理和日志

系统提供了完整的错误处理和日志系统：

```python
from custom_indicator_utils import error_handler, error_handler_decorator

# 使用装饰器自动处理错误
@error_handler_decorator
def my_calculation_method(self, price_data):
    # 你的计算逻辑
    pass

# 手动记录错误
error_handler.record_error(
    severity=ErrorSeverity.WARNING,
    message="参数值超出范围",
    indicator_name=self.name,
    instance_id=instance_id,
    extra_data={'param': param_value}
)

# 查看错误统计
errors = error_handler.get_errors(severity=ErrorSeverity.ERROR, limit=10)
for error in errors:
    print(f"[{error.severity.value}] {error.message}")
```

### 2. 性能监控

```python
from custom_indicator_utils import performance_monitor

# 监控指标计算性能
performance_monitor.start_timing("indicator_calculation")
# ... 执行计算 ...
duration = performance_monitor.stop_timing("indicator_calculation")

# 获取性能统计
stats = performance_monitor.get_statistics("indicator_calculation")
print(f"平均耗时: {stats['mean']:.4f}s")
print(f"最大耗时: {stats['max']:.4f}s")
```

### 3. 配置持久化

```python
from custom_indicator_utils import config_manager

# 保存指标配置
config = {'period': 20, 'factor': 2.0}
config_path = config_manager.save_indicator_config(
    "MyIndicator", 
    config, 
    "my_indicator_config.json"
)

# 加载配置
loaded_config = config_manager.load_indicator_config(config_path)

# 列出所有配置
configs = config_manager.list_configs(indicator_name="MyIndicator")
for config_info in configs:
    print(f"配置文件: {config_info['filename']}")
    print(f"创建时间: {config_info['metadata']['created_at']}")
```

### 4. 复合指标

创建结合多个技术指标的复合指标：

```python
class CompositeIndicator(PythonIndicator):
    """复合指标示例"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        
        # 设置权重参数
        self.config.parameters.setdefault('weight_trend', 0.4)
        self.config.parameters.setdefault('weight_momentum', 0.3)
        self.config.parameters.setdefault('weight_volatility', 0.3)
        
        # 初始化子指标状态
        self._trend_values = []
        self._momentum_values = []
        self._volatility_values = []
    
    def _calculate(self, price_data: dict) -> float:
        """计算复合指标值"""
        
        # 1. 计算趋势分量
        trend = self._calculate_trend(price_data)
        self._trend_values.append(trend)
        
        # 2. 计算动量分量
        momentum = self._calculate_momentum(price_data)
        self._momentum_values.append(momentum)
        
        # 3. 计算波动率分量
        volatility = self._calculate_volatility(price_data)
        self._volatility_values.append(volatility)
        
        # 4. 加权合成
        weight_trend = self.config.parameters.get('weight_trend', 0.4)
        weight_momentum = self.config.parameters.get('weight_momentum', 0.3)
        weight_volatility = self.config.parameters.get('weight_volatility', 0.3)
        
        composite = (
            trend * weight_trend +
            momentum * weight_momentum +
            volatility * weight_volatility
        )
        
        return composite
    
    def _calculate_trend(self, price_data: dict) -> float:
        """计算趋势分量"""
        # 实现趋势检测逻辑
        pass
    
    def _calculate_momentum(self, price_data: dict) -> float:
        """计算动量分量"""
        # 实现动量计算逻辑
        pass
    
    def _calculate_volatility(self, price_data: dict) -> float:
        """计算波动率分量"""
        # 实现波动率计算逻辑
        pass
```

## 最佳实践

### 1. 代码组织

```
my_indicators/
├── __init__.py
├── trend_indicators.py      # 趋势类指标
├── momentum_indicators.py   # 动量类指标  
├── volatility_indicators.py # 波动率类指标
├── composite_indicators.py  # 复合指标
└── utils.py                 # 工具函数
```

### 2. 参数验证

```python
def _validate_parameters(self):
    """验证参数"""
    period = self.config.parameters.get('period')
    if period is None or period <= 0:
        raise ValueError("参数 'period' 必须大于0")
    
    if 'factor' in self.config.parameters:
        factor = self.config.parameters['factor']
        if not 0 <= factor <= 10:
            raise ValueError("参数 'factor' 必须在0到10之间")
```

### 3. 性能优化

```python
class OptimizedIndicator(PythonIndicator):
    """性能优化的指标"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        
        # 使用numpy数组提高计算性能
        import numpy as np
        self._price_array = np.array([])
        self._period = self.config.parameters.get('period', 20)
    
    def _calculate(self, price_data: dict) -> float:
        """使用numpy优化计算"""
        close_price = price_data.get('close', 0)
        
        # 使用numpy数组
        self._price_array = np.append(self._price_array, close_price)
        
        if len(self._price_array) > self._period:
            self._price_array = self._price_array[-self._period:]
        
        if len(self._price_array) < self._period:
            return close_price
        
        # numpy计算平均值（比Python循环快）
        return np.mean(self._price_array)
```

### 4. 测试策略

```python
import unittest
from custom_indicator import PythonIndicator, IndicatorConfig

class TestMyIndicator(unittest.TestCase):
    """指标测试类"""
    
    def setUp(self):
        """测试准备"""
        config = IndicatorConfig(
            name="TestIndicator",
            parameters={'period': 10}
        )
        self.indicator = MySimpleIndicator(config)
    
    def test_calculation(self):
        """测试指标计算"""
        test_data = [
            {'close': 100, 'volume': 1000},
            {'close': 102, 'volume': 1200},
            {'close': 101, 'volume': 1100},
        ]
        
        values = []
        for data in test_data:
            value = self.indicator.update(data)
            values.append(value)
        
        # 验证计算结果
        self.assertEqual(len(values), 3)
        self.assertAlmostEqual(values[-1], 101.0, places=2)
    
    def test_signal_generation(self):
        """测试信号生成"""
        # 模拟价格数据
        price_data = {'close': 105, 'volume': 1000}
        
        # 更新指标
        self.indicator.update({'close': 100, 'volume': 1000})
        self.indicator.update({'close': 102, 'volume': 1000})
        value = self.indicator.update(price_data)
        
        # 获取信号
        signal = self.indicator._generate_signal(price_data, value)
        
        # 验证信号
        self.assertIn(signal, [SignalType.BUY, SignalType.SELL, SignalType.HOLD])

if __name__ == '__main__':
    unittest.main()
```

## 故障排除

### 常见问题

1. **Python环境问题**
   ```
   错误: Failed to initialize Python interpreter
   解决: 确保系统安装了Python 3.8+，并且python3命令可用
   ```

2. **模块导入错误**
   ```
   错误: ModuleNotFoundError: No module named 'custom_indicator'
   解决: 确保工作目录正确，或者使用sys.path.append()添加模块路径
   ```

3. **参数验证失败**
   ```
   错误: ValueError: Required parameter 'period' is missing
   解决: 在配置中提供所有必要参数
   ```

4. **性能问题**
   ```
   警告: Function _calculate took 0.150s
   解决: 优化计算逻辑，使用numpy，减少不必要的计算
   ```

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **使用诊断工具**
   ```python
   from custom_indicator_utils import print_diagnostics
   print_diagnostics()
   ```

3. **检查错误记录**
   ```python
   from custom_indicator_utils import error_handler
   errors = error_handler.get_errors(limit=10)
   for error in errors:
       print(error.to_json())
   ```

## 示例指标库

系统提供了丰富的示例指标，可以直接使用或作为参考：

1. **EnhancedMovingAverage** - 增强型移动平均线
2. **BollingerBands** - 布林带指标
3. **MACDIndicator** - MACD指标
4. **VolumeWeightedAveragePrice** - 成交量加权平均价格
5. **CustomCompositeIndicator** - 自定义复合指标

查看`python/custom_indicator_examples.py`获取完整示例。

## 下一步

1. **探索示例**：运行示例代码了解系统功能
2. **创建简单指标**：从修改现有示例开始
3. **测试策略**：使用回测引擎测试你的指标
4. **优化性能**：对高频交易场景进行性能优化
5. **分享贡献**：将有用的指标贡献到社区

## 支持与反馈

如果在使用过程中遇到问题或有改进建议：

1. 查看错误日志：`logs/custom_indicators.log`
2. 运行系统诊断：`python custom_indicator_utils.py`
3. 参考示例代码：`python/custom_indicator_examples.py`
4. 查阅开发文档：`docs/`目录

祝你开发顺利！🎉