#!/usr/bin/env python3
"""
简化的Web界面 - 不依赖外部包
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleWebHandler(BaseHTTPRequestHandler):
    """简单的HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = self.generate_html()
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/charts':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            charts_html = self.generate_charts_html()
            self.wfile.write(charts_html.encode('utf-8'))
            
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = self.generate_mock_data()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            
        elif self.path == '/api/chart-data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            chart_data = self.generate_chart_data()
            self.wfile.write(json.dumps(chart_data).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<h1>404 Not Found</h1>')
    
    def generate_html(self):
        """生成主页HTML"""
        return f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦞 PlusPlusTrader 量化交易系统</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .tab {{
            flex: 1;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 1em;
            transition: all 0.3s;
        }}
        
        .tab:hover {{
            background: #e9ecef;
        }}
        
        .tab.active {{
            background: white;
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }}
        
        .content {{
            padding: 40px;
            min-height: 400px;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .feature-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .feature-card:hover {{
            transform: translateY(-5px);
        }}
        
        .feature-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .code-block {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
        }}
        
        .status-bar {{
            background: #e9ecef;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .status-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .status-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #28a745;
        }}
        
        .btn {{
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #5a67d8;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .metric-label {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦞 PlusPlusTrader 量化交易系统</h1>
            <p>高性能C++核心 + 完整Python生态 · 专为A股市场设计</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('dashboard')">📊 仪表盘</button>
            <button class="tab" onclick="switchTab('guide')">📚 使用指南</button>
            <button class="tab" onclick="switchTab('examples')">💡 示例代码</button>
            <button class="tab" onclick="switchTab('config')">⚙️ 系统配置</button>
        </div>
        
        <div class="content">
            <!-- 仪表盘 -->
            <div id="dashboard" class="tab-content active">
                <h2>📊 实时监控仪表盘</h2>
                <div class="feature-grid">
                    <div class="metric-card">
                        <div class="metric-label">系统状态</div>
                        <div class="metric-value">运行中</div>
                        <div class="metric-label">最后更新: {datetime.now().strftime("%H:%M:%S")}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">处理延迟</div>
                        <div class="metric-value">≤100μs</div>
                        <div class="metric-label">C++高性能引擎</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Python版本</div>
                        <div class="metric-value">3.8+</div>
                        <div class="metric-label">完整生态集成</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">数据源</div>
                        <div class="metric-value">A股市场</div>
                        <div class="metric-label">T+1规则支持</div>
                    </div>
                </div>
                
                <h3>📈 实时数据</h3>
                <div id="realtime-data">
                    <p>加载中...</p>
                </div>
            </div>
            
            <!-- 使用指南 -->
            <div id="guide" class="tab-content">
                <h2>📚 PlusPlusTrader 完整功能指南</h2>
                <p><strong>PlusPlusTrader</strong> 是一个高性能的量化交易系统，结合了C++核心引擎（≤100μs延迟）和完整的Python生态系统，专为A股市场设计，支持高频交易、多策略回测、实时监控和自定义指标开发。</p>
                
                <h3>🚀 核心功能模块</h3>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>⚡ 高性能交易引擎</h3>
                        <p>C++核心引擎，延迟≤100μs，支持高频交易场景</p>
                    </div>
                    <div class="feature-card">
                        <h3>🐍 Python生态集成</h3>
                        <p>完整pybind11绑定，支持Python自定义指标开发</p>
                    </div>
                    <div class="feature-card">
                        <h3>🇨🇳 A股交易支持</h3>
                        <p>完整支持T+1规则、涨跌停机制、费率计算</p>
                    </div>
                    <div class="feature-card">
                        <h3>📊 先进回测系统</h3>
                        <p>多策略并行回测、详细性能统计、风险管理系统</p>
                    </div>
                </div>
                
                <h3>🛠️ 快速开始</h3>
                <div class="code-block">
# 克隆项目
git clone https://github.com/WangBreeze/PlusPlusTrader.git
cd PlusPlusTrader

# 一键安装（Linux/macOS）
chmod +x install.sh
./install.sh

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或 venv/Scripts/activate  # Windows

# 验证安装
python -c "import pplustrader as ppt; print('版本:', ppt.__version__)"
                </div>
                
                <h3>📥 历史数据下载</h3>
                <p><strong>数据下载脚本位置</strong>: <code>scripts/download_a_shares.py</code></p>
                
                <h4>📊 数据目录结构</h4>
                <div class="code-block">
PlusPlusTrader/data/
├── raw/          # 原始数据
│   └── stock/    # 股票数据
│       ├── 000001.SZ_SZSE_D.csv  # 深交所日线数据
│       ├── 600000.SH_SSE_D.csv   # 上交所日线数据
│       └── ...
└── processed/    # 处理后数据
                </div>
                
                <h3>💡 Python自定义指标示例</h3>
                <div class="code-block">
import pplustrader as ppt

# 创建自定义指标
class MyCustomIndicator(ppt.PythonIndicator):
    def __init__(self, period=20):
        super().__init__()
        self.period = period
        self.values = []
    
    def update(self, price):
        self.values.append(price)
        if len(self.values) > self.period:
            self.values.pop(0)
        
        if len(self.values) == self.period:
            return sum(self.values) / self.period
        return None

# 使用指标
indicator = MyCustomIndicator(period=10)
signal = indicator.update(100.0)
                </div>
            </div>
            
            <!-- 示例代码 -->
            <div id="examples" class="tab-content">
                <h2>💡 实用代码示例</h2>
                
                <h3>📈 简单移动平均线策略</h3>
                <div class="code-block">
import pplustrader as ppt

# 创建策略
class MovingAverageStrategy(ppt.PythonStrategy):
    def __init__(self):
        self.short_ma = ppt.SimpleMovingAverage(5)
        self.long_ma = ppt.SimpleMovingAverage(20)
    
    def on_tick(self, tick):
        short_val = self.short_ma.update(tick.price)
        long_val = self.long_ma.update(tick.price)
        
        if short_val and long_val:
            if short_val > long_val:
                return ppt.OrderSide.BUY
            elif short_val < long_val:
                return ppt.OrderSide.SELL
        return None

# 运行回测
strategy = MovingAverageStrategy()
engine = ppt.BacktestEngine()
results = engine.run(strategy, data)
                </div>
                
                <h3>📊 数据下载示例</h3>
                <div class="code-block">
# 下载A股历史数据
from scripts.download_a_shares import download_data

# 下载日线数据
download_data(
    symbols=['000001.SZ', '600000.SH'],
    start_date='2020-01-01',
    end_date='2024-01-01',
    frequency='D',
    source='akshare'
)
                </div>
                
                <h3>🎯 技术指标示例</h3>
                <div class="code-block">
import pplustrader as ppt

# 创建RSI指标
rsi = ppt.RelativeStrengthIndex(period=14)

# 更新数据
for price in price_data:
    rsi_value = rsi.update(price)
    if rsi_value:
        if rsi_value > 70:
            print("超买信号")
        elif rsi_value < 30:
            print("超卖信号")
                </div>
            </div>
            
            <!-- 系统配置 -->
            <div id="config" class="tab-content">
                <h2>⚙️ 系统配置</h2>
                
                <h3>📁 配置文件位置</h3>
                <div class="code-block">
PlusPlusTrader/config/
├── config.json          # 主配置文件
├── strategies/          # 策略配置
├── data_sources/        # 数据源配置
└── risk_management/     # 风险管理配置
                </div>
                
                <h3>🔧 主配置文件示例</h3>
                <div class="code-block">
{
    "trading": {
        "initial_capital": 100000,
        "commission_rate": 0.0003,
        "slippage": 0.0001
    },
    "data": {
        "source": "akshare",
        "update_frequency": "daily",
        "cache_enabled": true
    },
    "risk": {
        "max_position": 0.8,
        "stop_loss": 0.1,
        "take_profit": 0.2
    }
}
                </div>
                
                <h3>🚀 启动命令</h3>
                <div class="code-block">
# 启动Web界面
cd web
python3 simple_app.py

# 访问地址
http://127.0.0.1:8050

# K线图页面
http://127.0.0.1:8050/charts
                </div>
            </div>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-dot"></div>
                <span>PlusPlusTrader v1.0.0</span>
            </div>
            <div class="status-item">
                <span>系统运行正常 | 访问量: {random.randint(100, 999)}</span>
            </div>
        </div>
    </div>
    
    <script>
        function switchTab(tabName) {{
            // 隐藏所有标签内容
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // 移除所有标签的active类
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的标签内容
            document.getElementById(tabName).classList.add('active');
            
            // 添加active类到选中的标签
            event.target.classList.add('active');
            
            // 如果是仪表盘，加载实时数据
            if (tabName === 'dashboard') {{
                loadRealtimeData();
            }}
        }}
        
        function loadRealtimeData() {{
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('realtime-data').innerHTML = `
                        <div class="feature-grid">
                            <div class="feature-card">
                                <h3>市场状态</h3>
                                <p>${{data.market_status}}</p>
                            </div>
                            <div class="feature-card">
                                <h3>股票数量</h3>
                                <p>${{data.stock_count}}</p>
                            </div>
                            <div class="feature-card">
                                <h3>更新时间</h3>
                                <p>${{data.update_time}}</p>
                            </div>
                            <div class="feature-card">
                                <h3>系统负载</h3>
                                <p>${{data.system_load}}</p>
                            </div>
                        </div>
                    `;
                }})
                .catch(error => {{
                    document.getElementById('realtime-data').innerHTML = '<p>数据加载失败</p>';
                }});
        }}
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {{
            loadRealtimeData();
        }});
    </script>
