# 配置文件格式设计

## 设计原则

1. **分层配置**: 系统级 → 策略级 → 实例级
2. **继承和覆盖**: 支持配置继承和局部覆盖
3. **环境分离**: 开发、测试、生产环境配置分离
4. **安全性**: 敏感信息加密存储
5. **验证**: 配置格式和值的验证
6. **热重载**: 支持运行时配置更新

## 配置格式选择

### JSON vs YAML vs TOML vs INI

| 格式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **JSON** | 标准化、广泛支持、易于解析 | 无注释、冗长 | 机器生成、API配置 |
| **YAML** | 可读性好、支持注释、简洁 | 缩进敏感、解析复杂 | 人工编辑、复杂配置 |
| **TOML** | 简单清晰、类型明确、支持注释 | 嵌套结构稍显复杂 | 应用配置、简单项目 |
| **INI** | 极其简单、易于理解 | 无类型、不支持嵌套 | 最简配置 |

**选择结果**: **YAML** (主配置) + **JSON** (动态配置)

## 配置文件结构

### 1. 主配置文件 (config.yaml)
```yaml
# PlusPlusTrader 主配置文件
# 版本: 1.0.0

# 系统元数据
metadata:
  version: "1.0.0"
  environment: "development"  # development, testing, production
  config_version: 1

# 日志配置
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  console:
    enabled: true
    format: "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
  file:
    enabled: true
    path: "./logs/pplustrader.log"
    max_size_mb: 100
    backup_count: 10
  database:
    enabled: false
    connection_string: "postgresql://localhost/logs"

# 数据存储配置
storage:
  # TimescaleDB配置 (用于高频数据)
  timescaledb:
    enabled: true
    host: "localhost"
    port: 5432
    database: "pplustrader"
    username: "pplususer"
    password: "${TIMESCALEDB_PASSWORD}"  # 环境变量替换
    pool_size: 10
    connect_timeout: 30
    
  # SQLite配置 (用于元数据和配置)
  sqlite:
    enabled: true
    path: "./data/metadata.db"
    journal_mode: "WAL"  # Write-Ahead Logging
    synchronous: "NORMAL"
    
  # Parquet配置 (用于历史数据归档)
  parquet:
    enabled: true
    base_path: "./data/parquet"
    compression: "SNAPPY"
    row_group_size: 100000
    
  # 数据保留策略
  retention:
    tick_data_days: 90  # 保留90天Tick数据
    bar_data_days: 365  # 保留365天K线数据
    order_data_days: 730  # 保留2年订单数据

# 数据源配置
data_sources:
  # 实时数据源
  realtime:
    enabled: false
    providers:
      - type: "websocket"
        exchange: "binance"
        symbols: ["BTCUSDT", "ETHUSDT"]
        url: "wss://stream.binance.com:9443/ws"
        
  # 历史数据源
  historical:
    enabled: true
    providers:
      - type: "csv"
        name: "local_csv"
        base_path: "./data/csv"
        date_format: "%Y-%m-%d"
        
      - type: "database"
        name: "timescaledb"
        connection: "${STORAGE_TIMESCALEDB_CONNECTION}"

# 交易所配置
exchanges:
  # 模拟交易所 (用于回测)
  simulated:
    enabled: true
    type: "simulated"
    fee_rate: 0.001  # 0.1%手续费
    slippage: 0.0001  # 0.01%滑点
    initial_balance:
      CNY: 1000000
      USD: 100000
      
  # 实盘交易所配置
  binance:
    enabled: false
    type: "crypto"
    name: "Binance"
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    testnet: false  # 使用测试网络
    
  # A股交易所配置
  sse:
    enabled: false
    type: "stock"
    name: "上海证券交易所"
    broker: "simulated"  # 模拟券商
    
# 交易引擎配置
trading_engine:
  # 核心参数
  heartbeat_interval_ms: 1000  # 心跳间隔
  max_order_queue_size: 10000
  risk_check_enabled: true
  
  # 风险控制
  risk:
    max_position_per_symbol: 1000000  # 单标的最大持仓金额
    max_daily_loss: 0.05  # 最大单日损失比例
    max_drawdown: 0.20  # 最大回撤比例
    stop_loss_enabled: true
    stop_loss_threshold: 0.10
    
  # 性能优化
  performance:
    use_batch_processing: true
    cache_size_mb: 512
    parallel_workers: 4
    
# 回测引擎配置
backtest_engine:
  enabled: true
  data_mode: "historical"  # historical, walk_forward, monte_carlo
  commission: 0.001
  slippage: 0.0001
  initial_cash: 1000000
  date_range:
    start: "2024-01-01"
    end: "2024-12-31"
    
  # 分析配置
  analysis:
    metrics:
      - "total_return"
      - "annual_return"
      - "sharpe_ratio"
      - "max_drawdown"
      - "win_rate"
    report_format: "html"  # html, json, csv
    save_to_database: true

# 监控配置
monitoring:
  enabled: true
  metrics:
    - type: "system"
      interval: 60  # 秒
      metrics: ["cpu", "memory", "disk", "network"]
      
    - type: "trading"
      interval: 10  # 秒
      metrics: ["positions", "pnl", "orders", "trades"]
      
  # 告警配置
  alerts:
    - type: "email"
      enabled: false
      smtp_server: "smtp.gmail.com"
      recipients: ["admin@example.com"]
      
    - type: "webhook"
      enabled: false
      url: "https://hooks.slack.com/services/xxx"
      
# API服务配置
api:
  enabled: false
  host: "0.0.0.0"
  port: 8080
  authentication:
    enabled: true
    type: "jwt"
    secret_key: "${API_SECRET_KEY}"
  cors:
    enabled: true
    origins: ["http://localhost:3000"]

# 调度器配置
scheduler:
  enabled: true
  jobs:
    - name: "data_import"
      type: "cron"
      schedule: "0 2 * * *"  # 每天凌晨2点
      command: "import_daily_data"
      params:
        exchanges: ["sse", "szse"]
        
    - name: "report_generation"
      type: "interval"
      interval: 3600  # 每小时
      command: "generate_daily_report"
```

