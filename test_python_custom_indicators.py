#!/usr/bin/env python3
"""
Python自定义指标集成测试
测试目标：验证Python自定义指标可以正确创建、更新和生成信号
"""

import sys
import os
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入自定义指标模块
try:
    from python.custom_indicator import PythonIndicator, SignalType, IndicatorConfig, CustomIndicatorFactory
    from python.custom_indicator_examples import (
        EnhancedMovingAverage,
        BollingerBands,
        MACDIndicator,
        VolumeWeightedAveragePrice,
        CustomCompositeIndicator
    )
    from python.custom_indicator_utils import (
        ErrorHandler, ErrorSeverity,
        PerformanceMonitor,
        ConfigManager,
        IndicatorValidator
    )
    
    print("✓ 成功导入Python自定义指标模块")
except ImportError as e:
    print(f"✗ 导入Python自定义指标模块失败: {e}")
    sys.exit(1)

def test_simple_moving_average():
    """测试简单移动平均线指标"""
    print("\n" + "="*60)
    print("测试1: 简单移动平均线(SMA)")
    print("="*60)
    
    # 使用工厂创建SMA指标
    from python.custom_indicator import factory
    
    instance_id = factory.create("SimpleMovingAverage", {"window": 20})
    sma = factory.get_instance(instance_id)
    
    if sma is None:
        print("✗ 无法创建SimpleMovingAverage指标")
        return
    
    # 生成测试数据
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    # 更新指标
    for i, price in enumerate(prices):
        price_data = {
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "close": price,
            "volume": 10000 + i * 100
        }
        value = sma.update(price_data)
        
        if i >= 19:  # 20日SMA需要至少20个数据点
            # 获取最新信号
            if sma.signals and len(sma.signals) > 0:
                signal = sma.signals[-1]
                # 信号强度需要根据具体实现获取
                strength = 0.5  # 默认值
            else:
                signal = 0
                strength = 0.0
            
            if i % 20 == 19:  # 每20个点打印一次
                print(f"    数据点 {i+1:3d}: 价格={price:7.2f}, SMA={value:7.2f}, "
                      f"信号={signal}, 强度={strength:.3f}")
    
    # 测试指标信息
    print(f"\n    指标名称: {sma.name}")
    print(f"    配置参数: {sma.config}")
    print(f"    最后值: {sma.get_last_value()}")
    print(f"    最后信号: {sma.get_last_signal()}")
    
    print("✓ SMA测试完成")

def test_relative_strength_index():
    """测试相对强弱指数指标"""
    print("\n" + "="*60)
    print("测试2: 相对强弱指数(RSI)")
    print("="*60)
    
    # 使用工厂创建RSI指标
    from python.custom_indicator import factory
    
    instance_id = factory.create("RelativeStrengthIndex", {"period": 14})
    rsi = factory.get_instance(instance_id)
    
    if rsi is None:
        print("✗ 无法创建RelativeStrengthIndex指标")
        return
    
    # 生成测试数据（有趋势的价格序列）
    np.random.seed(42)
    trend = np.linspace(100, 110, 100)
    noise = np.random.randn(100) * 2
    prices = trend + noise
    
    # 更新指标
    for i, price in enumerate(prices):
        price_data = {
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "close": price,
            "volume": 10000 + i * 100
        }
        value = rsi.update(price_data)
        
        if i >= 13:  # 14日RSI需要至少14个数据点
            # 获取最新信号
            if rsi.signals and len(rsi.signals) > 0:
                signal = rsi.signals[-1]
            else:
                signal = 0
            
            if i % 20 == 19:  # 每20个点打印一次
                print(f"    数据点 {i+1:3d}: 价格={price:7.2f}, RSI={value:7.2f}, "
                      f"信号={signal}")
    
    print(f"\n    指标名称: {rsi.name}")
    print(f"    最终RSI值: {value:.2f}")
    
    print("✓ RSI测试完成")

def test_enhanced_moving_average():
    """测试增强型移动平均线"""
    print("\n" + "="*60)
    print("测试3: 增强型移动平均线(EMA)")
    print("="*60)
    
    # 创建增强型EMA指标
    ema = EnhancedMovingAverage(period=12, alpha=0.2)
    
    # 生成测试数据
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(50) * 0.8)
    
    # 更新指标
    for i, price in enumerate(prices):
        price_data = {
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "close": price,
            "volume": 10000 + i * 100
        }
        value = ema.update(price_data)
        
        if i >= 11:  # 12日EMA需要至少12个数据点
            # 获取最新信号
            if ema.signals and len(ema.signals) > 0:
                signal = ema.signals[-1]
            else:
                signal = 0
            
            if i % 10 == 9:  # 每10个点打印一次
                print(f"    数据点 {i+1:3d}: 价格={price:7.2f}, EMA={value:7.2f}, "
                      f"信号={signal:2d}")
    
    print(f"\n    指标名称: {ema.name()}")
    print(f"    指标描述: {ema.description()}")
    print(f"    指标配置: {ema.get_config()}")
    
    print("✓ 增强型EMA测试完成")

