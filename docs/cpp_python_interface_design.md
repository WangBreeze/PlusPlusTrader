# C++/Python接口详细设计

## 设计目标
1. **高性能**: C++核心处理高频数据，Python提供灵活策略开发
2. **易用性**: Python API简洁直观，符合Pythonic风格
3. **安全性**: 内存安全，避免内存泄漏和悬挂指针
4. **扩展性**: 易于添加新的数据类型和接口

## 架构设计

### 1. 绑定层次结构
```
C++核心层 (libpplustrader.so)
    ↓ pybind11绑定
Python C扩展 (_pplustrader_core.so)
    ↓ Python封装层
用户友好的Python API (pplustrader/__init__.py)
```

### 2. 模块划分
- **core模块**: 交易引擎核心接口
- **data模块**: 数据源和行情数据接口
- **exchange模块**: 交易所接口
- **strategy模块**: 策略基类和回调接口
- **backtest模块**: 回测引擎接口
- **utils模块**: 工具函数和类型转换

## 接口详细设计

### 1. 核心数据结构 (C++ → Python)

#### TickData结构
```cpp
// C++定义
struct TickData {
    std::string symbol;       // 标的代码
    double timestamp;         // 时间戳 (Unix秒，毫秒精度)
    double last_price;        // 最新价
    double volume;           // 成交量
    double amount;           // 成交额
    double bid_price;        // 买一价
    double ask_price;        // 卖一价
    int bid_volume;          // 买一量
    int ask_volume;          // 卖一量
};
```

#### BarData结构 (K线)
```cpp
struct BarData {
    std::string symbol;
    double timestamp;         // K线开始时间
    double open;
    double high;
    double low;
    double close;
    double volume;
    double amount;
    int frequency;           // 频率 (秒): 60=1分钟, 300=5分钟, 900=15分钟
};
```

#### Order结构
```cpp
struct Order {
    std::string order_id;    // 订单ID
    std::string symbol;
    std::string side;        // "BUY" or "SELL"
    std::string order_type;  // "LIMIT", "MARKET"
    double price;            // 限价单价格
    double quantity;         // 数量
    double filled_quantity;  // 已成交数量
    std::string status;      // "NEW", "PARTIALLY_FILLED", "FILLED", "CANCELED"
    double timestamp;        // 创建时间
};
```

### 2. 交易引擎接口 (TradingEngine)

#### C++类设计
```cpp
class TradingEngine {
public:
    TradingEngine(const std::string& config_path);
    ~TradingEngine();
    
    bool start();
    void stop();
    
    void add_strategy(std::shared_ptr<Strategy> strategy);
    void remove_strategy(const std::string& strategy_name);
    
    std::string submit_order(const Order& order);
    bool cancel_order(const std::string& order_id);
    
    std::vector<Order> get_orders() const;
    std::vector<Position> get_positions() const;
    
    void subscribe(const std::vector<std::string>& symbols);
    void unsubscribe(const std::vector<std::string>& symbols);
};
```

#### Python绑定设计
```python
# Python封装类
class TradingEngine:
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化交易引擎
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        pass
        
    def start(self) -> bool:
        """启动引擎，返回是否成功"""
        pass
        
    def stop(self):
        """停止引擎"""
        pass
        
    def add_strategy(self, strategy: 'Strategy') -> None:
        """添加策略"""
        pass
        
    def remove_strategy(self, strategy_name: str) -> None:
        """移除策略"""
        pass
        
    def submit_order(self, order: Dict) -> str:
        """
        提交订单
        
        Args:
            order: 订单字典，包含symbol, side, price, quantity等字段
            
        Returns:
            订单ID
        """
        pass
        
    def cancel_order(self, order_id: str) -> bool:
        """取消订单，返回是否成功"""
        pass
        
    def get_orders(self) -> List[Dict]:
        """获取所有订单"""
        pass
        
    def get_positions(self) -> List[Dict]:
        """获取所有持仓"""
        pass
        
    def subscribe(self, symbols: List[str]) -> None:
        """订阅行情"""
        pass
        
    def unsubscribe(self, symbols: List[str]) -> None:
        """取消订阅"""
        pass
```

### 3. 策略基类接口

#### C++策略基类 (支持Python继承)
```cpp
// C++抽象基类
class Strategy {
public:
    virtual ~Strategy() = default;
    
    virtual void initialize() = 0;
    virtual void cleanup() = 0;
    virtual void on_tick(const TickData& tick) = 0;
    virtual void on_bar(const BarData& bar) = 0;
    virtual void on_order(const Order& order) = 0;
    
    // 获取策略名称
    virtual std::string get_name() const = 0;
};
```

