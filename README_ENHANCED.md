# PlusPlusTrader - 高性能量化交易框架

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![C++](https://img.shields.io/badge/C++-17-blue.svg)](https://isocpp.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/WangBreeze/PlusPlusTrader)
[![Documentation](https://img.shields.io/badge/docs-complete-blue.svg)](https://github.com/WangBreeze/PlusPlusTrader/tree/main/docs)

**PlusPlusTrader** 是一个基于C++核心的高性能量化交易框架，专为A股市场设计，提供完整的Python接口、Web监控界面和丰富的交易工具。

## ✨ 核心特性

### 🚀 高性能引擎
- **C++核心** - 优化的交易引擎，支持高频场景
- **多线程处理** - 并行数据计算和策略执行
- **内存池管理** - 高效内存使用，减少分配开销

### 🐍 Python生态集成
- **完整Python API** - 通过pybind11提供原生Python接口
- **自定义指标系统** - 支持在Python中创建自定义技术指标
- **Jupyter Notebook支持** - 完整的交互式开发环境

### 📊 A股市场支持
- **T+1交易规则** - 符合A股实际交易规则
- **涨跌停限制** - 自动处理价格限制
- **费率计算** - 佣金、印花税、过户费自动计算
- **多数据源** - yfinance、akshare、tushare数据下载

### 🎨 可视化与监控
- **Web监控界面** - 基于Dash的实时可视化
- **K线图表** - 交互式技术分析图表
- **实时交易监控** - 交易信号、持仓、资金实时显示

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
