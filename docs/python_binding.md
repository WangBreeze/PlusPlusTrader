# Python绑定设计

## 目标
提供Python接口，让用户可以在Python中：
1. 使用C++交易引擎
2. 编写Python策略
3. 访问数据源和交易所
4. 进行回测和实盘交易

## 架构设计

### 核心接口
```
pplustrader/
├── __init__.py
├── core.py          # 交易引擎接口
├── data.py          # 数据源接口  
├── exchange.py      # 交易所接口
├── strategy.py      # 策略基类
├── backtest.py      # 回测引擎
└── utils.py         # 工具函数
```

### 绑定方式
使用pybind11创建C++扩展模块：
- `_pplustrader_core.so`: C++核心扩展
- Python层提供友好的API封装

## 接口设计

### 1. 交易引擎 (core.py)
```python
class TradingEngine:
    def __init__(self, config_path=None):
        pass
        
    def start(self):
        """启动引擎"""
        pass
        
    def stop(self):
        """停止引擎"""
        pass
        
    def add_strategy(self, strategy):
        """添加策略"""
        pass
        
    def submit_order(self, symbol, side, price, quantity, order_type='LIMIT'):
        """提交订单"""
        pass
        
    def cancel_order(self, order_id):
        """取消订单"""
        pass
```

### 2. 策略基类 (strategy.py)
```python
class Strategy:
    def __init__(self, name):
        self.name = name
        
    def initialize(self):
        """策略初始化"""
        pass
        
    def on_tick(self, tick):
        """行情回调"""
        pass
        
    def on_order(self, order):
        """订单回调"""
        pass
        
    def on_bar(self, bar):
        """K线回调"""
        pass
        
    def cleanup(self):
        """策略清理"""
        pass
```

### 3. Python策略示例
```python
import pplustrader as pt

class PythonMovingAverageStrategy(pt.Strategy):
    def __init__(self, symbol, short_period=10, long_period=30):
        super().__init__(f"PythonMA_{symbol}")
        self.symbol = symbol
        self.short_period = short_period
        self.long_period = long_period
        self.prices = []
        
    def initialize(self):
        print(f"策略 {self.name} 初始化")
        # 订阅行情
        self.subscribe([self.symbol])
        
    def on_tick(self, tick):
        if tick.symbol != self.symbol:
            return
            
        self.prices.append(tick.last_price)
        if len(self.prices) > self.long_period:
            self.prices.pop(0)
            
        if len(self.prices) >= self.long_period:
            # 计算移动平均
            short_ma = sum(self.prices[-self.short_period:]) / self.short_period
            long_ma = sum(self.prices[-self.long_period:]) / self.long_period
            
            # 交易逻辑
            if short_ma > long_ma:
                # 买入信号
                self.buy(self.symbol, 100)
            elif short_ma < long_ma:
                # 卖出信号
                self.sell(self.symbol, 100)
                
    def buy(self, symbol, quantity, price=None):
        """买入"""
        order = {
            'symbol': symbol,
            'side': 'BUY',
            'quantity': quantity,
            'price': price,
            'order_type': 'LIMIT' if price else 'MARKET'
        }
        self.submit_order(order)
        
    def sell(self, symbol, quantity, price=None):
        """卖出"""
        order = {
            'symbol': symbol,
            'side': 'SELL',
            'quantity': quantity,
            'price': price,
            'order_type': 'LIMIT' if price else 'MARKET'
        }
        self.submit_order(order)
```

### 4. 使用示例
```python
import pplustrader as pt
from datetime import datetime

# 创建引擎
engine = pt.TradingEngine('config.json')

# 创建策略
strategy = PythonMovingAverageStrategy('600519.SH', 10, 30)

# 添加策略
engine.add_strategy(strategy)

# 启动引擎
engine.start()

# 运行一段时间
import time
time.sleep(60)

# 停止引擎
engine.stop()
```

## 实现计划

### Phase 1: 基础绑定
1. 设置pybind11编译环境
2. 绑定TradingEngine核心类
3. 绑定基本数据结构（TickData, Order, Bar等）

### Phase 2: 策略绑定
1. 实现Python策略基类
2. 支持Python策略注册到C++引擎
3. 实现回调机制

### Phase 3: 数据源和交易所绑定
1. 绑定DataFeed接口
2. 绑定Exchange接口
3. 提供工厂方法

### Phase 4: 高级功能
1. 回测引擎Python接口
2. 性能分析工具
3. 可视化工具

## 技术要点

### 1. 内存管理
- 使用智能指针管理C++对象生命周期
- Python GC与C++对象释放协调

### 2. 回调机制
- Python策略回调到C++引擎
- 避免Python GIL影响性能

### 3. 数据转换
- C++数据结构到Python对象转换
- 支持numpy数组传递

### 4. 线程安全
- Python GIL管理
- 多线程环境下的回调安全

## 优势
1. **高性能**: C++核心处理高频数据和交易逻辑
2. **易用性**: Python接口简化策略开发
3. **灵活性**: 可以混合使用C++和Python策略
4. **可扩展性**: 方便添加新的数据源和交易所

## 时间估计
- Phase 1: 1-2天
- Phase 2: 2-3天  
- Phase 3: 1-2天
- Phase 4: 2-3天
- 总计: 6-10天