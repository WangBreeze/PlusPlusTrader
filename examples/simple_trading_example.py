#!/usr/bin/env python3
"""
简单的交易示例
展示如何使用PlusPlusTrader Python模块
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'build/python/bindings'))

print("=" * 70)
print("PlusPlusTrader - 简单交易示例")
print("=" * 70)

# 导入模块
import pplustrader as ppt

print(f"使用版本: {ppt.__version__}")
print(f"模块描述: {ppt.__description__}")
print()

# 1. 创建市场数据
print("1. 创建市场数据")
print("-" * 40)

# 创建多个tick数据
ticks = []
for i in range(10):
    tick = ppt.core.TickData()
    tick.symbol = "AAPL"
    tick.timestamp = 1000 + i * 100  # 模拟时间戳
    tick.open = 150.0 + i * 0.5
    tick.high = 151.0 + i * 0.5
    tick.low = 149.5 + i * 0.5
    tick.close = 150.5 + i * 0.5
    tick.volume = 1000000 + i * 100000
    ticks.append(tick)
    print(f"  Tick {i+1}: {tick.symbol} @ {tick.close:.2f}, 成交量: {tick.volume:,}")

print()

# 2. 创建订单
print("2. 创建交易订单")
print("-" * 40)

# 市价单
market_order = ppt.core.Order()
market_order.order_id = "MKT_001"
market_order.symbol = "AAPL"
market_order.type = ppt.core.OrderType.MARKET
market_order.side = ppt.core.OrderSide.BUY
market_order.price = 0.0  # 市价单价格为0
market_order.quantity = 100
market_order.status = ppt.core.OrderStatus.PENDING
market_order.created_at = 1234567890.0

# 限价单
limit_order = ppt.core.Order()
limit_order.order_id = "LMT_001"
limit_order.symbol = "AAPL"
limit_order.type = ppt.core.OrderType.LIMIT
limit_order.side = ppt.core.OrderSide.SELL
limit_order.price = 155.0
limit_order.quantity = 50
limit_order.status = ppt.core.OrderStatus.PENDING
limit_order.created_at = 1234567890.0

print(f"  市价单: {market_order}")
print(f"  限价单: {limit_order}")

print()

# 3. 管理账户信息
print("3. 管理账户信息")
print("-" * 40)

account = ppt.core.AccountInfo()
account.account_id = "TRADER_001"
account.equity = 100000.0
account.margin = 20000.0
account.free_margin = 80000.0
account.margin_level = 500.0
account.realized_pnl = 5000.0
account.unrealized_pnl = 2000.0

print(f"  账户ID: {account.account_id}")
print(f"  权益: ${account.equity:,.2f}")
print(f"  保证金: ${account.margin:,.2f}")
print(f"  可用保证金: ${account.free_margin:,.2f}")
print(f"  保证金水平: {account.margin_level:.1f}%")
print(f"  已实现盈亏: ${account.realized_pnl:,.2f}")
print(f"  未实现盈亏: ${account.unrealized_pnl:,.2f}")

print()

# 4. 技术分析
print("4. 技术分析")
print("-" * 40)

# 提取价格序列
prices = [tick.close for tick in ticks]
print(f"  价格序列: {[f'{p:.2f}' for p in prices]}")

# 计算移动平均
sma_5 = ppt.simple_moving_average(prices, 5)
sma_10 = ppt.simple_moving_average(prices, 3)  # 使用3日移动平均，因为数据点有限

print(f"  5日移动平均: {[f'{sma:.2f}' for sma in sma_5]}")
print(f"  3日移动平均: {[f'{sma:.2f}' for sma in sma_10]}")

# 简单的交易信号
if len(sma_5) >= 2 and len(sma_10) >= 2:
    last_sma_5 = sma_5[-1]
    last_sma_10 = sma_10[-1]
    
    if last_sma_5 > last_sma_10:
        signal = "买入信号 (5日线上穿3日线)"
    elif last_sma_5 < last_sma_10:
        signal = "卖出信号 (5日线下穿3日线)"
    else:
        signal = "持有信号 (均线交叉)"
    
    print(f"  交易信号: {signal}")
    print(f"  当前价格: {prices[-1]:.2f}")
    print(f"  5日SMA: {last_sma_5:.2f}")
    print(f"  3日SMA: {last_sma_10:.2f}")

print()

# 5. 回测模拟
print("5. 回测模拟")
print("-" * 40)

initial_capital = 100000.0
final_capital = ppt.simulate_backtest(initial_capital, prices)
profit = final_capital - initial_capital
profit_percent = (profit / initial_capital) * 100

print(f"  初始资本: ${initial_capital:,.2f}")
print(f"  最终资本: ${final_capital:,.2f}")
print(f"  总利润: ${profit:,.2f}")
print(f"  收益率: {profit_percent:.2f}%")

print()

# 6. 使用样本数据
print("6. 使用样本数据")
print("-" * 40)

sample_tick = ppt.create_tick_data()
sample_order = ppt.create_order()
sample_account = ppt.create_account_info()

print(f"  样本Tick数据: {sample_tick}")
print(f"  样本订单: {sample_order}")
print(f"  样本账户: {sample_account}")

print()

# 7. 总结
print("7. 功能总结")
print("-" * 40)

print("✅ 已实现的功能:")
print("  - 市场数据结构 (TickData)")
print("  - 订单管理 (Order)")
print("  - 账户管理 (AccountInfo)")
print("  - 订单类型枚举 (OrderType)")
print("  - 买卖方向枚举 (OrderSide)")
print("  - 订单状态枚举 (OrderStatus)")
print("  - 技术指标 (简单移动平均)")
print("  - 回测模拟")
print("  - 样本数据生成")

print()
print("🚀 下一步计划:")
print("  - 实现更多技术指标 (MACD, RSI, Bollinger Bands)")
print("  - 完整的回测引擎")
print("  - 实时数据适配器")
print("  - 风险管理模块")
print("  - 策略框架")

print()
print("=" * 70)
print("示例完成! PlusPlusTrader Python模块工作正常 🎉")
print("=" * 70)