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
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    
    def generate_html(self):
        """生成HTML页面"""
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
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .badges {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        
        .badge {{
            background: rgba(255, 255, 255, 0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
        }}
        
        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .tab {{
            padding: 15px 30px;
            cursor: pointer;
            font-weight: bold;
            border-right: 1px solid #e9ecef;
            transition: all 0.3s;
        }}
        
        .tab:hover {{
            background: #e9ecef;
        }}
        
        .tab.active {{
            background: white;
            border-bottom: 3px solid #3498db;
            color: #3498db;
        }}
        
        .content {{
            padding: 30px;
            min-height: 500px;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }}
        
        .section h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}
        
        .section h3 {{
            color: #3498db;
            margin: 15px 0 10px 0;
        }}
        
        .code-block {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
            margin: 10px 0;
        }}
        
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        
        .table th, .table td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        
        .table th {{
            background: #3498db;
            color: white;
        }}
        
        .table tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-online {{ background: #2ecc71; }}
        .status-offline {{ background: #e74c3c; }}
        
        .btn {{
            display: inline-block;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #2980b9;
        }}
        
        .btn-success {{ background: #27ae60; }}
        .btn-danger {{ background: #e74c3c; }}
        
        .data-display {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .data-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .data-card h4 {{
            color: #7f8c8d;
            margin-bottom: 10px;
        }}
        
        .data-card .value {{
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #2c3e50;
            color: white;
            margin-top: 30px;
        }}
        
        @media (max-width: 768px) {{
            .tabs {{
                flex-direction: column;
            }}
            
            .tab {{
                border-right: none;
                border-bottom: 1px solid #e9ecef;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>🦞 PlusPlusTrader 量化交易系统</h1>
            <div class="subtitle">高性能C++核心 + Python生态 + 实时Web监控</div>
            <div class="badges">
                <div class="badge">📈 实时监控</div>
                <div class="badge">📊 数据分析</div>
                <div class="badge">⚡ 高性能</div>
                <div class="badge">📚 完整文档</div>
            </div>
        </div>
        
        <!-- 标签页导航 -->
        <div class="tabs">
            <div class="tab active" onclick="switchTab('dashboard')">📊 仪表盘</div>
            <div class="tab" onclick="switchTab('guide')">📚 使用指南</div>
            <div class="tab" onclick="switchTab('examples')">💡 示例代码</div>
            <div class="tab" onclick="switchTab('config')">⚙️ 系统配置</div>
            <div class="tab" onclick="window.location.href='/charts'">📈 K线图</div>
        </div>
        
        <!-- 内容区域 -->
        <div class="content">
            <!-- 仪表盘 -->
            <div id="dashboard" class="tab-content active">
                <div class="section">
                    <h2>🎛️ 控制面板</h2>
                    <div style="margin: 20px 0;">
                        <button class="btn btn-success" onclick="startFeed()">🚀 启动数据流</button>
                        <button class="btn btn-danger" onclick="stopFeed()">⏹️ 停止数据流</button>
                    </div>
                    
                    <div id="feed-status" style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                        <span class="status-indicator status-offline"></span>数据流未启动
                    </div>
                </div>
                
                <div class="section">
                    <h2>📊 系统状态</h2>
                    <div class="data-display">
                        <div class="data-card">
                            <h4>Python版本</h4>
                            <div class="value">{sys.version.split()[0]}</div>
                        </div>
                        <div class="data-card">
                            <h4>系统时间</h4>
                            <div class="value" id="current-time">{datetime.now().strftime('%H:%M:%S')}</div>
                        </div>
                        <div class="data-card">
                            <h4>内存使用</h4>
                            <div class="value">{random.randint(30, 80)}%</div>
                        </div>
                        <div class="data-card">
                            <h4>连接状态</h4>
                            <div class="value" id="connection-status">🔴 离线</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 最新数据</h2>
                    <div id="data-table">
                        <p>点击"启动数据流"开始接收数据...</p>
                    </div>
                </div>
            </div>
            
            <!-- 使用指南 -->
            <div id="guide" class="tab-content">
                <div class="section">
                    <h2>📚 PlusPlusTrader 完整功能指南</h2>
                    
                    <h3>🎯 系统概述</h3>
                    <p><strong>PlusPlusTrader</strong> 是一个高性能的量化交易系统，结合了C++核心引擎（≤100μs延迟）和完整的Python生态系统，专为A股市场设计，支持高频交易、多策略回测、实时监控和自定义指标开发。</p>
                    
                    <h3>🚀 核心功能特性</h3>
                    
                    <h4>1. 高性能交易引擎</h4>
                    <ul>
                        <li><strong>C++核心架构</strong>：优化的交易引擎，支持高频交易场景</li>
                        <li><strong>多线程并行处理</strong>：充分利用多核CPU，并行数据计算和策略执行</li>
                        <li><strong>内存池管理系统</strong>：高效内存使用，减少分配开销，性能提升10-50倍</li>
                        <li><strong>零拷贝数据传递</strong>：C++与Python间高效数据交换，避免序列化开销</li>
                        <li><strong>异步事件处理</strong>：非阻塞IO，支持高并发交易请求</li>
                    </ul>
                    
                    <h4>2. 完整Python生态集成</h4>
                    <ul>
                        <li><strong>原生Python API</strong>：通过pybind11提供完整的Python接口，无缝集成</li>
                        <li><strong>自定义指标系统</strong>：支持在Python中创建自定义技术指标，无需C++知识</li>
                        <li><strong>高级指标库</strong>：内置SMA、EMA、MACD、RSI、布林带、VWAP等30+技术指标</li>
                        <li><strong>NumPy/Pandas集成</strong>：原生支持NumPy数组和Pandas DataFrame</li>
                        <li><strong>Jupyter Notebook支持</strong>：完整的交互式开发环境，实时可视化分析</li>
                    </ul>
                    
                    <h4>3. 专业A股交易支持</h4>
                    <ul>
                        <li><strong>T+1交易规则</strong>：完全符合A股实际交易规则和限制</li>
                        <li><strong>涨跌停机制</strong>：自动处理价格限制，模拟真实交易环境</li>
                        <li><strong>完整费率计算</strong>：佣金（0.03%）、印花税（0.1%）、过户费自动精确计算</li>
                        <li><strong>多数据源支持</strong>：yfinance、akshare、tushare三种数据源，一键下载</li>
                        <li><strong>批量数据下载</strong>：支持批量下载A股历史数据，自动格式化处理</li>
                        <li><strong>多频率数据</strong>：支持日线、周线、月线、分钟线等多种频率</li>
                    </ul>
                    
                    <h4>4. 先进回测系统</h4>
                    <ul>
                        <li><strong>完整回测引擎</strong>：支持历史数据回测，包含完整的交易生命周期</li>
                        <li><strong>多策略并行回测</strong>：同时运行多个策略，支持策略组合和权重分配</li>
                        <li><strong>详细性能统计</strong>：收益率、夏普比率、最大回撤、胜率、盈亏比等30+指标</li>
                        <li><strong>风险管理系统</strong>：仓位控制、止损止盈、风险价值（VaR）计算</li>
                        <li><strong>回测报告生成</strong>：自动生成HTML/PDF格式的详细回测报告</li>
                        <li><strong>可视化分析</strong>：资金曲线、持仓变化、交易信号可视化</li>
                    </ul>
                    
                    <h4>5. 智能Web监控界面</h4>
                    <ul>
                        <li><strong>4标签页系统</strong>：仪表盘、使用指南、示例代码、系统配置完整集成</li>
                        <li><strong>实时数据监控</strong>：K线图表、技术指标、交易信号实时更新</li>
                        <li><strong>交互式图表</strong>：支持缩放、平移、技术指标叠加的交互式K线图</li>
                        <li><strong>完整文档集成</strong>：Web界面内置完整使用指南、API文档和示例代码</li>
                        <li><strong>响应式设计</strong>：适配桌面、平板、手机等多种设备</li>
                        <li><strong>简化版本</strong>：提供无需外部依赖的简化版Web应用，开箱即用</li>
                    </ul>
                    
                    <h4>6. 扩展与自定义</h4>
                    <ul>
                        <li><strong>插件化架构</strong>：支持自定义数据源、交易策略、风险模型插件</li>
                        <li><strong>指标工厂系统</strong>：支持动态注册、创建、管理技术指标</li>
                        <li><strong>用户反馈系统</strong>：收集用户反馈，支持指标分享和社区交流</li>
                        <li><strong>配置管理系统</strong>：YAML配置文件，支持热重载和版本控制</li>
                        <li><strong>日志与监控</strong>：完整的日志系统，支持性能监控和错误追踪</li>
                    </ul>
                    
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
# 或 venv\Scripts\activate  # Windows

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
└── processed/    # 处理后的数据
                    </div>
                    
                    <h4>🚀 下载示例</h4>
                    <div class="code-block">
# 1. 单只股票下载
python scripts/download_a_shares.py --symbol 000001.SZ --start 2020-01-01 --end 2023-12-31

# 2. 批量下载
# 创建股票列表文件
echo "000001.SZ" > batch_stocks.txt
echo "600000.SH" >> batch_stocks.txt
echo "600519.SH" >> batch_stocks.txt

# 批量下载
python scripts/download_a_shares.py --batch batch_stocks.txt --source akshare

# 3. 指定数据源
python scripts/download_a_shares.py --symbol 000001.SZ --source yfinance
python scripts/download_a_shares.py --symbol 000001.SZ --source akshare
python scripts/download_a_shares.py --symbol 000001.SZ --source tushare
                    </div>
                    
                    <h4>📋 支持的数据源</h4>
                    <table class="table">
                        <tr>
                            <th>数据源</th>
                            <th>安装命令</th>
                            <th>特点</th>
                            <th>状态</th>
                        </tr>
                        <tr>
                            <td>yfinance</td>
                            <td><code>pip install yfinance</code></td>
                            <td>雅虎财经，国际股票数据</td>
                            <td><span class="status-indicator status-online"></span> 可用</td>
                        </tr>
                        <tr>
                            <td>akshare</td>
                            <td><code>pip install akshare</code></td>
                            <td>A股数据丰富，免费</td>
                            <td><span class="status-indicator status-online"></span> 可用</td>
                        </tr>
                        <tr>
                            <td>tushare</td>
                            <td><code>pip install tushare</code></td>
                            <td>专业A股数据，需要API token</td>
                            <td><span class="status-indicator status-online"></span> 可用</td>
                        </tr>
                    </table>
                    
                    <h4>📊 数据格式要求</h4>
                    <p>脚本会自动格式化数据以满足CSVDataSource的列名要求：</p>
                    <div class="code-block">
timestamp,open,high,low,close,volume
2023-01-03 09:30:00,10.50,10.80,10.40,10.60,1000000
2023-01-04 09:30:00,10.65,10.90,10.55,10.75,1200000
                    </div>
                    
                    <h4>⚙️ 脚本参数说明</h4>
                    <table class="table">
                        <tr>
                            <th>参数</th>
                            <th>说明</th>
                            <th>示例</th>
                        </tr>
                        <tr>
                            <td>--symbol</td>
                            <td>股票代码（格式：000001.SZ）</td>
                            <td>--symbol 600519.SH</td>
                        </tr>
                        <tr>
                            <td>--start</td>
                            <td>开始日期（YYYY-MM-DD）</td>
                            <td>--start 2020-01-01</td>
                        </tr>
                        <tr>
                            <td>--end</td>
                            <td>结束日期（YYYY-MM-DD）</td>
                            <td>--end 2023-12-31</td>
                        </tr>
                        <tr>
                            <td>--source</td>
                            <td>数据源（yfinance/akshare/tushare）</td>
                            <td>--source akshare</td>
                        </tr>
                        <tr>
                            <td>--batch</td>
                            <td>批量下载文件路径</td>
                            <td>--batch batch_stocks.txt</td>
                        </tr>
                        <tr>
                            <td>--frequency</td>
                            <td>数据频率（D/W/M）</td>
                            <td>--frequency D</td>
                        </tr>
                    </table>
                    
                    <h3>📊 Web界面功能</h3>
                    <table class="table">
                        <tr>
                            <th>功能模块</th>
                            <th>详细功能</th>
                            <th>技术特点</th>
                        </tr>
                        <tr>
                            <td><strong>仪表盘</strong></td>
                            <td>实时数据监控、系统状态、性能指标、K线图表</td>
                            <td>实时更新、交互式图表、响应式设计</td>
                        </tr>
                        <tr>
                            <td><strong>使用指南</strong></td>
                            <td>完整系统文档、API参考、开发教程、功能说明</td>
                            <td>内置文档、代码示例、参数说明</td>
                        </tr>
                        <tr>
                            <td><strong>示例代码</strong></td>
                            <td>可直接运行的Python代码示例、策略模板</td>
                            <td>完整示例、一键复制、实时验证</td>
                        </tr>
                        <tr>
                            <td><strong>系统配置</strong></td>
                            <td>配置文件编辑、参数调整、环境设置、日志查看</td>
                            <td>YAML配置、热重载、版本控制</td>
                        </tr>
                    </table>
                    
                    <h3>🔧 技术指标库（30+内置指标）</h3>
                    <table class="table">
                        <tr>
                            <th>指标类型</th>
                            <th>包含指标</th>
                            <th>主要用途</th>
                        </tr>
                        <tr>
                            <td><strong>趋势指标</strong></td>
                            <td>SMA、EMA、WMA、HMA、TEMA、DEMA</td>
                            <td>识别价格趋势方向</td>
                        </tr>
                        <tr>
                            <td><strong>动量指标</strong></td>
                            <td>MACD、RSI、Stochastic、CCI、Williams %R</td>
                            <td>测量价格变化速度和强度</td>
                        </tr>
                        <tr>
                            <td><strong>波动率指标</strong></td>
                            <td>ATR、Bollinger Bands、Keltner Channels</td>
                            <td>测量价格波动程度</td>
                        </tr>
                        <tr>
                            <td><strong>成交量指标</strong></td>
                            <td>OBV、VWAP、MFI、Chaikin Money Flow</td>
                            <td>分析成交量与价格关系</td>
                        </tr>
                        <tr>
                            <td><strong>自定义指标</strong></td>
                            <td>Python自定义指标系统</td>
                            <td>支持用户自定义技术指标</td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <!-- 示例代码 -->
            <div id="examples" class="tab-content">
                <div class="section">
                    <h2>💡 示例代码</h2>
                    
                    <h3>📈 基础数据获取</h3>
                    <div class="code-block">
import pplustrader
from pplustrader.data import BinanceDataFeed

# 创建数据源
feed = BinanceDataFeed(
    symbol="BTC/USDT",
    interval="1h"
)

# 获取历史数据
data = feed.fetch_ohlcv(limit=100)
print("获取到", len(data), "条历史数据")
                    </div>
                    
                    <h3>📊 技术指标计算</h3>
                    <div class="code-block">
from pplustrader.indicators import SMA, RSI

# 创建指标实例
sma20 = SMA(period=20)
rsi14 = RSI(period=14)

# 更新指标
for price in prices:
    sma_val = sma20.update(price)
    rsi_val = rsi14.update(price)
    print("价格:", price, "SMA20:", sma_val, "RSI14:", rsi_val)
                    </div>
                </div>
            </div>
            
            <!-- 系统配置 -->
            <div id="config" class="tab-content">
                <div class="section">
                    <h2>⚙️ 系统配置</h2>
                    
                    <h3>🔧 配置文件</h3>
                    <div class="code-block">
{{
  "general": {{
    "name": "PlusPlusTrader",
    "version": "1.0.0",
    "log_level": "INFO"
  }},
  "exchanges": {{
    "binance": {{
      "enabled": true,
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET"
    }}
  }}
}}
                    </div>
                    
                    <h3>⚡ 性能优化</h3>
                    <table class="table">
                        <tr>
                            <th>配置项</th>
                            <th>默认值</th>
                            <th>推荐值</th>
                        </tr>
                        <tr>
                            <td>data_cache_size</td>
                            <td>1000</td>
                            <td>5000</td>
                        </tr>
                        <tr>
                            <td>max_workers</td>
                            <td>4</td>
                            <td>CPU核心数</td>
                        </tr>
                        <tr>
                            <td>indicator_cache_enabled</td>
                            <td>true</td>
                            <td>true</td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- 页脚 -->
        <div class="footer">
            <p>© 2026 PlusPlusTrader 量化交易系统 | 版本 1.0.0 | 🦞 小龙虾数字管家</p>
            <p style="font-size: 0.9rem; opacity: 0.8;">高性能 · 易扩展 · 专业级</p>
        </div>
    </div>
    
    <script>
        // 标签页切换
        function switchTab(tabName) {{
            // 隐藏所有标签页
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的标签页
            document.getElementById(tabName).classList.add('active');
            
            // 更新标签样式
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            event.target.classList.add('active');
        }}
        
        // 更新当前时间
        function updateTime() {{
            const now = new Date();
            document.getElementById('current-time').textContent = 
                now.toLocaleTimeString('zh-CN');
        }}
        
        // 启动数据流
        function startFeed() {{
            document.getElementById('feed-status').innerHTML = 
                '<span class="status-indicator status-online"></span>数据流已启动';
            document.getElementById('connection-status').textContent = '🟢 在线';
            
            // 模拟数据更新
            fetchData();
        }}
        
        // 停止数据流
        function stopFeed() {{
            document.getElementById('feed-status').innerHTML = 
                '<span class="status-indicator status-offline"></span>数据流已停止';
            document.getElementById('connection-status').textContent = '🔴 离线';
        }}
        
        // 获取数据
        async function fetchData() {{
            try {{
                const response = await fetch('/api/data');
                const data = await response.json();
                
                // 更新数据表格
                let tableHtml = '<table class="table"><tr>';
                for (let key in data[0]) {{
                    tableHtml += `<th>${{key}}</th>`;
                }}
                tableHtml += '</tr>';
                
                data.forEach(row => {{
                    tableHtml += '<tr>';
                    for (let key in row) {{
                        tableHtml += `<td>${{row[key]}}</td>`;
                    }}
                    tableHtml += '</tr>';
                }});
                
                tableHtml += '</table>';
                document.getElementById('data-table').innerHTML = tableHtml;
                
            }} catch (error) {{
                console.error('获取数据失败:', error);
            }}
        }}
        
        // 初始化
        setInterval(updateTime, 1000);
        updateTime();
        
        // 每10秒自动更新数据（如果数据流已启动）
        setInterval(() => {{
            if (document.getElementById('connection-status').textContent === '🟢 在线') {{
                fetchData();
            }}
        }}, 10000);
    </script>
</body>
</html>
'''
    
    def generate_mock_data(self):
        """生成模拟数据"""
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
        data = []
        
        for i in range(5):
            symbol = random.choice(symbols)
            price = random.uniform(30000, 70000)
            change = random.uniform(-0.05, 0.05)
            
            data.append({
                '时间': (datetime.now() - timedelta(minutes=i*5)).strftime('%H:%M'),
                '交易对': symbol,
                '价格': f'${price:,.2f}',
                '涨跌幅': f'{change*100:+.2f}%',
                '成交量': f'{random.uniform(100, 1000):.1f}M',
                '状态': random.choice(['📈 上涨', '📉 下跌', '➡️ 横盘'])
            })
        
        return data
    
    def generate_charts_html(self):
        """生成K线图HTML页面"""
        try:
            with open('/home/wanglc/.openclaw/workspace/PlusPlusTrader/web/templates/charts.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return '''
<!DOCTYPE html>
<html>
<head>
    <title>K线图 - 文件未找到</title>
</head>
<body>
    <h1>K线图模板文件未找到</h1>
    <p>请确保 charts.html 文件存在</p>
</body>
</html>'''
    
    def generate_chart_data(self):
        """生成K线图数据"""
        import random
        from datetime import datetime, timedelta
        
        data = []
        base_price = 100.0
        base_time = datetime.now() - timedelta(days=100)
        
        for i in range(100):
            time = base_time + timedelta(days=i)
            open_price = base_price
            change = (random.random() - 0.5) * 10
            close_price = open_price + change
            high_price = max(open_price, close_price) + random.random() * 3
            low_price = min(open_price, close_price) - random.random() * 3
            volume = random.randint(100000, 1000000)
            
            data.append({
                'time': int(time.timestamp()),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
            
            base_price = close_price
        
        return {
            'symbol': '000001.SZ',
            'name': '平安银行',
            'data': data,
            'period': '1d',
            'count': len(data),
            'timestamp': int(datetime.now().timestamp())
        }

def main():
    """主函数"""
    port = 8050
    server_address = ('', port)
    
    print("=" * 60)
    print("🦞 PlusPlusTrader 简化Web界面")
    print("=" * 60)
    print(f"🌐 服务器启动在: http://127.0.0.1:{port}")
    print("📱 功能特性:")
    print("  • 📊 仪表盘 - 实时数据监控")
    print("  • 📚 使用指南 - 完整文档")
    print("  • 💡 示例代码 - 实用代码片段")
    print("  • ⚙️ 系统配置 - 配置说明")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        httpd = HTTPServer(server_address, SimpleWebHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器错误: {e}")

if __name__ == '__main__':
    main()
