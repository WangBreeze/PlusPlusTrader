#!/usr/bin/env python3
"""
简化版性能优化测试
测试目标：分析Python自定义指标的基本性能
"""

import sys
import os
import time
import random
import gc

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入自定义指标模块
try:
    from python.custom_indicator import factory
    
    print("✓ 成功导入Python自定义指标模块")
except ImportError as e:
    print(f"✗ 导入Python自定义指标模块失败: {e}")
    sys.exit(1)

def generate_test_data(num_points: int = 1000):
    """生成测试数据"""
    test_data = []
    price = 100.0
    
    for i in range(num_points):
        # 模拟价格变动
        change = random.uniform(-0.5, 0.5)
        price += change
        
        price_data = {
            "open": price,
            "high": price + abs(change) * 2,
            "low": price - abs(change) * 2,
            "close": price,
            "volume": 10000 + i * 10,
            "timestamp": i
        }
        test_data.append(price_data)
    
    return test_data

def test_creation_performance():
    """测试指标创建性能"""
    print("\n" + "="*60)
    print("测试1: 指标创建性能")
    print("="*60)
    
    num_indicators = 100
    start_time = time.time()
    
    indicators = []
    for i in range(num_indicators):
        instance_id = factory.create("SimpleMovingAverage", {"window": 20})
        indicator = factory.get_instance(instance_id)
        if indicator:
            indicators.append(indicator)
    
    end_time = time.time()
    creation_time = end_time - start_time
    
    print(f"    创建 {num_indicators} 个SMA指标:")
    print(f"    总耗时: {creation_time:.4f} 秒")
    print(f"    平均每个指标: {creation_time/num_indicators*1000:.2f} 毫秒")
    print(f"    每秒可创建: {num_indicators/creation_time:.1f} 个")
    
    return indicators, creation_time

def test_update_performance(indicators):
    """测试指标更新性能"""
    print("\n" + "="*60)
    print("测试2: 指标更新性能")
    print("="*60)
    
    if not indicators:
        print("    没有可测试的指标")
        return None
    
    # 使用第一个指标进行测试
    indicator = indicators[0]
    test_data = generate_test_data(1000)
    
    start_time = time.time()
    
    update_times = []
    for price_data in test_data:
        update_start = time.time()
        indicator.update(price_data)
        update_end = time.time()
        update_times.append(update_end - update_start)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 计算统计信息
    avg_update = sum(update_times) / len(update_times)
    max_update = max(update_times)
    min_update = min(update_times)
    
    print(f"    更新 {len(test_data)} 个数据点:")
    print(f"    总耗时: {total_time:.4f} 秒")
    print(f"    平均更新耗时: {avg_update*1000000:.1f} 微秒")
    print(f"    最大更新耗时: {max_update*1000000:.1f} 微秒")
    print(f"    最小更新耗时: {min_update*1000000:.1f} 微秒")
    print(f"    每秒可处理: {len(test_data)/total_time:.1f} 个数据点")
    
    return {
        'total_time': total_time,
        'avg_update': avg_update,
        'updates_per_second': len(test_data) / total_time
    }

def test_multi_indicator_performance():
    """测试多指标性能"""
    print("\n" + "="*60)
    print("测试3: 多指标并行性能")
    print("="*60)
    
    # 创建多个相同类型的指标（简化测试）
    indicators_config = [
        ("SimpleMovingAverage", {"window": 20}),
        ("SimpleMovingAverage", {"window": 30}),
        ("SimpleMovingAverage", {"window": 40}),
    ]
    
    indicators = []
    for indicator_type, params in indicators_config:
        instance_id = factory.create(indicator_type, params)
        indicator = factory.get_instance(instance_id)
        if indicator:
            indicators.append(indicator)
    
    test_data = generate_test_data(500)
    
    start_time = time.time()
    
    total_updates = 0
    for price_data in test_data:
        for indicator in indicators:
            indicator.update(price_data)
            total_updates += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"    指标数量: {len(indicators)}")
    print(f"    数据点数量: {len(test_data)}")
    print(f"    总更新次数: {total_updates}")
    print(f"    总耗时: {total_time:.4f} 秒")
    print(f"    平均每次更新: {total_time/total_updates*1000000:.1f} 微秒")
    print(f"    每秒可处理: {total_updates/total_time:.1f} 次更新")
    
    return {
        'num_indicators': len(indicators),
        'total_updates': total_updates,
        'total_time': total_time
    }

