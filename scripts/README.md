# A股数据下载脚本

## 概述

本脚本用于按照PlusPlusTrader项目规则下载A股数据，确保数据格式符合CSVDataSource要求，并按照项目目录结构保存数据。

## 功能特性

- ✅ 支持多种数据源：yfinance、akshare、tushare
- ✅ 自动格式化数据以符合CSVDataSource规范
- ✅ 按照项目规则命名文件和目录结构
- ✅ 支持单只股票和批量下载
- ✅ 支持多种数据频率（日线、周线、月线、分钟线）
- ✅ 数据质量检查和格式化

## 安装依赖

```bash
# 安装基础依赖
pip install pandas numpy

# 安装数据源库（选择其中一个或多个）
pip install yfinance          # 推荐，简单易用
pip install akshare           # 功能丰富，A股数据全面
pip install tushare           # 专业A股数据，需要API token
```

## 快速开始

### 1. 单只股票下载

```bash
# 使用yfinance下载平安银行日线数据
python download_a_shares.py \
  --symbol 000001.SZ \
  --start 2020-01-01 \
  --end 2023-12-31 \
  --interval 1d \
  --source yfinance

# 使用akshare下载贵州茅台日线数据
python download_a_shares.py \
  --symbol 600519.SS \
  --start 2021-01-01 \
  --end 2024-01-01 \
  --source akshare
```

### 2. 批量下载

```bash
# 下载示例股票列表中的所有股票
python download_a_shares.py \
  --batch example_stocks.txt \
  --start 2020-01-01 \
  --end 2023-12-31 \
  --source yfinance
```

### 3. 不同频率数据

```bash
# 下载60分钟数据
python download_a_shares.py \
  --symbol 000001.SZ \
  --interval 60m \
  --start 2023-01-01 \
  --end 2023-12-31

# 下载周线数据
python download_a_shares.py \
  --symbol 000001.SZ \
  --interval 1w \
  --start 2018-01-01 \
  --end 2023-12-31
```

## 输出格式

### 文件命名规则
```
{股票代码}_{交易所}_{频率}.csv

示例:
000001.SZ_SZSE_D.csv      # 平安银行日线数据
600000.SS_SSE_60.csv      # 浦发银行60分钟数据
300750.SZ_SZSE_W.csv      # 宁德时代周线数据
```

### 数据列规范
CSV文件包含以下列（符合CSVDataSource要求）：

| 列名 | 说明 | 类型 | 必填 |
|------|------|------|------|
| timestamp | 时间戳 | datetime | ✅ |
| open | 开盘价 | float | ✅ |
| high | 最高价 | float | ✅ |
| low | 最低价 | float | ✅ |
| close | 收盘价 | float | ✅ |
| volume | 成交量 | float | ✅ |
| adj_close | 调整后收盘价 | float | 可选 |
| amount | 成交额 | float | 可选 |
| symbol | 股票代码 | string | 可选 |
| exchange | 交易所 | string | 可选 |
| frequency | 数据频率 | string | 可选 |

### 目录结构
数据按照以下目录结构保存：
```
data/
└── raw/
    └── stock/
        ├── SSE/          # 上海证券交易所股票
        │   ├── 600000.SS_SSE_D.csv
        │   ├── 600036.SS_SSE_D.csv
        │   └── ...
        └── SZSE/         # 深圳证券交易所股票
            ├── 000001.SZ_SZSE_D.csv
            ├── 000002.SZ_SZSE_D.csv
            └── ...
```

## 数据源比较

| 数据源 | 优点 | 缺点 | 适用场景 |
|--------|------|------|----------|
| **yfinance** | 免费、无需注册、简单易用 | A股数据可能不完整 | 快速测试、教育用途 |
| **akshare** | A股数据全面、免费 | 接口可能变化、依赖多 | 专业A股分析 |
| **tushare** | 数据质量高、稳定 | 需要API token、有调用限制 | 生产环境、专业研究 |

## 使用示例

### 1. 为回测准备数据

```python
# 下载2020-2023年的A股数据用于回测
python download_a_shares.py \
  --batch stocks_for_backtest.txt \
  --start 2020-01-01 \
  --end 2023-12-31 \
  --source akshare \
  --interval 1d
```

### 2. 下载高频数据用于策略研究

```python
# 下载最近3个月的60分钟数据
python download_a_shares.py \
  --symbol 000001.SZ \
  --interval 60m \
  --start 2023-10-01 \
  --end 2024-01-01 \
  --source akshare
```

### 3. 定期更新数据

```bash
#!/bin/bash
# update_stocks.sh - 定期更新股票数据

# 更新日线数据（过去30天）
python download_a_shares.py \
  --batch my_portfolio.txt \
  --start $(date -d "30 days ago" +%Y-%m-%d) \
  --end $(date +%Y-%m-%d) \
  --source yfinance

# 更新到数据库或数据仓库
# ...
```

## 故障排除

### 常见问题

1. **"ModuleNotFoundError: No module named 'yfinance'"**
   ```bash
   pip install yfinance
   ```

2. **下载速度慢**
   - 减少请求频率，添加延迟
   - 使用批量下载时，控制并发数量
   - 考虑使用本地缓存

3. **数据缺失或不完整**
   - 检查股票代码格式是否正确
   - 验证数据源是否支持该股票
   - 检查网络连接

4. **文件保存失败**
   - 确保有写入权限
   - 检查磁盘空间
   - 验证目录路径是否正确

### 数据质量检查

```python
import pandas as pd

# 加载下载的数据
df = pd.read_csv('data/raw/stock/SZSE/000001.SZ_SZSE_D.csv')

# 检查数据质量
print(f"记录数: {len(df)}")
print(f"时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}")
print(f"缺失值统计:")
print(df.isnull().sum())
print(f"价格数据统计:")
print(df[['open', 'high', 'low', 'close']].describe())
```

## 高级用法

### 自定义数据源

您可以扩展`AShareDownloader`类来支持其他数据源：

```python
class CustomAShareDownloader(AShareDownloader):
    def download_custom(self, symbol, start_date, end_date, interval='1d'):
        # 实现自定义数据下载逻辑
        pass
```

### 数据预处理

下载后可以添加自定义的数据预处理：

```python
# 后处理脚本示例
def post_process(df):
    # 添加技术指标
    df['sma_20'] = df['close'].rolling(20).mean()
    df['sma_50'] = df['close'].rolling(50).mean()
    
    # 计算收益率
    df['returns'] = df['close'].pct_change()
    
    # 添加交易信号
    df['signal'] = (df['sma_20'] > df['sma_50']).astype(int)
    
    return df
```

### 集成到工作流

```python
# 自动化数据下载和回测工作流
import subprocess

# 1. 下载数据
subprocess.run([
    'python', 'download_a_shares.py',
    '--symbol', '000001.SZ',
    '--start', '2020-01-01',
    '--end', '2023-12-31'
])

# 2. 运行回测
# 使用PlusPlusTrader回测引擎
from pplustrader.backtest import BacktestEngine
# ...
```

## 许可证

本脚本是PlusPlusTrader项目的一部分，遵循相同的许可证。

## 贡献

欢迎提交Issue和Pull Request来改进本脚本。

## 更新日志

### v1.0 (2024-01-01)
- 初始版本发布
- 支持yfinance、akshare、tushare数据源
- 实现数据格式化和标准化
- 支持批量下载

---
*更多信息请参考项目主文档*