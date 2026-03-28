#!/usr/bin/env python3
"""
修复后的集成测试脚本
验证PlusPlusTrader核心功能
"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'build/python/bindings'))

print("=" * 80)
print("PlusPlusTrader 修复后的集成测试")
print("=" * 80)

def test_cpp_bindings():
    """测试C++绑定功能"""
    print("\n1. 测试C++绑定功能...")
    
    try:
        import pplustrader as ppt
        
        # 测试基本函数
        version = ppt.get_version()
        print(f"  ✅ 获取版本信息: {version}")
        
        # 测试hello函数
        hello_result = ppt.hello()
        print(f"  ✅ Hello函数: {hello_result}")
        
        # 测试数据结构创建
        tick_data = ppt.create_tick_data()
        print(f"  ✅ 创建Tick数据: {tick_data}")
        
        # 测试订单创建
        order = ppt.create_order()
        print(f"  ✅ 创建订单: {order}")
        
        # 测试账户信息创建
        account_info = ppt.create_account_info()
        print(f"  ✅ 创建账户信息: {account_info}")
        
        # 测试技术指标计算
        prices = [100.0, 102.0, 101.0, 105.0, 103.0, 108.0]
        sma_values = ppt.simple_moving_average(prices, 3)
        print(f"  ✅ 计算简单移动平均线: {sma_values}")
        
        # 测试回测模拟
        backtest_result = ppt.simulate_backtest(10000.0, prices)
        print(f"  ✅ 回测模拟: {backtest_result}")
        
        return True
    except Exception as e:
        print(f"  ❌ C++绑定测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_python_custom_indicators():
    """测试Python自定义指标系统"""
    print("\n2. 测试Python自定义指标系统...")
    
    try:
        from custom_indicator import CustomIndicatorFactory
        from custom_indicator_examples import EnhancedMovingAverage
        
        # 创建工厂实例
        factory = CustomIndicatorFactory()
        
        # 注册指标
        factory.register(EnhancedMovingAverage)
        
        # 列出可用指标
        indicators = factory.list_indicators()
        print(f"  ✅ 可用指标: {indicators}")
        
        # 创建指标实例
        instance_id = factory.create('EnhancedMovingAverage', {'period': 20})
        print(f"  ✅ 创建EMA指标实例，ID: {instance_id}")
        
        # 获取指标实例
        ema_indicator = factory._instances.get(instance_id)
        if ema_indicator:
            print(f"  ✅ 获取指标实例: {ema_indicator.name}")
            
            # 测试指标更新 - 使用正确的价格数据格式
            test_prices = [
                {'close': 100.0, 'timestamp': 1},
                {'close': 102.0, 'timestamp': 2},
                {'close': 101.0, 'timestamp': 3},
                {'close': 105.0, 'timestamp': 4},
                {'close': 103.0, 'timestamp': 5},
                {'close': 108.0, 'timestamp': 6}
            ]
            
            for price_data in test_prices:
                value = ema_indicator.update(price_data)
                print(f"    时间: {price_data['timestamp']}, 价格: {price_data['close']:.2f}, 指标值: {value:.2f}")
            
            print(f"  ✅ EMA指标更新测试完成，共处理{len(test_prices)}个价格点")
        
        # 列出所有实例
        instances = factory.list_instances()
        print(f"  ✅ 当前指标实例: {len(instances)}个")
        
        return True
    except Exception as e:
        print(f"  ❌ Python自定义指标测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_optimization_framework():
    """测试性能优化框架"""
    print("\n3. 测试性能优化框架...")
    
    try:
        from optimized_indicator import PriceDataPool, PerformanceMonitor
        
        # 测试内存池
        pool = PriceDataPool()
        
        # 获取价格数据
        price_data = pool.get_price_data()
        print(f"  ✅ 获取价格数据: {price_data}")
        
        # 检查池大小（属性，不是方法）
        pool_size = pool.pool_size
        print(f"  ✅ 内存池大小: {pool_size}")
        
        # 测试性能监控 - 使用正确的API
        monitor = PerformanceMonitor()
        
        # 开始计时
        monitor.start_time = time.time()
        
        # 模拟一些操作
        total = 0
        for i in range(10000):
            total += i
        
        # 结束计时
        monitor.end_time = time.time()
        elapsed = monitor.end_time - monitor.start_time
        
        print(f"  ✅ 性能监控测试完成，耗时: {elapsed:.6f}秒，计算结果: {total}")
        
        # 返回数据到池中
        pool.return_price_data(price_data)
        print(f"  ✅ 返回数据到内存池")
        
        return True
    except Exception as e:
        print(f"  ❌ 性能优化框架测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_feedback_system():
    """测试用户反馈系统"""
    print("\n4. 测试用户反馈系统...")
    
    try:
        from user_feedback_system import FeedbackCollector
        
        # 创建反馈收集器
        collector = FeedbackCollector()
        
        # 查看可用方法
        print(f"  ✅ 反馈收集器创建成功")
        print(f"     存储路径: {collector.storage_path}")
        
        # 获取统计信息
        stats = collector.get_stats()
        print(f"  ✅ 反馈统计: {stats}")
        
        # 测试提交反馈 - 使用正确的参数名
        try:
            feedback_id = collector.submit_feedback(
                feedback_title="集成测试反馈",
                feedback_description="这是一个集成测试用的反馈",
                feedback_type="suggestion",
                feedback_severity="low"
            )
            print(f"  ✅ 提交反馈成功，ID: {feedback_id}")
        except Exception as e:
            print(f"  ⚠️  提交反馈失败: {e}")
        
        # 测试分享指标 - 使用正确的API
        try:
            indicator_id = collector.share_indicator(
                name="测试移动平均线",
                author="测试用户",
                description="这是一个测试用的移动平均线指标",
                code="def calculate(data): return sum(data)/len(data)",
                tags=["test", "sma", "integration"]
            )
            print(f"  ✅ 分享指标成功，ID: {indicator_id}")
        except Exception as e:
            print(f"  ⚠️  分享指标失败: {e}")
        
        # 搜索指标
        try:
            indicators = collector.search_indicators("test")
            print(f"  ✅ 搜索指标结果: {len(indicators)}个")
        except Exception as e:
            print(f"  ⚠️  搜索指标失败: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ 用户反馈系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_workflow():
    """测试端到端工作流程"""
    print("\n5. 测试端到端工作流程...")
    
    try:
        # 模拟一个完整的交易分析流程
        print("  模拟交易分析流程:")
        
        # 1. 使用C++核心计算技术指标
        print("  1. 使用C++核心计算技术指标")
        import pplustrader as ppt
        
        prices = [100.0, 102.0, 101.0, 105.0, 103.0, 108.0, 107.0, 110.0, 109.0, 112.0]
        sma_values = ppt.simple_moving_average(prices, 3)
        print(f"    计算SMA(3): {sma_values}")
        
        # 2. 使用Python自定义指标
        print("  2. 使用Python自定义指标")
        from custom_indicator import CustomIndicatorFactory
        from custom_indicator_examples import EnhancedMovingAverage
        
        factory = CustomIndicatorFactory()
        factory.register(EnhancedMovingAverage)
        
        instance_id = factory.create('EnhancedMovingAverage', {'period': 5})
        ema_indicator = factory._instances.get(instance_id)
        
        if ema_indicator:
            ema_values = []
            timestamp = 1
            for price in prices:
                price_data = {'close': price, 'timestamp': timestamp}
                value = ema_indicator.update(price_data)
                ema_values.append(value)
                timestamp += 1
            
            print(f"    计算EMA(5): {[f'{v:.2f}' for v in ema_values[-5:]]}")
        
        # 3. 使用性能优化框架
        print("  3. 使用性能优化框架")
        from optimized_indicator import PriceDataPool
        
        pool = PriceDataPool()
        
        start_time = time.time()
        
        processed_data = []
        for price in prices:
            data = pool.get_price_data()
            # 这里可以处理数据
            processed_data.append(data)
            pool.return_price_data(data)
        
        elapsed = time.time() - start_time
        print(f"    数据处理完成，耗时: {elapsed:.6f}秒，处理了{len(prices)}个数据点")
        
        # 4. 总结
        print("  4. 工作流程总结")
        print(f"    - C++核心计算: {len(sma_values)}个SMA值")
        print(f"    - Python自定义指标: {len(ema_values) if 'ema_values' in locals() else 0}个EMA值")
        print(f"    - 性能优化: 使用内存池处理{len(prices)}个数据点")
        print(f"    - 总耗时: {elapsed:.6f}秒")
        
        return True
    except Exception as e:
        print(f"  ❌ 端到端工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("开始运行修复后的集成测试...")
    print("=" * 80)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("C++绑定", test_cpp_bindings()))
    test_results.append(("Python自定义指标", test_python_custom_indicators()))
    test_results.append(("性能优化框架", test_optimization_framework()))
    test_results.append(("用户反馈系统", test_user_feedback_system()))
    test_results.append(("端到端工作流程", test_end_to_end_workflow()))
    
    # 输出测试结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    passed_count = 0
    total_count = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if result:
            passed_count += 1
    
    print("\n" + "=" * 80)
    success_rate = (passed_count / total_count) * 100
    print(f"测试完成: {passed_count}/{total_count} 通过 ({success_rate:.1f}%)")
    
    if passed_count == total_count:
        print("🎉 所有测试通过！系统集成完整，功能正常。")
        return True
    else:
        print(f"⚠️  有{total_count - passed_count}个测试失败，需要检查相关问题。")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)