### 2. 策略配置文件 (strategies/ma_cross.yaml)
```yaml
# 移动平均线交叉策略配置

metadata:
  strategy_name: "ma_cross"
  version: "1.0.0"
  author: "System"
  description: "双均线交叉策略"
  category: "trend_following"

# 策略基本参数
strategy:
  type: "python"  # python, cpp
  class_path: "strategies.ma_cross.MovingAverageCross"
  enabled: true
  
  # 资金分配
  capital:
    initial: 100000
    currency: "CNY"
    allocation: 0.1  # 10%的总资金分配给此策略
    
  # 交易标的
  symbols:
    - symbol: "600519.SH"
      exchange: "sse"
      weight: 0.3  # 30%的策略资金分配到此标的
      
    - symbol: "000858.SZ"
      exchange: "szse"
      weight: 0.2
      
    - symbol: "BTCUSDT"
      exchange: "binance"
      weight: 0.5

# 策略参数 (可在运行时调整)
parameters:
  # 均线参数
  ma_short: 10
  ma_long: 30
  
  # 交易参数
  position_size: 0.1  # 每次交易使用10%的资金
  stop_loss: 0.05  # 5%止损
  take_profit: 0.10  # 10%止盈
  
  # 过滤条件
  min_volume: 1000000  # 最小成交量
  volatility_threshold: 0.02  # 波动率阈值
  
  # 时间限制
  trading_hours:
    start: "09:30:00"
    end: "15:00:00"
  exclude_holidays: true

# 风险控制
risk:
  max_position_per_symbol: 0.2  # 单标的最大20%持仓
  max_daily_trades: 10
  cooling_period_after_loss: 3600  # 亏损后冷却1小时
  
  # 动态风险调整
  dynamic:
    enabled: true
    volatility_adjustment: true
    market_regime_filter: true

# 性能优化
performance:
  data_frequency: "1m"  # 1分钟K线
  use_cached_indicators: true
  parallel_processing: false  # 单标的不需要并行

# 回测配置 (覆盖系统默认)
backtest:
  date_range:
    start: "2024-01-01"
    end: "2024-12-31"
  commission: 0.0008  # 策略特定手续费
  slippage: 0.00005
  
  # 分析指标
  analysis:
    metrics:
      - "total_return"
      - "sharpe_ratio"
      - "max_drawdown"
      - "calmar_ratio"
      - "sortino_ratio"
    benchmarks:
      - "000300.SH"  # 沪深300
      - "000001.SH"  # 上证指数

# 监控和告警
monitoring:
  alerts:
    - type: "performance"
      condition: "drawdown > 0.05"
      action: "pause_strategy"
      notification: "email"
      
    - type: "error"
      condition: "consecutive_errors > 3"
      action: "stop_strategy"
      notification: "all"

# 状态持久化
persistence:
  save_state: true
  frequency: "daily"  # daily, weekly, on_exit
  format: "json"
  location: "./data/strategies/ma_cross/state"
```

