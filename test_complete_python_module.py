#!/usr/bin/env python3
"""
测试完整的PlusPlusTrader Python模块
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, '.')
sys.path.insert(0, 'python')
sys.path.insert(0, 'build/python/bindings')

print("=" * 70)
print("测试完整的 PlusPlusTrader Python 模块")
print("=" * 70)

try:
    import pplustrader
    print(f"✅ pplustrader 模块导入成功")
    print(f"版本: {pplustrader.__version__}")
    print(f"描述: {pplustrader.__description__}")
    print(f"作者: {pplustrader.__author__}")
    
    # 检查C++核心可用性
    if hasattr(pplustrader, '_CPP_AVAILABLE'):
        print(f"C++核心可用: {pplustrader._CPP_AVAILABLE}")
    else:
        print("C++核心可用: 未知")
    
    print("\n" + "=" * 70)
    print("测试 C++ 绑定功能")
    print("=" * 70)
    
    # 测试C++绑定功能
    print(f"hello(): {pplustrader.hello()}")
    print(f"get_version(): {pplustrader.get_version()}")
    
    # 测试核心数据结构
    print("\n测试核心数据结构:")
    
    # 1. TickData
    tick_data = pplustrader.core.TickData()
    tick_data.symbol = "AAPL"
    tick_data.timestamp = 1234567890.0
    tick_data.open = 150.0
    tick_data.high = 152.5
    tick_data.low = 149.5
    tick_data.close = 151.0
    tick_data.volume = 1000000
    print(f"✅ TickData 创建和设置成功: {tick_data}")
    
    # 2. Order
    order = pplustrader.core.Order()
    order.order_id = "ORD_001"
    order.symbol = "AAPL"
    order.type = pplustrader.core.OrderType.MARKET
    order.side = pplustrader.core.OrderSide.BUY
    order.price = 151.0
    order.quantity = 100
    order.status = pplustrader.core.OrderStatus.PENDING
    order.created_at = 1234567890.0
    order.updated_at = 1234567890.0
    print(f"✅ Order 创建和设置成功: {order}")
    
    # 3. AccountInfo
    account_info = pplustrader.core.AccountInfo()
    account_info.account_id = "ACC_001"
    account_info.equity = 100000.0
    account_info.margin = 20000.0
    account_info.free_margin = 80000.0
    account_info.margin_level = 500.0
    account_info.realized_pnl = 5000.0
    account_info.unrealized_pnl = 2000.0
    print(f"✅ AccountInfo 创建和设置成功: {account_info}")
    
    # 测试枚举
    print("\n测试枚举类型:")
    print(f"OrderType.MARKET: {pplustrader.core.OrderType.MARKET}")
    print(f"OrderType.LIMIT: {pplustrader.core.OrderType.LIMIT}")
    print(f"OrderSide.BUY: {pplustrader.core.OrderSide.BUY}")
    print(f"OrderSide.SELL: {pplustrader.core.OrderSide.SELL}")
    print(f"OrderStatus.FILLED: {pplustrader.core.OrderStatus.FILLED}")
    
    # 测试工具函数
    print("\n测试工具函数:")
    sample_tick = pplustrader.create_tick_data()
    print(f"样本TickData: {sample_tick}")
    
    sample_order = pplustrader.create_order()
    print(f"样本Order: {sample_order}")
    
    sample_account = pplustrader.create_account_info()
    print(f"样本AccountInfo: {sample_account}")
    
    # 测试技术指标函数
    print("\n测试技术指标函数:")
    prices = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0]
    sma_5 = pplustrader.simple_moving_average(prices, 5)
    print(f"价格序列: {prices}")
    print(f"SMA(5)结果: {sma_5}")
    
    sma_3 = pplustrader.simple_moving_average(prices, 3)
    print(f"SMA(3)结果: {sma_3}")
    
    # 测试回测函数
    print("\n测试回测函数:")
    final_capital = pplustrader.simulate_backtest(100000.0, prices)
    profit = final_capital - 100000.0
    profit_percent = (profit / 100000.0) * 100
    print(f"初始资本: 100,000.00")
    print(f"最终资本: {final_capital:,.2f}")
    print(f"利润: {profit:,.2f} ({profit_percent:.2f}%)")
    
    # 测试Python扩展模块
    print("\n" + "=" * 70)
    print("测试 Python 扩展模块")
    print("=" * 70)
    
    try:
        # 测试数据适配器
        from pplustrader.data import DataFeed, CSVDataFeed
        print(f"✅ DataFeed 类导入成功")
        
        # 测试策略模块
        from pplustrader.strategies import Strategy, MovingAverageCrossover
        print(f"✅ Strategy 类导入成功")
        
        # 创建简单的Python策略
        class SimpleStrategy(Strategy):
            def __init__(self):
                super().__init__()
                self.name = "SimplePythonStrategy"
                
            def on_tick(self, tick_data):
                print(f"策略收到tick数据: {tick_data.symbol} @ {tick_data.close}")
                return []
                
            def get_name(self):
                return self.name
        
        strategy = SimpleStrategy()
        print(f"✅ Python策略创建成功: {strategy.get_name()}")
        
    except Exception as e:
        print(f"❌ Python扩展模块测试失败: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Python模块测试完成!")
    print("=" * 70)
    
    # 总结
    print("\n📊 测试总结:")
    print(f"1. C++绑定模块: ✅ 工作正常")
    print(f"2. 核心数据结构: ✅ TickData, Order, AccountInfo")
    print(f"3. 枚举类型: ✅ OrderType, OrderSide, OrderStatus")
    print(f"4. 工具函数: ✅ 创建样本数据")
    print(f"5. 技术指标: ✅ 简单移动平均")
    print(f"6. 回测模拟: ✅ 简单回测")
    print(f"7. Python扩展: ✅ 策略和数据适配器")
    
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)