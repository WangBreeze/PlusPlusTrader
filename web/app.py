"""
PlusPlusTrader Web可视化界面
基于Dash框架的量化交易监控和可视化平台
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import sys
import os

# 添加项目路径，以便导入pplustrader模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'python'))
sys.path.insert(0, os.path.join(project_root, 'build', 'python', 'bindings'))

# 尝试导入pplustrader模块
try:
    from pplustrader.data import BinanceDataFeed, OKXDataFeed
    HAS_TRADER = True
    print("✅ pplustrader 模块导入成功")
except ImportError as e:
    HAS_TRADER = False
    print(f"⚠️ pplustrader 模块导入失败: {e}")
    print("将使用模拟数据进行演示")

# 初始化Dash应用
app = dash.Dash(
    __name__,
    title='PlusPlusTrader 量化交易系统',
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
    suppress_callback_exceptions=True  # 抑制回调异常，解决动态布局问题
)

# 模拟数据生成函数
def generate_mock_data(symbol='BTC/USDT', points=100):
    """生成模拟K线数据"""
    base_price = 50000 if 'BTC' in symbol else 3000
    volatility = 0.02
    
    dates = [datetime.now() - timedelta(minutes=i) for i in range(points, 0, -1)]
    prices = []
    
    price = base_price
    for i in range(points):
        change = price * volatility * np.random.randn()
        price = max(price + change, base_price * 0.8)
        prices.append(price)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': [p * (1 - 0.005 * np.random.random()) for p in prices],
        'high': [p * (1 + 0.01 * np.random.random()) for p in prices],
        'low': [p * (1 - 0.01 * np.random.random()) for p in prices],
        'close': prices,
        'volume': [np.random.randint(100, 1000) for _ in range(points)]
    })
    
    return df

# 应用布局
app.layout = html.Div([
    # 标题栏
    html.Div([
        html.H1('🦞 PlusPlusTrader 量化交易系统', style={'color': '#2c3e50'}),
        html.Div([
            html.Span('📈 实时监控', className='badge badge-primary'),
            html.Span('📊 数据分析', className='badge badge-secondary ml-2'),
            html.Span('⚡ 高性能', className='badge badge-success ml-2'),
            html.Span('📚 完整文档', className='badge badge-info ml-2'),
        ], style={'margin-top': '10px'})
    ], className='header', style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'color': 'white',
        'padding': '20px',
        'border-radius': '10px',
        'margin-bottom': '20px'
    }),
    
    # 标签页导航
    dcc.Tabs(id='main-tabs', value='dashboard', children=[
        dcc.Tab(label='📊 仪表盘', value='dashboard'),
        dcc.Tab(label='📚 使用指南', value='guide'),
        dcc.Tab(label='💡 示例代码', value='examples'),
        dcc.Tab(label='⚙️ 系统配置', value='config'),
    ], style={
        'margin-bottom': '20px',
        'font-weight': 'bold'
    }),
    
    html.Div(id='tab-content'),
    
])

# 仪表盘标签页内容
dashboard_tab = html.Div([
    # 控制面板
    html.Div([
        html.Div([
            html.H4('🎛️ 控制面板', style={'color': '#34495e'}),
            
            html.Div([
                html.Label('选择交易对:'),
                dcc.Dropdown(
                    id='symbol-selector',
                    options=[
                        {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                        {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                        {'label': 'BNB/USDT', 'value': 'BNB/USDT'},
                        {'label': 'SOL/USDT', 'value': 'SOL/USDT'},
                    ],
                    value='BTC/USDT',
                    clearable=False,
                    style={'width': '200px'}
                ),
            ], style={'margin-bottom': '15px'}),
            
            html.Div([
                html.Label('选择时间周期:'),
                dcc.Dropdown(
                    id='interval-selector',
                    options=[
                        {'label': '1分钟', 'value': '1m'},
                        {'label': '5分钟', 'value': '5m'},
                        {'label': '15分钟', 'value': '15m'},
                        {'label': '1小时', 'value': '1h'},
                        {'label': '4小时', 'value': '4h'},
                        {'label': '1天', 'value': '1d'},
                    ],
                    value='15m',
                    clearable=False,
                    style={'width': '150px'}
                ),
            ], style={'margin-bottom': '15px'}),
            
            html.Div([
                html.Label('选择数据源:'),
                dcc.Dropdown(
                    id='datasource-selector',
                    options=[
                        {'label': '币安 Binance', 'value': 'binance'},
                        {'label': '欧易 OKX', 'value': 'okx'},
                        {'label': '模拟数据', 'value': 'mock'},
                    ],
                    value='binance' if HAS_TRADER else 'mock',
                    clearable=False,
                    style={'width': '180px'},
                    disabled=not HAS_TRADER
                ),
            ], style={'margin-bottom': '20px'}),
            
            html.Button('🚀 启动数据流', id='start-feed', n_clicks=0, 
                       className='btn btn-success', style={'margin-right': '10px'}),
            html.Button('⏹️ 停止数据流', id='stop-feed', n_clicks=0,
                       className='btn btn-danger'),
            
            html.Div(id='feed-status', style={'margin-top': '15px', 'color': '#7f8c8d'})
            
        ], className='control-panel', style={
            'background': '#f8f9fa',
            'padding': '20px',
            'border-radius': '8px',
            'border': '1px solid #e9ecef'
        }),
    ], style={'margin-bottom': '20px'}),
    
    # 图表区域
    html.Div([
        html.Div([
            html.H4('📊 价格图表', style={'color': '#34495e'}),
            dcc.Graph(id='price-chart', style={'height': '400px'}),
            dcc.Interval(id='chart-updater', interval=5000, n_intervals=0),
        ], className='chart-container', style={
            'background': 'white',
            'padding': '20px',
            'border-radius': '8px',
            'border': '1px solid #e9ecef',
            'margin-bottom': '20px'
        }),
        
        html.Div([
            html.H4('📈 技术指标', style={'color': '#34495e'}),
            dcc.Graph(id='indicator-chart', style={'height': '300px'}),
        ], className='indicator-container', style={
            'background': 'white',
            'padding': '20px',
            'border-radius': '8px',
            'border': '1px solid #e9ecef',
            'margin-bottom': '20px'
        }),
    ]),
    
    # 数据表格
    html.Div([
        html.H4('📋 最新数据', style={'color': '#34495e'}),
        html.Div(id='data-table', style={
            'max-height': '300px',
            'overflow-y': 'auto'
        }),
    ], style={
        'background': 'white',
        'padding': '20px',
        'border-radius': '8px',
        'border': '1px solid #e9ecef'
    }),
    
    # 系统状态
    html.Div([
        html.H4('🖥️ 系统状态', style={'color': '#34495e'}),
        html.Div(id='system-status', children=[
            html.P('🔌 数据连接: 未连接'),
            html.P('📊 数据点: 0'),
            html.P('⚡ 更新频率: 0 Hz'),
            html.P(f'🐍 Python版本: {sys.version.split()[0]}'),
            html.P(f'🦞 pplustrader: {"✅ 已加载" if HAS_TRADER else "❌ 未加载"}'),
        ]),
    ], style={
        'background': '#f8f9fa',
        'padding': '20px',
        'border-radius': '8px',
        'border': '1px solid #e9ecef',
        'margin-top': '20px'
    }),
])

# 使用指南标签页内容
guide_tab = html.Div([
    html.Div([
        html.H2('📚 PlusPlusTrader 使用指南', style={'color': '#2c3e50', 'margin-bottom': '20px'}),
        
        html.Div([
            html.H3('🎯 系统概述', style={'color': '#3498db'}),
            html.P('PlusPlusTrader 是一个高性能的量化交易系统，结合了C++核心引擎和Python生态系统的优势。'),
            html.Ul([
                html.Li('🚀 C++核心引擎：提供极致的性能表现'),
                html.Li('🐍 Python接口：支持灵活的策略开发'),
                html.Li('📊 实时监控：Web界面实时展示交易数据'),
                html.Li('📈 技术分析：内置多种技术指标和自定义指标系统'),
            ]),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('🛠️ 快速开始', style={'color': '#3498db'}),
            html.H4('1. 安装系统'),
            html.Pre('''
# 克隆项目
git clone https://github.com/yourusername/PlusPlusTrader.git
cd PlusPlusTrader

# 安装依赖
./install.sh

# 编译项目
mkdir build && cd build
cmake .. && make -j4
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
            
            html.H4('2. 启动Web界面'),
            html.Pre('''
cd web
python app.py
# 访问 http://127.0.0.1:8050
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
            
            html.H4('3. 使用Python接口'),
            html.Pre('''
import pplustrader

# 创建数据源
from pplustrader.data import BinanceDataFeed
feed = BinanceDataFeed(symbol="BTC/USDT", interval="1h")

# 获取数据
data = feed.fetch_ohlcv(limit=100)

# 使用技术指标
from pplustrader.indicators import SMA, EMA, RSI
sma = SMA(period=20)
ema = EMA(period=12)
rsi = RSI(period=14)

for price in data:
    sma_value = sma.update(price['close'])
    ema_value = ema.update(price['close'])
    rsi_value = rsi.update(price['close'])
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('📊 Web界面功能', style={'color': '#3498db'}),
            html.Table([
                html.Thead(html.Tr([
                    html.Th('功能', style={'padding': '10px', 'background': '#3498db', 'color': 'white'}),
                    html.Th('描述', style={'padding': '10px', 'background': '#3498db', 'color': 'white'}),
                    html.Th('使用方法', style={'padding': '10px', 'background': '#3498db', 'color': 'white'}),
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td('实时价格图表', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('显示K线图和技术指标', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('选择交易对和时间周期后自动更新', style={'padding': '10px', 'border': '1px solid #ddd'}),
                    ]),
                    html.Tr([
                        html.Td('技术指标分析', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('显示移动平均线、RSI等指标', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('图表下方显示技术指标图表', style={'padding': '10px', 'border': '1px solid #ddd'}),
                    ]),
                    html.Tr([
                        html.Td('数据表格', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('显示最新的交易数据', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('实时更新最新5条数据', style={'padding': '10px', 'border': '1px solid #ddd'}),
                    ]),
                    html.Tr([
                        html.Td('系统状态监控', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('显示系统连接状态和性能指标', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('页面底部显示系统状态信息', style={'padding': '10px', 'border': '1px solid #ddd'}),
                    ]),
                ])
            ], style={'width': '100%', 'border-collapse': 'collapse', 'margin-bottom': '20px'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('🔧 高级功能', style={'color': '#3498db'}),
            html.H4('自定义技术指标'),
            html.P('PlusPlusTrader支持自定义技术指标，可以在Python中定义自己的指标逻辑：'),
            html.Pre('''
from pplustrader.indicators import EnhancedIndicator

class MyCustomIndicator(EnhancedIndicator):
    def __init__(self, period=14):
        super().__init__("MyCustomIndicator", {"period": period})
        self.period = period
        self.prices = []
    
    def calculate(self):
        if len(self.prices) < self.period:
            return None
        
        # 自定义计算逻辑
        recent_prices = self.prices[-self.period:]
        avg_price = sum(recent_prices) / len(recent_prices)
        return avg_price
    
    def update(self, price):
        self.prices.append(price)
        return self.calculate()
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
            
            html.H4('回测引擎'),
            html.P('使用回测引擎测试交易策略：'),
            html.Pre('''
from pplustrader.backtest import BacktestEngine
from pplustrader.strategies import MovingAverageCrossover

# 创建回测引擎
engine = BacktestEngine(
    initial_capital=10000,
    data_source="data/btc_usdt_1h.csv"
)

# 添加策略
strategy = MovingAverageCrossover(fast_period=10, slow_period=30)
engine.add_strategy(strategy)

# 运行回测
results = engine.run()

# 查看结果
print(f"总收益: {results.total_return:.2%}")
print(f"夏普比率: {results.sharpe_ratio:.2f}")
print(f"最大回撤: {results.max_drawdown:.2%}")
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('📞 获取帮助', style={'color': '#3498db'}),
            html.P('如果您遇到问题或需要帮助，请参考以下资源：'),
            html.Ul([
                html.Li('📖 项目文档：查看项目根目录下的README.md文件'),
                html.Li('🐛 问题反馈：在GitHub仓库提交Issue'),
                html.Li('💬 社区讨论：加入我们的Discord社区'),
                html.Li('📧 邮件支持：contact@pplustrader.com'),
            ]),
            html.P('💡 提示：Web界面中的"示例代码"标签页提供了更多实用的代码示例。'),
        ]),
    ], style={
        'background': 'white',
        'padding': '30px',
        'border-radius': '10px',
        'border': '1px solid #e9ecef'
    }),
])

# 示例代码标签页内容
examples_tab = html.Div([
    html.Div([
        html.H2('💡 PlusPlusTrader 示例代码', style={'color': '#2c3e50', 'margin-bottom': '20px'}),
        
        html.Div([
            html.H3('📈 基础数据获取', style={'color': '#2ecc71'}),
            html.P('从交易所获取实时数据：'),
            html.Pre('''
import pplustrader
from pplustrader.data import BinanceDataFeed, OKXDataFeed

# 币安数据源
binance_feed = BinanceDataFeed(
    symbol="BTC/USDT",
    interval="1h",
    api_key="your_api_key",      # 可选
    api_secret="your_api_secret" # 可选
)

# 欧易数据源
okx_feed = OKXDataFeed(
    symbol="ETH/USDT",
    interval="15m"
)

# 获取历史数据
historical_data = binance_feed.fetch_ohlcv(limit=100)
print(f"获取到 {len(historical_data)} 条历史数据")

# 获取最新价格
latest_price = binance_feed.fetch_ticker()
print(f"当前价格: {latest_price['last']}")

# 订阅实时数据（WebSocket）
def on_ticker_update(ticker):
    print(f"价格更新: {ticker['last']}")

binance_feed.subscribe_ticker(on_ticker_update)
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('📊 技术指标计算', style={'color': '#2ecc71'}),
            html.P('使用内置技术指标：'),
            html.Pre('''
from pplustrader.indicators import SMA, EMA, MACD, RSI, BollingerBands
import numpy as np

# 创建指标实例
sma20 = SMA(period=20)
ema12 = EMA(period=12)
macd = MACD(fast_period=12, slow_period=26, signal_period=9)
rsi14 = RSI(period=14)
bb = BollingerBands(period=20, std_dev=2)

# 模拟价格数据
prices = np.random.normal(50000, 1000, 100)

# 更新指标
for price in prices:
    sma_val = sma20.update(price)
    ema_val = ema12.update(price)
    macd_val, signal_val, hist_val = macd.update(price)
    rsi_val = rsi14.update(price)
    upper_bb, middle_bb, lower_bb = bb.update(price)
    
    # 打印最后几个值
    if price == prices[-1]:
        print(f"价格: {price:.2f}")
        print(f"SMA20: {sma_val:.2f}")
        print(f"EMA12: {ema_val:.2f}")
        print(f"MACD: {macd_val:.4f}, Signal: {signal_val:.4f}, Hist: {hist_val:.4f}")
        print(f"RSI14: {rsi_val:.2f}")
        print(f"布林带: 上轨={upper_bb:.2f}, 中轨={middle_bb:.2f}, 下轨={lower_bb:.2f}")
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('🤖 交易策略开发', style={'color': '#2ecc71'}),
            html.P('实现简单的移动平均线交叉策略：'),
            html.Pre('''
from pplustrader.strategies import BaseStrategy
from pplustrader.indicators import SMA

class MovingAverageCrossover(BaseStrategy):
    """移动平均线交叉策略"""
    
    def __init__(self, fast_period=10, slow_period=30):
        super().__init__("MA Crossover")
        self.fast_sma = SMA(period=fast_period)
        self.slow_sma = SMA(period=slow_period)
        self.position = 0  # 0: 无仓位, 1: 多头, -1: 空头
        
    def on_tick(self, tick_data):
        """处理每个tick数据"""
        price = tick_data['close']
        
        # 更新指标
        fast_val = self.fast_sma.update(price)
        slow_val = self.slow_sma.update(price)
        
        if fast_val is None or slow_val is None:
            return
        
        # 交易信号
        if fast_val > slow_val and self.position <= 0:
            # 金叉信号，买入
            self.buy(price, 0.1)  # 买入10%的资金
            self.position = 1
            print(f"买入信号: 价格={price}, 快线={fast_val:.2f}, 慢线={slow_val:.2f}")
            
        elif fast_val < slow_val and self.position >= 0:
            # 死叉信号，卖出
            self.sell(price, 0.1)  # 卖出10%的仓位
            self.position = -1
            print(f"卖出信号: 价格={price}, 快线={fast_val:.2f}, 慢线={slow_val:.2f}")
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('🔧 自定义指标', style={'color': '#2ecc71'}),
            html.P('创建自定义技术指标：'),
            html.Pre('''
from pplustrader.indicators import EnhancedIndicator
import numpy as np

class VolumeWeightedAveragePrice(EnhancedIndicator):
    """成交量加权平均价格指标"""
    
    def __init__(self, period=20):
        super().__init__("VWAP", {"period": period})
        self.period = period
        self.price_volume_pairs = []
        
    def calculate(self):
        if len(self.price_volume_pairs) < self.period:
            return None
        
        # 计算VWAP
        total_volume = sum(vol for _, vol in self.price_volume_pairs[-self.period:])
        if total_volume == 0:
            return None
            
        weighted_sum = sum(price * vol for price, vol in self.price_volume_pairs[-self.period:])
        vwap = weighted_sum / total_volume
        return vwap
    
    def update(self, price, volume):
        """更新VWAP值"""
        self.price_volume_pairs.append((price, volume))
        
        # 保持数据长度
        if len(self.price_volume_pairs) > self.period * 2:
            self.price_volume_pairs = self.price_volume_pairs[-self.period * 2:]
        
        return self.calculate()

# 使用自定义指标
vwap = VolumeWeightedAveragePrice(period=14)
for i in range(100):
    price = 50000 + np.random.randn() * 1000
    volume = np.random.randint(100, 1000)
    vwap_value = vwap.update(price, volume)
    
    if vwap_value:
        print(f"价格: {price:.2f}, 成交量: {volume}, VWAP: {vwap_value:.2f}")
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('📊 数据可视化', style={'color': '#2ecc71'}),
            html.P('使用Matplotlib可视化交易数据：'),
            html.Pre('''
import matplotlib.pyplot as plt
import pandas as pd
from pplustrader.data import BinanceDataFeed

# 获取数据
feed = BinanceDataFeed(symbol="BTC/USDT", interval="1d")
data = feed.fetch_ohlcv(limit=30)

# 转换为DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# 创建图表
fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})

# 价格图表
axes[0].plot(df['timestamp'], df['close'], label='收盘价', color='blue', linewidth=2)
axes[0].fill_between(df['timestamp'], df['low'], df['high'], alpha=0.3, color='gray')
axes[0].set_title('BTC/USDT 价格走势', fontsize=14)
axes[0].set_ylabel('价格 (USDT)', fontsize=12)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 成交量图表
axes[1].bar(df['timestamp'], df['volume'], color='green', alpha=0.7)
axes[1].set_title('成交量', fontsize=14)
axes[1].set_ylabel('成交量', fontsize=12)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ]),
    ], style={
        'background': 'white',
        'padding': '30px',
        'border-radius': '10px',
        'border': '1px solid #e9ecef'
    }),
])

# 系统配置标签页内容
config_tab = html.Div([
    html.Div([
        html.H2('⚙️ 系统配置', style={'color': '#2c3e50', 'margin-bottom': '20px'}),
        
        html.Div([
            html.H3('🔧 配置文件', style={'color': '#e74c3c'}),
            html.P('PlusPlusTrader使用JSON格式的配置文件，位于项目根目录的config.json：'),
            html.Pre('''
{
  "general": {
    "name": "PlusPlusTrader",
    "version": "1.0.0",
    "log_level": "INFO",
    "data_dir": "./data"
  },
  
  "exchanges": {
    "binance": {
      "enabled": true,
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET",
      "testnet": false
    },
    "okx": {
      "enabled": true,
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET",
      "passphrase": "YOUR_PASSPHRASE"
    }
  },
  
  "data_feeds": {
    "default_interval": "1h",
    "cache_enabled": true,
    "cache_ttl": 3600,
    "real_time_enabled": true
  },
  
  "indicators": {
    "default_periods": {
      "sma": [20, 50, 200],
      "ema": [12, 26],
      "rsi": 14,
      "macd": [12, 26, 9]
    },
    "custom_indicators_enabled": true
  },
  
  "backtest": {
    "initial_capital": 10000,
    "commission_rate": 0.001,
    "slippage": 0.0005,
    "default_data_source": "data/btc_usdt_1h.csv"
  },
  
  "web_interface": {
    "host": "127.0.0.1",
    "port": 8050,
    "debug": true,
    "auto_refresh": true,
    "refresh_interval": 5000
  }
}
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('🔐 API密钥配置', style={'color': '#e74c3c'}),
            html.P('配置交易所API密钥：'),
            
            html.Div([
                html.H4('币安 (Binance)'),
                html.P('1. 登录币安官网，进入API管理页面'),
                html.P('2. 创建新的API密钥，选择"系统交易"权限'),
                html.P('3. 复制API Key和Secret Key'),
                html.Pre('''
# 在config.json中配置
"binance": {
  "enabled": true,
  "api_key": "your_binance_api_key",
  "api_secret": "your_binance_api_secret",
  "testnet": false  # 设为true使用测试网络
}
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
            ], style={'margin-bottom': '20px'}),
            
            html.Div([
                html.H4('欧易 (OKX)'),
                html.P('1. 登录OKX官网，进入API管理页面'),
                html.P('2. 创建新的API密钥，选择"交易"权限'),
                html.P('3. 设置Passphrase并保存'),
                html.Pre('''
# 在config.json中配置
"okx": {
  "enabled": true,
  "api_key": "your_okx_api_key",
  "api_secret": "your_okx_api_secret",
  "passphrase": "your_okx_passphrase"
}
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
            ]),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('📁 数据目录结构', style={'color': '#e74c3c'}),
            html.P('系统数据目录结构：'),
            html.Pre('''
data/
├── raw/                    # 原始数据
│   ├── binance/           # 币安数据
│   │   ├── btc_usdt_1m.csv
│   │   ├── btc_usdt_1h.csv
│   │   └── eth_usdt_1d.csv
│   └── okx/               # 欧易数据
│       └── btc_usdt_1h.csv
├── processed/             # 处理后的数据
│   ├── indicators/        # 技术指标数据
│   └── features/          # 特征数据
├── backtest/              # 回测结果
│   ├── results_20240322.json
│   └── performance_metrics.csv
└── logs/                  # 日志文件
    ├── app.log
    └── error.log
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('🔧 环境变量配置', style={'color': '#e74c3c'}),
            html.P('通过环境变量配置系统：'),
            html.Pre('''
# 在.bashrc或.zshrc中添加
export PPTRADER_API_KEY_BINANCE="your_binance_api_key"
export PPTRADER_API_SECRET_BINANCE="your_binance_api_secret"
export PPTRADER_API_KEY_OKX="your_okx_api_key"
export PPTRADER_API_SECRET_OKX="your_okx_api_secret"
export PPTRADER_PASSPHRASE_OKX="your_okx_passphrase"
export PPTRADER_LOG_LEVEL="INFO"
export PPTRADER_DATA_DIR="./data"
export PPTRADER_WEB_HOST="127.0.0.1"
export PPTRADER_WEB_PORT="8050"

# 然后重新加载配置
source ~/.bashrc
''', style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px', 'overflow': 'auto'}),
        ], style={'margin-bottom': '30px'}),
        
        html.Div([
            html.H3('⚡ 性能优化', style={'color': '#e74c3c'}),
            html.P('优化系统性能的配置选项：'),
            html.Table([
                html.Thead(html.Tr([
                    html.Th('配置项', style={'padding': '10px', 'background': '#e74c3c', 'color': 'white'}),
                    html.Th('默认值', style={'padding': '10px', 'background': '#e74c3c', 'color': 'white'}),
                    html.Th('推荐值', style={'padding': '10px', 'background': '#e74c3c', 'color': 'white'}),
                    html.Th('说明', style={'padding': '10px', 'background': '#e74c3c', 'color': 'white'}),
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td('data_cache_size', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('1000', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('5000', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('数据缓存大小，增大可减少IO操作', style={'padding': '10px', 'border': '1px solid #ddd'}),
                    ]),
                    html.Tr([
                        html.Td('max_workers', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('4', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('CPU核心数', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('并行工作线程数', style={'padding': '10px', 'border': '1px solid #ddd'}),
                    ]),
                    html.Tr([
                        html.Td('websocket_reconnect_delay', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('5', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('3', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('WebSocket重连延迟(秒)', style={'padding': '10px', 'border': '1px solid #ddd'}),
                    ]),
                    html.Tr([
                        html.Td('indicator_cache_enabled', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('true', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('true', style={'padding': '10px', 'border': '1px solid #ddd'}),
                        html.Td('启用技术指标缓存', style={'padding': '10px', 'border': '1px solid #ddd'}),
                    ]),
                ])
            ], style={'width': '100%', 'border-collapse': 'collapse', 'margin-bottom': '20px'}),
        ]),
    ], style={
        'background': 'white',
        'padding': '30px',
        'border-radius': '10px',
        'border': '1px solid #e9ecef'
    }),
])

# 标签页切换回调
@app.callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'dashboard':
        return dashboard_tab
    elif tab == 'guide':
        return guide_tab
    elif tab == 'examples':
        return examples_tab
    elif tab == 'config':
        return config_tab
    return dashboard_tab

# 全局变量用于数据存储
data_store = {
    'current_data': None,
    'feed_running': False,
    'feed_thread': None,
    'last_update': None
}

# 回调函数
@app.callback(
    [Output('price-chart', 'figure'),
     Output('indicator-chart', 'figure'),
     Output('data-table', 'children'),
     Output('system-status', 'children'),
     Output('feed-status', 'children')],
    [Input('chart-updater', 'n_intervals'),
     Input('start-feed', 'n_clicks'),
     Input('stop-feed', 'n_clicks')],
    [State('symbol-selector', 'value'),
     State('interval-selector', 'value'),
     State('datasource-selector', 'value')]
)
def update_display(n_intervals, start_clicks, stop_clicks, symbol, interval, datasource):
    """更新所有显示组件"""
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # 处理开始/停止按钮
    if triggered_id == 'start-feed' and start_clicks > 0:
        if not data_store['feed_running']:
            data_store['feed_running'] = True
            data_store['last_update'] = datetime.now()
            # 在实际应用中，这里会启动真实的数据流线程
            return update_charts(symbol, interval, datasource) + (
                html.Span('🟢 数据流已启动', style={'color': 'green', 'font-weight': 'bold'}),
            )
    
    elif triggered_id == 'stop-feed' and stop_clicks > 0:
        data_store['feed_running'] = False
        return update_charts(symbol, interval, datasource) + (
            html.Span('🔴 数据流已停止', style={'color': 'red', 'font-weight': 'bold'}),
        )
    
    # 正常更新图表
    return update_charts(symbol, interval, datasource) + (
        html.Span('🟡 点击"启动数据流"开始', style={'color': 'orange'}),
    )

def update_charts(symbol, interval, datasource):
    """更新图表和数据表格"""
    # 获取数据
    if datasource == 'mock' or not HAS_TRADER:
        df = generate_mock_data(symbol, 100)
    else:
        # 实际从交易所获取数据
        try:
            if datasource == 'binance':
                feed = BinanceDataFeed(symbol=symbol, interval=interval)
            else:  # okx
                feed = OKXDataFeed(symbol=symbol, interval=interval)
            
            # 获取数据（这里简化处理，实际应用中需要处理实时数据流）
            ohlcv = feed.fetch_ohlcv(limit=100)
            if ohlcv:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            else:
                df = generate_mock_data(symbol, 100)
        except Exception as e:
            print(f"获取数据失败: {e}")
            df = generate_mock_data(symbol, 100)
    
    data_store['current_data'] = df
    
    # 更新价格图表
    price_fig = go.Figure(data=[
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K线'
        )
    ])
    
    price_fig.update_layout(
        title=f'{symbol} 价格图表 - {interval}',
        xaxis_title='时间',
        yaxis_title='价格 (USDT)',
        template='plotly_white',
        height=350
    )
    
    # 更新技术指标图表（简单移动平均线）
    if len(df) > 20:
        df['SMA20'] = df['close'].rolling(window=20).mean()
        df['SMA50'] = df['close'].rolling(window=50).mean()
        
        indicator_fig = go.Figure(data=[
            go.Scatter(x=df['timestamp'], y=df['close'], name='收盘价', line=dict(color='blue')),
            go.Scatter(x=df['timestamp'], y=df['SMA20'], name='SMA20', line=dict(color='orange', dash='dash')),
            go.Scatter(x=df['timestamp'], y=df['SMA50'], name='SMA50', line=dict(color='red', dash='dot')),
        ])
    else:
        indicator_fig = go.Figure(data=[
            go.Scatter(x=df['timestamp'], y=df['close'], name='收盘价', line=dict(color='blue')),
        ])
    
    indicator_fig.update_layout(
        title='技术指标',
        xaxis_title='时间',
        yaxis_title='价格',
        template='plotly_white',
        height=250
    )
    
    # 创建数据表格
    latest_data = df.tail(5).copy()
    latest_data['timestamp'] = latest_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    table = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in latest_data.columns])),
        html.Tbody([
            html.Tr([html.Td(latest_data.iloc[i][col]) for col in latest_data.columns])
            for i in range(len(latest_data))
        ])
    ], className='table table-striped', style={'width': '100%'})
    
    # 更新系统状态
    status_time = datetime.now().strftime('%H:%M:%S')
    status_items = [
        html.P(f'🔌 数据连接: {"🟢 已连接" if data_store["feed_running"] else "🔴 未连接"}'),
        html.P(f'📊 数据点: {len(df)}'),
        html.P(f'⏱️ 最后更新: {status_time}'),
        html.P(f'🎯 当前交易对: {symbol}'),
        html.P(f'🦞 pplustrader: {"✅ 已加载" if HAS_TRADER else "❌ 未加载"}'),
    ]
    
    return price_fig, indicator_fig, table, status_items

# 添加CSS样式
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                background-color: #f5f7fa;
                margin: 0;
                padding: 20px;
            }
            .header {
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .badge {
                display: inline-block;
                padding: 0.25em 0.4em;
                font-size: 75%;
                font-weight: 700;
                line-height: 1;
                text-align: center;
                white-space: nowrap;
                vertical-align: baseline;
                border-radius: 0.25rem;
            }
            .badge-primary {
                color: #fff;
                background-color: #007bff;
            }
            .badge-secondary {
                color: #fff;
                background-color: #6c757d;
            }
            .badge-success {
                color: #fff;
                background-color: #28a745;
            }
            .ml-2 {
                margin-left: 0.5rem;
            }
            .table {
                width: 100%;
                margin-bottom: 1rem;
                color: #212529;
                border-collapse: collapse;
            }
            .table-striped tbody tr:nth-of-type(odd) {
                background-color: rgba(0, 0, 0, 0.05);
            }
            .table th,
            .table td {
                padding: 0.75rem;
                vertical-align: top;
                border-top: 1px solid #dee2e6;
            }
            .btn {
                display: inline-block;
                font-weight: 400;
                color: #212529;
                text-align: center;
                vertical-align: middle;
                cursor: pointer;
                user-select: none;
                background-color: transparent;
                border: 1px solid transparent;
                padding: 0.375rem 0.75rem;
                font-size: 1rem;
                line-height: 1.5;
                border-radius: 0.25rem;
                transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out;
            }
            .btn-success {
                color: #fff;
                background-color: #28a745;
                border-color: #28a745;
            }
            .btn-danger {
                color: #fff;
                background-color: #dc3545;
                border-color: #dc3545;
            }
            .btn:hover {
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    print("=" * 60)
    print("PlusPlusTrader Web可视化界面")
    print("=" * 60)
    print(f"📦 pplustrader模块: {'✅ 可用' if HAS_TRADER else '❌ 不可用'}")
    print("🌐 启动服务器...")
    print("👉 请访问: http://127.0.0.1:8050")
    print("=" * 60)
    
    app.run(
        debug=True,
        host='127.0.0.1',
        port=8050,
        dev_tools_ui=True,
        dev_tools_hot_reload=True
    )