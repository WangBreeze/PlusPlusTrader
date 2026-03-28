#!/usr/bin/env python3
"""
Python自定义指标系统性能测试
测试Python与C++交互的性能表现
"""

import time
import sys
import os
import numpy as np

# 添加python目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python"))

from custom_indicator import SimpleMovingAverage, RelativeStrengthIndex, CustomIndicatorFactory

def test_sma_performance():
    """测试SMA指标性能"""
    print("=" * 60)
    print("测试1: SimpleMovingAverage 性能测试")
    print("=" * 60)
    
    # 创建SMA指标
    from custom_indicator import IndicatorConfig
    config = IndicatorConfig(
        name="SMA",
        parameters={"period": 20},
        required_parameters=["period"]
    )
    sma = SimpleMovingAverage(config)
    
    # 生成测试数据
    test_data = np.random.randn(10000) * 10 + 100  # 正态分布数据
    
    # 测试性能
    start_time = time.time()
    
    values = []
    signals = []
    for price in test_data:
        price_data = {"close": price, "open": price, "high": price, "low": price, "volume": 1000}
        value = sma.update(price_data)
        values.append(value)
        signals.append(sma.signals[-1] if sma.signals else None)
    
    end_time = time.time()
    
    # 计算性能指标
    total_time = end_time - start_time
    avg_time_per_update = total_time / len(test_data) * 1000  # 毫秒
    updates_per_second = len(test_data) / total_time
    
    print(f"测试数据量: {len(test_data)} 条")
    print(f"总耗时: {total_time:.4f} 秒")
    print(f"平均每次更新耗时: {avg_time_per_update:.6f} 毫秒")
    print(f"每秒更新次数: {updates_per_second:.2f}")
    print(f"最终SMA值: {values[-1]:.4f}")
    
    return total_time, avg_time_per_update

def test_rsi_performance():
    """测试RSI指标性能"""
    print("\n" + "=" * 60)
    print("测试2: RelativeStrengthIndex 性能测试")
    print("=" * 60)
    
    # 创建RSI指标
    from custom_indicator import IndicatorConfig
    config = IndicatorConfig(
        name="RSI",
        parameters={"period": 14},
        required_parameters=["period"]
    )
    rsi = RelativeStrengthIndex(config)
    
    # 生成测试数据
    test_data = np.random.randn(10000) * 2 + 50  # 价格数据
    
    # 测试性能
    start_time = time.time()
    
    values = []
    signals = []
    for price in test_data:
        price_data = {"close": price, "open": price, "high": price, "low": price, "volume": 1000}
        value = rsi.update(price_data)
        values.append(value)
        signals.append(rsi.signals[-1] if rsi.signals else None)
    
    end_time = time.time()
    
    # 计算性能指标
    total_time = end_time - start_time
    avg_time_per_update = total_time / len(test_data) * 1000  # 毫秒
    updates_per_second = len(test_data) / total_time
    
    print(f"测试数据量: {len(test_data)} 条")
    print(f"总耗时: {total_time:.4f} 秒")
    print(f"平均每次更新耗时: {avg_time_per_update:.6f} 毫秒")
    print(f"每秒更新次数: {updates_per_second:.2f}")
    print(f"最终RSI值: {values[-1]:.4f}")
    
    return total_time, avg_time_per_update

def test_factory_performance():
    """测试工厂模式性能"""
    print("\n" + "=" * 60)
    print("测试3: 指标工厂性能测试")
    print("=" * 60)
    
    from custom_indicator import IndicatorConfig
    factory = CustomIndicatorFactory()
    
    # 测试创建指标的性能
    start_time = time.time()
    
    indicators = []
    for i in range(1000):
        if i % 2 == 0:
            config = IndicatorConfig(
                name="SMA",
                parameters={"period": 20},
                required_parameters=["period"]
            )
            indicator = SimpleMovingAverage(config)
        else:
            config = IndicatorConfig(
                name="RSI",
                parameters={"period": 14},
                required_parameters=["period"]
            )
            indicator = RelativeStrengthIndex(config)
        indicators.append(indicator)
    
    end_time = time.time()
    
    # 计算性能指标
    total_time = end_time - start_time
    avg_time_per_create = total_time / len(indicators) * 1000  # 毫秒
    creates_per_second = len(indicators) / total_time
    
    print(f"创建指标数量: {len(indicators)} 个")
    print(f"总耗时: {total_time:.4f} 秒")
    print(f"平均每个指标创建耗时: {avg_time_per_create:.6f} 毫秒")
    print(f"每秒创建指标数: {creates_per_second:.2f}")
    
    return total_time, avg_time_per_create