#### Python策略基类
```python
from abc import ABC, abstractmethod
from typing import Dict, List

class Strategy(ABC):
    """策略抽象基类"""
    
    def __init__(self, name: str):
        self._name = name
        self._engine = None  # 由TradingEngine设置
        
    @property
    def name(self) -> str:
        return self._name
        
    def set_engine(self, engine: 'TradingEngine'):
        """设置交易引擎（内部调用）"""
        self._engine = engine
        
    @abstractmethod
    def initialize(self):
        """策略初始化"""
        pass
        
    @abstractmethod  
    def cleanup(self):
        """策略清理"""
        pass
        
    @abstractmethod
    def on_tick(self, tick: Dict):
        """Tick数据回调"""
        pass
        
    @abstractmethod
    def on_bar(self, bar: Dict):
        """K线数据回调"""
        pass
        
    @abstractmethod
    def on_order(self, order: Dict):
        """订单状态回调"""
        pass
        
    def subscribe(self, symbols: List[str]):
        """订阅行情（便捷方法）"""
        if self._engine:
            self._engine.subscribe(symbols)
            
    def submit_order(self, order: Dict) -> str:
        """提交订单（便捷方法）"""
        if self._engine:
            return self._engine.submit_order(order)
        raise RuntimeError("Strategy not attached to an engine")
        
    def cancel_order(self, order_id: str) -> bool:
        """取消订单（便捷方法）"""
        if self._engine:
            return self._engine.cancel_order(order_id)
        raise RuntimeError("Strategy not attached to an engine")
```

### 4. 回调机制实现

#### Python到C++的回调桥梁
```cpp
// Python策略包装器
class PythonStrategyWrapper : public Strategy {
public:
    PythonStrategyWrapper(pybind11::object py_strategy);
    ~PythonStrategyWrapper();
    
    void initialize() override;
    void cleanup() override;
    void on_tick(const TickData& tick) override;
    void on_bar(const BarData& bar) override;
    void on_order(const Order& order) override;
    
    std::string get_name() const override;
    
private:
    pybind11::object py_strategy_;  // Python策略对象
    pybind11::gil_scoped_acquire gil_;  // GIL管理
};
```

### 5. 内存管理策略

#### 智能指针策略
```cpp
// C++端使用shared_ptr管理对象
using TradingEnginePtr = std::shared_ptr<TradingEngine>;
using StrategyPtr = std::shared_ptr<Strategy>;

// Python绑定确保正确的引用计数
PYBIND11_MODULE(_pplustrader_core, m) {
    pybind11::class_<TradingEngine, TradingEnginePtr>(m, "TradingEngine")
        .def(pybind11::init<const std::string&>())
        .def("start", &TradingEngine::start)
        .def("stop", &TradingEngine::stop)
        // ... 其他方法
        ;
    
    pybind11::class_<Strategy, StrategyPtr>(m, "StrategyBase")
        .def("get_name", &Strategy::get_name)
        ;
}
```

#### Python对象的生命周期管理
```python
# Python端确保C++对象不被提前释放
class TradingEngine:
    def __init__(self, config_path=None):
        # 保存对C++对象的引用
        self._cpp_engine = _pplustrader_core.TradingEngine(config_path or "")
        
    def __getattr__(self, name):
        # 代理所有方法到C++对象
        return getattr(self._cpp_engine, name)
```

### 6. 数据转换辅助函数

#### C++到Python的类型转换
```cpp
// TickData转换
pybind11::dict tick_to_dict(const TickData& tick) {
    return pybind11::dict(
        "symbol"_a = tick.symbol,
        "timestamp"_a = tick.timestamp,
        "last_price"_a = tick.last_price,
        "volume"_a = tick.volume,
        "amount"_a = tick.amount,
        "bid_price"_a = tick.bid_price,
        "ask_price"_a = tick.ask_price,
        "bid_volume"_a = tick.bid_volume,
        "ask_volume"_a = tick.ask_volume
    );
}

// Python字典到TickData转换
TickData dict_to_tick(const pybind11::dict& dict) {
    TickData tick;
    tick.symbol = dict["symbol"].cast<std::string>();
    tick.timestamp = dict["timestamp"].cast<double>();
    // ... 其他字段
    return tick;
}
```

### 7. 线程安全和GIL管理

#### GIL策略
```cpp
// 从C++回调Python时获取GIL
void PythonStrategyWrapper::on_tick(const TickData& tick) {
    pybind11::gil_scoped_acquire acquire;  // 获取GIL
    
    try {
        py_strategy_.attr("on_tick")(tick_to_dict(tick));
    } catch (const pybind11::error_already_set& e) {
        // 处理Python异常
        std::cerr << "Python error in on_tick: " << e.what() << std::endl;
    }
}

// C++线程中长时间运行时不持有GIL
void TradingEngine::process_ticks() {
    while (running_) {
        TickData tick = get_next_tick();
        
        // 对每个策略的回调需要获取GIL
        for (auto& strategy : strategies_) {
            // 获取GIL，调用策略回调
            pybind11::gil_scoped_acquire acquire;
            strategy->on_tick(tick);
        }
    }
}
```

