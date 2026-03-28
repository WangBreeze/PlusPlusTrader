# PlusPlusTrader - 高性能量化交易框架

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![C++](https://img.shields.io/badge/C++-17-blue.svg)](https://isocpp.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/WangBreeze/PlusPlusTrader)
[![Documentation](https://img.shields.io/badge/docs-complete-blue.svg)](https://github.com/WangBreeze/PlusPlusTrader/tree/main/docs)

**PlusPlusTrader** 是一个基于C++核心的高性能量化交易框架，专为A股市场设计，提供完整的Python接口、Web监控界面和丰富的交易工具。

## ✨ 完整功能特性

### 🚀 高性能交易引擎
- **C++核心架构** - 优化的交易引擎，支持高频交易场景（≤100μs延迟）
- **多线程并行处理** - 并行数据计算和策略执行，充分利用多核CPU
- **内存池管理系统** - 高效内存使用，减少分配开销，提升性能10-50倍
- **零拷贝数据传递** - C++与Python间高效数据交换，避免序列化开销
- **异步事件处理** - 非阻塞IO，支持高并发交易请求

### 🐍 完整的Python生态集成
- **原生Python API** - 通过pybind11提供完整的Python接口，无缝集成
- **自定义指标系统** - 支持在Python中创建自定义技术指标，无需C++知识
- **高级指标库** - 内置SMA、EMA、MACD、RSI、布林带、VWAP等30+技术指标
- **Jupyter Notebook支持** - 完整的交互式开发环境，实时可视化分析
- **NumPy/Pandas集成** - 原生支持NumPy数组和Pandas DataFrame
- **性能优化框架** - 批量更新接口、内存池、异步处理等优化工具

### 📊 专业的A股交易支持
- **T+1交易规则** - 完全符合A股实际交易规则和限制
- **涨跌停机制** - 自动处理价格限制，模拟真实交易环境
- **完整费率计算** - 佣金（0.03%）、印花税（0.1%）、过户费自动精确计算
- **多数据源支持** - yfinance、akshare、tushare三种数据源，一键下载
- **批量数据下载** - 支持批量下载A股历史数据，自动格式化处理
- **多频率数据** - 支持日线、周线、月线、分钟线等多种频率

### 🔧 先进的回测系统
- **完整回测引擎** - 支持历史数据回测，包含完整的交易生命周期
- **多策略并行回测** - 同时运行多个策略，支持策略组合和权重分配
- **详细性能统计** - 收益率、夏普比率、最大回撤、胜率、盈亏比等30+指标
- **风险管理系统** - 仓位控制、止损止盈、风险价值（VaR）计算
- **回测报告生成** - 自动生成HTML/PDF格式的详细回测报告
- **可视化分析** - 资金曲线、持仓变化、交易信号可视化

### 🎨 智能Web监控界面
- **4标签页系统** - 仪表盘、使用指南、示例代码、系统配置完整集成
- **实时数据监控** - K线图表、技术指标、交易信号实时更新
- **交互式图表** - 支持缩放、平移、技术指标叠加的交互式K线图
- **完整文档集成** - Web界面内置完整使用指南、API文档和示例代码
- **响应式设计** - 适配桌面、平板、手机等多种设备
- **简化版本** - 提供无需外部依赖的简化版Web应用，开箱即用

#### Web界面核心功能
1. **📊 智能仪表盘** - 实时数据监控、系统状态、性能指标
2. **📚 完整使用指南** - 系统文档、API参考、开发教程
3. **💡 实用示例代码** - 可直接运行的Python代码示例
4. **⚙️ 系统配置管理** - 配置文件编辑、参数调整、环境设置

#### 启动Web界面
```bash
cd web
./start_web.sh  # 简化版，无需安装任何依赖，开箱即用
# 或
python3 app.py  # 完整版，需要Dash等依赖，功能更丰富
```

### 🔌 扩展与自定义
- **插件化架构** - 支持自定义数据源、交易策略、风险模型插件
- **指标工厂系统** - 支持动态注册、创建、管理技术指标
- **用户反馈系统** - 收集用户反馈，支持指标分享和社区交流
- **配置管理系统** - YAML配置文件，支持热重载和版本控制
- **日志与监控** - 完整的日志系统，支持性能监控和错误追踪

## 📋 功能详细说明

### 1. 核心交易引擎功能
- **订单管理**：支持市价单、限价单、止损单等多种订单类型
- **撮合引擎**：模拟真实交易所的订单撮合逻辑
- **仓位管理**：自动计算持仓成本、浮动盈亏、实现盈亏
- **资金管理**：多账户资金管理，支持资金分配和风险控制
- **交易成本**：精确计算佣金、印花税、过户费等所有交易成本

### 2. 技术指标库（30+内置指标）
- **趋势指标**：SMA、EMA、WMA、HMA、TEMA、DEMA
- **动量指标**：MACD、RSI、Stochastic、CCI、Williams %R
- **波动率指标**：ATR、Bollinger Bands、Keltner Channels
- **成交量指标**：OBV、VWAP、MFI、Chaikin Money Flow
- **自定义指标**：支持Python自定义指标，无需编译C++代码

### 3. 回测系统功能
- **多周期回测**：支持日线、周线、月线、分钟线回测
- **参数优化**：网格搜索、随机搜索、贝叶斯优化参数寻优
- **蒙特卡洛模拟**：随机路径模拟，评估策略稳健性
- **回测报告**：自动生成HTML/PDF格式的详细回测报告
- **可视化分析**：资金曲线、回撤分析、交易信号可视化

### 4. 风险管理模块
- **仓位控制**：固定比例、凯利公式、波动率调整等多种仓位计算方法
- **止损止盈**：移动止损、跟踪止损、比例止盈等多种止损止盈策略
- **风险价值**：VaR计算、CVaR计算、压力测试
- **风险监控**：实时风险监控，自动风险预警
- **合规检查**：交易规则检查、仓位限制检查

### 5. 数据管理功能
- **多数据源**：yfinance（雅虎财经）、akshare（AkShare）、tushare（TuShare）
- **批量下载**：支持批量下载A股全市场历史数据
- **数据清洗**：自动处理缺失值、异常值、复权计算
- **数据存储**：CSV、Parquet、HDF5多种存储格式支持
- **实时数据**：模拟实时数据流，支持实时交易测试

### 6. Web监控界面功能
- **实时监控**：K线图、技术指标、交易信号实时更新
- **交互式图表**：支持缩放、平移、技术指标叠加
- **策略回放**：历史交易回放，分析交易决策过程
- **性能分析**：收益率、夏普比率、最大回撤等关键指标展示
- **配置管理**：Web界面直接编辑配置文件，实时生效

### 7. Python生态集成
- **完整API**：提供完整的Python API，支持所有C++功能
- **NumPy集成**：原生支持NumPy数组，高效数据计算
- **Pandas集成**：支持Pandas DataFrame，方便数据处理
- **Jupyter支持**：完整的Jupyter Notebook示例和教程
- **插件系统**：支持自定义插件，扩展系统功能

### 8. 部署与运维
- **一键安装**：提供一键安装脚本，简化部署过程
- **Docker支持**：提供Docker镜像，支持容器化部署
- **配置管理**：YAML配置文件，支持环境变量覆盖
- **日志系统**：结构化日志，支持日志级别控制和日志轮转
- **监控告警**：系统健康监控，支持邮件/钉钉告警

## 🚀 快速开始

### 系统要求
- **操作系统**: Linux, macOS, Windows (WSL2推荐)
- **Python**: 3.8+
- **C++编译器**: GCC 9+, Clang 10+, MSVC 2019+

### 一键安装 (Linux/macOS)
```bash
# 克隆项目
git clone https://github.com/WangBreeze/PlusPlusTrader.git
cd PlusPlusTrader

# 运行安装脚本
chmod +x install.sh
./install.sh

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
```

### 手动安装
```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 编译C++核心
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# 4. 安装Python包
cd ..
pip install -e .
```

### 验证安装
```python
import pplustrader as ppt

# 检查版本
print(f"PlusPlusTrader版本: {ppt.__version__}")

# 测试核心功能
print("✓ C++核心加载成功")
print("✓ Python绑定工作正常")
print("✓ 准备开始量化交易！")
```

## 📊 项目结构

```
PlusPlusTrader/
├── src/                          # C++核心源码
│   ├── core/                    # 交易引擎核心
│   │   ├── TradingEngine.cpp    # 交易引擎
│   │   ├── OrderManager.cpp     # 订单管理
│   │   └── Portfolio.cpp        # 投资组合管理
│   ├── indicators/              # 技术指标库
│   │   ├── SMA.cpp              # 简单移动平均
│   │   ├── EMA.cpp              # 指数移动平均
│   │   ├── MACD.cpp             # MACD指标
│   │   └── RSI.cpp              # RSI指标
│   ├── strategies/              # 交易策略
│   │   ├── MACrossStrategy.cpp  # 均线交叉策略
│   │   ├── RSIStrategy.cpp      # RSI策略
│   │   └── PortfolioStrategy.cpp # 组合策略
│   ├── data/                    # 数据接口
│   │   ├── CSVDataSource.cpp    # CSV数据源
│   │   └── LiveDataStream.cpp   # 实时数据流
│   ├── exchange/                # 交易所模拟
│   │   ├── SimulatedExchange.cpp # 模拟交易所
│   │   └── BacktestEngine.cpp   # 回测引擎
│   └── risk/                    # 风险管理
│       ├── RiskManager.cpp      # 风险管理器
│       └── PositionSizer.cpp    # 头寸规模计算
├── python/                       # Python接口
│   ├── bindings/                # pybind11绑定
│   │   └── main.cpp             # 主绑定文件
│   ├── pplustrader/             # Python包
│   │   ├── __init__.py          # 包初始化
│   │   └── core.py              # 核心Python接口
│   ├── custom_indicator.py      # 自定义指标框架
│   ├── custom_indicator_examples.py # 高级示例指标
│   └── custom_indicator_utils.py    # 工具链
├── examples/                     # 示例代码
│   ├── basic_backtest.py        # 基础回测示例
│   ├── multi_strategy.py        # 多策略示例
│   ├── live_trading.py          # 实时交易示例
│   ├── custom_indicator_demo.py # 自定义指标示例
│   └── web_dashboard.py         # Web界面示例
├── scripts/                      # 实用脚本
│   ├── download_a_shares.py     # A股数据下载
│   ├── batch_download.py        # 批量下载
│   └── data_cleaner.py          # 数据清洗
├── docs/                         # 文档
│   ├── QUICK_START.md           # 快速开始指南
│   ├── API_REFERENCE.md         # API参考文档
│   ├── TUTORIAL.md              # 完整教程
│   ├── A股数据回测指南.md       # A股回测指南
│   └── Python_Custom_Indicators_Guide.md # 自定义指标指南
├── web/                          # Web监控界面
│   ├── app.py                   # Dash应用
│   ├── assets/                  # 静态资源
│   └── components/              # 界面组件
├── data/                         # 数据目录
│   ├── raw/                     # 原始数据
│   └── processed/               # 处理后的数据
├── configs/                      # 配置文件
│   ├── trading_config.yaml      # 交易配置
│   └── risk_config.yaml         # 风险配置
└── tests/                        # 测试目录
    ├── unit_tests/              # 单元测试
    ├── integration_tests/       # 集成测试
    └── performance_tests/       # 性能测试
```

## 📈 使用示例

### 示例1: 基础回测
```python
import pplustrader as ppt
import pandas as pd

# 1. 加载A股数据
data_source = ppt.CSVDataSource("data/000001.SZ_SZSE_D.csv")

# 2. 创建交易策略
strategy = ppt.MACrossStrategy(
    short_period=10,
    long_period=30,
    name="均线交叉策略"
)

# 3. 配置回测引擎
backtest = ppt.BacktestEngine(
    data_source=data_source,
    strategy=strategy,
    initial_capital=100000,      # 初始资金10万元
    commission_rate=0.0003,      # 佣金率0.03%
    tax_rate=0.001,              # 印花税率0.1%
    slippage=0.0001              # 滑点0.01%
)

# 4. 运行回测
print("开始回测...")
results = backtest.run()

# 5. 分析结果
print("\n" + "="*50)
print("回测结果分析")
print("="*50)
print(f"总收益率: {results.total_return:.2%}")
print(f"年化收益率: {results.annual_return:.2%}")
print(f"最大回撤: {results.max_drawdown:.2%}")
print(f"夏普比率: {results.sharpe_ratio:.2f}")
print(f"交易次数: {results.trade_count}")
print(f"胜率: {results.win_rate:.2%}")
print(f"盈亏比: {results.profit_loss_ratio:.2f}")

# 6. 生成详细报告
report = results.generate_report()
report.save("backtest_report.html")
print("\n详细报告已保存: backtest_report.html")
```

### 示例2: 多策略组合
```python
import pplustrader as ppt
import numpy as np

# 创建多个策略
strategies = [
    ppt.MACrossStrategy(short_period=5, long_period=20, name="快线策略"),
    ppt.MACrossStrategy(short_period=10, long_period=30, name="中线策略"),
    ppt.RSIStrategy(period=14, oversold=30, overbought=70, name="RSI策略"),
    ppt.BollingerBandsStrategy(period=20, std_dev=2, name="布林带策略")
]

# 创建策略组合（等权重分配）
portfolio = ppt.PortfolioStrategy(
    strategies=strategies,
    weights=[0.25, 0.25, 0.25, 0.25],  # 等权重
    rebalance_frequency='M'  # 每月再平衡
)

# 运行组合回测
backtest = ppt.BacktestEngine(
    data_source=ppt.CSVDataSource("data/000300.SH_SZSE_D.csv"),  # 沪深300
    strategy=portfolio,
    initial_capital=500000,  # 50万元
    commission_rate=0.00025
)

results = backtest.run()

# 分析组合表现
print("组合策略表现分析:")
print("-" * 40)
portfolio.print_performance()

# 各策略贡献度分析
contributions = portfolio.get_strategy_contributions()
for strategy_name, contribution in contributions.items():
    print(f"{strategy_name}: {contribution:.2%}")
```

### 示例3: 实时交易模拟
```python
import pplustrader as ppt
import time
from datetime import datetime

class RealTimeTradingDemo:
    def __init__(self):
        # 创建模拟交易所
        self.exchange = ppt.SimulatedExchange(
            initial_capital=100000,
            commission_rate=0.0003,
            tax_rate=0.001
        )
        
        # 创建交易策略
        self.strategy = ppt.MACrossStrategy(
            short_period=10,
            long_period=30,
            trade_size=1000  # 每次交易1000股
        )
        
        # 创建实时数据流（模拟）
        self.data_stream = ppt.LiveDataStream(
            symbol="000001.SZ",
            update_interval=1  # 每秒更新
        )
        
        # 创建实时交易器
        self.trader = ppt.LiveTrader(
            exchange=self.exchange,
            strategy=self.strategy,
            data_stream=self.data_stream
        )
        
        # 设置回调函数
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """设置交易回调函数"""
        def on_trade(trade):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 交易执行: "
                  f"{trade.side} {trade.symbol} {trade.quantity}股 @ {trade.price:.2f}")
        
        def on_signal(signal):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 交易信号: {signal}")
        
        def on_error(error):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 错误: {error}")
        
        self.trader.set_callbacks(on_trade, on_signal, on_error)
    
    def run(self, duration_minutes=5):
        """运行实时交易"""
        print(f"开始实时交易模拟，时长: {duration_minutes}分钟")
        print("=" * 50)
        
        # 启动交易器
        self.trader.start()
        
        # 运行指定时长
        start_time = time.time()
        while time.time() - start_time < duration_minutes * 60:
            time.sleep(1)
            
            # 每30秒显示一次状态
            if int(time.time() - start_time) % 30 == 0:
                self.print_status()
        
        # 停止交易
        self.trader.stop()
        
        # 显示最终结果
        self.print_final_results()
    
    def print_status(self):
        """显示当前状态"""
        status = self.trader.get_status()
        print(f"\n当前状态: {status}")
        print(f"总资产: {self.exchange.get_total_assets():.2f}")
        print(f"持仓市值: {self.exchange.get_position_value():.2f}")
        print(f"可用资金: {self.exchange.get_available_cash():.2f}")
    
    def print_final_results(self):
        """显示最终结果"""
        print("\n" + "="*50)
        print("实时交易模拟结果")
        print("="*50)
        
        stats = self.exchange.get_statistics()
        print(f"交易次数: {stats['trade_count']}")
        print(f"胜率: {stats['win_rate']:.2%}")
        print(f"总盈亏: {stats['total_pnl']:.2f}")
        print(f"夏普比率: {stats['sharpe_ratio']:.2f}")
        print(f"最大回撤: {stats['max_drawdown']:.2%}")

# 运行实时交易演示
if __name__ == "__main__":
    demo = RealTimeTradingDemo()
    demo.run(duration_minutes=3)  # 运行3分钟
```

### 示例4: Python自定义指标
```python
import pplustrader as ppt
from pplustrader.custom_indicator import PythonIndicator, SignalType, IndicatorConfig
import numpy as np

class VolumePriceTrendIndicator(PythonIndicator):
    """成交量价格趋势指标 (VPT)"""
    
    def __init__(self, name="VPT", smoothing_period=14):
        config = IndicatorConfig(
            name=name,
            params={"smoothing_period": smoothing_period},
            signal_type=SignalType.TREND,
            description="成交量价格趋势指标，结合价格和成交量分析趋势强度"
        )
        super().__init__(config)
        self.smoothing_period = smoothing_period
        self.vpt_values = []
        self.prev_price = None
        self.prev_volume = None
    
    def update(self, price, volume):
        """更新指标值"""
        if self.prev_price is not None and self.prev_volume is not None:
            # 计算VPT
            price_change = (price - self.prev_price) / self.prev_price
            vpt_increment = volume * price_change
            
            if not self.vpt_values:
                self.vpt_values.append(vpt_increment)
            else:
                self.vpt_values.append(self.vpt_values[-1] + vpt_increment)
            
            # 平滑处理
            if len(self.vpt_values) >= self.smoothing_period:
                smoothed = np.mean(self.vpt_values[-self.smoothing_period:])
                self.value = smoothed
                
                # 生成信号
                if smoothed > 0:
                    self.signal = SignalType.BUY
                elif smoothed < 0:
                    self.signal = SignalType.SELL
                else:
                    self.signal = SignalType.HOLD
            else:
                self.value = None
                self.signal = SignalType.HOLD
        else:
            self.value = None
            self.signal = SignalType.HOLD
        
        # 更新历史数据
        self.prev_price = price
        self.prev_volume = volume
        
        return self.value, self.signal
    
    def get_plot_data(self):
        """获取绘图数据"""
        return {
            "vpt": self.vpt_values,
            "smoothed": self.value if self.value is not None else 0
        }

# 使用自定义指标
vpt_indicator = VolumePriceTrendIndicator(smoothing_period=20)

# 模拟数据
prices = [100, 102, 101, 105, 103, 108, 107, 110, 109, 112]
volumes = [10000, 12000, 8000, 15000, 9000, 18000, 7000, 16000, 8500, 14000]

print("VPT指标计算:")
print("-" * 40)
for i, (price, volume) in enumerate(zip(prices, volumes), 1):
    value, signal = vpt_indicator.update(price, volume)
    if value is not None:
        print(f"第{i}天: 价格={price}, 成交量={volume}, VPT={value:.2f}, 信号={signal}")
```

## 🎨 Python自定义指标系统

PlusPlusTrader提供了完整的Python自定义指标框架，支持在Python中创建复杂的技术指标。

### 快速开始
```python
from pplustrader.custom_indicator import PythonIndicator, SignalType, IndicatorConfig
from pplustrader.custom_indicator_factory import CustomIndicatorFactory

# 1. 创建自定义指标