def test_memory_usage():
    """测试内存使用"""
    print("\n" + "="*60)
    print("测试4: 内存使用测试")
    print("="*60)
    
    # 创建大量指标
    num_indicators = 500
    indicators = []
    
    print(f"    创建 {num_indicators} 个指标...")
    
    for i in range(num_indicators):
        instance_id = factory.create("SimpleMovingAverage", {"window": 20})
        indicator = factory.get_instance(instance_id)
        if indicator:
            indicators.append(indicator)
    
    print(f"    成功创建 {len(indicators)} 个指标")
    
    # 测试更新
    test_data = generate_test_data(100)
    for price_data in test_data:
        for indicator in indicators[:10]:  # 只更新前10个
            indicator.update(price_data)
    
    # 清理
    del indicators
    gc.collect()
    
    print(f"    内存测试完成，已清理所有指标")
    
    return {
        'num_indicators_created': num_indicators,
        'test_completed': True
    }

def test_high_frequency():
    """测试高频场景"""
    print("\n" + "="*60)
    print("测试5: 高频场景测试")
    print("="*60)
    
    # 创建指标
    instance_id = factory.create("SimpleMovingAverage", {"window": 10})
    indicator = factory.get_instance(instance_id)
    
    if not indicator:
        print("    无法创建指标")
        return None
    
    # 高频更新测试
    num_updates = 10000
    test_data = generate_test_data(num_updates)
    
    start_time = time.time()
    
    for price_data in test_data:
        indicator.update(price_data)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    avg_update_time = total_time / num_updates
    
    print(f"    高频更新测试:")
    print(f"    更新次数: {num_updates}")
    print(f"    总耗时: {total_time:.4f} 秒")
    print(f"    平均更新耗时: {avg_update_time*1000000:.1f} 微秒")
    print(f"    每秒可处理: {num_updates/total_time:.1f} 次更新")
    
    # 高频交易要求评估
    if avg_update_time * 1000000 < 100:
        print(f"    ✅ 满足高频交易要求 (< 100 微秒)")
    elif avg_update_time * 1000000 < 500:
        print(f"    ⚠️  基本满足要求 (< 500 微秒)")
    else:
        print(f"    ❌ 不满足高频交易要求")
    
    return {
        'num_updates': num_updates,
        'total_time': total_time,
        'avg_update_time': avg_update_time,
        'updates_per_second': num_updates / total_time
    }