## 实现计划

### Phase 1: 基础框架 (2-3天)
1. 配置pybind11编译环境
2. 绑定基本数据结构 (TickData, BarData, Order)
3. 实现基础类型转换
4. 创建Python包框架

### Phase 2: 引擎绑定 (2-3天)
1. 绑定TradingEngine核心类
2. 实现Python策略基类
3. 实现Python到C++的回调桥接
4. 添加内存管理机制

### Phase 3: 数据接口 (2天)
1. 绑定DataFeed和DataSource接口
2. 实现CSV数据源Python接口
3. 添加数据库数据源支持
4. 实现实时数据订阅

### Phase 4: 交易所接口 (2天)
1. 绑定Exchange接口
2. 实现模拟交易所Python接口
3. 添加实盘交易所适配
4. 实现订单管理

### Phase 5: 回测引擎 (2-3天)
1. 绑定BacktestEngine
2. 实现Python回测接口
3. 添加结果分析和统计
4. 实现性能优化

## 构建配置

### CMake配置
```cmake
# 查找Python和pybind11
find_package(Python3 COMPONENTS Development REQUIRED)
find_package(pybind11 REQUIRED)

# 创建Python模块
pybind11_add_module(_pplustrader_core
    src/bindings/core_bindings.cpp
    src/bindings/data_bindings.cpp
    src/bindings/strategy_bindings.cpp
    src/bindings/utils_bindings.cpp
)

# 链接依赖库
target_link_libraries(_pplustrader_core PRIVATE
    pplustrader_core
    pybind11::module
    ${Python3_LIBRARIES}
)
```

### Python包配置
```python
# setup.py
from setuptools import setup, find_packages, Extension
import pybind11
from pybind11.setup_helpers import Pybind11Extension

ext_modules = [
    Pybind11Extension(
        "pplustrader._core",
        ["src/bindings/core_bindings.cpp"],
        include_dirs=[
            pybind11.get_include(),
            pybind11.get_include(user=True),
            "src/include"
        ],
        language="c++"
    ),
]

setup(
    name="pplustrader",
    version="0.1.0",
    packages=find_packages(),
    ext_modules=ext_modules,
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.2.0",
    ],
)
```

## 使用示例

### Python策略开发
```python
import pplustrader as pt
import pandas as pd

class MyStrategy(pt.Strategy):
    def __init__(self, symbol):
        super().__init__("MyStrategy")
        self.symbol = symbol
        self.prices = []
        
    def initialize(self):
        self.subscribe([self.symbol])
        print(f"Strategy {self.name} initialized for {self.symbol}")
        
    def on_tick(self, tick):
        if tick['symbol'] != self.symbol:
            return
            
        self.prices.append(tick['last_price'])
        
        if len(self.prices) >= 20:
            ma_short = pd.Series(self.prices[-10:]).mean()
            ma_long = pd.Series(self.prices[-20:]).mean()
            
            if ma_short > ma_long * 1.01:  # 短期均线上穿长期均线1%
                self.submit_order({
                    'symbol': self.symbol,
                    'side': 'BUY',
                    'price': tick['last_price'],
                    'quantity': 100
                })
                
    def on_order(self, order):
        print(f"Order update: {order['order_id']} - {order['status']}")

# 使用策略
engine = pt.TradingEngine('config.json')
strategy = MyStrategy('600519.SH')
engine.add_strategy(strategy)

engine.start()
# ... 运行引擎
engine.stop()
```

## 注意事项

1. **性能考虑**: 高频Tick数据回调时避免频繁的Python-C++转换
2. **异常处理**: 确保Python异常不会导致C++程序崩溃
3. **内存泄漏**: 仔细管理Python对象的引用计数
4. **线程安全**: 多线程环境下的GIL管理
5. **版本兼容**: 确保与不同Python版本的兼容性

## 测试策略

### 单元测试
```python
import unittest
import pplustrader as pt

class TestTradingEngine(unittest.TestCase):
    def test_engine_creation(self):
        engine = pt.TradingEngine()
        self.assertIsNotNone(engine)
        
    def test_order_submission(self):
        engine = pt.TradingEngine()
        order_id = engine.submit_order({
            'symbol': 'TEST',
            'side': 'BUY',
            'price': 100.0,
            'quantity': 10
        })
        self.assertIsInstance(order_id, str)

if __name__ == '__main__':
    unittest.main()
```

## 后续优化

1. **性能优化**: 使用numpy数组批量传输数据
2. **异步支持**: 支持asyncio异步接口
3. **类型提示**: 添加完整的类型注解
4. **文档生成**: 自动生成API文档
5. **缓存机制**: 数据缓存减少重复计算