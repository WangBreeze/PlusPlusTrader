#!/usr/bin/env python3
"""
Simple Python strategy example for PlusPlusTrader
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

class SimplePythonStrategy:
    """
    A simple Python strategy that uses the C++ base class
    """
    def __init__(self, name="PythonStrategy"):
        self.name = name
        self.ma_period = 20
        self.ma = None
        self.position = 0
        
    def initialize(self):
        """Initialize the strategy"""
        print(f"[{self.name}] Initializing Python strategy")
        # Create a moving average indicator
        self.ma = pplustrader.create_moving_average(self.ma_period)
        return True
        
    def on_tick(self, tick):
        """Handle new market data"""
        if not self.ma:
            return
            
        # Update the moving average
        self.ma.update(tick.close)
        
        if not self.ma.is_ready():
            return
            
        ma_value = self.ma.get_value()
        
        # Simple crossover strategy
        if tick.close > ma_value and self.position <= 0:
            # Buy signal
            print(f"[{self.name}] Buy signal: Price {tick.close} > MA {ma_value}")
            # Create a buy order
            order = pplustrader.Order()
            order.symbol = tick.symbol
            order.side = pplustrader.OrderSide.BUY
            order.type = pplustrader.OrderType.MARKET
            order.quantity = 100
            order.status = pplustrader.OrderStatus.PENDING
            
            # In a real implementation, you would submit this order
            # For now, just log it
            self.position = 100
            return order
            
        elif tick.close < ma_value and self.position >= 0:
            # Sell signal
            print(f"[{self.name}] Sell signal: Price {tick.close} < MA {ma_value}")
            # Create a sell order
            order = pplustrader.Order()
            order.symbol = tick.symbol
            order.side = pplustrader.OrderSide.SELL
            order.type = pplustrader.OrderType.MARKET
            order.quantity = 100
            order.status = pplustrader.OrderStatus.PENDING
            
            # In a real implementation, you would submit this order
            # For now, just log it
            self.position = -100
            return order
            
        return None
        
    def on_order(self, order):
        """Handle order updates"""
        print(f"[{self.name}] Order update: {order.order_id} - {order.status}")
        
        if order.status == pplustrader.OrderStatus.FILLED:
            if order.side == pplustrader.OrderSide.BUY:
                print(f"  Bought {order.quantity} of {order.symbol} at {order.price}")
            else:
                print(f"  Sold {order.quantity} of {order.symbol} at {order.price}")

def test_basic_functionality():
    """Test basic functionality of the Python bindings"""
    print("=" * 60)
    print("Testing PlusPlusTrader Python bindings")
    print("=" * 60)
    
    # Test creating objects
    print("\n1. Creating objects...")
    
    # Create a tick
    tick = pplustrader.TickData()
    tick.symbol = "AAPL"
    tick.timestamp = 1234567890
    tick.open = 150.0
    tick.high = 152.0
    tick.low = 149.5
    tick.close = 151.5
    tick.volume = 1000000
    
    print(f"Created tick: {tick.symbol} @ {tick.close}")
    
    # Create an order
    order = pplustrader.Order()
    order.order_id = "TEST_001"
    order.symbol = "AAPL"
    order.side = pplustrader.OrderSide.BUY
    order.type = pplustrader.OrderType.MARKET
    order.quantity = 100
    order.price = 151.5
    order.status = pplustrader.OrderStatus.PENDING
    
    print(f"Created order: {order.order_id} for {order.quantity} shares")
    
    # Create account info
    account = pplustrader.AccountInfo()
    account.account_id = "ACC_001"
    account.equity = 100000.0
    account.free_margin = 80000.0
    
    print(f"Created account: {account.account_id} with equity {account.equity}")
    
    # Test enums
    print("\n2. Testing enums...")
    print(f"OrderSide.BUY = {pplustrader.OrderSide.BUY}")
    print(f"OrderType.MARKET = {pplustrader.OrderType.MARKET}")
    print(f"OrderStatus.PENDING = {pplustrader.OrderStatus.PENDING}")
    
    # Test strategy
    print("\n3. Testing strategy...")
    strategy = SimplePythonStrategy("TestStrategy")
    if strategy.initialize():
        print("Strategy initialized successfully")
        
        # Test with some ticks
        for i in range(30):
            tick.close = 150.0 + i * 0.5  # Simulate rising prices
            result = strategy.on_tick(tick)
            if result:
                print(f"  Generated order at price {tick.close}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_basic_functionality()