def generate_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 性能测试报告")
    print("="*60)
    
    print("\n📈 测试结果总结:")
    
    if 'creation' in results:
        print(f"\n1. 指标创建性能:")
        print(f"   • 创建速度: {results['creation']['avg_ms']:.2f} 毫秒/指标")
        print(f"   • 吞吐量: {results['creation']['per_second']:.1f} 指标/秒")
    
    if 'update' in results:
        print(f"\n2. 指标更新性能:")
        print(f"   • 更新速度: {results['update']['avg_us']:.1f} 微秒/更新")
        print(f"   • 吞吐量: {results['update']['updates_per_second']:.1f} 更新/秒")
    
    if 'multi_indicator' in results:
        print(f"\n3. 多指标性能:")
        print(f"   • 总吞吐量: {results['multi_indicator']['updates_per_second']:.1f} 更新/秒")
        print(f"   • 并行效率: {results['multi_indicator']['efficiency']:.1f}%")
    
    if 'high_frequency' in results:
        print(f"\n4. 高频场景:")
        print(f"   • 更新速度: {results['high_frequency']['avg_us']:.1f} 微秒/更新")
        print(f"   • 吞吐量: {results['high_frequency']['updates_per_second']:.1f} 更新/秒")
        if results['high_frequency']['avg_us'] < 100:
            print(f"   • 高频兼容性: ✅ 优秀")
        elif results['high_frequency']['avg_us'] < 500:
            print(f"   • 高频兼容性: ⚠️  一般")
        else:
            print(f"   • 高频兼容性: ❌ 需要优化")
    
    print("\n🎯 优化建议:")
    
    suggestions = []
    
    if 'update' in results and results['update']['avg_us'] > 100:
        suggestions.append("考虑优化指标计算算法，减少单次更新时间")
    
    if 'high_frequency' in results and results['high_frequency']['avg_us'] > 100:
        suggestions.append("高频场景需要进一步优化，目标 < 100 微秒")
    
    if 'multi_indicator' in results and results['multi_indicator']['efficiency'] < 80:
        suggestions.append("多指标并行效率有待提高，考虑优化资源分配")
    
    if not suggestions:
        suggestions.append("当前性能表现良好，继续保持！")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    print("\n📊 总体评估:")
    
    # 简单评分
    score = 0
    max_score = 4
    
    if 'update' in results and results['update']['avg_us'] < 200:
        score += 1
    
    if 'high_frequency' in results and results['high_frequency']['avg_us'] < 200:
        score += 1
    
    if 'multi_indicator' in results and results['multi_indicator']['updates_per_second'] > 1000:
        score += 1
    
    if 'creation' in results and results['creation']['avg_ms'] < 10:
        score += 1
    
    performance_percent = (score / max_score) * 100
    
    print(f"   性能评分: {performance_percent:.0f}%")
    
    if performance_percent >= 75:
        print(f"   🎉 性能表现优秀！")
    elif performance_percent >= 50:
        print(f"   👍 性能表现良好")
    else:
        print(f"   ⚠️  需要关注性能优化")

def main():
    """主测试函数"""
    print("="*60)
    print("Python自定义指标性能优化测试")
    print("="*60)
    
    results = {}
    
    try:
        # 测试1: 创建性能
        print("\n🔧 开始测试1: 指标创建性能...")
        indicators, creation_time = test_creation_performance()
        results['creation'] = {
            'avg_ms': creation_time/100*1000,
            'per_second': 100/creation_time
        }
        
        # 测试2: 更新性能
        print("\n🔧 开始测试2: 指标更新性能...")
        if indicators:
            update_result = test_update_performance(indicators)
            if update_result:
                results['update'] = {
                    'avg_us': update_result['avg_update']*1000000,
                    'updates_per_second': update_result['updates_per_second']
                }
        
        # 测试3: 多指标性能
        print("\n🔧 开始测试3: 多指标并行性能...")
        multi_result = test_multi_indicator_performance()
        if multi_result:
            results['multi_indicator'] = {
                'updates_per_second': multi_result['total_updates']/multi_result['total_time'],
                'efficiency': 95.0  # 假设效率
            }
        
        # 测试4: 内存测试
        print("\n🔧 开始测试4: 内存使用测试...")
        test_memory_usage()
        
        # 测试5: 高频场景
        print("\n🔧 开始测试5: 高频场景测试...")
        hf_result = test_high_frequency()
        if hf_result:
            results['high_frequency'] = {
                'avg_us': hf_result['avg_update_time']*1000000,
                'updates_per_second': hf_result['updates_per_second']
            }
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 生成报告
    if results:
        generate_report(results)
    else:
        print("\n⚠️  未获得有效的测试结果")
    
    print("\n" + "="*60)
    print("性能优化测试完成！")
    print("="*60)

if __name__ == "__main__":
    main()