#!/usr/bin/env python3
"""
自定义指标示例
==============

这个示例展示了如何使用PlusPlusTrader的Python自定义指标系统，
创建和使用自定义技术指标。

作者: PlusPlusTrader团队
日期: 2026-03-22
"""

import pplustrader as ppt
from pplustrader.custom_indicator import (
    PythonIndicator, 
    SignalType, 
    IndicatorConfig,
    IndicatorFactory
)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 示例1: 基础自定义指标
# ============================================================================

class SimpleTrendIndicator(PythonIndicator):
    """
    简单趋势指标示例
    
    这是一个基础的自定义指标，用于演示如何创建自定义指标。
    它计算价格的简单移动平均，并根据价格与均线的位置生成交易信号。
    """
    
    def __init__(self, period=20, name="简单趋势指标"):
        """
        初始化指标
        
        Args:
            period: 移动平均周期
            name: 指标名称
        """
        config = IndicatorConfig(
            name=name,
            params={"period": period},
            signal_type=SignalType.TREND,
            description="简单趋势指标，基于价格与移动平均线的关系",
            version="1.0.0",
            author="PlusPlusTrader"
        )
        super().__init__(config)
        
        self.period = period
        self.price_history = []
        self.sma_values = []
        
        print(f"初始化 {name}，周期={period}")
    
    def update(self, price, volume=None):
        """
        更新指标值
        
        Args:
            price: 当前价格
            volume: 成交量（可选）
        
        Returns:
            tuple: (指标值, 交易信号)
        """
        # 保存价格历史
        self.price_history.append(price)
        
        # 计算简单移动平均
        if len(self.price_history) >= self.period:
            sma = np.mean(self.price_history[-self.period:])
            self.sma_values.append(sma)
            self.value = sma
            
            # 生成交易信号
            price_sma_ratio = price / sma
            
            if price_sma_ratio > 1.02:  # 价格高于均线2%
                self.signal = SignalType.STRONG_BUY
                signal_strength = "强烈买入"
            elif price_sma_ratio > 1.005:  # 价格高于均线0.5%
                self.signal = SignalType.BUY
                signal_strength = "买入"
            elif price_sma_ratio < 0.98:  # 价格低于均线2%
                self.signal = SignalType.STRONG_SELL
                signal_strength = "强烈卖出"
            elif price_sma_ratio < 0.995:  # 价格低于均线0.5%
                self.signal = SignalType.SELL
                signal_strength = "卖出"
            else:
                self.signal = SignalType.HOLD
                signal_strength = "持有"
            
            # 计算额外指标
            self.metadata = {
                "price_sma_ratio": price_sma_ratio,
                "signal_strength": signal_strength,
                "price": price,
                "sma": sma
            }
            
        else:
            # 数据不足，返回None
            self.value = None
            self.signal = SignalType.HOLD
            self.metadata = {"status": "等待数据"}
        
        return self.value, self.signal
    
    def reset(self):
        """重置指标状态"""
        self.price_history = []
        self.sma_values = []
        self.value = None
        self.signal = SignalType.HOLD
        self.metadata = {}
        print(f"{self.name} 已重置")
    
    def get_history(self):
        """获取历史数据"""
        return {
            "prices": self.price_history.copy(),
            "sma": self.sma_values.copy()
        }
    
    def plot(self, save_path=None):
        """绘制指标图表"""
        if len(self.price_history) < self.period:
            print("数据不足，无法绘图")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 子图1: 价格和SMA
        ax1.plot(self.price_history, label='价格', color='blue', linewidth=2)
        ax1.plot(range(self.period-1, len(self.price_history)), 
                self.sma_values, label=f'SMA({self.period})', 
                color='red', linestyle='--', linewidth=2)
        
        # 标记信号点
        signals = []
        for i in range(len(self.sma_values)):
            idx = i + self.period - 1
            price = self.price_history[idx]
            sma = self.sma_values[i]
            
            if price > sma * 1.02:
                ax1.scatter(idx, price, color='green', marker='^', s=100, zorder=5)
                signals.append((idx, price, '强烈买入'))
            elif price > sma * 1.005:
                ax1.scatter(idx, price, color='lightgreen', marker='^', s=80, zorder=5)
                signals.append((idx, price, '买入'))
            elif price < sma * 0.98:
                ax1.scatter(idx, price, color='red', marker='v', s=100, zorder=5)
                signals.append((idx, price, '强烈卖出'))
            elif price < sma * 0.995:
                ax1.scatter(idx, price, color='orange', marker='v', s=80, zorder=5)
                signals.append((idx, price, '卖出'))
        
        ax1.set_title(f'{self.name} - 价格与移动平均线', fontsize=14)
        ax1.set_xlabel('时间索引', fontsize=12)
        ax1.set_ylabel('价格', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 子图2: 价格/SMA比率
        ratios = []
        for i in range(len(self.sma_values)):
            idx = i + self.period - 1
            ratio = self.price_history[idx] / self.sma_values[i]
            ratios.append(ratio)
        
        ax2.plot(range(self.period-1, len(self.price_history)), 
                ratios, label='价格/SMA比率', color='purple', linewidth=2)
        ax2.axhline(y=1.02, color='green', linestyle='--', alpha=0.5, label='强烈买入线')
        ax2.axhline(y=1.005, color='lightgreen', linestyle=':', alpha=0.5, label='买入线')
        ax2.axhline(y=1.0, color='gray', linestyle='-', alpha=0.3, label='均衡线')
        ax2.axhline(y=0.995, color='orange', linestyle=':', alpha=0.5, label='卖出线')
        ax2.axhline(y=0.98, color='red', linestyle='--', alpha=0.5, label='强烈卖出线')
        
        ax2.set_title('价格/SMA比率', fontsize=14)
        ax2.set_xlabel('时间索引', fontsize=12)
        ax2.set_ylabel('比率', fontsize=12)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"图表已保存: {save_path}")
        else:
            plt.show()