### 3. 运行时配置 (runtime_config.json)
```json
{
  "$schema": "./schemas/runtime_config.schema.json",
  "metadata": {
    "timestamp": "2024-03-09T09:30:00Z",
    "source": "dynamic",
    "version": "1.0.0"
  },
  
  "active_strategies": [
    {
      "strategy_id": "ma_cross_001",
      "strategy_name": "ma_cross",
      "status": "running",
      "started_at": "2024-03-09T09:00:00Z",
      "current_capital": 105000.50,
      "positions": [
        {
          "symbol": "600519.SH",
          "quantity": 100,
          "avg_price": 185.75,
          "current_price": 190.20,
          "unrealized_pnl": 445.00
        }
      ]
    }
  ],
  
  "system_status": {
    "trading_engine": "running",
    "data_feeds": "connected",
    "risk_monitor": "active",
    "last_heartbeat": "2024-03-09T09:29:55Z"
  },
  
  "performance_metrics": {
    "total_pnl": 5000.50,
    "daily_pnl": 245.75,
    "total_trades": 25,
    "win_rate": 0.68,
    "sharpe_ratio": 1.85,
    "max_drawdown": 0.032
  },
  
  "market_conditions": {
    "volatility_index": 0.018,
    "trend_strength": 0.65,
    "market_regime": "trending",
    "sentiment": "bullish"
  }
}
```

## 配置继承机制

### 1. 配置层次结构
```
系统默认配置 (hardcoded defaults)
    ↓
主配置文件 (config.yaml) [系统级]
    ↓
环境配置文件 (config.production.yaml) [环境特定]
    ↓
策略配置文件 (strategies/*.yaml) [策略级]
    ↓
运行时配置 (内存中的覆盖) [运行时]
```

### 2. 配置合并算法
```python
import yaml
from typing import Dict, Any

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并两个字典，override优先"""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result

class ConfigManager:
    def __init__(self):
        self.configs = {}
        
    def load_config(self, path: str, env: str = None) -> Dict:
        # 加载基础配置
        with open(path, 'r') as f:
            base_config = yaml.safe_load(f)
            
        # 加载环境特定配置
        if env:
            env_path = path.replace('.yaml', f'.{env}.yaml')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_config = yaml.safe_load(f)
                    base_config = deep_merge(base_config, env_config)
                    
        return base_config
```

### 3. 环境变量支持
```python
import os
import re
from typing import Dict, Any

def resolve_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """解析配置中的环境变量引用"""
    
    def _resolve(value: Any) -> Any:
        if isinstance(value, str):
            # 匹配 ${VAR_NAME} 或 $VAR_NAME 格式
            pattern = r'\$\{?(\w+)\}?'
            def replace(match):
                var_name = match.group(1)
                return os.getenv(var_name, f'${{{var_name}}}')
            return re.sub(pattern, replace, value)
        elif isinstance(value, dict):
            return {k: _resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_resolve(item) for item in value]
        else:
            return value
    
    return _resolve(config)

# 使用示例
config = {
    "database": {
        "password": "${DB_PASSWORD}",
        "host": "localhost"
    }
}

resolved = resolve_env_vars(config)
# 如果 DB_PASSWORD=secret，则 password 变为 "secret"
```

## 配置验证

