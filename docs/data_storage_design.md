# 数据存储方案设计

## 需求分析

### 数据类型
1. **Tick数据**: 高频数据，每秒可能多条
2. **K线数据**: 不同周期的OHLCV数据
3. **财务数据**: 基本面数据，更新频率低
4. **策略数据**: 策略状态和参数
5. **交易数据**: 订单、成交、持仓
6. **回测结果**: 性能指标和交易记录

### 性能要求
1. **写入性能**: 支持高速Tick数据写入
2. **查询性能**: 支持复杂时间范围查询
3. **存储效率**: 压缩存储，减少磁盘占用
4. **并发访问**: 支持多线程/多进程读写

### 容量估算
| 数据类型 | 每日数据量 | 每月数据量 | 每年数据量 |
|---------|-----------|-----------|-----------|
| Tick数据 (A股, 1个标的) | 10-20MB | 300-600MB | 3.6-7.2GB |
| Tick数据 (100个标的) | 1-2GB | 30-60GB | 360-720GB |
| 1分钟K线 (100个标的) | 50-100MB | 1.5-3GB | 18-36GB |
| 订单/交易数据 | 1-10MB | 30-300MB | 360MB-3.6GB |

## 候选方案比较

### 方案1: SQLite + 自定义二进制存储
**优点**:
- 零配置，无需数据库服务
- 单个文件，易于备份和管理
- 支持ACID事务
- 良好的并发读取

**缺点**:
- 写入性能有限 (特别是高频Tick数据)
- 存储效率不如专用时序数据库
- 复杂查询性能较差

### 方案2: PostgreSQL + TimescaleDB
**优点**:
- 专业的时序数据库扩展
- 优秀的时序数据查询性能
- 支持SQL，易于使用
- 自动数据压缩和分区
- 成熟可靠，社区活跃

**缺点**:
- 需要安装和维护数据库服务
- 资源消耗较大
- 配置相对复杂

### 方案3: InfluxDB
**优点**:
- 专为时序数据设计
- 极高的写入性能
- 简单易用的查询语言 (Flux)
- 内置数据保留策略

**缺点**:
- 查询功能相对有限
- 社区版限制较多
- 数据迁移相对困难

### 方案4: HDF5 + Parquet
**优点**:
- 极高的读取性能
- 优秀的压缩率
- 适合批处理分析
- 易于与Python生态系统集成

**缺点**:
- 写入性能一般
- 不适合频繁更新
- 并发访问能力有限

### 方案5: 混合存储策略
**核心思想**: 根据数据类型和使用场景选择不同存储方案

## 推荐方案: 混合存储策略

### 1. 高频Tick数据: TimescaleDB
- 使用PostgreSQL + TimescaleDB存储原始Tick数据
- 利用时序数据库的自动分区和压缩
- 支持复杂的时间范围查询

### 2. K线数据: SQLite + Parquet
- SQLite存储最新的K线数据 (便于实时查询)
- Parquet文件存储历史K线数据 (便于批处理分析)

### 3. 元数据和配置: SQLite
- 标的列表、交易所信息等
- 策略配置和参数
- 系统状态信息

### 4. 回测结果: SQLite + JSON
- SQLite存储结构化结果
- JSON文件存储详细交易记录和性能指标

## TimescaleDB存储设计

### 数据表设计

#### tick_data 表 (时序数据)
```sql
CREATE TABLE tick_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(32) NOT NULL,
    exchange VARCHAR(16) NOT NULL,
    last_price DECIMAL(18, 8),
    volume DECIMAL(18, 4),
    amount DECIMAL(18, 4),
    bid_price DECIMAL(18, 8),
    ask_price DECIMAL(18, 8),
    bid_volume INTEGER,
    ask_volume INTEGER,
    PRIMARY KEY (time, symbol, exchange)
);

-- 创建时序超表
SELECT create_hypertable('tick_data', 'time');
```

#### bar_data 表 (K线数据)
```sql
CREATE TABLE bar_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(32) NOT NULL,
    exchange VARCHAR(16) NOT NULL,
    frequency INTEGER NOT NULL,  -- 秒数: 60=1分钟, 300=5分钟
    open DECIMAL(18, 8),
    high DECIMAL(18, 8),
    low DECIMAL(18, 8),
    close DECIMAL(18, 8),
    volume DECIMAL(18, 4),
    amount DECIMAL(18, 4),
    PRIMARY KEY (time, symbol, exchange, frequency)
);

SELECT create_hypertable('bar_data', 'time');
```

