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
                
                <h3>🎯 简单交易策略</h3>
                <div class="code-block">
from pplustrader.strategies import BaseStrategy
from pplustrader.indicators import SMA

class SimpleMAStrategy(BaseStrategy):
    """简单移动平均线策略"""
    
    def __init__(self):
        super().__init__()
        self.sma_fast = SMA(period=10)
        self.sma_slow = SMA(period=30)
        self.position = 0
        
    def on_tick(self, tick_data):
        price = tick_data['last']
        
        # 更新指标
        fast = self.sma_fast.update(price)
        slow = self.sma_slow.update(price)
        
        # 交易逻辑
        if fast > slow and self.position <= 0:
            # 金叉买入
            self.buy(price, 1)
            self.position = 1
        elif fast < slow and self.position >= 0:
            # 死叉卖出
            self.sell(price, 1)
            self.position = -1
                </div>
                
                <h3>📊 回测示例</h3>
                <div class="code-block">
from pplustrader.backtest import BacktestEngine
from pplustrader.data import CSVDataSource

# 创建数据源
data_source = CSVDataSource("data/BTC_USDT_1h.csv")

# 创建策略
strategy = SimpleMAStrategy()

# 创建回测引擎
backtest = BacktestEngine(
    data_source=data_source,
    strategy=strategy,
    initial_capital=10000
)

# 运行回测
results = backtest.run()

# 输出结果
print("总收益:", results.total_return)
print("夏普比率:", results.sharpe_ratio)
print("最大回撤:", results.max_drawdown)
                </div>
            </div>
        </div>
        
        <!-- 系统配置 -->
        <div id="config" class="tab-content">
            <div class="section">
                <h2>⚙️ 系统配置</h2>
                
                <h3>配置文件示例 (config.yaml)</h3>
                <div class="code-block">
# 交易配置
trading:
  exchange: "binance"
  api_key: "${BINANCE_API_KEY}"
  api_secret: "${BINANCE_API_SECRET}"
  testnet: true  # 使用测试网络
  
# 数据源配置
data:
  sources:
    - type: "binance"
      symbols: ["BTC/USDT", "ETH/USDT"]
      intervals: ["1h", "4h", "1d"]
    - type: "csv"
      directory: "./data"
  
# 策略配置
strategies:
  - name: "ma_cross"
    class: "SimpleMAStrategy"
    params:
      fast_period: 10
      slow_period: 30
  
# 风险控制
risk:
  max_position_size: 0.1  # 最大仓位10%
  stop_loss: 0.05  # 止损5%
  take_profit: 0.1  # 止盈10%
                </div>
                
                <h3>环境变量</h3>
                <div class="code-block">
# 设置环境变量
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"
export PYTHONPATH="/path/to/PlusPlusTrader/python:$PYTHONPATH"

# 运行程序
python your_strategy.py
                </div>
                
                <h3>Docker部署</h3>
                <div class="code-block">
# Dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目代码
COPY . /app
WORKDIR /app

# 编译C++核心
RUN mkdir build && cd build \
    && cmake .. -DCMAKE_BUILD_TYPE=Release \
    && make -j4

# 安装Python依赖
RUN pip install -e ./python

# 运行应用
CMD ["python", "web/simple_app.py"]
                </div>
            </div>
        </div>
        
        <footer>
            <p>🦞 PlusPlusTrader 量化交易系统 | 版本 1.0.0 | 最后更新: ''' + datetime.now().strftime('%Y-%m-%d') + '''</p>
            <p style="margin-top: 10px; font-size: 0.8em; color: #888;">
                <span class="status-indicator status-online"></span> 核心引擎: 运行中 |
                <span class="status-indicator status-online"></span> 数据源: 连接正常 |
                <span class="status-indicator status-online"></span> Web服务: 活跃
            </p>
        </footer>
    </div>
    
    <script>
        // 标签切换功能
        function switchTab(tabName) {
            // 隐藏所有标签内容
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 移除所有标签按钮的激活状态
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // 显示选中的标签内容
            document.getElementById(tabName).classList.add('active');
            
            // 激活对应的标签按钮
            event.target.classList.add('active');
        }
        
        // 刷新数据
        function refreshData() {
            location.reload();
        }
        
        // 获取API数据
        function fetchApiData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    const apiDataDiv = document.getElementById('api-data');
                    const apiDataContent = document.getElementById('api-data-content');
                    
                    apiDataContent.textContent = JSON.stringify(data, null, 2);
                    apiDataDiv.style.display = 'block';
                    
                    // 平滑滚动到数据区域
                    apiDataDiv.scrollIntoView({ behavior: 'smooth' });
                })
                .catch(error => {
                    console.error('获取API数据失败:', error);
                    alert('获取数据失败，请检查服务器状态');
                });
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🦞 PlusPlusTrader Web界面已加载');
        });
    </script>
</body>
</html>'''
        
        return html_template
    
    def generate_mock_data(self):
        """生成模拟数据"""
        now = datetime.now()
        
        # 生成随机价格数据
        prices = []
        base_price = 50000
        for i in range(100):
            timestamp = int((now - timedelta(hours=i)).timestamp() * 1000)
            open_price = base_price + random.uniform(-1000, 1000)
            high_price = open_price + random.uniform(0, 500)
            low_price = open_price - random.uniform(0, 500)
            close_price = random.uniform(low_price, high_price)
            volume = random.uniform(10, 100)
            
            prices.append({
                'timestamp': timestamp,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': round(volume, 2)
            })
        
        # 生成系统状态
        system_status = {
            'core_engine': {
                'status': 'running',
                'version': '1.0.0',
                'uptime': random.randint(1000, 10000)
            },
            'data_feeds': {
                'binance': {'connected': True, 'latency': random.randint(10, 100)},
                'csv': {'connected': True, 'files': random.randint(5, 20)}
            },
            'indicators': {
                'count': 24,
                'loaded': True
            },
            'memory_usage': {
                'used_mb': random.randint(100, 500),
                'total_mb': 1024
            }
        }
        
        return {
            'timestamp': int(now.timestamp() * 1000),
            'prices': prices,
            'system_status': system_status,
            'market_summary': {
                'btc_price': round(random.uniform(45000, 55000), 2),
                'eth_price': round(random.uniform(2500, 3500), 2),
                'total_volume_24h': round(random.uniform(20, 50), 1),
                'fear_greed_index': random.randint(40, 70)
            }
        }

def run_server(port=8080):
    """运行HTTP服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleWebHandler)
    
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
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器错误: {e}")

if __name__ == '__main__':
    # 设置端口
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"⚠️ 无效的端口号: {sys.argv[1]}，使用默认端口8080")
    
    run_server(port)