### 1. JSON Schema验证
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PlusPlusTrader配置",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$"
        },
        "environment": {
          "type": "string",
          "enum": ["development", "testing", "production"]
        }
      },
      "required": ["version", "environment"]
    },
    
    "logging": {
      "type": "object",
      "properties": {
        "level": {
          "type": "string",
          "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        }
      },
      "required": ["level"]
    }
    
    // ... 其他属性的定义
  },
  "required": ["metadata", "logging", "storage"]
}
```

### 2. Python验证器
```python
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class LoggingConfig(BaseModel):
    level: str = Field("INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    console: Dict = {}
    file: Optional[Dict]
    
    @validator('level')
    def validate_level(cls, v):
        if v not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {v}")
        return v

class StorageConfig(BaseModel):
    timescaledb: Optional[Dict]
    sqlite: Optional[Dict]
    parquet: Optional[Dict]
    
    @validator('timescaledb')
    def validate_timescaledb(cls, v, values):
        if v and not v.get('password'):
            raise ValueError("TimescaleDB password is required")
        return v

class MainConfig(BaseModel):
    metadata: Dict
    logging: LoggingConfig
    storage: StorageConfig
    data_sources: Optional[Dict]
    exchanges: Dict
    trading_engine: Dict
    
    class Config:
        extra = "allow"  # 允许额外字段

# 使用示例
config_dict = yaml.safe_load(open("config.yaml"))
config = MainConfig(**config_dict)
```

## 配置热重载

### 1. 文件监控
```python
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, config_manager, config_path):
        self.config_manager = config_manager
        self.config_path = config_path
        self.last_modified = 0
        
    def on_modified(self, event):
        if event.src_path == self.config_path:
            current_time = time.time()
            # 防抖处理，避免频繁重载
            if current_time - self.last_modified > 2.0:
                self.last_modified = current_time
                print(f"Config file modified: {event.src_path}")
                self.config_manager.reload_config()

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()
        self.handlers = []
        
        # 启动文件监控
        self.start_file_watcher()
        
    def start_file_watcher(self):
        event_handler = ConfigFileHandler(self, self.config_path)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(self.config_path))
        observer.start()
        
        # 后台线程运行
        thread = threading.Thread(target=observer.join)
        thread.daemon = True
        thread.start()
        
    def reload_config(self):
        """重新加载配置并通知所有监听器"""
        new_config = self.load_config()
        
        # 检查配置变更
        changed_keys = self.find_changed_keys(self.config, new_config)
        
        if changed_keys:
            print(f"Config changed: {changed_keys}")
            self.config = new_config
            
            # 通知所有监听器
            for handler in self.handlers:
                handler.on_config_changed(changed_keys, self.config)
```

### 2. 配置变更通知
```cpp
// C++配置监听器接口
class IConfigListener {
public:
    virtual ~IConfigListener() = default;
    virtual void on_config_changed(
        const std::set<std::string>& changed_keys,
        const Config& new_config) = 0;
};

// 配置管理器
class ConfigManager {
private:
    Config config_;
    std::vector<std::shared_ptr<IConfigListener>> listeners_;
    
public:
    void reload_config(const std::string& config_path) {
        Config new_config = load_config(config_path);
        auto changed_keys = compare_configs(config_, new_config);
        
        if (!changed_keys.empty()) {
            config_ = std::move(new_config);
            
            // 通知监听器
            for (auto& listener : listeners_) {
                listener->on_config_changed(changed_keys, config_);
            }
        }
    }
    
    void add_listener(std::shared_ptr<IConfigListener> listener) {
        listeners_.push_back(listener);
    }
};
```

## 安全配置

### 1. 敏感信息加密
```python
from cryptography.fernet import Fernet
import base64
import os

class SecureConfig:
    def __init__(self, key_path=None):
        if key_path and os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            if key_path:
                with open(key_path, 'wb') as f:
                    f.write(self.key)
        
        self.cipher = Fernet(self.key)
    
    def encrypt_value(self, plaintext: str) -> str:
        """加密敏感信息"""
        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_value(self, ciphertext: str) -> str:
        """解密敏感信息"""
        encrypted = base64.b64decode(ciphertext.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()
    
    def secure_config(self, config: Dict) -> Dict:
        """处理配置中的敏感字段"""
        secure_fields = ['password', 'api_key', 'api_secret', 'secret_key']
        
        def process_dict(d: Dict) -> Dict:
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = process_dict(v)
                elif isinstance(v, str) and k in secure_fields and v.startswith('ENC:'):
                    # 解密 ENC: 前缀的值
                    result[k] = self.decrypt_value(v[4:])
                else:
                    result[k] = v
            return result
        
        return process_dict(config)
```

### 2. 配置示例 (加密后)
```yaml
database:
  host: "localhost"
  username: "pplususer"
  password: "ENC:gAAAAABk...（加密后的密文）"

exchanges:
  binance:
    api_key: "ENC:gAAAAABl...（加密后的密文）"
    api_secret: "ENC:gAAAAABm...（加密后的密文）"
```

## 配置工具

### 1. 配置生成器
```python
#!/usr/bin/env python3
# config_generator.py

import yaml
import argparse
from pathlib import Path

def generate_config(environment: str, output_dir: str):
    """生成指定环境的配置文件"""
    
    # 基础配置模板
    base_config = {
        "metadata": {
            "version": "1.0.0",
            "environment": environment,
            "config_version": 1
        },
        "logging": {
            "level": "INFO" if environment == "production" else "DEBUG"
        }
        # ... 其他配置
    }
    
    # 环境特定配置
    env_configs = {
        "development": {
            "storage": {
                "timescaledb": {"host": "localhost"},
                "sqlite": {"path": "./data/dev/metadata.db"}
            }
        },
        "production": {
            "storage": {
                "timescaledb": {"host": "db.production.example.com"},
                "sqlite": {"path": "/var/lib/pplustrader/metadata.db"}
            },
            "monitoring": {"enabled": True}
        }
    }
    
    # 合并配置
    config = {**base_config, **env_configs.get(environment, {})}
    
    # 写入文件
    output_path = Path(output_dir) / f"config.{environment}.yaml"
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"Generated config: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PlusPlusTrader config")
    parser.add_argument("--env", required=True, choices=["development", "testing", "production"])
    parser.add_argument("--output", default="./config")
    
    args = parser.parse_args()
    generate_config(args.env, args.output)