### 索引优化
```sql
-- 创建复合索引加速查询
CREATE INDEX idx_tick_symbol_time ON tick_data (symbol, time DESC);
CREATE INDEX idx_bar_symbol_freq_time ON bar_data (symbol, frequency, time DESC);

-- 创建空间索引 (用于分区)
CREATE INDEX idx_tick_symbol_exchange ON tick_data (symbol, exchange);
```

### 数据保留策略
```sql
-- 自动删除90天前的Tick数据
SELECT add_retention_policy('tick_data', INTERVAL '90 days');

-- 压缩7天前的数据
ALTER TABLE tick_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,exchange'
);

SELECT add_compression_policy('tick_data', INTERVAL '7 days');
```

## SQLite存储设计

### 数据库结构
```sql
-- 标的元数据
CREATE TABLE symbols (
    symbol TEXT PRIMARY KEY,
    exchange TEXT NOT NULL,
    name TEXT,
    currency TEXT DEFAULT 'CNY',
    lot_size INTEGER DEFAULT 100,
    min_price_increment DECIMAL(10, 8),
    min_order_quantity DECIMAL(18, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 交易所信息
CREATE TABLE exchanges (
    exchange_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'stock', 'crypto', 'forex'
    country TEXT,
    timezone TEXT,
    trading_hours TEXT,  -- JSON格式的交易时间
    fee_structure TEXT,  -- JSON格式的费率结构
    is_active BOOLEAN DEFAULT 1
);

-- 策略配置
CREATE TABLE strategies (
    strategy_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'python', 'cpp'
    config TEXT,  -- JSON格式的策略配置
    status TEXT DEFAULT 'stopped',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单记录
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    strategy_id TEXT,
    symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    side TEXT NOT NULL,  -- 'BUY', 'SELL'
    order_type TEXT NOT NULL,  -- 'LIMIT', 'MARKET'
    price DECIMAL(18, 8),
    quantity DECIMAL(18, 4),
    filled_quantity DECIMAL(18, 4) DEFAULT 0,
    status TEXT NOT NULL,  -- 'NEW', 'PARTIAL', 'FILLED', 'CANCELLED'
    create_time TIMESTAMP NOT NULL,
    update_time TIMESTAMP NOT NULL,
    FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id)
);

-- 持仓记录
CREATE TABLE positions (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    quantity DECIMAL(18, 4) DEFAULT 0,
    avg_price DECIMAL(18, 8),
    unrealized_pnl DECIMAL(18, 8),
    realized_pnl DECIMAL(18, 8),
    update_time TIMESTAMP NOT NULL,
    FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id)
);
```

## Parquet文件存储设计

### 目录结构
```
data/
├── ticks/                     # Tick数据
│   ├── exchange=SSE/         # 上海交易所
│   │   ├── symbol=600519/    # 标的代码
│   │   │   ├── 2025/        # 年份
│   │   │   │   ├── 01/      # 月份
│   │   │   │   │   └── 01.parquet  # 每日数据
│   │   │   │   └── ...
│   │   │   └── ...
│   │   └── ...
│   └── exchange=BINANCE/
│       └── ...
├── bars/                      # K线数据
│   ├── frequency=60/         # 1分钟K线
│   │   ├── exchange=SSE/
│   │   │   └── symbol=600519/
│   │   │       ├── 2025.parquet
│   │   │       └── 2026.parquet
│   │   └── ...
│   ├── frequency=300/        # 5分钟K线
│   └── ...
├── backtest_results/         # 回测结果
│   ├── strategy=ma_cross/
│   │   ├── 20250309_120000.json  # 回测配置和结果
│   │   └── trades.parquet        # 交易记录
│   └── ...
└── metadata/                 # 元数据
    ├── symbols.parquet
    ├── exchanges.parquet
    └── ...
```

### Parquet文件格式
```python
import pyarrow as pa
import pyarrow.parquet as pq

# Tick数据schema
tick_schema = pa.schema([
    pa.field('timestamp', pa.timestamp('ms')),  # 时间戳
    pa.field('last_price', pa.float64()),       # 最新价
    pa.field('volume', pa.float64()),           # 成交量
    pa.field('amount', pa.float64()),           # 成交额
    pa.field('bid_price', pa.float64()),        # 买一价
    pa.field('ask_price', pa.float64()),        # 卖一价
    pa.field('bid_volume', pa.int32()),         # 买一量
    pa.field('ask_volume', pa.int32()),         # 卖一量
])

# K线数据schema
bar_schema = pa.schema([
    pa.field('timestamp', pa.timestamp('ms')),
    pa.field('open', pa.float64()),
    pa.field('high', pa.float64()),
    pa.field('low', pa.float64()),
    pa.field('close', pa.float64()),
    pa.field('volume', pa.float64()),
    pa.field('amount', pa.float64()),
])
```

