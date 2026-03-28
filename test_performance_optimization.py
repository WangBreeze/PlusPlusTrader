#!/usr/bin/env python3
"""
Python自定义指标性能优化测试
测试目标：分析Python/C++交互性能，优化高频场景下的表现
"""

import sys
import os
import time
import numpy as np
import psutil
import gc
from typing import Dict, List, Any, Tuple
import threading
import multiprocessing as mp

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入自定义指标模块
try:
    from python.custom_indicator import PythonIndicator, SignalType, IndicatorConfig, factory
    from python.custom_indicator_examples import (
        EnhancedMovingAverage,
        BollingerBands,
        MACDIndicator
    )
    from python.custom_indicator_utils import (
        PerformanceMonitor,
        ErrorHandler,
        ErrorSeverity
    )
    
    print("✓ 成功导入Python自定义指标模块")
except ImportError as e:
    print(f"✗ 导入Python自定义指标模块失败: {e}")
    sys.exit(1)

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.results = {}
        self.monitor = PerformanceMonitor()
        self.error_handler = ErrorHandler()
        
    def measure_memory_usage(self, label: str):
        """测量内存使用情况"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss,  # 物理内存使用
            'vms': memory_info.vms,  # 虚拟内存使用
            'label': label
        }
    
    def measure_execution_time(self, func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time
    
    def generate_test_data(self, num_points: int = 10000) -> List[Dict[str, Any]]:
        """生成测试数据"""
        np.random.seed(42)
        
        # 生成价格序列
        prices = 100 + np.cumsum(np.random.randn(num_points) * 0.5)
        
        # 生成完整的价格数据
        test_data = []
        for i, price in enumerate(prices):
            price_data = {
                "open": price,
                "high": price * (1 + np.random.rand() * 0.02),
                "low": price * (1 - np.random.rand() * 0.02),
                "close": price,
                "volume": 10000 + i * 100 + np.random.randint(-500, 500),
                "timestamp": i
            }
            test_data.append(price_data)
        
        return test_data

def test_indicator_creation_performance():
    """测试指标创建性能"""
    print("\n" + "="*60)
    print("测试1: 指标创建性能")
    print("="*60)
    
    analyzer = PerformanceAnalyzer()
    
    # 测试创建多个指标的性能
    num_indicators = 100
    indicators = []
    
    start_time = time.perf_counter()
    
    for i in range(num_indicators):
        # 创建SMA指标
        instance_id = factory.create("SimpleMovingAverage", {"window": 20})
        indicator = factory.get_instance(instance_id)
        if indicator:
            indicators.append(indicator)
    
    end_time = time.perf_counter()
    
    creation_time = end_time - start_time
    avg_creation_time = creation_time / num_indicators
    
    print(f"    创建 {num_indicators} 个指标:")
    print(f"    总耗时: {creation_time:.6f} 秒")
    print(f"    平均每个指标耗时: {avg_creation_time:.6f} 秒")
    print(f"    每秒可创建指标数: {num_indicators / creation_time:.2f}")
    
    # 测量内存使用
    memory_before = analyzer.measure_memory_usage("创建前")
    memory_after = analyzer.measure_memory_usage("创建后")
    
    memory_increase = memory_after['rss'] - memory_before['rss']
    print(f"    内存增加: {memory_increase / 1024:.2f} KB")
    print(f"    每个指标内存占用: {memory_increase / num_indicators / 1024:.2f} KB")
    
    return {
        'num_indicators': num_indicators,
        'total_time': creation_time,
        'avg_time': avg_creation_time,
        'memory_increase': memory_increase
    }

def test_indicator_update_performance():
    """测试指标更新性能"""
    print("\n" + "="*60)
    print("测试2: 指标更新性能")
    print("="*60)
    
    analyzer = PerformanceAnalyzer()
    
    # 创建测试指标
    instance_id = factory.create("SimpleMovingAverage", {"window": 20})
    sma = factory.get_instance(instance_id)
    
    if not sma:
        print("✗ 无法创建SMA指标")
        return None
    
    # 生成测试数据
    test_data = analyzer.generate_test_data(num_points=10000)
    
    # 测试更新性能
    update_times = []
    
    start_time = time.perf_counter()
    
    for price_data in test_data:
        update_start = time.perf_counter()
        sma.update(price_data)
        update_end = time.perf_counter()
        update_times.append(update_end - update_start)
    
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_update_time = np.mean(update_times)
    max_update_time = np.max(update_times)
    min_update_time = np.min(update_times)
    
    print(f"    更新 {len(test_data)} 个数据点:")
    print(f"    总耗时: {total_time:.6f} 秒")
    print(f"    平均更新耗时: {avg_update_time * 1e6:.2f} 微秒")
    print(f"    最大更新耗时: {max_update_time * 1e6:.2f} 微秒")
    print(f"    最小更新耗时: {min_update_time * 1e6:.2f} 微秒")
    print(f"    每秒可处理数据点: {len(test_data) / total_time:.2f}")
    
    # 分析更新时间的分布
    percentiles = [50, 90, 95, 99]
    for p in percentiles:
        percentile_value = np.percentile(update_times, p) * 1e6
        print(f"    {p}% 分位数: {percentile_value:.2f} 微秒")
    
    return {
        'num_updates': len(test_data),
        'total_time': total_time,
        'avg_update_time': avg_update_time,
        'max_update_time': max_update_time,
        'min_update_time': min_update_time,
        'updates_per_second': len(test_data) / total_time
    }

def test_multi_indicator_performance():
    """测试多指标并行性能"""
    print("\n" + "="*60)
    print("测试3: 多指标并行性能")
    print("="*60)
    
    analyzer = PerformanceAnalyzer()
    
    # 创建多个不同类型的指标
    indicators_config = [
        ("SimpleMovingAverage", {"window": 20}),
        ("RelativeStrengthIndex", {"period": 14}),
        ("EnhancedMovingAverage", {"period": 12, "alpha": 0.2}),
        ("BollingerBands", {"period": 20, "num_std": 2.0}),
        ("MACDIndicator", {"fast_period": 12, "slow_period": 26, "signal_period": 9})
    ]
    
    indicators = []
    for indicator_type, params in indicators_config:
        instance_id = factory.create(indicator_type, params)
        indicator = factory.get_instance(instance_id)
        if indicator:
            indicators.append(indicator)
    
    # 生成测试数据
    test_data = analyzer.generate_test_data(num_points=5000)
    
    # 测试并行更新性能
    start_time = time.perf_counter()
    
    for price_data in test_data:
        for indicator in indicators:
            indicator.update(price_data)
    
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    total_updates = len(test_data) * len(indicators)
    
    print(f"    指标数量: {len(indicators)}")
    print(f"    数据点数量: {len(test_data)}")
    print(f"    总更新次数: {total_updates}")
    print(f"    总耗时: {total_time:.6f} 秒")
    print(f"    平均每次更新耗时: {total_time / total_updates * 1e6:.2f} 微秒")
    print(f"    每秒可处理更新: {total_updates / total_time:.2f}")
    
    return {
        'num_indicators': len(indicators),
        'num_data_points': len(test_data),
        'total_updates': total_updates,
        'total_time': total_time,
        'avg_update_time': total_time / total_updates
    }

def test_high_frequency_scenario():
    """测试高频交易场景性能"""
    print("\n" + "="*60)
    print("测试4: 高频交易场景性能")
    print("="*60)
    
    analyzer = PerformanceAnalyzer()
    
    # 创建高频交易场景的指标
    instance_id = factory.create("SimpleMovingAverage", {"window": 10})
    sma = factory.get_instance(instance_id)
    
    if not sma:
        print("✗ 无法创建SMA指标")
        return None
    
    # 生成高频数据（更多数据点，更小的价格变动）
    np.random.seed(42)
    num_points = 50000  # 5万个数据点，模拟高频场景
    
    # 生成高频价格序列
    prices = 100 + np.cumsum(np.random.randn(num_points) * 0.1)  # 更小的波动
    
    # 测试高频更新
    start_time = time.perf_counter()
    
    update_times = []
    for i, price in enumerate(prices):
        price_data = {
            "open": price,
            "high": price * 1.001,
            "low": price * 0.999,
            "close": price,
            "volume": 1000 + i % 100,
            "timestamp": i
        }
        
        update_start = time.perf_counter()
        sma.update(price_data)
        update_end = time.perf_counter()
        update_times.append(update_end - update_start)
    
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_update_time = np.mean(update_times)
    
    print(f"    高频场景测试:")
    print(f"    数据点数量: {num_points:,}")
    print(f"    总耗时: {total_time:.6f} 秒")
    print(f"    平均更新耗时: {avg_update_time * 1e6:.2f} 微秒")
    print(f"    每秒可处理数据点: {num_points / total_time:.2f}")
    
    # 检查是否满足高频交易要求（通常需要 < 100 微秒）
    if avg_update_time * 1e6 < 100:
        print(f"    ✅ 满足高频交易要求 (< 100 微秒)")
    else:
        print(f"    ⚠️  可能不满足高频交易要求")
    
    # 分析延迟分布
    percentiles = [50, 90, 95, 99, 99.9]
    print(f"\n    延迟分布:")
    for p in percentiles:
        percentile_value = np.percentile(update_times, p) * 1e6
        print(f"    {p}% 分位数: {percentile_value:.2f} 微秒")
    
    return {
        'num_points': num_points,
        'total_time': total_time,
        'avg_update_time': avg_update_time,
        'updates_per_second': num_points / total_time,
        'meets_hft_requirement': avg_update_time * 1e6 < 100
    }

def test_memory_optimization():
    """测试内存优化"""
    print("\n" + "="*60)
    print("测试5: 内存优化测试")
    print("="*60)
    
    analyzer = PerformanceAnalyzer()
    
    # 测试大量指标的内存使用
    num_indicators = 1000
    indicators = []
    
    # 测量初始内存
    initial_memory = analyzer.measure_memory_usage("初始")
    
    # 创建大量指标
    for i in range(num_indicators):
        instance_id = factory.create("SimpleMovingAverage", {"window": 20})
        indicator = factory.get_instance(instance_id)
        if indicator:
            indicators.append(indicator)
    
    # 测量创建后内存
    after_creation_memory = analyzer.measure_memory_usage("创建后")
    
    # 更新指标数据
    test_data = analyzer.generate_test_data(num_points=100)
    for price_data in test_data:
        for indicator in indicators[:10]:  # 只更新前10个指标，避免内存爆炸
            indicator.update(price_data)
    
    # 测量更新后内存
    after_update_memory = analyzer.measure_memory_usage("更新后")
    
    # 清理指标
    del indicators
    gc.collect()
    
    # 测量清理后内存
    after_cleanup_memory = analyzer.measure_memory_usage("清理后")
    
    print(f"    内存使用分析:")
    print(f"    初始内存: {initial_memory['rss'] / 1024 / 1024:.2f} MB")
    print(f"    创建 {num_indicators} 个指标后: {after_creation_memory['rss'] / 1024 / 1024:.2f} MB")
    print(f"    内存增加: {(after_creation_memory['rss'] - initial_memory['rss']) / 1024:.2f} KB")
    print(f"    每个指标内存: {(after_creation_memory['rss'] - initial_memory['rss']) / num_indicators:.2f} 字节")
    
    print(f"\n    更新数据后: {after_update_memory['rss'] / 1024 / 1024:.2f} MB")
    print(f"    清理后: {after_cleanup_memory['rss'] / 1024 / 1024:.2f} MB")
    print(f"    内存泄漏: {(after_cleanup_memory['rss'] - initial_memory['rss']) / 1024:.2f} KB")
    
    # 检查内存泄漏
    memory_leak = after_cleanup_memory['rss'] - initial_memory['rss']
    if memory_leak < 1024:  # 小于1KB认为是可接受的
        print(f"    ✅ 内存泄漏检查通过 (< 1KB)")
    else:
        print(f"    ⚠️  检测到潜在内存泄漏: {memory_leak / 1024:.2f} KB")
    
    return {
        'num_indicators': num_indicators,
        'initial_memory': initial_memory['rss'],
        'after_creation_memory': after_creation_memory['rss'],
        'after_update_memory': after_update_memory['rss'],
        'after_cleanup_memory': after_cleanup_memory['rss'],
        'memory_leak': memory_leak
    }

def test_cpp_python_interaction():
    """测试C++/Python交互性能"""
    print("\n" + "="*60)
    print("测试6: C++/Python交互性能")
    print("="*60)
    
    # 尝试导入C++绑定
    try:
        import pplustrader
        print("✓ 成功导入C++ Python绑定")
        
        # 测试C++函数的调用性能
        test_data = []
        for i in range(1000):
            test_data.append({
                'timestamp': i,
                'open': 100.0 + i * 0.01,
                'high': 101.0 + i * 0.01,
                'low': 99.0 + i * 0.01,
                'close': 100.0 + i * 0.01,
                'volume': 10000
            })
        
        print(f"    C++绑定可用，准备进行交互性能测试...")
        print(f"    （注意：需要实现具体的C++绑定测试）")
        
        return {
            'cpp_binding_available': True,
            'test_data_size': len(test_data)
        }
        
    except ImportError as e:
        print(f"✗ 无法导入C++ Python绑定: {e}")
        print(f"    C++绑定可能未编译或路径不正确")
        
        return {
            'cpp_binding_available': False,
            'error': str(e)
        }

def generate_performance_report(results: Dict[str, Any]):
    """生成性能报告"""
    print("\n" + "="*60)
    print("📊 性能优化测试报告")
    print("="*60)
    
    print("\n📈 性能指标总结:")
    
    if 'creation' in results:
        print(f"\n1. 指标创建性能:")
        print(f"   • 创建速度: {results['creation']['avg_time']*1000:.2f} 毫秒/指标")
        print(f"   • 内存占用: {results['creation']['memory_increase']/results['creation']['num_indicators']:.2f} 字节/指标")
    
    if 'update' in results:
        print(f"\n2. 指标更新性能:")
        print(f"   • 更新速度: {results['update']['avg_update_time']*1e6:.2f} 微秒/更新")
        print(f"   • 吞吐量: {results['update']['updates_per_second']:.2f} 更新/秒")
    
    if 'multi_indicator' in results:
        print(f"\n3. 多指标并行性能:")
        print(f"   • 总吞吐量: {results['multi_indicator']['total_updates']/results['multi_indicator']['total_time']:.2f} 更新/秒")
        print(f"   • 平均延迟: {results['multi_indicator']['avg_update_time']*1e6:.2f} 微秒/更新")
    
    if 'high_frequency' in results:
        print(f"\n4. 高频场景性能:")
        print(f"   • 更新速度: {results['high_frequency']['avg_update_time']*1e6:.2f} 微秒/更新")
        print(f"   • 吞吐量: {results['high_frequency']['updates_per_second']:.2f} 数据点/秒")
        if results['high_frequency']['meets_hft_requirement']:
            print(f"   • 高频交易兼容性: ✅ 满足 (< 100 微秒)")
        else:
            print(f"   • 高频交易兼容性: ⚠️  可能需要优化")
    
    if 'memory' in results:
        print(f"\n5. 内存使用分析:")
        print(f"   • 每个指标内存: {(results['memory']['after_creation_memory'] - results['memory']['initial_memory'])/results['memory']['num_indicators']:.2f} 字节")
        print(f"   • 内存泄漏: {results['memory']['memory_leak']/1024:.2f} KB")
        if results['memory']['memory_leak'] < 1024:
            print(f"   • 内存泄漏检查: ✅ 通过")
        else:
            print(f"   • 内存泄漏检查: ⚠️  需要关注")
    
    if 'cpp_interaction' in results:
        print(f"\n6. C++/Python交互:")
        if results['cpp_interaction']['cpp_binding_available']:
            print(f"   • C++绑定状态: ✅ 可用")
        else:
            print(f"   • C++绑定状态: ⚠️  不可用")
    
    print("\n🎯 性能优化建议:")
    
    # 基于测试结果给出建议
    suggestions = []
    
    if 'update' in results and results['update']['avg_update_time'] * 1e6 > 50:
        suggestions.append("考虑优化指标更新算法，减少计算复杂度")
    
    if 'high_frequency' in results and not results['high_frequency']['meets_hft_requirement']:
        suggestions.append("高频场景需要进一步优化，目标 < 100 微秒/更新")
    
    if 'memory' in results and results['memory']['memory_leak'] > 1024:
        suggestions.append("检测到潜在内存泄漏，需要检查资源释放逻辑")
    
    if 'cpp_interaction' in results and not results['cpp_interaction']['cpp_binding_available']:
        suggestions.append("C++/Python交互需要优化，确保绑定正确编译")
    
    if not suggestions:
        suggestions.append("当前性能表现良好，继续保持！")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    print("\n📊 总体评估:")
    
    # 计算总体评分
    score = 0
    max_score = 0
    
    if 'update' in results:
        max_score += 2
        if results['update']['avg_update_time'] * 1e6 < 100:
            score += 2
        elif results['update']['avg_update_time'] * 1e6 < 500:
            score += 1
    
    if 'high_frequency' in results:
        max_score += 2
        if results['high_frequency']['meets_hft_requirement']:
            score += 2
        elif results['high_frequency']['avg_update_time'] * 1e6 < 500:
            score += 1
    
    if 'memory' in results:
        max_score += 2
        if results['memory']['memory_leak'] < 1024:
            score += 2
        elif results['memory']['memory_leak'] < 10240:
            score += 1
    
    if max_score > 0:
        performance_score = (score / max_score) * 100
        print(f"   性能评分: {performance_score:.1f}%")
        
        if performance_score >= 80:
            print(f"   🎉 性能表现优秀！")
        elif performance_score >= 60:
            print(f"   👍 性能表现良好，有优化空间")
        else:
            print(f"   ⚠️  需要重点关注性能优化")
    else:
        print(f"   无法计算性能评分，测试数据不足")

def main():
    """主测试函数"""
    print("="*60)
    print("Python自定义指标性能优化测试")
    print("="*60)
    
    # 检查依赖
    try:
        import psutil
        import numpy as np
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请安装: pip install psutil numpy")
        sys.exit(1)
    
    # 运行性能测试
    results = {}
    
    try:
        # 测试1: 指标创建性能
        print("\n🔧 开始测试1: 指标创建性能...")
        results['creation'] = test_indicator_creation_performance()
        
        # 测试2: 指标更新性能
        print("\n🔧 开始测试2: 指标更新性能...")
        results['update'] = test_indicator_update_performance()
        
        # 测试3: 多指标并行性能
        print("\n🔧 开始测试3: 多指标并行性能...")
        results['multi_indicator'] = test_multi_indicator_performance()
        
        # 测试4: 高频场景性能
        print("\n🔧 开始测试4: 高频场景性能...")
        results['high_frequency'] = test_high_frequency_scenario()
        
        # 测试5: 内存优化
        print("\n🔧 开始测试5: 内存优化测试...")
        results['memory'] = test_memory_optimization()
        
        # 测试6: C++/Python交互
        print("\n🔧 开始测试6: C++/Python交互性能...")
        results['cpp_interaction'] = test_cpp_python_interaction()
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 生成性能报告
    if results:
        generate_performance_report(results)
    else:
        print("\n⚠️  未获得有效的测试结果")
    
    print("\n" + "="*60)
    print("性能优化测试完成！")
    print("="*60)

if __name__ == "__main__":
    main()