def test_batch_update_performance():
    """测试批量更新性能"""
    print("\n" + "=" * 60)
    print("测试4: 批量更新性能测试")
    print("=" * 60)
    
    # 创建多个指标
    from custom_indicator import IndicatorConfig
    indicators = []
    for i in range(100):
        if i % 3 == 0:
            config = IndicatorConfig(
                name="SMA",
                parameters={"period": 20},
                required_parameters=["period"]
            )
            indicators.append(SimpleMovingAverage(config))
        elif i % 3 == 1:
            config = IndicatorConfig(
                name="RSI",
                parameters={"period": 14},
                required_parameters=["period"]
            )
            indicators.append(RelativeStrengthIndex(config))
        else:
            config = IndicatorConfig(
                name="SMA",
                parameters={"period": 50},
                required_parameters=["period"]
            )
            indicators.append(SimpleMovingAverage(config))
    
    # 生成测试数据
    test_data = np.random.randn(1000) * 5 + 100
    
    # 测试批量更新性能
    start_time = time.time()
    
    for price in test_data:
        price_data = {"close": price, "open": price, "high": price, "low": price, "volume": 1000}
        for indicator in indicators:
            indicator.update(price_data)
    
    end_time = time.time()
    
    # 计算性能指标
    total_time = end_time - start_time
    total_updates = len(test_data) * len(indicators)
    avg_time_per_update = total_time / total_updates * 1000  # 毫秒
    updates_per_second = total_updates / total_time
    
    print(f"指标数量: {len(indicators)} 个")
    print(f"数据量: {len(test_data)} 条")
    print(f"总更新次数: {total_updates} 次")
    print(f"总耗时: {total_time:.4f} 秒")
    print(f"平均每次更新耗时: {avg_time_per_update:.6f} 毫秒")
    print(f"每秒更新次数: {updates_per_second:.2f}")
    
    return total_time, avg_time_per_update

def test_memory_usage():
    """测试内存使用情况"""
    print("\n" + "=" * 60)
    print("测试5: 内存使用测试")
    print("=" * 60)
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 创建大量指标
    from custom_indicator import IndicatorConfig
    indicators = []
    
    print(f"初始内存使用: {initial_memory:.2f} MB")
    
    # 创建1000个指标
    for i in range(1000):
        config = IndicatorConfig(
            name="SMA",
            parameters={"period": 20},
            required_parameters=["period"]
        )
        indicator = SimpleMovingAverage(config)
        indicators.append(indicator)
    
    # 更新数据
    test_data = np.random.randn(100) * 5 + 100
    for price in test_data:
        price_data = {"close": price, "open": price, "high": price, "low": price, "volume": 1000}
        for indicator in indicators:
            indicator.update(price_data)
    
    # 检查内存使用
    current_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = current_memory - initial_memory
    
    print(f"创建 {len(indicators)} 个指标后内存使用: {current_memory:.2f} MB")
    print(f"内存增加: {memory_increase:.2f} MB")
    print(f"平均每个指标占用内存: {memory_increase / len(indicators):.4f} MB")
    
    return memory_increase

def generate_performance_report():
    """生成性能测试报告"""
    print("\n" + "=" * 60)
    print("Python自定义指标系统性能测试报告")
    print("=" * 60)
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")
    print()
    
    # 运行所有测试
    results = {}
    
    results['sma'] = test_sma_performance()
    results['rsi'] = test_rsi_performance()
    results['factory'] = test_factory_performance()
    results['batch'] = test_batch_update_performance()
    results['memory'] = test_memory_usage()
    
    # 生成总结报告
    print("\n" + "=" * 60)
    print("性能测试总结")
    print("=" * 60)
    
    print("\n1. 单个指标更新性能:")
    print(f"   SMA: {results['sma'][1]:.6f} 毫秒/次")
    print(f"   RSI: {results['rsi'][1]:.6f} 毫秒/次")
    
    print("\n2. 工厂创建性能:")
    print(f"   平均创建时间: {results['factory'][1]:.6f} 毫秒/个")
    
    print("\n3. 批量更新性能:")
    print(f"   平均更新时间: {results['batch'][1]:.6f} 毫秒/次")
    
    print("\n4. 内存使用:")
    print(f"   内存增加: {results['memory']:.2f} MB (1000个指标)")
    
    print("\n5. 性能评级:")
    
    # 性能评级
    sma_speed = results['sma'][1]
    if sma_speed < 0.1:
        rating = "优秀 (适合高频交易)"
    elif sma_speed < 1.0:
        rating = "良好 (适合日内交易)"
    elif sma_speed < 10.0:
        rating = "一般 (适合日线级别)"
    else:
        rating = "较差 (需要优化)"
    
    print(f"   更新速度: {rating}")
    print(f"   建议: {get_recommendation(results)}")
    
    return results

def get_recommendation(results):
    """根据测试结果给出优化建议"""
    sma_speed = results['sma'][1]
    memory_usage = results['memory']
    
    recommendations = []
    
    if sma_speed > 1.0:
        recommendations.append("考虑优化Python/C++数据传递性能")
    
    if sma_speed > 0.5:
        recommendations.append("建议使用批量更新接口减少调用开销")
    
    if memory_usage > 50:
        recommendations.append("考虑实现指标共享内存池")
    
    if len(recommendations) == 0:
        return "当前性能满足大多数应用场景，无需特殊优化"
    else:
        return "; ".join(recommendations)

if __name__ == "__main__":
    print("开始Python自定义指标系统性能测试...")
    try:
        results = generate_performance_report()
        print("\n" + "=" * 60)
        print("性能测试完成！")
        print("=" * 60)
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        print("请确保已正确编译和安装Python绑定模块")
        sys.exit(1)