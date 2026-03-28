#!/usr/bin/env python3
"""
PlusPlusTrader 用户反馈系统示例
展示如何使用反馈系统的各种功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.user_feedback_system import (
    FeedbackCollector,
    UserFeedback,
    SharedIndicator,
    FeedbackType,
    FeedbackSeverity
)

def example_basic_usage():
    """基本使用示例"""
    print("="*60)
    print("示例1: 基本使用")
    print("="*60)
    
    # 创建反馈收集器
    collector = FeedbackCollector("example_feedback_data")
    
    # 示例1: 提交错误报告
    print("\n1. 提交错误报告")
    bug_report = UserFeedback(
        feedback_type=FeedbackType.BUG_REPORT,
        title="SMA指标窗口大小验证缺失",
        description="""
问题描述：
当设置窗口大小为0或负数时，SimpleMovingAverage指标会崩溃。

重现步骤：
1. 创建SMA指标，窗口大小为0
2. 尝试更新指标
3. 程序崩溃

期望行为：
应该验证窗口大小，如果无效则抛出有意义的异常。
""",
        severity=FeedbackSeverity.MEDIUM,
        user_id="example_user_001",
        indicator_name="SimpleMovingAverage",
        indicator_config={"window": 0}
    )
    
    feedback_id = collector.submit_feedback(bug_report)
    print(f"   反馈提交成功，ID: {feedback_id}")
    
    # 示例2: 提交功能请求
    print("\n2. 提交功能请求")
    feature_request = UserFeedback(
        feedback_type=FeedbackType.FEATURE_REQUEST,
        title="添加布林带指标",
        description="""
功能描述：
请求添加布林带(Bollinger Bands)技术指标。

功能细节：
1. 计算上轨、中轨、下轨
2. 支持可配置的标准差倍数
3. 提供带宽和%b指标
4. 支持信号生成

使用场景：
波动率分析、超买超卖判断、趋势确认。
""",
        severity=FeedbackSeverity.LOW,
        user_id="example_user_002"
    )
    
    feedback_id = collector.submit_feedback(feature_request)
    print(f"   反馈提交成功，ID: {feedback_id}")
    
    # 示例3: 共享自定义指标
    print("\n3. 共享自定义指标")
    custom_indicator = SharedIndicator(
        name="动态RSI策略",
        description="""
基于RSI的动态交易策略。
特点：
1. 动态调整RSI周期
2. 自适应超买超卖阈值
3. 风险控制模块
4. 绩效统计功能
""",
        author="策略开发者",
        author_email="developer@example.com",
        indicator_code="""
class DynamicRSIStrategy:
    '''动态RSI交易策略'''
    
    def __init__(self, base_period=14, volatility_factor=0.5):
        self.base_period = base_period
        self.volatility_factor = volatility_factor
        self.prices = []
        self.gains = []
        self.losses = []
        
    def calculate_volatility(self):
        '''计算价格波动率'''
        if len(self.prices) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(self.prices)):
            returns.append((self.prices[i] - self.prices[i-1]) / self.prices[i-1])
        
        if returns:
            import numpy as np
            return np.std(returns)
        return 0.0
    
    def calculate_dynamic_period(self):
        '''计算动态周期'''
        volatility = self.calculate_volatility()
        dynamic_period = int(self.base_period * (1 + volatility * self.volatility_factor))
        return max(5, min(50, dynamic_period))  # 限制在5-50之间
    
    def update(self, price):
        '''更新策略'''
        self.prices.append(price)
        
        if len(self.prices) > 100:  # 限制历史数据长度
            self.prices.pop(0)
        
        # 计算价格变化
        if len(self.prices) >= 2:
            change = self.prices[-1] - self.prices[-2]
            if change > 0:
                self.gains.append(change)
                self.losses.append(0)
            else:
                self.gains.append(0)
                self.losses.append(abs(change))
        
        # 限制列表长度
        max_len = self.calculate_dynamic_period()
        if len(self.gains) > max_len:
            self.gains.pop(0)
        if len(self.losses) > max_len:
            self.losses.pop(0)
        
        # 计算RSI
        if len(self.gains) >= 2 and len(self.losses) >= 2:
            avg_gain = sum(self.gains) / len(self.gains)
            avg_loss = sum(self.losses) / len(self.losses)
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            # 生成交易信号
            if rsi > 70:
                return "SELL", rsi
            elif rsi < 30:
                return "BUY", rsi
            else:
                return "HOLD", rsi
        
        return "HOLD", 50.0  # 默认值
    
    def get_performance(self):
        '''获取性能统计'''
        if len(self.prices) < 2:
            return {}
        
        returns = []
        for i in range(1, len(self.prices)):
            returns.append((self.prices[i] - self.prices[i-1]) / self.prices[i-1])
        
        if returns:
            import numpy as np
            return {
                "total_return": (self.prices[-1] - self.prices[0]) / self.prices[0],
                "avg_return": np.mean(returns),
                "volatility": np.std(returns),
                "sharpe_ratio": np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            }
        
        return {}