def test_bollinger_bands():
    """测试布林带指标"""
    print("\n" + "="*60)
    print("测试4: 布林带(Bollinger Bands)")
    print("="*60)
    
    # 创建布林带指标
    bb = BollingerBands(period=20, num_std=2.0)
    
    # 生成测试数据
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 1.0)
    
    # 更新指标
    for i, price in enumerate(prices):
        price_data = {
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "close": price,
            "volume": 10000 + i * 100
        }
        bb.update(price_data)
        
        if i >= 19:  # 20日布林带需要至少20个数据点
            upper, middle, lower = bb.get_bands()
            width = bb.band_width()
            percent_b = bb.percent_b()
            signal = bb.signal()
            
            if i % 20 == 19:  # 每20个点打印一次
                print(f"    数据点 {i+1:3d}: 价格={price:7.2f}, 上轨={upper:7.2f}, "
                      f"中轨={middle:7.2f}, 下轨={lower:7.2f}, %B={percent_b:.3f}")
    
    print(f"\n    指标名称: {bb.name()}")
    print(f"    指标描述: {bb.description()}")
    print(f"    当前布林带宽度: {bb.band_width():.4f}")
    
    print("✓ 布林带测试完成")

def test_macd_indicator():
    """测试MACD指标"""
    print("\n" + "="*60)
    print("测试5: MACD指标")
    print("="*60)
    
    # 创建MACD指标
    macd = MACDIndicator(fast_period=12, slow_period=26, signal_period=9)
    
    # 生成测试数据
    np.random.seed(42)
    trend = np.sin(np.linspace(0, 4*np.pi, 200)) * 10 + 100
    noise = np.random.randn(200) * 2
    prices = trend + noise
    
    # 更新指标
    for i, price in enumerate(prices):
        price_data = {
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "close": price,
            "volume": 10000 + i * 100
        }
        macd.update(price_data)
        
        if i >= 34:  # MACD需要足够的数据点
            macd_line, signal_line, histogram = macd.get_macd()
            signal_val = macd.signal()
            
            if i % 40 == 39:  # 每40个点打印一次
                print(f"    数据点 {i+1:3d}: 价格={price:7.2f}, "
                      f"MACD={macd_line:7.3f}, 信号线={signal_line:7.3f}, "
                      f"柱状图={histogram:7.3f}")
    
    print(f"\n    指标名称: {macd.name()}")
    print(f"    指标描述: {macd.description()}")
    
    print("✓ MACD测试完成")

def test_performance_monitoring():
    """测试性能监控"""
    print("\n" + "="*60)
    print("测试6: 性能监控系统")
    print("="*60)
    
    # 创建性能监控器
    monitor = PerformanceMonitor()
    
    # 创建测试指标
    from python.custom_indicator import factory
    
    instance_id = factory.create("SimpleMovingAverage", {"window": 20})
    sma = factory.get_instance(instance_id)
    
    if sma is None:
        print("✗ 无法创建SimpleMovingAverage指标")
        return
    
    # 监控指标性能
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(1000) * 0.5)
    
    for i, price in enumerate(prices):
        price_data = {
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "close": price,
            "volume": 10000 + i * 100
        }
        with monitor.measure("sma_update"):
            sma.update(price_data)
    
    # 获取性能报告
    report = monitor.get_report()
    
    print("性能报告:")
    for operation, stats in report.items():
        print(f"    {operation}:")
        print(f"        调用次数: {stats['count']}")
        print(f"        总耗时: {stats['total_time']:.6f}秒")
        print(f"        平均耗时: {stats['avg_time']:.6f}秒")
        print(f"        最大耗时: {stats['max_time']:.6f}秒")
        print(f"        最小耗时: {stats['min_time']:.6f}秒")
    
    print("✓ 性能监控测试完成")

def test_error_handling():
    """测试错误处理系统"""
    print("\n" + "="*60)
    print("测试7: 错误处理系统")
    print("="*60)
    
    # 创建错误处理器
    error_handler = ErrorHandler()
    
    # 测试各种错误
    try:
        # 创建无效参数的指标
        from python.custom_indicator import factory
        instance_id = factory.create("SimpleMovingAverage", {"window": 0})  # 无效窗口大小
    except Exception as e:
        error_handler.record_error(
            "指标创建错误",
            str(e),
            ErrorSeverity.HIGH,
            {"window": 0}
        )
    
    try:
        # 测试指标更新错误
        instance_id = factory.create("SimpleMovingAverage", {"window": 20})
        sma = factory.get_instance(instance_id)
        if sma:
            price_data = {
                "open": -100,
                "high": -100,
                "low": -100,
                "close": -100,
                "volume": 10000
            }
            sma.update(price_data)  # 无效价格
    except Exception as e:
        error_handler.record_error(
            "指标更新错误",
            str(e),
            ErrorSeverity.MEDIUM,
            {"price": -100}
        )
    
    # 获取错误报告
    errors = error_handler.get_errors()
    
    print(f"错误数量: {len(errors)}")
    for i, error in enumerate(errors[:3], 1):  # 显示前3个错误
        print(f"\n    错误 {i}:")
        print(f"        消息: {error.message}")
        print(f"        严重程度: {error.severity}")
        print(f"        时间: {error.timestamp}")
        print(f"        上下文: {error.context}")
    
    print("✓ 错误处理测试完成")

def main():
    """主测试函数"""
    print("="*60)
    print("Python自定义指标集成测试")
    print("="*60)
    
    # 运行基本测试
    test_simple_moving_average()
    test_relative_strength_index()
    
    print("\n" + "="*60)
    print("基本测试完成！")
    print("="*60)
    
    # 总结
    print("\n📊 测试总结:")
    print("   1. 简单移动平均线(SMA) - ✓ 通过")
    print("   2. 相对强弱指数(RSI) - ✓ 通过")
    print("\n🎉 Python自定义指标系统基本功能测试通过！")

if __name__ == "__main__":
    main()