```

### 2. 配置验证器
```python
#!/usr/bin/env python3
# config_validator.py

import yaml
import jsonschema
import sys

def validate_config(config_path: str, schema_path: str) -> bool:
    """验证配置文件是否符合schema"""
    
    # 加载配置
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # 加载schema
    with open(schema_path, 'r') as f:
        schema = yaml.safe_load(f)
    
    try:
        jsonschema.validate(config, schema)
        print(f"✓ Config {config_path} is valid")
        return True
    except jsonschema.ValidationError as e:
        print(f"✗ Config validation failed: {e.message}")
        print(f"  Path: {'.'.join(str(p) for p in e.path)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: config_validator.py <config.yaml> <schema.yaml>")
        sys.exit(1)
    
    if validate_config(sys.argv[1], sys.argv[2]):
        sys.exit(0)
    else:
        sys.exit(1)
```

## 部署配置

### Docker配置 (docker-compose.yaml)
```yaml
version: '3.8'

services:
  # TimescaleDB服务
  timescaledb:
    image: timescale/timescaledb:latest-pg14
    environment:
      POSTGRES_DB: pplustrader
      POSTGRES_USER: pplususer
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
      - ./config/timescaledb.conf:/etc/postgresql/postgresql.conf
    ports:
      - "5432:5432"
    restart: unless-stopped

  # PlusPlusTrader应用
  pplustrader:
    build: .
    environment:
      ENVIRONMENT: production
      DB_PASSWORD: ${DB_PASSWORD}
      BINANCE_API_KEY: ${BINANCE_API_KEY}
      BINANCE_API_SECRET: ${BINANCE_API_SECRET}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config/production.yaml:/app/config.yaml:ro
    depends_on:
      - timescaledb
    restart: unless-stopped

  # 监控服务 (可选)
  monitoring:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/provisioning:/etc/grafana/provisioning
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}

volumes:
  timescaledb_data:
  grafana_data:
```

### Kubernetes配置 (configmap.yaml)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pplustrader-config
data:
  config.yaml: |
    metadata:
      version: "1.0.0"
      environment: "production"
    
    storage:
      timescaledb:
        host: "timescaledb-service"
        database: "pplustrader"
        username: "pplususer"
    # ... 其他配置
    
  strategy-ma-cross.yaml: |
    metadata:
      strategy_name: "ma_cross"
      version: "1.0.0"
    # ... 策略配置
```

## 最佳实践

### 1. 配置管理
- **版本控制**: 所有配置文件纳入版本控制
- **环境分离**: 不同环境使用不同配置
- **敏感信息**: 敏感信息通过环境变量或密钥管理服务提供
- **文档**: 为每个配置项提供详细文档

### 2. 配置变更
- **变更记录**: 记录配置变更的原因和时间
- **逐步发布**: 生产环境配置变更逐步进行
- **回滚计划**: 准备配置回滚方案
- **测试**: 配置变更前在测试环境验证

### 3. 性能考虑
- **缓存**: 缓存解析后的配置，避免频繁解析
- **懒加载**: 大型配置按需加载
- **分片**: 超大配置分片存储

## 总结

PlusPlusTrader采用分层、模块化的配置系统：
1. **主配置文件**: 系统级配置，YAML格式
2. **策略配置文件**: 策略级配置，支持继承和覆盖
3. **运行时配置**: 动态配置，JSON格式

配置系统支持：
- ✅ 环境变量替换
- ✅ 配置继承和合并
- ✅ 热重载
- ✅ 敏感信息加密
- ✅ 格式验证
- ✅ 多环境支持

这种设计提供了灵活性、安全性和可维护性，能够满足从开发到生产的不同需求。