""",
        indicator_config={
            "base_period": 14,
            "volatility_factor": 0.5
        },
        dependencies=["numpy"],
        tags=["rsi", "dynamic", "strategy", "volatility"],
        version="1.0.0",
        license="MIT"
    )
    
    indicator_id = collector.share_indicator(custom_indicator)
    print(f"   指标共享成功，ID: {indicator_id}")
    
    # 示例4: 搜索和下载指标
    print("\n4. 搜索和下载指标")
    indicators = collector.search_indicators(query="RSI", min_rating=0.0)
    
    if indicators:
        print(f"   找到 {len(indicators)} 个RSI相关指标")
        
        # 下载第一个指标
        downloaded = collector.download_indicator(indicators[0].indicator_id)
        if downloaded:
            print(f"   下载成功: {downloaded.name}")
            print(f"   下载次数: {downloaded.downloads}")
            
            # 保存指标代码
            filename = f"downloaded_{downloaded.name.replace(' ', '_')}.py"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(downloaded.indicator_code)
            print(f"   代码已保存到: {filename}")
    
    # 示例5: 评价指标
    print("\n5. 评价指标")
    if indicators:
        success = collector.rate_indicator(
            indicators[0].indicator_id,
            rating=4.5,
            comment="很好的动态RSI策略，波动率调整很实用！"
        )
        
        if success:
            print("   评价成功！")
    
    # 示例6: 查看统计信息
    print("\n6. 查看统计信息")
    stats = collector.get_stats()
    
    print(f"   总反馈数: {stats['total_feedbacks']}")
    print(f"   总指标数: {stats['total_indicators']}")
    print(f"   总下载数: {stats['total_downloads']}")
    
    print("\n   反馈类型分布:")
    for fb_type, count in stats['feedbacks_by_type'].items():
        if count > 0:
            print(f"     {fb_type}: {count}")
    
    # 停止收集器
    collector.stop()
    
    print("\n" + "="*60)
    print("基本使用示例完成！")
    print("="*60)

def example_advanced_usage():
    """高级使用示例"""
    print("\n" + "="*60)
    print("示例2: 高级使用")
    print("="*60)
    
    collector = FeedbackCollector("advanced_example_data")
    
    # 批量提交反馈
    print("\n1. 批量提交反馈")
    
    feedbacks = [
        UserFeedback(
            feedback_type=FeedbackType.PERFORMANCE_ISSUE,
            title=f"性能测试反馈 {i}",
            description=f"这是第{i}个性能测试反馈",
            severity=FeedbackSeverity.LOW,
            user_id=f"tester_{i:03d}"
        )
        for i in range(1, 6)
    ]
    
    feedback_ids = []
    for feedback in feedbacks:
        feedback_id = collector.submit_feedback(feedback)
        feedback_ids.append(feedback_id)
    
    print(f"   批量提交了 {len(feedback_ids)} 个反馈")
    
    # 获取反馈列表
    print("\n2. 获取反馈列表")
    all_feedbacks = collector.get_all_feedbacks(limit=10)
    
    print(f"   获取到 {len(all_feedbacks)} 个反馈:")
    for fb in all_feedbacks[:3]:  # 只显示前3个
        print(f"   - {fb.title} ({fb.feedback_type.value})")
    
    if len(all_feedbacks) > 3:
        print(f"   ... 还有 {len(all_feedbacks) - 3} 个反馈")
    
    # 更新反馈状态
    print("\n3. 更新反馈状态")
    if all_feedbacks:
        success = collector.update_feedback_status(
            all_feedbacks[0].feedback_id,
            status="in_progress",
            response="我们正在处理这个反馈，感谢您的报告！"
        )
        
        if success:
            print("   状态更新成功")
    
    # 复杂搜索
    print("\n4. 复杂搜索")
    indicators = collector.search_indicators(
        query="策略",
        tags=["dynamic", "volatility"],
        min_rating=4.0
    )
    
    print(f"   找到 {len(indicators)} 个匹配指标")
    
    # 获取单个指标
    print("\n5. 获取单个指标")
    if indicators:
        indicator = collector.get_indicator(indicators[0].indicator_id)
        if indicator:
            print(f"   指标名称: {indicator.name}")
            print(f"   作者: {indicator.author}")
            print(f"   版本: {indicator.version}")
            print(f"   评分: {indicator.rating:.1f}/5.0")
            print(f"   下载: {indicator.downloads}次")
            print(f"   标签: {', '.join(indicator.tags)}")
    
    # 停止收集器
    collector.stop()
    
    print("\n" + "="*60)
    print("高级使用示例完成！")
    print("="*60)

def example_integration_with_trading_system():
    """与交易系统集成示例"""
    print("\n" + "="*60)
    print("示例3: 与交易系统集成")
    print("="*60)
    
    # 模拟交易系统
    class TradingSystem:
        def __init__(self):
            self.feedback_collector = FeedbackCollector("trading_system_feedback")
            self.performance_data = []
            
        def track_performance(self, metric_name, value):
            """跟踪性能指标"""
            self.performance_data.append({
                "metric": metric_name,
                "value": value,
                "timestamp": time.time()
            })
            
            # 如果性能下降，自动提交反馈
            if metric_name == "update_latency_ms" and value > 100:
                self._report_performance_issue(value)
        
        def _report_performance_issue(self, latency):
            """报告性能问题"""
            feedback = UserFeedback(
                feedback_type=FeedbackType.PERFORMANCE_ISSUE,
                title="指标更新延迟过高",
                description=f"""
