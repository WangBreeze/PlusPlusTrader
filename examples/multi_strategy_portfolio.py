#!/usr/bin/env python3
"""
多策略组合示例
===============

这个示例展示了如何创建和管理多策略投资组合，
包括策略权重分配、风险控制和绩效分析。

作者: PlusPlusTrader团队
日期: 2026-03-22
"""

import pplustrader as ppt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class MultiStrategyPortfolioDemo:
    """
    多策略组合演示类
    """
    
    def __init__(self):
        """初始化"""
        self.strategies = []
        self.portfolio = None
        self.results = None
        self.initial_capital = 1000000  # 100万元
        
    def create_strategies(self):
        """
        创建多个交易策略
        """
        print("创建交易策略...")
        print("-" * 40)
        
        # 1. 趋势跟踪策略 - 双均线交叉
        trend_strategy = ppt.MACrossStrategy(
            short_period=10,
            long_period=30,
            name="趋势跟踪",
            trade_size=2000,
            stop_loss=0.08,
            take_profit=0.15
        )
        self.strategies.append(trend_strategy)
        print(f"✓ {trend_strategy.name}: 双均线交叉策略")
        
        # 2. 均值回归策略 - RSI
        mean_reversion_strategy = ppt.RSIStrategy(
            period=14,
            oversold=30,
            overbought=70,
            name="均值回归",
            trade_size=1500,
            stop_loss=0.06,
            take_profit=0.12
        )
        self.strategies.append(mean_reversion_strategy)
        print(f"✓ {mean_reversion_strategy.name}: RSI超买超卖策略")
        
        # 3. 波动率策略 - 布林带
        volatility_strategy = ppt.BollingerBandsStrategy(
            period=20,
            std_dev=2,
            name="波动率交易",
            trade_size=1000,
            stop_loss=0.07,
            take_profit=0.10
        )
        self.strategies.append(volatility_strategy)
        print(f"✓ {volatility_strategy.name}: 布林带突破策略")
        
        # 4. 动量策略 - MACD
        momentum_strategy = ppt.MACDStrategy(
            fast_period=12,
            slow_period=26,
            signal_period=9,
            name="动量交易",
            trade_size=1800,
            stop_loss=0.05,
            take_profit=0.18
        )
        self.strategies.append(momentum_strategy)
        print(f"✓ {momentum_strategy.name}: MACD动量策略")
        
        # 5. 量价策略 - 成交量加权
        volume_strategy = ppt.VolumeWeightedStrategy(
            volume_period=20,
            price_period=10,
            name="量价分析",
            trade_size=1200,
            stop_loss=0.04,
            take_profit=0.08
        )
        self.strategies.append(volume_strategy)
        print(f"✓ {volume_strategy.name}: 量价配合策略")
        
        print(f"\n共创建 {len(self.strategies)} 个策略")
        return self.strategies
    
    def create_portfolio(self, weights=None):
        """
        创建投资组合
        
        Args:
            weights: 策略权重列表，None表示等权重
        """
        print("\n创建投资组合...")
        print("-" * 40)
        
        if weights is None:
            # 等权重分配
            weights = [1.0 / len(self.strategies)] * len(self.strategies)
        
        # 验证权重
        if len(weights) != len(self.strategies):
            raise ValueError("权重数量必须与策略数量一致")
        
        if abs(sum(weights) - 1.0) > 0.001:
            raise ValueError(f"权重总和必须为1.0，当前为{sum(weights):.4f}")
        
        # 创建组合策略
        self.portfolio = ppt.PortfolioStrategy(
            strategies=self.strategies,
            weights=weights,
            name="多策略组合",
            rebalance_frequency='M',  # 每月再平衡
            risk_budget=0.15,         # 风险预算15%
            max_drawdown_limit=0.20   # 最大回撤限制20%
        )
        
        # 显示组合配置
        print(f"组合名称: {self.portfolio.name}")
        print(f"策略数量: {len(self.strategies)}")
        print(f"再平衡频率: {self.portfolio.rebalance_frequency}")
        print(f"风险预算: {self.portfolio.risk_budget:.1%}")
        print(f"最大回撤限制: {self.portfolio.max_drawdown_limit:.1%}")
        
        # 显示各策略权重
        print("\n策略权重分配:")
        for i, (strategy, weight) in enumerate(zip(self.strategies, weights), 1):
            print(f"  {i}. {strategy.name}: {weight:.1%}")
        
        return self.portfolio
    
    def run_backtest(self, data_file=None):
        """
        运行组合回测
        
        Args:
            data_file: 数据文件路径，None表示使用模拟数据
        """
        print("\n运行组合回测...")
        print("-" * 40)
        
        # 准备数据
        if data_file and os.path.exists(data_file):
            print(f"使用数据文件: {data_file}")
            data_source = ppt.CSVDataSource(data_file)
        else:
            print("使用模拟数据")
            data_source = self.create_simulated_data()
        
        # 创建回测引擎
        backtest = ppt.BacktestEngine(
            data_source=data_source,
            strategy=self.portfolio,
            initial_capital=self.initial_capital,
            commission_rate=0.00025,  # 较低佣金率
            tax_rate=0.001,
            slippage=0.00005,         # 较低滑点
            start_date="2025-01-01",
            end_date="2025-12-31",
            verbose=False
        )
        
        print(f"初始资金: {self.initial_capital:,.0f} 元")
        print(f"回测期间: {backtest.start_date} 至 {backtest.end_date}")
        
        # 执行回测
        import time
        start_time = time.time()
        print("\n开始回测计算...")
        
        self.results = backtest.run()
        
        end_time = time.time()
        print(f"回测完成! 耗时: {end_time - start_time:.2f} 秒")
        
        return self.results
    
    def create_simulated_data(self):
        """
        创建模拟数据
        """
        # 生成一年的交易日
        dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='B')
        
        # 创建有趋势和波动的价格序列
        np.random.seed(42)
        n = len(dates)
        
        # 基础趋势
        trend = np.linspace(100, 130, n)
        
        # 季节性波动
        seasonal = 5 * np.sin(2 * np.pi * np.arange(n) / 63)
        
        # 随机波动
        noise = np.random.normal(0, 2, n)
        
        # 合成价格
        close_prices = trend + seasonal + noise
        
        # 生成OHLCV数据
        data = {
            'open': close_prices * 0.99 + np.random.normal(0, 0.5, n),
            'high': close_prices * 1.01 + np.abs(np.random.normal(0, 0.8, n)),
            'low': close_prices * 0.99 - np.abs(np.random.normal(0, 0.8, n)),
            'close': close_prices,
            'volume': np.random.lognormal(13, 0.5, n).astype(int)
        }
        
        df = pd.DataFrame(data, index=dates)
        
        # 保存到文件
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/portfolio_simulation.csv')
        
        return ppt.CSVDataSource('data/portfolio_simulation.csv')
    
    def analyze_results(self):
        """
        分析回测结果
        """
        if self.results is None:
            print("请先运行回测")
            return
        
        print("\n" + "=" * 60)
        print("组合回测结果分析")
        print("=" * 60)
        
        # 1. 整体表现
        print("\n1. 整体表现")
        print("-" * 40)
        
        print(f"总收益率: {self.results.total_return:+.2%}")
        print(f"年化收益率: {self.results.annual_return:+.2%}")
        print(f"最大回撤: {self.results.max_drawdown:.2%}")
        print(f"夏普比率: {self.results.sharpe_ratio:.2f}")
        print(f"索提诺比率: {self.results.sortino_ratio:.2f}")
        print(f"卡玛比率: {self.results.calmar_ratio:.2f}")
        
        # 2. 风险指标
        print("\n2. 风险指标")
        print("-" * 40)
        
        print(f"波动率: {self.results.volatility:.2%}")
        print(f"下行风险: {self.results.downside_risk:.2%}")
        print(f"VAR(95%): {self.results.var_95:.2%}")
        print(f"CVAR(95%): {self.results.cvar_95:.2%}")
        print(f"最大单日亏损: {self.results.max_daily_loss:.2%}")
        
        # 3. 交易统计
        print("\n3. 交易统计")
        print("-" * 40)
        
        print(f"总交易次数: {self.results.trade_count}")
        print(f"盈利交易: {self.results.winning_trades}")
        print(f"亏损交易: {self.results.losing_trades}")
        print(f"胜率: {self.results.win_rate:.2%}")
        print(f"盈亏比: {self.results.profit_loss_ratio:.2f}")
        print(f"平均持仓时间: {self.results.avg_holding_days:.1f} 天")
        
        # 4. 各策略贡献度
        print("\n4. 策略贡献度分析")
        print("-" * 40)
        
        contributions = self.portfolio.get_strategy_contributions()
        for strategy_name, contribution in contributions.items():
            print(f"  {strategy_name}: {contribution:+.2%}")
        
        # 5. 相关性分析
        print("\n5. 策略相关性分析")
        print("-" * 40)
        
        correlations = self.portfolio.get_strategy_correlations()
        if correlations is not None:
            print("策略间相关系数矩阵:")
            print(correlations.round(3))
        
        # 6. 风险贡献
        print("\n6. 风险贡献分析")
        print("-" * 40)
        
        risk_contributions = self.portfolio.get_risk_contributions()
        for strategy_name, risk_contribution in risk_contributions.items():
            print(f"  {strategy_name}: {risk_contribution:.1%}")
    
    def visualize_results(self):
        """
        可视化结果
        """
        if self.results is None:
            print("请先运行回测")
            return
        
        print("\n生成可视化图表...")
        
        try:
            # 创建大图
            fig = plt.figure(figsize=(16, 12))
            
            # 1. 资金曲线对比
            ax1 = plt.subplot(3, 2, 1)
            equity_curve = self.results.get_equity_curve()
            ax1.plot(equity_curve.index, equity_curve.values, 
                    label='组合资金', color='blue', linewidth=2)
            
            # 基准对比（假设基准收益10%）
            baseline = self.initial_capital * (1 + 0.10 * np.arange(len(equity_curve)) / 252)
            ax1.plot(equity_curve.index, baseline, 
                    label='基准(10%)', color='gray', linestyle='--', alpha=0.7)
            
            ax1.set_title('资金曲线对比', fontsize=12)
            ax1.set_ylabel('资金 (元)', fontsize=10)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. 回撤曲线
            ax2 = plt.subplot(3, 2, 2)
            drawdown = self.results.get_drawdown_curve()
            ax2.fill_between(drawdown.index, 0, drawdown.values * 100,
                           alpha=0.5, color='red', label='回撤')
            ax2.axhline(y=-20, color='orange', linestyle='--', alpha=0.5, label='警戒线')
            
            ax2.set_title('回撤曲线', fontsize=12)
            ax2.set_ylabel('回撤 (%)', fontsize=10)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # 3. 月度收益
            ax3 = plt.subplot(3, 2, 3)
            monthly_returns = self.results.get_monthly_returns()
            colors = ['green' if r >= 0 else 'red' for r in monthly_returns.values]
            ax3.bar(range(len(monthly_returns)), monthly_returns.values * 100, 
                   color=colors, alpha=0.7)
            
            ax3.set_title('月度收益率', fontsize=12)
            ax3.set_ylabel('收益率 (%)', fontsize=10)
            ax3.set_xticks(range(len(monthly_returns)))
            ax3.set_xticklabels([m.strftime('%Y-%m') for m in monthly_returns.index], 
                               rotation=45, fontsize=8)
            ax3.axhline(y=0, color='black', linewidth=0.5)
            ax3.grid(True, alpha=0.3, axis='y')
            
            # 4. 策略权重变化
            ax4 = plt.subplot(3, 2, 4)
            weight_history = self.portfolio.get_weight_history()
            if weight_history is not None:
                for i, strategy_name in enumerate(self.portfolio.strategy_names):
                    weights = weight_history[strategy_name]
                    ax4.plot(weights.index, weights.values * 100, 
                            label=strategy_name, linewidth=1.5)
                
                ax4.set_title('策略权重变化', fontsize=12)
                ax4.set_ylabel('权重 (%)', fontsize=10)
                ax4.legend(fontsize=8)
                ax4.grid(True, alpha=0.3)
            
            # 5. 收益分布
            ax5 = plt.subplot(3, 2, 5)
            daily_returns = self.results.get_daily_returns()
            ax5.hist(daily_returns.values * 100, bins=50, alpha=0.7, 
                    color='skyblue', edgecolor='black')
            ax5.axvline(x=0, color='red', linestyle='--', alpha=0.7)
            
            ax5.set_title('日收益分布', fontsize=12)
            ax5.set_xlabel('日收益率 (%)', fontsize=10)
            ax5.set_ylabel('频数', fontsize=10)
            ax5.grid(True, alpha=0.3)
            
            # 6. 滚动夏普比率
            ax6 = plt.subplot(3, 2, 6)
            rolling_sharpe = self.results.get_rolling_sharpe(window=60)
            ax6.plot(rolling_sharpe.index, rolling_sharpe.values, 
                    color='purple', linewidth=1.5)
            ax6.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
            ax6.axhline(y=1, color='green', linestyle='--', alpha=0.5, label='良好')
            ax6.axhline(y=2, color='blue', linestyle='--', alpha=0.5, label='优秀')
            
            ax6.set_title('滚动夏普比率(60日)', fontsize=12)
            ax6.set_ylabel('夏普比率', fontsize=10)
            ax6.legend(fontsize=8)
            ax6.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('portfolio_results.png', dpi=150, bbox_inches='tight')
            print("✓ 图表已保存: portfolio_results.png")
            
        except Exception as e:
            print(f"⚠️ 图表生成失败: {e}")
    
    def generate_report(self):
        """
        生成详细报告
        """
        if self.results is None:
            print("请先运行回测")
            return
        
        print("\n生成详细报告...")
        
        try:
            # 生成HTML报告
            report = self.results.generate_report(
                title="多策略组合分析报告",
                author="PlusPlusTrader",
                include_charts=True,
                include_trades=True,
                include_metrics=True,
                include_strategy_analysis=True
            )
            
            report.save("portfolio_report.html")
            print("✓ HTML报告已保存: portfolio_report.html")
            
            # 生成Excel报告
            excel_report = self.results.export_to_excel()
            excel_report.save("portfolio_analysis.xlsx")
            print("✓ Excel报告已保存: portfolio_analysis.xlsx")
            
        except Exception as e:
            print(f"⚠️ 报告生成失败: {e}")
    
    def run_optimization(self):
        """
        运行组合优化
        """
        print("\n运行组合优化...")
        print("-" * 40)
        
        # 定义优化目标
        objectives = [
            ('maximize', 'sharpe_ratio'),  # 最大化夏普比率
            ('minimize', 'max_drawdown'),  # 最小化最大回撤
            ('maximize', 'total_return')   # 最大化总收益
        ]
        
        # 定义权重范围
        weight_bounds = [(0.05, 0.40) for _ in range(len(self.strategies))]
        
        # 运行优化
        print("正在优化权重分配...")
        optimized_weights = self.portfolio.optimize_weights(
            objectives=objectives,
            weight_bounds=weight_bounds,
            method='nsga2',  # 多目标遗传算法
            population_size=50,
            generations=100
        )
        
        print("\n优化结果:")
        print("-" * 20)
        for i, (strategy, weight) in enumerate(zip(self.strategies, optimized_weights), 1):
            print(f"  {i}. {strategy.name}: {weight:.1%}")
        
        return optimized_weights

