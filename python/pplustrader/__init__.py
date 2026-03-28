"""
PlusPlusTrader - 量化交易系统
整合了高性能C++核心和Python生态工具
"""

import sys
import os
import warnings

# 添加C++扩展模块的路径
# 假设从项目根目录运行，构建目录为./build/python/bindings/
_this_dir = os.path.dirname(__file__)
_project_root = os.path.abspath(os.path.join(_this_dir, '../../'))
_build_dir = os.path.join(_project_root, 'build/python/bindings')

if os.path.exists(_build_dir):
    if _build_dir not in sys.path:
        sys.path.insert(0, _build_dir)
else:
    warnings.warn(f"C++扩展模块目录不存在: {_build_dir}")

# 导入C++核心模块
try:
    # 使用一个技巧：临时修改sys.modules来避免循环导入
    import sys
    import importlib.util
    
    # 保存原始的pplustrader模块引用
    original_module = sys.modules.get('pplustrader')
    
    # 尝试从多个位置导入C++模块
    cpp_module_paths = [
        os.path.join(_project_root, 'build/python/bindings/pplustrader.cpython-313-x86_64-linux-gnu.so'),
        os.path.join(_project_root, 'python/build/lib.linux-x86_64-cpython-313/pplustrader.cpython-313-x86_64-linux-gnu.so'),
        os.path.join(_project_root, 'python/pplustrader.cpython-313-x86_64-linux-gnu.so')
    ]
    
    _cpp = None
    for path in cpp_module_paths:
        if os.path.exists(path):
            try:
                # 临时从sys.modules中移除pplustrader以避免循环导入
                if 'pplustrader' in sys.modules:
                    del sys.modules['pplustrader']
                
                # 使用正确的模块名称导入
                spec = importlib.util.spec_from_file_location("pplustrader", path)
                _cpp = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(_cpp)
                print(f"✅ C++核心模块已从 {path} 加载")
                break
            except Exception as e:
                warnings.warn(f"从 {path} 导入C++模块失败: {e}")
                continue
            finally:
                # 恢复原始的pplustrader模块
                if original_module:
                    sys.modules['pplustrader'] = original_module
    
    if _cpp is None:
        raise ImportError("无法找到C++核心模块")
    
    # 检查模块结构并暴露适当的属性
    # 注意：编译的模块可能没有子模块结构，所以我们需要检查
    if hasattr(_cpp, 'core'):
        core = _cpp.core
    else:
        # 如果模块没有子模块结构，直接使用模块本身
        core = _cpp
    
    # 其他模块暂时使用核心模块
    data = exchange = risk = backtest = core
    
    # 标记C++模块可用
    _CPP_AVAILABLE = True
    
    # 尝试重新导出核心功能（如果可用）
    try:
        if hasattr(core, 'TickData'):
            TickData = core.TickData
            Order = core.Order
            AccountInfo = core.AccountInfo
            OrderType = core.OrderType
            OrderSide = core.OrderSide
            OrderStatus = core.OrderStatus
        else:
            # 如果核心模块没有这些类，创建占位符
            TickData = Order = AccountInfo = None
            OrderType = OrderSide = OrderStatus = None
    except:
        TickData = Order = AccountInfo = None
        OrderType = OrderSide = OrderStatus = None
    
except ImportError as e:
    warnings.warn(f"无法导入C++扩展模块: {e}")
    _CPP_AVAILABLE = False
    # 定义空的占位符
    core = data = exchange = risk = backtest = None
    TickData = Order = AccountInfo = None
    OrderType = OrderSide = OrderStatus = None

# 导入Python扩展模块（数据适配器、策略等）
from . import data as py_data
from . import exchange as py_exchange
from . import risk as py_risk
from . import backtest as py_backtest
from . import strategies as py_strategies

# 如果C++模块可用，将Python扩展与C++模块合并
if _CPP_AVAILABLE:
    # 将Python数据适配器添加到data模块
    for attr in dir(py_data):
        if not attr.startswith('_'):
            setattr(data, attr, getattr(py_data, attr))
    
    # 类似地合并其他模块
    # ...

# 导出常用类
if _CPP_AVAILABLE:
    # 注意：C++模块可能没有这些子模块，所以我们需要检查
    try:
        # 尝试从核心模块导入
        if hasattr(core, 'Strategy'):
            Strategy = core.Strategy
        if hasattr(core, 'Indicator'):
            Indicator = core.Indicator
        if hasattr(core, 'TradingEngine'):
            TradingEngine = core.TradingEngine
        
        # 其他模块暂时使用核心模块
        DataFeed = CSVDataFeed = BinanceDataFeed = OKXDataFeed = core
        Exchange = SimulatedExchange = core
        RiskManager = PositionSizing = core
        BacktestEngine = BacktestResult = core
        
    except Exception as e:
        warnings.warn(f"导出C++类时出错: {e}")
        # 创建占位符
        Strategy = Indicator = TradingEngine = None
        DataFeed = CSVDataFeed = BinanceDataFeed = OKXDataFeed = None
        Exchange = SimulatedExchange = None
        RiskManager = PositionSizing = None
        BacktestEngine = BacktestResult = None

# 版本信息
__version__ = '0.1.0'
__author__ = 'PlusPlusTrader Team'
__description__ = '高性能量化交易系统'

# 导出C++可用状态
_CPP_AVAILABLE = _CPP_AVAILABLE

print(f"PlusPlusTrader {__version__} 已加载 - C++核心{'可用' if _CPP_AVAILABLE else '不可用'}")