检测到指标更新延迟过高: {latency:.1f}ms

系统状态:
- 当前时间: {datetime.now().isoformat()}
- 平均延迟: {self._calculate_avg_latency():.1f}ms
- 最大延迟: {self._calculate_max_latency():.1f}ms

可能原因:
1. 数据量过大
2. 指标计算复杂
3. 系统资源不足
""",
                severity=FeedbackSeverity.HIGH,
                performance_data={
                    "current_latency_ms": latency,
                    "avg_latency_ms": self._calculate_avg_latency(),
                    "max_latency_ms": self._calculate_max_latency(),
                    "data_points": len(self.performance_data)
                }
            )
            
            feedback_id = self.feedback_collector.submit_feedback(feedback)
            print(f"   自动提交性能问题反馈，ID: {feedback_id}")
        
        def _calculate_avg_latency(self):
            """计算平均延迟"""
            latencies = [d["value"] for d in self.performance_data 
                        if d["metric"] == "update_latency_ms"]
            return sum(latencies) / len(latencies) if latencies else 0
        
        def _calculate_max_latency(self):
            """计算最大延迟"""
            latencies = [d["value"] for d in self.performance_data 
                        if d["metric"] == "update_latency_ms"]
            return max(latencies) if latencies else 0
        
        def share_successful_strategy(self, strategy_name, returns):
            """分享成功策略"""
            if returns > 0.1:  # 收益率超过10%
                indicator = SharedIndicator(
                    name=f"高收益策略: {strategy_name}",
                    description=f"""