# ============================================================================
# 示例2: 高级自定义指标 - 成交量加权价格指标
# ============================================================================

class VolumeWeightedPriceIndicator(PythonIndicator):
    """
    成交量加权价格指标 (VWPI)
    
    这是一个高级自定义指标，结合价格和成交量信息，
    计算成交量加权价格，并分析量价关系。
    """
    
    def __init__(self, period=20, name="成交量加权价格指标"):
        """
        初始化VWPI指标
        
        Args:
            period: 计算周期
            name: 指标名称
        """
        config = IndicatorConfig(
            name=name,
            params={"period": period},
            signal_type=SignalType.VOLUME,
            description="成交量加权价格指标，分析量价配合关系",
            version="1.0.0",
            author="PlusPlusTrader"
        )
        super().__init__(config)
        
        self.period = period
        self.price_history = []
        self.volume_history = []
        self.vwap_history = []
        self.volume_ratio_history = []
        
        # 统计信息
        self.stats = {
            "total_up_volume": 0,
            "total_down_volume": 0,
            "strong_buy_signals": 0,
            "strong_sell_signals": 0
        }
    
    def update(self, price, volume):
        """
        更新指标值
        
        Args:
            price: 当前价格
            volume: 当前成交量
        
        Returns:
            tuple: (VWAP值, 交易信号)
        """
        # 保存历史数据
        self.price_history.append(price)
        self.volume_history.append(volume)
        
        # 计算成交量加权平均价格 (VWAP)
        if len(self.price_history) >= self.period:
            recent_prices = self.price_history[-self.period:]
            recent_volumes = self.volume_history[-self.period:]
            
            total_value = sum(p * v for p, v in zip(recent_prices, recent_volumes))
            total_volume = sum(recent_volumes)
            
            vwap = total_value / total_volume if total_volume > 0 else price
            self.vwap_history.append(vwap)
            self.value = vwap
            
            # 计算成交量比率
            avg_volume = np.mean(recent_volumes)
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
            self.volume_ratio_history.append(volume_ratio)
            
            # 更新统计
            if price > recent_prices[-2] if len(recent_prices) > 1 else price:
                self.stats["total_up_volume"] += volume
            else:
                self.stats["total_down_volume"] += volume
            
            # 生成交易信号（基于量价配合）
            price_vwap_ratio = price / vwap
            signal_strength = "持有"
            
            if price_vwap_ratio > 1.01 and volume_ratio > 1.5:
                # 价涨量增，强烈买入信号
                self.signal = SignalType.STRONG_BUY
                signal_strength = "强烈买入"
                self.stats["strong_buy_signals"] += 1
            elif price_vwap_ratio > 1.005 and volume_ratio > 1.2:
                # 价涨量增，买入信号
                self.signal = SignalType.BUY
                signal_strength = "买入"
            elif price_vwap_ratio < 0.99 and volume_ratio > 1.5:
                # 价跌量增，强烈卖出信号
                self.signal = SignalType.STRONG_SELL
                signal_strength = "强烈卖出"
                self.stats["strong_sell_signals"] += 1
            elif price_vwap_ratio < 0.995 and volume_ratio > 1.2:
                # 价跌量增，卖出信号
                self.signal = SignalType.SELL
                signal_strength = "卖出"
            elif price_vwap_ratio > 1.01 and volume_ratio < 0.8:
                # 价涨量缩，谨慎信号
                self.signal = SignalType.WEAK_BUY
                signal_strength = "谨慎买入"
            elif price_vwap_ratio < 0.99 and volume_ratio < 0.8:
                # 价跌量缩，谨慎信号
                self.signal = SignalType.WEAK_SELL
                signal_strength = "谨慎卖出"
            else:
                self.signal = SignalType.HOLD
                signal_strength = "持有"
            
            # 保存元数据
            self.metadata = {
                "price": price,
                "volume": volume,
                "vwap": vwap,
                "volume_ratio": volume_ratio,
                "price_vwap_ratio": price_vwap_ratio,
                "signal_strength": signal_strength,
                "avg_volume": avg_volume
            }
            
        else:
            # 数据不足
            self.value = None
            self.signal = SignalType.HOLD
            self.metadata = {"status": "等待数据"}
        
        return self.value, self.signal
    
    def get_statistics(self):
        """获取统计信息"""
        return self.stats.copy()
    
    def plot(self, save_path=None):
        """绘制VWPI指标图表"""
        if len(self.vwap_history) < 1:
            print("数据不足，无法绘图")
            return
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 12))
        
        # 子图1: 价格和VWAP
        ax1 = axes[0]
        price_start_idx = self.period - 1
        price_indices = range(price_start_idx, len(self.price_history))
        
        ax1.plot(price_indices, self.price_history[price_start_idx:], 
                label='价格', color='blue', linewidth=2)
        ax1.plot(price_indices, self.vwap_history, 
                label=f'VWAP({self.period})', color='red', linestyle='--', linewidth=2)
        
        ax1.set_title(f'{self.name} - 价格与成交量加权平均价', fontsize=14)
        ax1.set_ylabel('价格', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 子图2: 成交量
        ax2 = axes[1]
        volume_indices = range(price_start_idx, len(self.volume_history))
        volumes = self.volume_history[price_start_idx:]
        
        # 根据价格变化着色
        colors = []
        for i in range(1, len(self.price_history[price_start_idx:])):
            if self.price_history[price_start_idx + i] > self.price_history[price_start_idx + i - 1]:
                colors.append('green')
            else:
                colors.append('red')
        colors.append('gray')  # 最后一个
        
        ax2.bar(volume_indices, volumes, color=colors, alpha=0.7, label='成交量')
        ax2.axhline(y=np.mean(volumes), color='orange', linestyle='--', 
                   label=f'平均成交量: {np.mean(volumes):.0f}')
        
        ax2.set_title('成交量', fontsize=14)
        ax2.set_ylabel('成交量', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 子图3: 成交量比率和信号
        ax3 = axes[2]
        
        # 成交量比率
        ax3.plot(price_indices, self.volume_ratio_history, 
                label='成交量比率', color='purple', linewidth=2)
        ax3.axhline(y=1.0, color='gray', linestyle='-', alpha=0.3, label='基准线')
        ax3.axhline(y=1.5, color='red', linestyle='--', alpha=0.5, label='高量线')
        ax3.axhline(y=0.8, color='blue', linestyle='--', alpha=0.5, label='低量线')
        
        # 标记信号
        for i, metadata in enumerate(self.metadata_history if hasattr(self, 'metadata_history') else []):
            if 'signal_strength' in metadata:
                idx = price_start_idx + i
                signal = metadata['signal_strength']
                
                if signal == "强烈买入":
                    ax3.scatter(idx, self.volume_ratio_history[i], 
                              color='green', marker='^', s=150, zorder=5)
                elif signal == "买入":
                    ax3.scatter(idx, self.volume_ratio_history[i], 
                              color='lightgreen', marker='^', s=100, zorder=5)
                elif signal == "强烈卖出":
                    ax3.scatter(idx, self.volume_ratio_history[i], 
                              color='red', marker='v', s=150, zorder=5)
                elif signal == "卖出":
                    ax3.scatter(idx, self.volume_ratio_history[i], 
                              color='orange', marker='v', s=100, zorder=5)
        
        ax3.set_title('成交量比率与交易信号', fontsize=14)
        ax3.set_xlabel('时间索引', fontsize=12)
        ax3.set_ylabel('成交量比率', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"图表已保存: {save_path}")
        else:
            plt.show()

# ============================================================================
# 示例3: 使用指标工厂
# ============================================================================

def demo_indicator_factory():
    """演示指标工厂的使用"""
    print("\n" + "=" * 60)
    print("指标工厂演示")
    print("=" * 60)
    
    # 创建指标工厂实例
    factory = IndicatorFactory()
    
    # 注册自定义指标
    factory.register_indicator(
        name="simple_trend",
        indicator_class=SimpleTrendIndicator,
        description="简单趋势指标",
        category="trend",
        default_params={"period": 20}
    )
    
    factory.register_indicator(
        name="volume_weighted",
        indicator_class=VolumeWeightedPriceIndicator,
        description="成交量加权价格指标",
        category="volume",
        default_params={"period": 20}
    )
    
    print("已注册指标:")
    for name, info in factory.list_indicators().items():
        print(f"  - {name}: {info['description']}")
    
    # 使用工厂创建指标
    print("\n使用工厂创建指标:")
    
    # 创建简单趋势指标
    trend_indicator = factory.create_indicator(
        name="simple_trend",
        params={"period": 14}
    )
    print(f"✓ 创建: {trend_indicator.name}")
    
    # 创建成交量加权指标
    volume_indicator = factory.create_indicator(
        name="volume_weighted",
        params={"period": 10}
    )
    print(f"✓ 创建: {volume_indicator.name}")
    
    return factory

# ============================================================================
# 示例4: 在回测中使用自定义指标
# ============================================================================

def demo_custom_indicator_in_backtest():
    """演示在回测中使用自定义指标"""
    print("\n" + "=" * 60)
    print("在回测中使用自定义指标")
    print("=" * 60)
    
    # 创建自定义策略
    class CustomIndicatorStrategy(ppt.BaseStrategy):
        """使用自定义指标的策略"""
        
        def __init__(self, name="自定义指标策略"):
            super().__init__(name=name)
            
            # 创建自定义指标
            self.trend_indicator = SimpleTrendIndicator(period=20)
            self.volume_indicator = VolumeWeightedPriceIndicator(period=20)
            
            # 状态变量
            self.position = 0
            self.entry_price = 0
        
        def on_bar(self, bar):
            """处理每个K线"""
            price = bar['close']
            volume = bar['volume']
            
            # 更新指标
            trend_value, trend_signal = self.trend_indicator.update(price)
            volume_value, volume_signal = self.volume_indicator.update(price, volume)
            
            # 生成交易信号（结合两个指标）
            if (trend_signal == SignalType.STRONG_BUY and 
                volume_signal in [SignalType.BUY, SignalType.STRONG_BUY]):
                # 趋势强烈看涨且量能配合，买入信号
                return self.generate_signal(
                    side='BUY',
                    quantity=1000,
                    reason="趋势+量能双重买入信号"
                )
            
            elif (trend_signal == SignalType.STRONG_SELL and 
                  volume_signal in [SignalType.SELL, SignalType.STRONG_SELL]):
                # 趋势强烈看跌且量能配合，卖出信号
                return self.generate_signal(
                    side='SELL',
                    quantity=1000 if self.position > 0 else 0,
                    reason="趋势+量能双重卖出信号"
                )
            
            elif self.position > 0 and trend_signal == SignalType.SELL:
                # 持有多头但趋势转弱，平仓
                return self.generate_signal(
                    side='SELL',
                    quantity=self.position,
                    reason="趋势转弱，平仓"
                )
            
            return None  # 无信号
        
        def get_indicator_values(self):
            """获取指标值"""
            return {
                "trend_value": self.trend_indicator.value,
                "trend_signal": self.trend_indicator.signal,
                "volume_value": self.volume_indicator.value,
                "volume_signal": self.volume_indicator.signal
            }
    
    # 创建策略实例
    strategy = CustomIndicatorStrategy()
    
    print(f"创建策略: {strategy.name}")
    print("策略使用两个自定义指标:")
    print("  1. SimpleTrendIndicator - 趋势分析")
    print("  2. VolumeWeightedPriceIndicator - 量价分析")
    
    return strategy

# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 70)
    print("PlusPlusTrader - 自定义指标示例")
    print("=" * 70)
    print()
    
    print("选择演示模式:")
    print("1. 基础指标演示")
    print("2. 高级指标演示")
    print("3. 指标工厂演示")
    print("4. 回测集成演示")
    print("5. 完整演示")
    
    try:
        choice = input("\n请选择模式 (1-5): ").strip()
        
        if choice == '1' or choice == '5':
            # 基础指标演示
            print("\n" + "=" * 60)
            print("基础指标演示 - SimpleTrendIndicator")
            print("=" * 60)
            
            # 创建指标
            indicator = SimpleTrendIndicator(period=10, name="测试趋势指标")
            
            # 模拟价格数据
            print("\n模拟价格数据更新:")
            prices = [100, 102, 101, 105, 103, 108, 107, 110, 109, 112,
                      115, 113, 116, 118, 117, 120, 119, 122, 121, 125]
            
            for i, price in enumerate(prices, 1):
                value, signal = indicator.update(price)
                if value is not None:
                    print(f"第{i}天: 价格={price}, SMA={value:.2f}, 信号={signal}")
            
            # 绘制图表
            indicator.plot("simple_trend_indicator.png")
            
            # 显示历史数据
            history = indicator.get_history()
            print(f"\n历史数据统计:")
            print(f"  价格数量: {len(history['prices'])}")
            print(f"  SMA数量: {len(history['sma'])}")
            print(f"  最后SMA值: {history['sma'][-1] if history['sma'] else 'N/A'}")
        
        if choice == '2' or choice == '5':
            # 高级指标演示
            print("\n" + "=" * 60)
            print("高级指标演示 - VolumeWeightedPriceIndicator")
            print("=" * 60)
            
            # 创建指标
            indicator = VolumeWeightedPriceIndicator(period=10, name="测试VWPI指标")
            
            # 模拟价格和成交量数据
            print("\n模拟量价数据更新:")
            np.random.seed(42)
            n = 30
            base_price = 100
            prices = base_price + np.cumsum(np.random.randn(n) * 2)
            volumes = np.random.lognormal(10, 0.5, n).astype(int)
            
            for i in range(n):
                value, signal = indicator.update(prices[i], volumes[i])
                if value is not None:
                    metadata = indicator.metadata
                    print(f"第{i+1}天: 价格={prices[i]:.2f}, VWAP={value:.2f}, "
                          f"成交量={volumes[i]}, 信号={signal}")
            
            # 绘制图表
            indicator.plot("volume_weighted_indicator.png")
            
            # 显示统计信息
            stats = indicator.get_statistics()
            print(f"\n统计信息:")
            print(f"  上涨成交量: {stats['total_up_volume']:,}")
            print(f"  下跌成交量: {stats['total_down_volume']:,}")
            print(f"  强烈买入信号: {stats['strong_buy_signals']}")
            print(f"  强烈卖出信号: {stats['strong_sell_signals']}")
        
        if choice == '3' or choice == '5':
            # 指标工厂演示
            factory = demo_indicator_factory()
            
            # 测试工厂功能
            print("\n工厂功能测试:")
            
            # 获取指标信息
            indicator_info = factory.get_indicator_info("simple_trend")
            print(f"指标信息: {indicator_info}")
            
            # 批量创建指标
            indicators = factory.create_indicators([
                {"name": "simple_trend", "params": {"period": 14}},
                {"name": "volume_weighted", "params": {"period": 20}}
            ])
            print(f"批量创建 {len(indicators)} 个指标")
        
        if choice == '4' or choice == '5':
            # 回测集成演示
            strategy = demo_custom_indicator_in_backtest()
            
            print("\n策略测试:")
            # 模拟几个K线数据
            test_bars = [
                {'close': 100, 'volume': 10000},
                {'close': 102, 'volume': 12000},
                {'close': 101, 'volume': 8000},
                {'close': 105, 'volume': 15000},
                {'close': 108, 'volume': 18000}
            ]
            
            print("模拟K线处理:")
            for i, bar in enumerate(test_bars, 1):
                signal = strategy.on_bar(bar)
                indicator_values = strategy.get_indicator_values()
                
                print(f"K线{i}: 价格={bar['close']}, 成交量={bar['volume']}")
                print(f"  趋势信号: {indicator_values['trend_signal']}")
                print(f"  量价信号: {indicator_values['volume_signal']}")
                if signal:
                    print(f"  交易信号: {signal}")
        
        print("\n" + "=" * 70)
        print("自定义指标示例完成!")
        print("=" * 70)
        
        print("\n生成的文件:")
        if choice in ['1', '5']:
            print("  - simple_trend_indicator.png (趋势指标图表)")
        if choice in ['2', '5']:
            print("  - volume_weighted_indicator.png (量价指标图表)")
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n感谢使用 PlusPlusTrader! 🚀")

if __name__ == "__main__":
    main()