</body>
</html>
'''
    
    def generate_charts_html(self):
        """生成K线图页面HTML"""
        return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📈 PlusPlusTrader K线图 - 专业金融图表</title>
    <script src="https://unpkg.com/lightweight-charts@5.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
        }}
        
        .header {{
            background: #16213e;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 1.5em;
        }}
        
        .controls {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .control-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        select, button {{
            background: #0f3460;
            color: white;
            border: 1px solid #533483;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
        }}
        
        button:hover {{
            background: #533483;
        }}
        
        .main-content {{
            display: flex;
            height: calc(100vh - 80px);
        }}
        
        .chart-container {{
            flex: 1;
            position: relative;
        }}
        
        #chart {{
            width: 100%;
            height: 100%;
        }}
        
        .sidebar {{
            width: 300px;
            background: #16213e;
            padding: 20px;
            overflow-y: auto;
        }}
        
        .indicator-section {{
            margin-bottom: 25px;
        }}
        
        .indicator-section h3 {{
            color: #e94560;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .indicator-item {{
            background: #0f3460;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .indicator-value {{
            font-weight: bold;
            color: #4ecca3;
        }}
        
        .legend {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(22, 33, 62, 0.9);
            padding: 10px;
            border-radius: 5px;
            font-size: 0.9em;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        
        .legend-color {{
            width: 12px;
            height: 12px;
            margin-right: 8px;
            border-radius: 2px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 PlusPlusTrader 专业K线图</h1>
        <div class="controls">
            <div class="control-group">
                <label>股票:</label>
                <select id="stockSelect">
                    <option value="000001.SZ">平安银行 (000001.SZ)</option>
                    <option value="600000.SH">浦发银行 (600000.SH)</option>
                    <option value="000001.SZ">深证成指 (000001.SZ)</option>
                </select>
            </div>
            <div class="control-group">
                <label>周期:</label>
                <select id="periodSelect">
                    <option value="D">日线</option>
                    <option value="W">周线</option>
                    <option value="M">月线</option>
                </select>
            </div>
            <button onclick="loadChartData()">加载数据</button>
            <button onclick="toggleIndicators()">切换指标</button>
        </div>
    </div>
    
    <div class="main-content">
        <div class="chart-container">
            <div id="chart"></div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #2962FF;"></div>
                    <span>收盘价</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #FF6B00;"></div>
                    <span>移动平均线</span>
                </div>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="indicator-section">
                <h3>📊 技术指标</h3>
                <div class="indicator-item">
                    <span>MA(5)</span>
                    <span class="indicator-value" id="ma5">--</span>
                </div>
                <div class="indicator-item">
                    <span>MA(20)</span>
                    <span class="indicator-value" id="ma20">--</span>
                </div>
                <div class="indicator-item">
                    <span>MA(60)</span>
                    <span class="indicator-value" id="ma60">--</span>
                </div>
            </div>
            
            <div class="indicator-section">
                <h3>📈 RSI指标</h3>
                <div class="indicator-item">
                    <span>RSI(14)</span>
                    <span class="indicator-value" id="rsi">--</span>
                </div>
            </div>
            
            <div class="indicator-section">
                <h3>📉 MACD指标</h3>
                <div class="indicator-item">
                    <span>DIF</span>
                    <span class="indicator-value" id="dif">--</span>
                </div>
                <div class="indicator-item">
                    <span>DEA</span>
                    <span class="indicator-value" id="dea">--</span>
                </div>
                <div class="indicator-item">
                    <span>MACD</span>
                    <span class="indicator-value" id="macd">--</span>
                </div>
            </div>
            
            <div class="indicator-section">
                <h3>💡 交易信号</h3>
                <div class="indicator-item">
                    <span>当前信号</span>
                    <span class="indicator-value" id="signal">--</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let chart;
        let candlestickSeries;
        let ma5Series, ma20Series, ma60Series;
        
        function initChart() {{
            const chartElement = document.getElementById('chart');
            
            chart = LightweightCharts.createChart(chartElement, {{
                width: chartElement.clientWidth,
                height: chartElement.clientHeight,
                layout: {{
                    background: {{ color: '#1a1a2e' }},
                    textColor: '#d1d4dc',
                }},
                grid: {{
                    vertLines: {{ color: '#2B2B43' }},
                    horzLines: {{ color: '#2B2B43' }},
                }},
                crosshair: {{
                    mode: LightweightCharts.CrosshairMode.Normal,
                }},
                rightPriceScale: {{
                    borderColor: '#2B2B43',
                }},
                timeScale: {{
                    borderColor: '#2B2B43',
                    timeVisible: true,
                }},
            }});
            
            candlestickSeries = chart.addCandlestickSeries({{
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderDownColor: '#ef5350',
                borderUpColor: '#26a69a',
                wickDownColor: '#ef5350',
                wickUpColor: '#26a69a',
            }});
            
            ma5Series = chart.addLineSeries({{
                color: '#2196F3',
                lineWidth: 2,
                title: 'MA5'
            }});
            
            ma20Series = chart.addLineSeries({{
                color: '#FF9800',
                lineWidth: 2,
                title: 'MA20'
            }});
            
            ma60Series = chart.addLineSeries({{
                color: '#4CAF50',
                lineWidth: 2,
                title: 'MA60'
            }});
            
            // 响应式调整
            window.addEventListener('resize', () => {{
                chart.applyOptions({{
                    width: chartElement.clientWidth,
                    height: chartElement.clientHeight
                }});
            }});
        }}
        
        function loadChartData() {{
            fetch('/api/chart-data')
                .then(response => response.json())
                .then(data => {{
                    // 更新K线数据
                    candlestickSeries.setData(data.candles);
                    
                    // 更新均线数据
                    ma5Series.setData(data.ma5);
                    ma20Series.setData(data.ma20);
                    ma60Series.setData(data.ma60);
                    
                    // 更新指标数值
                    if (data.indicators) {{
                        document.getElementById('ma5').textContent = data.indicators.ma5.toFixed(2);
                        document.getElementById('ma20').textContent = data.indicators.ma20.toFixed(2);
                        document.getElementById('ma60').textContent = data.indicators.ma60.toFixed(2);
                        document.getElementById('rsi').textContent = data.indicators.rsi.toFixed(2);
                        document.getElementById('dif').textContent = data.indicators.dif.toFixed(2);
                        document.getElementById('dea').textContent = data.indicators.dea.toFixed(2);
                        document.getElementById('macd').textContent = data.indicators.macd.toFixed(2);
                        document.getElementById('signal').textContent = data.indicators.signal;
                    }}
                }})
                .catch(error => {{
                    console.error('加载数据失败:', error);
                }});
        }}
        
        function toggleIndicators() {{
            // 切换指标显示/隐藏
            const isVisible = ma5Series._options.visible !== false;
            ma5Series.applyOptions({{ visible: !isVisible }});
            ma20Series.applyOptions({{ visible: !isVisible }});
            ma60Series.applyOptions({{ visible: !isVisible }});
        }}
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {{
            initChart();
            loadChartData();
            
            // 定时刷新数据
            setInterval(loadChartData, 5000);
        }});
    </script>
</body>
</html>
'''
    
    def generate_mock_data(self):
        """生成模拟数据"""
        return {{
            "market_status": "正常交易",
            "stock_count": 5000,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_load": f"{random.randint(20, 60)}%"
        }}
    
    def generate_chart_data(self):
        """生成图表数据"""
        # 生成模拟K线数据
        base_price = 100
        candles = []
        ma5_data = []
        ma20_data = []
        ma60_data = []
        
        for i in range(100):
            date = (datetime.now() - timedelta(days=100-i)).strftime("%Y-%m-%d")
            open_price = base_price + random.uniform(-2, 2)
            close_price = open_price + random.uniform(-1, 1)
            high = max(open_price, close_price) + random.uniform(0, 1)
            low = min(open_price, close_price) - random.uniform(0, 1)
            
            candles.append({{
                "time": date,
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close_price, 2)
            }})
            
            base_price = close_price
            
            # 计算均线
            if i >= 4:
                ma5 = sum(c["close"] for c in candles[-5:]) / 5
                ma5_data.append({{"time": date, "value": round(ma5, 2)}})
            
            if i >= 19:
                ma20 = sum(c["close"] for c in candles[-20:]) / 20
                ma20_data.append({{"time": date, "value": round(ma20, 2)}})
            
            if i >= 59:
                ma60 = sum(c["close"] for c in candles[-60:]) / 60
                ma60_data.append({{"time": date, "value": round(ma60, 2)}})
        
        return {{
            "candles": candles,
            "ma5": ma5_data,
            "ma20": ma20_data,
            "ma60": ma60_data,
            "indicators": {{
                "ma5": ma5_data[-1]["value"] if ma5_data else 0,
                "ma20": ma20_data[-1]["value"] if ma20_data else 0,
                "ma60": ma60_data[-1]["value"] if ma60_data else 0,
                "rsi": random.uniform(30, 70),
                "dif": random.uniform(-1, 1),
                "dea": random.uniform(-1, 1),
                "macd": random.uniform(-0.5, 0.5),
                "signal": random.choice(["买入", "卖出", "持有", "观望"])
            }}
        }}
    
    def log_message(self, format, *args):
        """重写日志方法，减少输出"""
        pass

def main():
    print("=" * 60)
    print("🦞 PlusPlusTrader 简化Web界面")
    print("=" * 60)
    print("🌐 服务器启动在: http://127.0.0.1:8050")
    print("📱 功能特性:")
    print("  • 📊 仪表盘 - 实时数据监控")
    print("  • 📚 使用指南 - 完整文档")
    print("  • 💡 示例代码 - 实用代码片段")
    print("  • ⚙️ 系统配置 - 配置说明")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        server_address = ('0.0.0.0', 8050)
        httpd = HTTPServer(server_address, SimpleWebHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器错误: {e}")

if __name__ == '__main__':
    main()