自动发现的成功交易策略。
策略特点:
- 收益率: {returns*100:.1f}%
- 发现时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 数据来源: 历史回测

注意事项:
此策略基于历史数据发现，未来表现可能不同。
建议进行充分测试后再用于实盘交易。
""",
                    author="自动策略发现系统",
                    indicator_code=f"""
# {strategy_name} 策略
# 收益率: {returns*100:.1f}%
# 生成时间: {datetime.now().isoformat()}

class {strategy_name.replace(' ', '_')}Strategy:
    '''自动发现的交易策略'''
    
    def __init__(self):
        self.returns = {returns}
        self.discovery_date = "{datetime.now().isoformat()}"
        
    def get_info(self):
        return {{
            "name": "{strategy_name}",
            "returns": {returns},
            "discovery_date": self.discovery_date
        }}
""",
                    tags=["auto-discovered", "high-return", strategy_name.lower()],
                    version="1.0.0"
                )
                
                indicator_id = self.feedback_collector.share_indicator(indicator)
                print(f"   自动分享成功策略，ID: {indicator_id}")
        
        def stop(self):
            """停止系统"""
            self.feedback_collector.stop()
    
    # 运行示例
    import time
    from datetime import datetime
    
    print("\n模拟交易系统运行...")
    
    trading_system = TradingSystem()
    
    # 模拟性能数据
    print("\n1. 模拟性能跟踪...")
    for i in range(10):
        latency = 50 + i * 10  # 逐渐增加的延迟
        trading_system.track_performance("update_latency_ms", latency)
        time.sleep(0.1)
    
    # 模拟成功策略发现
    print("\n2. 模拟策略发现...")
    trading_system.share_successful_strategy("双均线黄金交叉", 0.15)
    trading_system.share_successful_strategy("RSI超卖反弹", 0.12)
    
    # 停止系统
    trading_system.stop()
    
    print("\n" + "="*60)
    print("交易系统集成示例完成！")
    print("="*60)

def main():
    """主函数"""
    print("PlusPlusTrader 用户反馈系统示例")
    print("="*60)
    
    # 运行所有示例
    example_basic_usage()
    example_advanced_usage()
    example_integration_with_trading_system()
    
    print("\n" + "="*60)
    print("所有示例运行完成！")
    print("="*60)
    
    print("\n🎯 示例总结:")
    print("1. 基本使用 - 展示了反馈提交、指标分享、搜索下载等基本功能")
    print("2. 高级使用 - 展示了批量操作、状态更新、复杂搜索等高级功能")
    print("3. 系统集成 - 展示了如何与交易系统集成，实现自动反馈和策略分享")
    
    print("\n📁 生成的文件:")
    print("1. example_feedback_data/ - 基本示例数据")
    print("2. advanced_example_data/ - 高级示例数据")
    print("3. trading_system_feedback/ - 系统集成示例数据")
    print("4. downloaded_*.py - 下载的指标代码文件")
    
    print("\n🚀 下一步:")
    print("1. 查看生成的数据文件了解系统工作原理")
    print("2. 修改示例代码以适应您的具体需求")
    print("3. 将反馈系统集成到您的交易应用程序中")
    print("4. 使用交互式界面体验完整功能")
    
    print("\n💡 提示:")
    print("• 运行 python3 python/user_feedback_system.py 启动交互式界面")
    print("• 查看 docs/User_Feedback_System_Guide.md 获取完整文档")
    print("• 在实际使用前，请根据需求调整存储路径和配置")

if __name__ == "__main__":
    main()