## 数据访问层设计

### 抽象接口
```cpp
// C++数据访问接口
class IDataStorage {
public:
    virtual ~IDataStorage() = default;
    
    // Tick数据操作
    virtual bool store_tick(const TickData& tick) = 0;
    virtual std::vector<TickData> get_ticks(
        const std::string& symbol,
        const std::string& exchange,
        time_t start_time,
        time_t end_time,
        int limit = 1000) = 0;
    
    // K线数据操作
    virtual bool store_bar(const BarData& bar) = 0;
    virtual std::vector<BarData> get_bars(
        const std::string& symbol,
        const std::string& exchange,
        int frequency,
        time_t start_time,
        time_t end_time) = 0;
        
    // 订单操作
    virtual bool store_order(const Order& order) = 0;
    virtual Order get_order(const std::string& order_id) = 0;
    virtual std::vector<Order> get_orders(
        const std::string& strategy_id,
        time_t start_time,
        time_t end_time) = 0;
};
```

### TimescaleDB实现
```cpp
class TimescaleDBStorage : public IDataStorage {
private:
    pqxx::connection conn_;
    
public:
    TimescaleDBStorage(const std::string& connection_string);
    ~TimescaleDBStorage();
    
    bool store_tick(const TickData& tick) override {
        pqxx::work txn(conn_);
        
        txn.exec_prepared(
            "insert_tick",
            tick.timestamp,
            tick.symbol,
            tick.exchange,
            tick.last_price,
            tick.volume,
            tick.amount,
            tick.bid_price,
            tick.ask_price,
            tick.bid_volume,
            tick.ask_volume
        );
        
        txn.commit();
        return true;
    }
    
    // 其他方法实现...
};
```

### SQLite实现
```cpp
class SQLiteStorage : public IDataStorage {
private:
    sqlite3* db_;
    
public:
    SQLiteStorage(const std::string& db_path);
    ~SQLiteStorage();
    
    bool store_order(const Order& order) override {
        sqlite3_stmt* stmt;
        const char* sql = R"(
            INSERT INTO orders 
            (order_id, strategy_id, symbol, exchange, side, order_type, 
             price, quantity, filled_quantity, status, create_time, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        )";
        
        // 准备和执行语句
        // ...
        
        return true;
    }
    
    // 其他方法实现...
};
```

## 数据同步机制

### 1. 实时数据管道
```
实时数据源 → 数据处理器 → TimescaleDB (热数据) → Parquet (冷数据)
                              ↓
                       SQLite (元数据)
```

### 2. 批处理数据迁移
```python
# 定期将热数据迁移到冷存储
def migrate_hot_to_cold():
    # 查询90天前的数据
    hot_data = query_timescaledb("""
        SELECT * FROM tick_data 
        WHERE time < NOW() - INTERVAL '90 days'
    """)
    
    # 转换为Parquet格式
    df = pd.DataFrame(hot_data)
    df.to_parquet(f"data/ticks/{date}.parquet")
    
    # 从TimescaleDB删除已迁移的数据
    delete_from_timescaledb("""
        DELETE FROM tick_data 
        WHERE time < NOW() - INTERVAL '90 days'
    """)
```

## 性能优化策略

### 1. 批量写入
```cpp
// 批量写入Tick数据
class BatchWriter {
private:
    std::vector<TickData> buffer_;
    size_t batch_size_;
    IDataStorage* storage_;
    
public:
    void add_tick(const TickData& tick) {
        buffer_.push_back(tick);
        if (buffer_.size() >= batch_size_) {
            flush();
        }
    }
    
    void flush() {
        if (buffer_.empty()) return;
        
        // 批量写入数据库
        storage_->batch_store_ticks(buffer_);
        buffer_.clear();
    }
};
```

### 2. 数据缓存
```cpp
// LRU缓存热数据
class DataCache {
private:
    struct CacheEntry {
        std::string key;
        std::vector<TickData> data;
        time_t timestamp;
    };
    
    std::list<CacheEntry> cache_list_;
    std::unordered_map<std::string, 
        typename std::list<CacheEntry>::iterator> cache_map_;
    size_t max_size_;
    
public:
    std::vector<TickData> get_ticks(
        const std::string& symbol,
        time_t start_time,
        time_t end_time) {
        
        std::string key = symbol + "_" + 
                         std::to_string(start_time) + "_" +
                         std::to_string(end_time);
        
        auto it = cache_map_.find(key);
        if (it != cache_map_.end()) {
            // 缓存命中，移动到最近使用位置
            cache_list_.splice(cache_list_.begin(), cache_list_, it->second);
            return it->second->data;
        }
        
        // 缓存未命中，从数据库加载
        auto data = storage_->get_ticks(symbol, start_time, end_time);
        
        // 添加到缓存
        add_to_cache(key, data);
        return data;
    }
};
```

