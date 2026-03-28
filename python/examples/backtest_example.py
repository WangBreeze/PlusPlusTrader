#!/usr/bin/env python3
"""
Backtest example for PlusPlusTrader
"""

import sys
import os

# Add the bindings directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pplustrader
    print("Successfully imported pplustrader module")
except ImportError as e:
    print(f"Failed to import pplustrader: {e}")
    print("Make sure the module is built and in your Python path")
    sys.exit(1)

class MovingAverageCrossStrategy:
    """
    Moving average crossover strategy implemented in Python
    """
    def __init__(self, fast_period=10, slow_period=30):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.fast_ma = None
        self.slow_ma = None
        self.position = 0
        self.trades = []
        
    def initialize(self):
        """Initialize indicators"""
        self.fast_ma = pplustrader.create_moving_average(self.fast_period)
        self.slow_ma = pplustrader.create_moving_average(self.slow_period)
        return True
        
    def on_tick(self, tick):
        """Handle new market data"""
        if not self.fast_ma or not self.slow_ma:
            return None
            
        # Update indicators
        self.fast_ma.update(tick.close)
        self.slow_ma.update(tick.close)
        
        if not self.fast_ma.is_ready() or not self.slow_ma.is_ready():
            return None
            
        fast_value = self.fast_ma.get_value()
        slow_value = self.slow_ma.get_value()
        
        # Crossover logic
        order = None
        
        if fast_value > slow_value and self.position <= 0:
            # Golden cross - buy signal
            print(f"[MA Cross] BUY: Fast MA ({fast_value:.2f}) > Slow MA ({slow_value:.2f})")
            
            order = pplustrader.Order()
            order.symbol = tick.symbol
            order.side = pplustrader.OrderSide.BUY
            order.type = pplustrader.OrderType.MARKET
            order.quantity = 100
            order.price = tick.close
            order.status = pplustrader.OrderStatus.PENDING
            
            self.position = 100
            self.trades.append({
                'type': 'BUY',
                'price': tick.close,
                'time': tick.timestamp
            })
            
        elif fast_value < slow_value and self.position >= 0:
            # Death cross - sell signal
            print(f"[MA Cross] SELL: Fast MA ({fast_value:.2f}) < Slow MA ({slow_value:.2f})")
            
            order = pplustrader.Order()
            order.symbol = tick.symbol
            order.side = pplustrader.OrderSide.SELL
            order.type = pplustrader.OrderType.MARKET
            order.quantity = 100
            order.price = tick.close
            order.status = pplustrader.OrderStatus.PENDING
            
            self.position = -100
            self.trades.append({
                'type': 'SELL',
                'price': tick.close,
                'time': tick.timestamp
            })
            
        return order
        
    def on_order(self, order):
        """Handle order updates"""
        if order.status == pplustrader.OrderStatus.FILLED:
            print(f"[MA Cross] Order filled: {order.side} {order.quantity} @ {order.price}")
        elif order.status == pplustrader.OrderStatus.REJECTED:
            print(f"[MA Cross] Order rejected: {order.order_id}")
            
    def get_results(self):
        """Get strategy results"""
        return {
            'total_trades': len(self.trades),
            'position': self.position,
            'trades': self.trades
        }

def run_backtest_example():
    """Run a simple backtest example"""
    print("=" * 60)
    print("PlusPlusTrader Backtest Example")
    print("=" * 60)
    
    # Create a backtest engine
    engine = pplustrader.BacktestEngine()
    print("Created backtest engine")
    
    # Create a CSV data source
    data_source = pplustrader.create_csv_data_source()
    print("Created CSV data source")
    
    # Set data source (in a real example, we would load actual data)
    engine.set_data_source(data_source)
    
    # Create and set strategy
    strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=30)
    # Note: In a real implementation, we would need to wrap the Python strategy
    # in a C++ compatible wrapper. For now, we'll simulate the backtest.
    
    print("\nSimulating backtest with generated data...")
    
    # Generate some sample data
    import random
    ticks = []
    
    # Create 100 ticks of sample data
    base_price = 100.0
    for i in range(100):
        tick = pplustrader.TickData()
        tick.symbol = "TEST"
        tick.timestamp = 1609459200 + i * 3600  # 1-hour intervals
        tick.open = base_price + random.uniform(-2, 2)
        tick.high = tick.open + random.uniform(0, 3)
        tick.low = tick.open - random.uniform(0, 3)
        tick.close = tick.open + random.uniform(-1, 1)
        tick.volume = 10000 + random.randint(-2000, 2000)
        ticks.append(tick)
        
        # Update base price with some drift
        base_price += random.uniform(-0.5, 0.5)
    
    # Run strategy on the ticks
    strategy.initialize()
    
    for i, tick in enumerate(ticks):
        if i % 20 == 0:
            print(f"\nTick {i}: Price = {tick.close:.2f}")
        
        order = strategy.on_tick(tick)
        if order:
            # Simulate order execution
            order.status = pplustrader.OrderStatus.FILLED
            strategy.on_order(order)
    
    # Show results
    results = strategy.get_results()
    print("\n" + "=" * 60)
    print("Backtest Results:")
    print(f"  Total trades: {results['total_trades']}")
    print(f"  Final position: {results['position']}")
    
    if results['trades']:
        print("\n  Trade history:")
        for i, trade in enumerate(results['trades']):
            print(f"    Trade {i+1}: {trade['type']} @ {trade['price']:.2f}")
    
    print("\n" + "=" * 60)
    print("Backtest example completed!")
    print("=" * 60)
    
    # Test additional functionality
    print("\nTesting additional functionality...")
    
    # Test creating different order types
    limit_order = pplustrader.Order()
    limit_order.symbol = "AAPL"
    limit_order.side = pplustrader.OrderSide.BUY
    limit_order.type = pplustrader.OrderType.LIMIT
    limit_order.price = 150.0
    limit_order.quantity = 50
    limit_order.status = pplustrader.OrderStatus.PENDING
    
    print(f"Created limit order: {limit_order.quantity} shares @ {limit_order.price}")
    
    # Test account info
    account = pplustrader.AccountInfo()
    account.account_id = "BACKTEST_ACC"
    account.equity = 100000.0
    account.free_margin = 85000.0
    account.margin = 15000.0
    
    print(f"Created account: {account.account_id} (Equity: ${account.equity:.2f})")
    
    return True

if __name__ == "__main__":
    run_backtest_example()