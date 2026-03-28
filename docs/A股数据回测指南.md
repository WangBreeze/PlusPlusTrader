# A股数据回测指南

## 概述

PlusPlusTrader 是一个高性能量化交易框架，支持A股数据的回测和分析。本文档详细说明如何按照项目规则要求下载A股数据，并使用该数据进行回测。

## 数据规则要求

### 1. 数据格式规范
A股数据必须符合以下格式要求，才能被系统的 `CSVDataSource` 正确加载：

- **必须字段**：
  - `timestamp`：时间戳（格式：YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD）
  - `open`：开盘价（浮点数）
  - `high`：最高价（浮点数）
  - `low`：最低价（浮点数）
  - `close`：收盘价（浮点数）
  - `volume`：成交量（整数或浮点数）

- **可选字段**：
  - `adj_close`：调整后收盘价
  - `turnover`：成交额
  - `amount`：成交金额

- **列名支持**：系统支持常见的列名变体（大小写不敏感）：
  - `timestamp` → `date`, `time`, `datetime`
  - `volume` → `vol`
  - `adj_close` → `adj close`, `adjusted_close`

### 2. 文件命名规则
A股数据文件命名必须遵循以下约定：
```
{股票代码}_{交易所}_{频率}.csv
```

示例：
- `000001.SZ_SSE_D.csv`（平安银行，日线数据）
- `600000.SS_SSE_60.csv`（浦发银行，60分钟数据）
- `000858.SZ_SSE_W.csv`（五粮液，周线数据）

其中：
- **股票代码**：标准A股代码（如 `000001.SZ`, `600000.SS`）
- **交易所**：`SSE`（上海证券交易所）或 `SZSE`（深圳证券交易所）
- **频率**：
  - `D`：日线数据
  - `W`：周线数据
  - `M`：月线数据
  - `60`：60分钟数据
  - `30`：30分钟数据
  - `15`：15分钟数据
  - `5`：5分钟数据
  - `1`：1分钟数据

### 3. 目录结构规则
数据必须按照以下目录结构存储：
```
data/
├── raw/                    # 原始数据
│   ├── stock/             # 股票数据
│   │   ├── SSE/           # 上海交易所
│   │   └── SZSE/          # 深圳交易所
│   └── index/             # 指数数据
├── processed/             # 处理后的数据（清洗、复权等）
└── fundamental/           # 基本面数据
```

## 数据下载方法

### 方法一：使用 scripts/download_a_shares.py 脚本

我们提供了一个专门的A股数据下载脚本，可以按照上述规则自动下载和格式化数据：

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install yfinance pandas

# 运行下载脚本
python scripts/download_a_shares.py \
  --symbol 000001.SZ \
  --start_date 2020-01-01 \
  --end_date 2023-12-31 \
  --interval 1d \
  --output_dir data/raw/stock/SZSE
```

### 方法二：手动下载并格式化

如果您从其他数据源下载数据，需要按照以下步骤格式化：

1. **数据清洗**：
   - 去除缺失值
   - 按时间排序
   - 检查价格数据的有效性（无零值或负值）

2. **格式转换**：
   - 确保列名符合要求
   - 时间戳格式标准化
   - 数值类型转换

3. **文件保存**：
   - 使用正确的文件名规范
   - 保存到正确的目录位置
   - CSV格式，UTF-8编码

## 回测流程

### 1. 配置数据源
在配置文件中指定A股数据文件路径：

```yaml
data_source:
  type: "csv"
  path: "data/raw/stock/SZSE/000001.SZ_SZSE_D.csv"
  symbol: "000001.SZ"
  exchange: "SZSE"
```

### 2. 创建回测配置
```python
# Python示例
import pplustrader as ppt

config = {
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 1000000,
    "data_source": "data/raw/stock/SZSE/000001.SZ_SZSE_D.csv",
    "strategy": "my_a_share_strategy",
    "commission_rate": 0.0003,  # A股佣金费率
    "tax_rate": 0.001,         # 印花税
}
```

### 3. 运行回测
```python
from pplustrader.backtest import BacktestEngine
from pplustrader.strategies import MovingAverageCrossover

# 创建回测引擎
engine = BacktestEngine(config)

# 加载数据
engine.load_data()

# 创建策略
strategy = MovingAverageCrossover(
    short_window=10,
    long_window=30
)

# 运行回测
results = engine.run(strategy)

# 分析结果
print(f"总收益: {results.total_return:.2%}")
print(f"年化收益: {results.annualized_return:.2%}")
print(f"最大回撤: {results.max_drawdown:.2%}")
print(f"夏普比率: {results.sharpe_ratio:.2f}")
```

## 注意事项

### 1. A股特殊规则
- **交易时间**：上午 9:30-11:30，下午 13:00-15:00
- **涨跌停限制**：±10%（ST股为±5%）
- **T+1交易**：当日买入，次日方可卖出
- **手续费**：佣金（通常0.03%）、印花税（0.1%）、过户费（0.002%）

### 2. 数据质量检查
在使用A股数据前，请检查：
- 是否有停牌日期的数据缺失
- 除权除息是否已处理（建议使用复权数据）
- 成交量的单位是否正确（手 vs 股）

### 3. 回测准确性
为提高A股回测的准确性，建议：
- 使用复权价格进行计算
- 考虑交易成本（佣金、印花税、过户费）
- 模拟T+1交易规则
- 考虑涨跌停限制对交易的影响

## 故障排除

### 常见问题

1. **数据加载失败**
   - 检查文件路径是否正确
   - 确认列名是否符合规范
   - 验证时间戳格式

2. **回测结果异常**
   - 检查是否考虑了A股交易规则
   - 验证手续费设置是否正确
   - 确认数据是否已复权

3. **性能问题**
   - 对于大量A股数据，建议使用C++核心模块
   - 考虑数据预处理，减少实时计算量
   - 使用适当的数据缓存机制

## 进阶功能

### 1. 多股票回测
系统支持同时回测多个A股标的，可用于：
- 股票组合优化
- 市场中性策略
- 行业轮动策略

### 2. 基本面数据集成
结合财务数据（市盈率、市净率、ROE等）进行量化分析：

```python
# 加载基本面数据
fundamental_data = ppt.load_fundamental_data("000001.SZ")
```

### 3. 实时数据接入
系统支持实时A股数据接入，可用于：
- 盘中监控
- 实时信号生成
- 自动化交易

## 联系与支持

如有A股数据回测相关问题，请：
1. 查阅项目文档
2. 检查示例代码
3. 提交GitHub Issue

---
*最后更新：2024年*
*版本：v1.0*