def main():
    """
    主函数
    """
    print("=" * 70)
    print("PlusPlusTrader - 多策略组合示例")
    print("=" * 70)
    print()
    
    # 创建演示实例
    demo = MultiStrategyPortfolioDemo()
    
    try:
        # 1. 创建策略
        demo.create_strategies()
        
        # 2. 创建组合（等权重）
        demo.create_portfolio()
        
        # 3. 运行回测
        demo.run_backtest()
        
        # 4. 分析结果
        demo.analyze_results()
        
        # 5. 可视化
        demo.visualize_results()
        
        # 6. 生成报告
        demo.generate_report()
        
        # 7. 运行优化（可选）
        run_opt = input("\n是否运行组合优化? (y/n): ").lower().strip()
        if run_opt == 'y':
            optimized_weights = demo.run_optimization()
            
            # 使用优化权重重新运行
            print("\n使用优化权重重新运行...")
            demo.create_portfolio(weights=optimized_weights)
            demo.run_backtest()
            demo.analyze_results()
        
        print("\n" + "=" * 70)
        print("多策略组合示例完成!")
        print("=" * 70)
        print("\n生成的文件:")
        print("  - portfolio_results.png (组合分析图表)")
        print("  - portfolio_report.html (HTML详细报告)")
        print("  - portfolio_analysis.xlsx (Excel分析报告)")
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n感谢使用 PlusPlusTrader! 🚀")

if __name__ == "__main__":
    import os
    main()