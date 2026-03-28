# PlusPlusTrader Python Bindings

Python bindings for the PlusPlusTrader C++ algorithmic trading framework.

## Features

- **Full C++ API access**: Access all core classes from Python
- **Strategy development**: Implement trading strategies in Python
- **Backtesting**: Run backtests with Python strategies
- **Data analysis**: Use Python's data science ecosystem with trading data
- **Visualization**: Integrate with Matplotlib, Plotly, etc.

## Installation

### Prerequisites

- Python 3.7 or higher
- CMake 3.12 or higher
- C++ compiler with C++17 support
- Git (for fetching pybind11)

### Building from source

```bash
# Clone the repository
git clone https://github.com/yourusername/PlusPlusTrader.git
cd PlusPlusTrader

# Create build directory
mkdir build && cd build

# Configure with Python bindings
cmake .. -DBUILD_PYTHON_BINDINGS=ON

# Build
make -j4

# Install (optional)
sudo make install
```

### Development installation

For development, you can add the build directory to your Python path:

```python
import sys
sys.path.insert(0, '/path/to/PlusPlusTrader/build/python/bindings')
import pplustrader
```

## Quick Start

### Basic usage

```python
import pplustrader

# Create market data
tick = pplustrader.TickData()
tick.symbol = "AAPL"
tick.close = 150.25
tick.volume = 1000000

# Create an order
order = pplustrader.Order()
order.symbol = "AAPL"
order.side = pplustrader.OrderSide.BUY
order.type = pplustrader.OrderType.MARKET
order.quantity = 100
order.price = 150.25

# Create indicators
ma = pplustrader.create_moving_average(20)
ma.update(150.0)
ma.update(151.0)
ma.update(152.0)

if ma.is_ready():
    print(f"Moving average: {ma.get_value()}")
```

### Creating a strategy

```python
import pplustrader

class SimpleStrategy:
    def __init__(self):
        self.ma = pplustrader.create_moving_average(20)
        self.position = 0
        
    def on_tick(self, tick):
        self.ma.update(tick.close)
        
        if not self.ma.is_ready():
            return None
            
        ma_value = self.ma.get_value()
        
        if tick.close > ma_value and self.position <= 0:
            # Buy signal
            order = pplustrader.Order()
            order.symbol = tick.symbol
            order.side = pplustrader.OrderSide.BUY
            order.type = pplustrader.OrderType.MARKET
            order.quantity = 100
            return order
            
        elif tick.close < ma_value and self.position >= 0:
            # Sell signal
            order = pplustrader.Order()
            order.symbol = tick.symbol
            order.side = pplustrader.OrderSide.SELL
            order.type = pplustrader.OrderType.MARKET
            order.quantity = 100
            return order
            
        return None
```

### Running a backtest

```python
import pplustrader

# Create backtest engine
engine = pplustrader.BacktestEngine()

# Create data source
data_source = pplustrader.create_csv_data_source()
engine.set_data_source(data_source)

# Create and set strategy
strategy = SimpleStrategy()

# Run backtest (simplified)
# Note: Full backtest integration requires additional setup
```

## API Reference

### Core Classes

- **TickData**: Market data point
- **Order**: Trading order
- **AccountInfo**: Account information
- **BaseStrategy**: Base strategy class (abstract)

### Enums

- **OrderType**: MARKET, LIMIT, STOP, STOP_LIMIT
- **OrderSide**: BUY, SELL
- **OrderStatus**: UNKNOWN, PENDING, SUBMITTED, FILLED, PARTIALLY_FILLED, CANCELLED, REJECTED

### Indicators

- **Indicator**: Base indicator class
- **MA**: Moving average
- **MACD**: Moving Average Convergence Divergence
- **RSI**: Relative Strength Index

### Data Sources

- **DataFeed**: Base data feed class
- **CSVDataSource**: CSV file data source

### Backtest

- **BacktestEngine**: Backtesting engine
- **SimulatedExchange**: Simulated exchange for backtesting

## Examples

See the `examples/` directory for complete examples:

1. `simple_strategy.py` - Basic strategy implementation
2. `backtest_example.py` - Backtest simulation

## Advanced Usage

### Custom indicators in Python

You can create custom indicators by extending the C++ Indicator class via pybind11, 
or implement them purely in Python.

### Integration with pandas

```python
import pandas as pd
import pplustrader

# Convert pandas DataFrame to ticks
def df_to_ticks(df, symbol="AAPL"):
    ticks = []
    for idx, row in df.iterrows():
        tick = pplustrader.TickData()
        tick.symbol = symbol
        tick.timestamp = int(idx.timestamp())
        tick.open = row['Open']
        tick.high = row['High']
        tick.low = row['Low']
        tick.close = row['Close']
        tick.volume = row['Volume']
        ticks.append(tick)
    return ticks
```

### Real-time trading

For real-time trading, you would need to implement exchange-specific adapters.
The framework provides the abstraction; you provide the implementation.

## Troubleshooting

### Import errors

If you get `ImportError: No module named 'pplustrader'`:

1. Make sure you've built the Python bindings
2. Add the build directory to your Python path:
   ```python
   import sys
   sys.path.insert(0, '/path/to/PlusPlusTrader/build/python/bindings')
   ```

### Build errors

If CMake can't find Python:

```bash
# Specify Python executable
cmake .. -DBUILD_PYTHON_BINDINGS=ON -DPython3_EXECUTABLE=/usr/bin/python3
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For questions and support, please open an issue on GitHub.