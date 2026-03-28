#!/usr/bin/env python3
"""
基础回测示例
============

这个示例展示了如何使用PlusPlusTrader进行基础的股票回测。
包括数据加载、策略创建、回测执行和结果分析。

作者: PlusPlusTrader团队
日期: 2026-03-22
"""

import pplustrader as ppt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def basic_backtest_demo():
    """
    基础回测演示函数
    """
    print("=" * 60)
    print("PlusPlusTrader - 基础回测示例")
    print("=" * 60)
    
    # =========================================================================
    # 1. 数据准备
    # =========================================================================
    print("\n1. 数据准备")
    print("-" * 40)
    
    # 方法1: 使用CSV数据文件
    data_file = "data/000001.SZ_SZSE_D.csv"
    print(f"加载数据文件: {data_file}")
    
    try:
        data_source = ppt.CSVDataSource(data_file)
        print("✓ CSV数据加载成功")
    except FileNotFoundError:
        print("⚠️ 数据文件不存在，使用模拟数据")
        # 创建模拟数据
        dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='D')
        data = {
            'open': [100 + i * 0.1 for i in range(len(dates))],
            'high': [101 + i * 0.1 for i in range(len(dates))],
            'low': [99 + i * 0.1 for i in range(len(dates))],
            'close': [100.5 + i * 0.1 for i in range(len(dates))],
            'volume': [1000000 + i * 10000 for i in range(len(dates))]
        }
        df = pd.DataFrame(data, index=dates)
        df.to_csv("data/simulated_stock.csv")
        data_source = ppt.CSVDataSource("data/simulated_stock.csv")
        print("✓ 模拟数据创建成功")
    
    # 显示数据基本信息
    print(f"数据周期: {len(data_source)} 个交易日")
    print(f"数据字段: {data_source.get_columns()}")
    
    # =========================================================================
    # 2. 策略创建
    # =========================================================================
    print("\n2. 策略创建")
    print("-" * 40)
    
    # 创建移动平均交叉策略
    strategy = ppt.MACrossStrategy(
        short_period=10,      # 短期均线周期
        long_period=30,       # 长期均线周期
        name="双均线策略",    # 策略名称
        trade_size=1000,      # 每次交易数量
        stop_loss=0.05,       # 止损比例 5%
        take_profit=0.10      # 止盈比例 10%
    )
    
    print(f"策略名称: {strategy.name}")
    print(f"短期均线: {strategy.short_period} 日")
    print(f"长期均线: {strategy.long_period} 日")
    print(f"交易数量: {strategy.trade_size} 股/次")
    print(f"止损比例: {strategy.stop_loss:.1%}")
    print(f"止盈比例: {strategy.take_profit:.1%}")
    
    # =========================================================================
    # 3. 回测配置
    # =========================================================================
    print("\n3. 回测配置")
    print("-" * 40)
    
    backtest = ppt.BacktestEngine(
        data_source=data_source,      # 数据源
        strategy=strategy,            # 交易策略
        initial_capital=100000,       # 初始资金 10万元
        commission_rate=0.0003,       # 佣金率 0.03%
        tax_rate=0.001,               # 印花税率 0.1%
        slippage=0.0001,              # 滑点 0.01%
        start_date="2025-01-01",      # 开始日期
        end_date="2025-12-31",        # 结束日期
        verbose=True                  # 显示详细日志
    )
    
    print(f"初始资金: {backtest.initial_capital:,.2f} 元")
    print(f"佣金率: {backtest.commission_rate:.4%}")
    print(f"印花税率: {backtest.tax_rate:.3%}")
    print(f"滑点: {backtest.slippage:.4%}")
    print(f"回测期间: {backtest.start_date} 至 {backtest.end_date}")
    
    # =========================================================================
    # 4. 执行回测
    # =========================================================================
    print("\n4. 执行回测")
    print("-" * 40)
    
    print("开始回测...")
    import time
    start_time = time.time()
    
    results = backtest.run()
    
    end_time = time.time()
    print(f"回测完成! 耗时: {end_time - start_time:.2f} 秒")
    
    # =========================================================================
    # 5. 结果分析
    # =========================================================================
    print("\n5. 回测结果分析")
    print("-" * 40)
    
    # 基本统计
    print(f"总收益率: {results.total_return:+.2%}")
    print(f"年化收益率: {results.annual_return:+.2%}")
    print(f"最大回撤: {results.max_drawdown:.2%}")
    print(f"夏普比率: {results.sharpe_ratio:.2f}")
    print(f"索提诺比率: {results.sortino_ratio:.2f}")
    print(f"卡玛比率: {results.calmar_ratio:.2f}")
    
    # 交易统计
    print(f"\n交易统计:")
    print(f"总交易次数: {results.trade_count}")
    print(f"盈利交易: {results.winning_trades}")
    print(f"亏损交易: {results.losing_trades}")
    print(f"胜率: {results.win_rate:.2%}")
    print(f"平均盈利: {results.avg_win:.2f}")
    print(f"平均亏损: {results.avg_loss:.2f}")
    print(f"盈亏比: {results.profit_loss_ratio:.2f}")
    
    # 风险指标
    print(f"\n风险指标:")
    print(f"波动率: {results.volatility:.2%}")
    print(f"下行风险: {results.downside_risk:.2%}")
    print(f"VAR(95%): {results.var_95:.2%}")
    print(f"CVAR(95%): {results.cvar_95:.2%}")
    
    # =========================================================================
    # 6. 可视化
    # =========================================================================
    print("\n6. 生成可视化图表")
    print("-" * 40)
    
    try:
        # 创建图表
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # 子图1: 价格和交易信号
        ax1 = axes[0]
        prices = results.get_price_series()
        ax1.plot(prices.index, prices.values, label='收盘价', color='blue', alpha=0.7)
        
        # 标记买入点
        buy_signals = results.get_buy_signals()
        if len(buy_signals) > 0:
            ax1.scatter(buy_signals.index, buy_signals.values, 
                       color='green', marker='^', s=100, label='买入信号', zorder=5)
        
        # 标记卖出点
        sell_signals = results.get_sell_signals()
        if len(sell_signals) > 0:
            ax1.scatter(sell_signals.index, sell_signals.values,
                       color='red', marker='v', s=100, label='卖出信号', zorder=5)
        
        ax1.set_title('价格走势与交易信号', fontsize=14)
        ax1.set_ylabel('价格 (元)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 子图2: 资金曲线
        ax2 = axes[1]
        equity_curve = results.get_equity_curve()
        ax2.plot(equity_curve.index, equity_curve.values, 
                label='资金曲线', color='green', linewidth=2)
        
        # 标记最大回撤
        drawdown = results.get_drawdown_curve()
        ax2.fill_between(drawdown.index, drawdown.values, 0,
                        alpha=0.3, color='red', label='回撤区间')
        
        ax2.set_title('资金曲线与回撤', fontsize=14)
        ax2.set_ylabel('资金 (元)', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 子图3: 月度收益
        ax3 = axes[2]
        monthly_returns = results.get_monthly_returns()
        colors = ['green' if r >= 0 else 'red' for r in monthly_returns.values]
        ax3.bar(range(len(monthly_returns)), monthly_returns.values, 
               color=colors, alpha=0.7)
        
        ax3.set_title('月度收益率', fontsize=14)
        ax3.set_xlabel('月份', fontsize=12)
        ax3.set_ylabel('收益率 (%)', fontsize=12)
        ax3.set_xticks(range(len(monthly_returns)))
        ax3.set_xticklabels([m.strftime('%Y-%m') for m in monthly_returns.index], rotation=45)
        ax3.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('backtest_results.png', dpi=150, bbox_inches='tight')
        print("✓ 图表已保存: backtest_results.png")
        
    except Exception as e:
        print(f"⚠️ 图表生成失败: {e}")
    
    # =========================================================================
    # 7. 生成报告
    # =========================================================================
    print("\n7. 生成详细报告")
    print("-" * 40)
    
    try:
        # 生成HTML报告
        report = results.generate_report(
            title="基础回测分析报告",
            author="PlusPlusTrader",
            include_charts=True,
            include_trades=True,
            include_metrics=True
        )
        
        report.save("backtest_report.html")
        print("✓ HTML报告已保存: backtest_report.html")
        
        # 生成文本摘要
        summary = results.generate_summary()
        with open("backtest_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)
        print("✓ 文本摘要已保存: backtest_summary.txt")
        
    except Exception as e:
        print(f"⚠️ 报告生成失败: {e}")
    
    # =========================================================================
    # 8. 策略优化建议
    # =========================================================================
    print("\n8. 策略优化建议")
    print("-" * 40)
    
    suggestions = results.get_optimization_suggestions()
    if suggestions:
        print("基于回测结果，建议考虑以下优化:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    else:
        print("策略表现良好，无需重大调整。")
    
    print("\n" + "=" * 60)
    print("基础回测示例完成!")
    print("=" * 60)
    
    return results

def advanced_analysis(results):
    """
    高级分析功能
    """
    print("\n" + "=" * 60)
    print("高级分析功能")
    print("=" * 60)
    
    # 1. 参数敏感性分析
    print("\n1. 参数敏感性分析")
    print("-" * 40)
    
    param_ranges = {
        'short_period': [5, 10, 15, 20],
        'long_period': [20, 30, 40, 50]
    }
    
    sensitivity = results.analyze_parameter_sensitivity(param_ranges)
    if sensitivity:
        print("参数对收益的影响:")
        for param, values in sensitivity.items():
            print(f"  {param}: {values}")
    
    # 2. 市场环境分析
    print("\n2. 市场环境分析")
    print("-" * 40)
    
    market_analysis = results.analyze_market_conditions()
    if market_analysis:
        print("不同市场环境下的表现:")
        for condition, performance in market_analysis.items():
            print(f"  {condition}: {performance:.2%}")
    
    # 3. 风险调整收益
    print("\n3. 风险调整收益分析")
    print("-" * 40)
    
    risk_adjusted = results.calculate_risk_adjusted_returns()
    print(f"信息比率: {risk_adjusted.get('information_ratio', 0):.2f}")
    print(f"特雷诺比率: {risk_adjusted.get('treynor_ratio', 0):.2f}")
    print(f"詹森阿尔法: {risk_adjusted.get('jensen_alpha', 0):.2%}")
    
    # 4. 交易成本分析
    print("\n4. 交易成本分析")
    print("-" * 40)
    
    cost_analysis = results.analyze_trading_costs()
    print(f"总交易成本: {cost_analysis.get('total_cost', 0):.2f} 元")
    print(f"成本占收益比例: {cost_analysis.get('cost_return_ratio', 0):.2%}")
    print(f"平均单笔成本: {cost_analysis.get('avg_cost_per_trade', 0):.2f} 元")

if __name__ == "__main__":
    """
    主函数
    """
    print("PlusPlusTrader 基础回测示例")
    print("版本: 1.0.0")
    print("日期: 2026-03-22")
    print()
    
    try:
        # 运行基础回测
        results = basic_backtest_demo()
        
        # 运行高级分析（可选）
        run_advanced = input("\n是否运行高级分析? (y/n): ").lower().strip()
        if run_advanced == 'y':
            advanced_analysis(results)
        
        print("\n🎉 示例运行完成!")
        print("生成的文件:")
        print("  - backtest_results.png (图表)")
        print("  - backtest_report.html (HTML报告)")
        print("  - backtest_summary.txt (文本摘要)")
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n感谢使用 PlusPlusTrader! 🚀")