### 3. 查询优化
```sql
-- 使用分区键查询
SELECT * FROM tick_data
WHERE symbol = '600519.SH'
  AND exchange = 'SSE'
  AND time >= '2025-01-01'
  AND time < '2025-02-01'
ORDER BY time DESC
LIMIT 1000;

-- 使用索引加速
CREATE INDEX idx_tick_symbol_time 
ON tick_data (symbol, time DESC)
INCLUDE (last_price, volume, bid_price, ask_price);
```

## 备份和恢复策略

### 1. 定期备份
```bash
#!/bin/bash
# 备份脚本
BACKUP_DIR="/backup/pplustrader"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份TimescaleDB
pg_dump -U postgres pplustrader > "$BACKUP_DIR/timescaledb_$DATE.sql"

# 备份SQLite
cp /data/pplustrader/metadata.db "$BACKUP_DIR/metadata_$DATE.db"

# 备份Parquet数据 (增量备份)
rsync -av --delete /data/pplustrader/parquet/ "$BACKUP_DIR/parquet_$DATE/"
```

### 2. 数据恢复
```python
def restore_from_backup(backup_date):
    # 恢复数据库
    os.system(f"psql -U postgres pplustrader < {backup_date}/timescaledb.sql")
    
    # 恢复SQLite
    shutil.copy(f"{backup_date}/metadata.db", "/data/pplustrader/metadata.db")
    
    # 恢复Parquet数据
    shutil.copytree(f"{backup_date}/parquet", "/data/pplustrader/parquet")
```

## 监控和维护

### 1. 存储监控
```sql
-- 监控表大小
SELECT 
    hypertable_name,
    pg_size_pretty(hypertable_size) as size,
    compression_status
FROM timescaledb_information.hypertables;

-- 监控查询性能
SELECT 
    calls,
    total_time,
    mean_time,
    query
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### 2. 数据完整性检查
```python
def check_data_integrity():
    # 检查数据连续性
    gaps = find_data_gaps("tick_data", "600519.SH", "2025-01-01", "2025-01-31")
    
    # 检查数据一致性
    verify_parquet_vs_database("2025-01-01")
    
    # 修复数据问题
    if gaps:
        refill_missing_data(gaps)
```

## 实施计划

### Phase 1: 基础存储 (1周)
1. 安装和配置TimescaleDB
2. 创建SQLite数据库
3. 实现基础数据访问接口
4. 编写数据迁移工具

### Phase 2: 性能优化 (1周)
1. 实现批量写入和缓存
2. 优化查询索引
3. 添加数据压缩
4. 实现数据分区策略

### Phase 3: 高级功能 (1周)
1. 实现数据同步机制
2. 添加备份恢复功能
3. 实现监控和告警
4. 优化内存使用

### Phase 4: 集成测试 (3天)
1. 性能压力测试
2. 数据一致性测试
3. 故障恢复测试
4. 集成到交易系统

## 资源需求

### 硬件需求
- **CPU**: 4核心以上 (用于数据压缩和查询)
- **内存**: 16GB以上 (用于数据缓存)
- **存储**: SSD硬盘，容量根据数据量估算
- **网络**: 千兆网络 (用于数据同步)

### 软件需求
- **PostgreSQL 14+** + TimescaleDB 2.10+
- **SQLite 3.35+**
- **pyarrow** (Parquet支持)
- **libpqxx** (C++ PostgreSQL客户端)

## 风险评估和应对

### 风险1: 数据丢失
- **应对**: 定期备份 + 实时复制 + 数据校验

### 风险2: 性能瓶颈
- **应对**: 读写分离 + 缓存 + 数据分区

### 风险3: 存储空间不足
- **应对**: 数据生命周期管理 + 自动清理 + 存储监控

### 风险4: 数据不一致
- **应对**: 事务保证 + 数据校验 + 修复工具

## 总结

混合存储策略提供了灵活性、性能和易用性的平衡：
1. **TimescaleDB**: 处理高频实时数据
2. **SQLite**: 存储配置和元数据
3. **Parquet**: 归档历史数据用于分析

这种架构可以根据实际需求进行扩展和调整，为PlusPlusTrader提供可靠的数据存储基础。