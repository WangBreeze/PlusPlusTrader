#!/usr/bin/env python3
"""
实时交易模拟示例
================

这个示例展示了如何使用PlusPlusTrader进行实时交易模拟，
包括实时数据流、交易执行、风险控制和监控界面。

作者: PlusPlusTrader团队
日期: 2026-03-22
"""

import pplustrader as ppt
import pandas as pd
import numpy as np
import time
import threading
import queue
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import warnings
warnings.filterwarnings('ignore')

class LiveTradingSimulation:
    """
    实时交易模拟类
    """
    
    def __init__(self, initial_capital=100000, symbol="000001.SZ"):
        """
        初始化实时交易模拟
        
        Args:
            initial_capital: 初始资金
            symbol: 交易标的代码
        """
        self.initial_capital = initial_capital
        self.symbol = symbol
        self.is_running = False
        self.data_queue = queue.Queue()
        self.trade_queue = queue.Queue()
        
        # 初始化组件
        self.setup_components()
        
        # 统计数据
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0,
            'max_drawdown': 0,
            'peak_equity': initial_capital
        }
        
        print(f"实时交易模拟初始化完成")
        print(f"交易标的: {symbol}")
        print(f"初始资金: {initial_capital:,.0f} 元")
    
    def setup_components(self):
        """设置交易组件"""
        # 1. 创建模拟交易所
        self.exchange = ppt.SimulatedExchange(
            initial_capital=self.initial_capital,
            commission_rate=0.0003,  # 佣金率0.03%
            tax_rate=0.001,          # 印花税率0.1%
            slippage=0.0001,         # 滑点0.01%
            name="模拟交易所"
        )
        
        # 2. 创建交易策略
        self.strategy = ppt.MACrossStrategy(
            short_period=5,
            long_period=20,
            name="实时均线策略",
            trade_size=1000,    # 每次交易1000股
            stop_loss=0.05,     # 止损5%
            take_profit=0.10    # 止盈10%
        )
        
        # 3. 创建实时数据流
        self.data_stream = ppt.LiveDataStream(
            symbol=self.symbol,
            update_interval=1,      # 每秒更新
            data_source='simulated', # 模拟数据源
            volatility=0.02,        # 波动率2%
            trend=0.0001            # 微小上涨趋势
        )
        
        # 4. 创建实时交易器
        self.trader = ppt.LiveTrader(
            exchange=self.exchange,
            strategy=self.strategy,
            data_stream=self.data_stream,
            max_position=10000,     # 最大持仓10000股
            max_daily_loss=0.03,    # 最大日亏损3%
            trade_throttle=5        # 交易频率限制（秒）
        )
        
        # 5. 设置回调函数
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """设置回调函数"""
        def on_market_data(data):
            """市场数据回调"""
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.data_queue.put({
                'timestamp': timestamp,
                'type': 'data',
                'data': data
            })
        
        def on_trade_signal(signal):
            """交易信号回调"""
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.data_queue.put({
                'timestamp': timestamp,
                'type': 'signal',
                'signal': signal
            })
        
        def on_order_executed(order):
            """订单执行回调"""
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.trade_queue.put({
                'timestamp': timestamp,
                'type': 'trade',
                'order': order
            })
            
            # 更新统计
            self.stats['total_trades'] += 1
            if order.pnl > 0:
                self.stats['winning_trades'] += 1
            elif order.pnl < 0:
                self.stats['losing_trades'] += 1
            self.stats['total_pnl'] += order.pnl
        
        def on_error(error):
            """错误回调"""
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.data_queue.put({
                'timestamp': timestamp,
                'type': 'error',
                'error': str(error)
            })
        
        # 注册回调
        self.data_stream.set_callback(on_market_data)
        self.strategy.set_signal_callback(on_trade_signal)
        self.exchange.set_trade_callback(on_order_executed)
        self.trader.set_error_callback(on_error)
    
    def start(self, duration_minutes=10):
        """
        启动实时交易
        
        Args:
            duration_minutes: 运行时长（分钟）
        """
        print(f"\n启动实时交易模拟，时长: {duration_minutes}分钟")
        print("=" * 60)
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        # 启动数据流
        self.data_stream.start()
        
        # 启动交易器
        self.trader.start()
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # 启动显示线程
        display_thread = threading.Thread(target=self.display_loop)
        display_thread.daemon = True
        display_thread.start()
        
        # 运行指定时长
        try:
            start_time = time.time()
            while time.time() - start_time < duration_minutes * 60:
                if not self.is_running:
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n用户中断交易")
        
        # 停止交易
        self.stop()
        
        # 显示最终结果
        self.show_final_results()
    
    def stop(self):
        """停止交易"""
        print("\n停止交易...")
        self.is_running = False
        self.trader.stop()
        self.data_stream.stop()
        self.stats['end_time'] = datetime.now()
    
    def monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                # 更新资金曲线峰值
                total_assets = self.exchange.get_total_assets()
                if total_assets > self.stats['peak_equity']:
                    self.stats['peak_equity'] = total_assets
                
                # 计算当前回撤
                current_drawdown = (self.stats['peak_equity'] - total_assets) / self.stats['peak_equity']
                if current_drawdown > self.stats['max_drawdown']:
                    self.stats['max_drawdown'] = current_drawdown
                
                # 检查风险限制
                if current_drawdown > 0.10:  # 回撤超过10%
                    print("⚠️ 警告: 回撤超过10%，考虑暂停交易")
                
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                print(f"监控错误: {e}")
    
    def display_loop(self):
        """显示循环"""
        last_display_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            # 每5秒显示一次状态
            if current_time - last_display_time >= 5:
                self.display_status()
                last_display_time = current_time
            
            # 处理数据队列
            self.process_queues()
            
            time.sleep(0.1)
    
    def process_queues(self):
        """处理数据队列"""
        # 处理数据队列
        while not self.data_queue.empty():
            try:
                item = self.data_queue.get_nowait()
                self.handle_data_item(item)
            except queue.Empty:
                break
        
        # 处理交易队列
        while not self.trade_queue.empty():
            try:
                item = self.trade_queue.get_nowait()
                self.handle_trade_item(item)
            except queue.Empty:
                break
    
    def handle_data_item(self, item):
        """处理数据项"""
        if item['type'] == 'data':
            data = item['data']
            # 可以在这里添加数据处理逻辑
            pass
        elif item['type'] == 'signal':
            signal = item['signal']
            print(f"[{item['timestamp']}] 信号: {signal}")
        elif item['type'] == 'error':
            error = item['error']
            print(f"[{item['timestamp']}] 错误: {error}")
    
    def handle_trade_item(self, item):
        """处理交易项"""
        if item['type'] == 'trade':
            order = item['order']
            side = "买入" if order.side == 'BUY' else "卖出"
            print(f"[{item['timestamp']}] 交易执行: {side} {order.quantity}股 @ {order.price:.2f}")
    
    def display_status(self):
        """显示当前状态"""
        status = self.trader.get_status()
        total_assets = self.exchange.get_total_assets()
        position = self.exchange.get_position(self.symbol)
        available_cash = self.exchange.get_available_cash()
        
        print("\n" + "-" * 60)
        print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"状态: {status}")
        print(f"总资产: {total_assets:,.2f} 元")
        print(f"持仓: {position.quantity if position else 0} 股")
        print(f"可用资金: {available_cash:,.2f} 元")
        print(f"交易次数: {self.stats['total_trades']}")
        print(f"累计盈亏: {self.stats['total_pnl']:+.2f} 元")
        print(f"当前回撤: {self.stats['max_drawdown']:.2%}")
        print("-" * 60)
    
    def show_final_results(self):
        """显示最终结果"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        print("\n" + "=" * 60)
        print("实时交易模拟结果")
        print("=" * 60)
        
        print(f"开始时间: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"运行时长: {duration}")
        
        print(f"\n交易统计:")
        print(f"总交易次数: {self.stats['total_trades']}")
        if self.stats['total_trades'] > 0:
            win_rate = self.stats['winning_trades'] / self.stats['total_trades']
            print(f"胜率: {win_rate:.2%}")
            print(f"盈利交易: {self.stats['winning_trades']}")
            print(f"亏损交易: {self.stats['losing_trades']}")
        
        print(f"\n资金统计:")
        final_assets = self.exchange.get_total_assets()
        total_return = (final_assets - self.initial_capital) / self.initial_capital
        print(f"初始资金: {self.initial_capital:,.2f} 元")
        print(f"最终资产: {final_assets:,.2f} 元")
        print(f"总收益率: {total_return:+.2%}")
        print(f"累计盈亏: {self.stats['total_pnl']:+.2f} 元")
        print(f"最大回撤: {self.stats['max_drawdown']:.2%}")
        
        print(f"\n持仓统计:")
        position = self.exchange.get_position(self.symbol)
        if position:
            print(f"当前持仓: {position.quantity} 股")
            print(f"持仓成本: {position.avg_cost:.2f} 元")
            print(f"持仓市值: {position.market_value:,.2f} 元")
            print(f"浮动盈亏: {position.unrealized_pnl:+.2f} 元")
        else:
            print("无持仓")
        
        # 生成交易记录
        self.save_trade_log()
    
    def save_trade_log(self):
        """保存交易日志"""
        try:
            trades = self.exchange.get_trade_history()
            if trades:
                df = pd.DataFrame([{
                    '时间': trade.timestamp,
                    '方向': trade.side,
                    '数量': trade.quantity,
                    '价格': trade.price,
                    '金额': trade.amount,
                    '佣金': trade.commission,
                    '税费': trade.tax,
                    '盈亏': trade.pnl
                } for trade in trades])
                
                df.to_csv('trade_log.csv', index=False, encoding='utf-8-sig')
                print(f"✓ 交易日志已保存: trade_log.csv")
        except Exception as e:
            print(f"⚠️ 保存交易日志失败: {e}")
    
    def run_with_visualization(self, duration_minutes=5):
        """
        运行带可视化的实时交易
        
        Args:
            duration_minutes: 运行时长
        """
        print("启动带可视化的实时交易...")
        
        # 创建图形
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        plt.subplots_adjust(hspace=0.4, wspace=0.3)
        
        # 初始化数据存储
        self.price_history = []
        self.equity_history = []
        self.time_history = []
        self.signal_history = []
        
        # 启动交易
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        # 启动数据流和交易器
        self.data_stream.start()
        self.trader.start()
        
        # 创建动画
        ani = FuncAnimation(fig, self.update_plot, interval=1000, 
                          blit=False, cache_frame_data=False)
        
        # 设置停止条件
        def stop_condition():
            start_time = time.time()
            while time.time() - start_time < duration_minutes * 60:
                if not self.is_running:
                    return False
                time.sleep(0.1)
            return True
        
        # 显示图形
        plt.show(block=False)
        
        # 运行指定时长
        try:
            if stop_condition():
                self.stop()
        except KeyboardInterrupt:
            print("\n用户中断")
            self.stop()
        
        # 关闭图形
        plt.close()
        
        # 显示结果
        self.show_final_results()
    
    def update_plot(self, frame):
        """更新图表"""
        if not self.is_running:
            return
        
        # 获取当前数据
        current_price = self.data_stream.get_current_price()
        total_assets = self.exchange.get_total_assets()
        current_time = datetime.now()
        
        # 更新历史数据
        self.price_history.append(current_price)
        self.equity_history.append(total_assets)
        self.time_history.append(current_time)
        
        # 限制数据长度
        max_points = 100
        if len(self.price_history) > max_points:
            self.price_history = self.price_history[-max_points:]
            self.equity_history = self.equity_history[-max_points:]
            self.time_history = self.time_history[-max_points:]
        
        # 清空图表
        for ax in plt.gcf().get_axes():
            ax.clear()
        
        # 子图1: 价格走势
        ax1 = plt.subplot(2, 2, 1)
        if self.price_history:
            ax1.plot(self.time_history, self.price_history, 'b-', linewidth=2, label='价格')
            ax1.set_title('实时价格走势', fontsize=12)
            ax1.set_ylabel('价格 (元)', fontsize=10)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 子图2: 资金曲线
        ax2 = plt.subplot(2, 2, 2)
        if self.equity_history:
            ax2.plot(self.time_history, self.equity_history, 'g-', linewidth=2, label='总资产')
            ax2.axhline(y=self.initial_capital, color='r', linestyle='--', alpha=0.5, label='初始资金')
            ax2.set_title('资金曲线', fontsize=12)
            ax2.set_ylabel('资金 (元)', fontsize=10)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # 子图3: 持仓信息
        ax3 = plt.subplot(2, 2, 3)
        position = self.exchange.get_position(self.symbol)
        if position:
            labels = ['持仓市值', '可用资金']
            sizes = [position.market_value, self.exchange.get_available_cash()]
            colors = ['lightcoral', 'lightskyblue']
            ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax3.set_title('资产分布', fontsize=12)
        else:
            ax3.text(0.5, 0.5, '无持仓', ha='center', va='center', fontsize=14)
            ax3.set_title('持仓状态', fontsize=12)
        
        # 子图4: 交易统计
        ax4 = plt.subplot(2, 2, 4)
        if self.stats['total_trades'] > 0:
            labels = ['盈利交易', '亏损交易']
            sizes = [self.stats['winning_trades'], self.stats['losing_trades']]
            colors = ['lightgreen', 'lightcoral']
            ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax4.set_title(f'交易统计 (共{self.stats["total_trades"]}笔)', fontsize=12)
        else:
            ax4.text(0.5, 0.5, '暂无交易', ha='center', va='center', fontsize=14)
            ax4.set_title('交易统计', fontsize=12)
        
        plt.tight_layout()
        
        # 处理队列
        self.process_queues()

def main():
    """
    主函数
    """
    print("=" * 70)
    print("PlusPlusTrader - 实时交易模拟示例")
    print("=" * 70)
    print()
    
    print("选择运行模式:")
    print("1. 基础模式 (控制台输出)")
    print("2. 可视化模式 (实时图表)")
    print("3. 高级模式 (完整功能)")
    
    try:
        choice = input("\n请选择模式 (1-3): ").strip()
        
        # 创建模拟实例
        simulation = LiveTradingSimulation(
            initial_capital=100000,
            symbol="000001.SZ"
        )
        
        if choice == '1':
            # 基础模式
            duration = int(input("运行时长 (分钟, 默认5): ") or "5")
            simulation.start(duration_minutes=duration)
            
        elif choice == '2':
            # 可视化模式
            duration = int(input("运行时长 (分钟, 默认3): ") or "3")
            simulation.run_with_visualization(duration_minutes=duration)
            
        elif choice == '3':
            # 高级模式
            print("\n高级模式配置:")
            capital = float(input("初始资金 (默认100000): ") or "100000")
            symbol = input("交易标的 (默认000001.SZ): ") or "000001.SZ"
            duration = int(input("运行时长 (分钟, 默认10): ") or "10")
            
            simulation = LiveTradingSimulation(
                initial_capital=capital,
                symbol=symbol
            )
            simulation.start(duration_minutes=duration)
            
        else:
            print("无效选择，使用默认模式")
            simulation.start(duration_minutes=5)
        
        print("\n" + "=" * 70)
        print("实时交易模拟完成!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n感谢使用 PlusPlusTrader! 🚀")

if __name__ == "__main__":
    main()