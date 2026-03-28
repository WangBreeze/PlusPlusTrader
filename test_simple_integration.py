#!/usr/bin/env python3
"""
简化集成测试脚本
验证PlusPlusTrader核心功能
"""

import sys
import os
import time
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'build/python/bindings'))

print("=" * 80)
print("PlusPlusTrader 简化集成测试")
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
        backtest_result = ppt.simulate_backtest()
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
        
        # 获取工厂实例
        factory = CustomIndicatorFactory.get_instance()
        
        # 注册指标
        factory.register(EnhancedMovingAverage)
        
        # 列出可用指标
        indicators = factory.list_indicators()
        print(f"  ✅ 可用指标: {indicators}")
        
        # 创建指标实例
        ema_indicator = factory.create('EnhancedMovingAverage', period=20)
        print(f"  ✅ 创建EMA指标: {ema_indicator.name}")
        
        # 测试指标更新
        test_prices = [100.0, 102.0, 101.0, 105.0, 103.0, 108.0, 107.0, 110.0, 109.0, 112.0]
        
        results = []
        for price in test_prices:
            value, signal = ema_indicator.update(price)
            results.append((price, value, signal))
        
        print(f"  ✅ EMA指标更新测试完成，共处理{len(test_prices)}个价格点")
        print(f"     最后结果: 价格={results[-1][0]}, 指标值={results[-1][1]:.2f}, 信号={results[-1][2]}")
        
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
        
        # 检查池大小
        pool_size = pool.pool_size()
        print(f"  ✅ 内存池大小: {pool_size}")
        
        # 测试性能监控
        monitor = PerformanceMonitor()
        monitor.start_timer("test_operation")
        
        # 模拟一些操作
        for i in range(1000):
            _ = i * i
        
        elapsed = monitor.stop_timer("test_operation")
        print(f"  ✅ 性能监控测试完成，耗时: {elapsed:.6f}秒")
        
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
        
        # 提交测试反馈
        feedback_id = collector.submit_feedback(
            title="集成测试反馈",
            description="这是一个集成测试用的反馈",
            feedback_type="suggestion",
            severity="low"
        )
        
        print(f"  ✅ 提交反馈成功，ID: {feedback_id}")
        
        # 获取反馈
        feedback = collector.get_feedback(feedback_id)
        print(f"  ✅ 获取反馈: {feedback['title'] if feedback else '无'}")
        
        # 获取统计信息
        stats = collector.get_stats()
        print(f"  ✅ 反馈统计: {stats}")
        
        # 分享一个指标
        indicator_id = collector.share_indicator(
            name="测试指标",
            author="测试用户",
            description="集成测试用的指标",
            code="def calculate(data): return sum(data)/len(data)",
            tags=["test", "integration"]
        )
        
        print(f"  ✅ 分享指标成功，ID: {indicator_id}")
        
        # 搜索指标
        indicators = collector.search_indicators("test")
        print(f"  ✅ 搜索指标结果: {len(indicators)}个")
        
        # 评分指标
        if indicators:
            collector.rate_indicator(indicators[0]['id'], 5, "很好的测试指标")
            print(f"  ✅ 指标评分完成")
        
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
        
        # 1. 数据准备
        print("  1. 数据准备 - 生成测试价格数据")
        np.random.seed(42)
        prices = np.random.normal(100, 5, 50).tolist()  # 50个随机价格
        
        # 2. 技术分析
        print("  2. 技术分析 - 使用Python自定义指标")
        from custom_indicator import CustomIndicatorFactory
        from custom_indicator_examples import EnhancedMovingAverage
        
        factory = CustomIndicatorFactory.get_instance()
        factory.register(EnhancedMovingAverage)
        
        ema_short = factory.create('EnhancedMovingAverage', period=10)
        ema_long = factory.create('EnhancedMovingAverage', period=20)
        
        # 3. 信号生成
        print("  3. 信号生成 - 分析价格数据")
        signals = []
        for i, price in enumerate(prices):
            short_val, _ = ema_short.update(price)
            long_val, _ = ema_long.update(price)
            
            # 简单的双均线策略
            if i >= 20:  # 确保有足够的数据
                if short_val > long_val:
                    signals.append(("BUY", price, short_val, long_val))
                elif short_val < long_val:
                    signals.append(("SELL", price, short_val, long_val))
                else:
                    signals.append(("HOLD", price, short_val, long_val))
        
        print(f"  4. 结果分析 - 共生成{len(signals)}个交易信号")
        
        if signals:
            last_signal = signals[-1]
            print(f"     最后信号: {last_signal[0]} at {last_signal[1]:.2f} "
                  f"(EMA10={last_signal[2]:.2f}, EMA20={last_signal[3]:.2f})")
        
        # 4. 性能优化
        print("  5. 性能优化 - 使用优化框架")
        from optimized_indicator import PriceDataPool
        pool = PriceDataPool()
        
        optimized_count = 0
        for price in prices[-5:]:  # 测试最后5个价格
            data = pool.get_price_data()
            optimized_count += 1
            pool.return_price_data(data)
        
        print(f"  6. 完成 - 使用内存池优化处理了{optimized_count}个数据点")
        
        return True
    except Exception as e:
        print(f"  ❌ 端到端工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("开始运行简化集成测试...")
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