# PlusPlusTrader API 参考文档

## 📋 目录

1. [核心模块](#核心模块)
2. [数据模块](#数据模块)
3. [策略模块](#策略模块)
4. [指标模块](#指标模块)
5. [回测模块](#回测模块)
6. [交易模块](#交易模块)
7. [风险管理](#风险管理)
8. [工具函数](#工具函数)

## 🧠 核心模块

### `pplustrader`

```python
import pplustrader as ppt

# 版本信息
ppt.__version__           # 版本号
ppt.__author__            # 作者
ppt.__license__           # 许可证

# 系统信息
ppt.get_system_info()     # 获取系统信息
ppt.check_dependencies()  # 检查依赖
```

## 📊 数据模块

### `DataSource` - 数据源基类

```python
class DataSource:
    """数据源基类"""
    
    def __init__(self, name="DataSource"):
        self.name = name
        self.current_index = 0
    
    def __len__(self):
        """返回数据长度"""
        pass
    
    def __getitem__(self, index):
        """获取指定位置的数据"""
        pass
    
    def reset(self):
        """重置数据指针"""
        self.current_index = 0
    
    def next(self):
        """获取下一个数据"""
        if self.current_index < len(self):
            data = self[self.current_index]
            self.current_index += 1
            return data
        return None
    
    def get_columns(self):
        """返回数据列名"""
        pass
    
    def to_dataframe(self):
        """转换为DataFrame"""
        pass
```

### `CSVDataSource` - CSV文件数据源

```python
class CSVDataSource(DataSource):
    """
    CSV文件数据源
    
    从CSV文件加载股票数据，支持OHLCV格式。
    """
    
    def __init__(self, filepath, date_col='date', 
                 price_cols=['open', 'high', 'low', 'close', 'volume'],
                 delimiter=',', encoding='utf-8'):
        """
        初始化CSV数据源
        
        Args:
            filepath: CSV文件路径
            date_col: 日期列名
            price_cols: 价格列名列表
            delimiter: 分隔符
            encoding: 文件编码
        """
        pass
    
    # 继承自DataSource的方法
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        return self.data.iloc[index].to_dict()
    
    def get_columns(self):
        return list(self.data.columns)
    
    def to_dataframe(self):
        return self.data.copy()
```

### `LiveDataStream` - 实时数据流

```python
class LiveDataStream:
    """
    实时数据流
    
    提供实时市场数据，支持模拟和真实数据源。
    """
    
    def __init__(self, symbol, data_source='simulated', 
                 update_interval=1, **kwargs):
        """
        初始化实时数据流
        
        Args:
            symbol: 交易标的代码
            data_source: 数据源类型 ('simulated', 'yfinance', 'akshare')
            update_interval: 更新间隔（秒）
            **kwargs: 其他参数
                - volatility: 模拟数据波动率
                - trend: 模拟数据趋势
                - api_key: API密钥（真实数据源）
        """
        pass
    
    def start(self):
        """启动数据流"""
        pass
    
    def stop(self):
        """停止数据流"""
        pass
    
    def get_current_price(self):
        """获取当前价格"""
        pass
    
    def get_recent_prices(self, n=100):
        """获取最近n个价格"""
        pass
    
    def set_callback(self, callback):
        """设置数据回调函数"""
        pass
```

## 🎯 策略模块

### `BaseStrategy` - 策略基类

```python
class BaseStrategy:
    """
    策略基类
    
    所有交易策略的基类，定义了策略的基本接口。
    """
    
    def __init__(self, name="BaseStrategy", **kwargs):
        """
        初始化策略
        
        Args:
            name: 策略名称
            **kwargs: 策略参数
        """
        self.name = name
        self.params = kwargs
        self.position = 0
        self.entry_price = 0
    
    def on_bar(self, bar):
        """
        处理每个K线
        
        Args:
            bar: K线数据字典，包含OHLCV等信息
        
        Returns:
            TradeSignal or None: 交易信号或None
        """
        raise NotImplementedError("子类必须实现on_bar方法")
    
    def generate_signal(self, side, quantity, reason=""):
        """
        生成交易信号
        
        Args:
            side: 交易方向 ('BUY'/'SELL')
            quantity: 交易数量
            reason: 交易原因
        
        Returns:
            TradeSignal: 交易信号对象
        """
        pass
    
    def reset(self):
        """重置策略状态"""
        self.position = 0
        self.entry_price = 0
    
    def get_status(self):
        """获取策略状态"""
        return {
            "name": self.name,
            "position": self.position,
            "entry_price": self.entry_price,
            "params": self.params
        }
```

### `MACrossStrategy` - 移动平均交叉策略

```python
class MACrossStrategy(BaseStrategy):
    """
    移动平均交叉策略
    
    基于短期和长期移动平均线的交叉产生交易信号。
    """
    
    def __init__(self, short_period=10, long_period=30, 
                 trade_size=1000, stop_loss=0.05, 
                 take_profit=0.10, **kwargs):
        """
        初始化均线交叉策略
        
        Args:
            short_period: 短期均线周期
            long_period: 长期均线周期
            trade_size: 每次交易数量
            stop_loss: 止损比例
            take_profit: 止盈比例
            **kwargs: 其他参数传递给基类
        """
        super().__init__(name="MACrossStrategy", **kwargs)
        
        self.short_period = short_period
        self.long_period = long_period
        self.trade_size = trade_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        
        # 技术指标
        self.short_sma = ppt.SMA(period=short_period)
        self.long_sma = ppt.SMA(period=long_period)
        
        # 状态变量
        self.short_value = None
        self.long_value = None
        self.cross_signal = None  # 'golden'金叉, 'dead'死叉
    
    def on_bar(self, bar):
        """
        处理K线数据
        
        Args:
            bar: 包含'close'价格的K线数据
        
        Returns:
            TradeSignal or None: 交易信号
        """
        price = bar['close']
        
        # 更新指标
        prev_short = self.short_value
        prev_long = self.long_value
        
        self.short_value = self.short_sma.update(price)
        self.long_value = self.long_sma.update(price)
        
        # 检查数据是否足够
        if self.short_value is None or self.long_value is None:
            return None
        
        # 检测交叉信号
        signal = None
        
        if prev_short is not None and prev_long is not None:
            # 金叉：短线上穿长线
            if (prev_short <= prev_long and 
                self.short_value > self.long_value):
                self.cross_signal = 'golden'
                signal = self.generate_signal(
                    side='BUY',
                    quantity=self.trade_size,
                    reason=f"金叉信号: SMA{self.short_period}上穿SMA{self.long_period}"
                )
            
            # 死叉：短线下穿长线
            elif (prev_short >= prev_long and 
                  self.short_value < self.long_value):
                self.cross_signal = 'dead'
                signal = self.generate_signal(
                    side='SELL',
                    quantity=self.trade_size if self.position > 0 else 0,
                    reason=f"死叉信号: SMA{self.short_period}下穿SMA{self.long_period}"
                )
        
        # 止损止盈检查
        if self.position > 0 and self.entry_price > 0:
            current_return = (price - self.entry_price) / self.entry_price
            
            if current_return <= -self.stop_loss:
                # 触发止损
                signal = self.generate_signal(
                    side='SELL',
                    quantity=self.position,
                    reason=f"止损触发: 亏损{current_return:.2%}"
                )
            elif current_return >= self.take_profit:
                # 触发止盈
                signal = self.generate_signal(
                    side='SELL',
                    quantity=self.position,
                    reason=f"止盈触发: 盈利{current_return:.2%}"
                )
        
        return signal
    
    def update_position(self, side, quantity, price):
        """
        更新持仓信息
        
        Args:
            side: 交易方向
            quantity: 交易数量
            price: 交易价格
        """
        if side == 'BUY':
            self.position += quantity
            # 更新平均成本
            if self.entry_price == 0:
                self.entry_price = price
            else:
                total_cost = self.position * self.entry_price + quantity * price
                self.entry_price = total_cost / (self.position + quantity)
        elif side == 'SELL':
            self.position = max(0, self.position - quantity)
            if self.position == 0:
                self.entry_price = 0
    
    def get_indicators(self):
        """获取指标值"""
        return {
            "short_sma": self.short_value,
            "long_sma": self.long_value,
            "cross_signal": self.cross_signal
        }
```

### `RSIStrategy` - RSI策略

```python
class RSIStrategy(BaseStrategy):
    """
    RSI策略
    
    基于相对强弱指数(RSI)的超买超卖信号进行交易。
    """
    
    def __init__(self, period=14, oversold=30, overbought=70,
                 trade_size=1000, **kwargs):
        """
        初始化RSI策略
        
        Args:
            period: RSI计算周期
            oversold: 超卖阈值
            overbought: 超买阈值
            trade_size: 每次交易数量
            **kwargs: 其他参数
        """
        super().__init__(name="RSIStrategy", **kwargs)
        
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.trade_size = trade_size
        
        self.rsi_indicator = ppt.RSI(period=period)
        self.rsi_value = None
        self.prev_rsi = None
    
    def on_bar(self, bar):
        """
        处理K线数据
        
        Args:
            bar: 包含'close'价格的K线数据
        
        Returns:
            TradeSignal or None: 交易信号
        """
        price = bar['close']
        
        # 更新RSI
        self.prev_rsi = self.rsi_value
        self.rsi_value = self.rsi_indicator.update(price)
        
        if self.rsi_value is None:
            return None
        
        signal = None
        
        # 超卖区域买入信号
        if (self.prev_rsi is not None and 
            self.prev_rsi <= self.oversold and 
            self.rsi_value > self.oversold):
            # RSI从超卖区域上穿
            signal = self.generate_signal(
                side='BUY',
                quantity=self.trade_size,
                reason=f"RSI超卖反弹: {self.rsi_value:.1f} > {self.oversold}"
            )
        
        # 超买区域卖出信号
        elif (self.prev_rsi is not None and 
              self.prev_rsi >= self.overbought and 
              self.rsi_value < self.overbought):
            # RSI从超买区域下穿
            signal = self.generate_signal(
                side='SELL',
                quantity=self.trade_size if self.position > 0 else 0,
                reason=f"RSI超买回落: {self.rsi_value:.1f} < {self.overbought}"
            )
        
        return signal
```

### `PortfolioStrategy` - 组合策略

```python
class PortfolioStrategy(BaseStrategy):
    """
    组合策略
    
    管理多个子策略，进行权重分配和风险控制。
    """
    
    def __init__(self, strategies, weights=None, 
                 rebalance_frequency='M', **kwargs):
        """
        初始化组合策略
        
        Args:
            strategies: 子策略列表
            weights: 策略权重列表，None表示等权重
            rebalance_frequency: 再平衡频率 ('D'日, 'W'周, 'M'月)
            **kwargs: 其他参数
        """
        super().__init__(name="PortfolioStrategy", **kwargs)
        
        self.strategies = strategies
        self.strategy_names = [s.name for s in strategies]
        
        # 权重分配
        if weights is None:
            self.weights = [1.0 / len(strategies)] * len(strategies)
        else:
            self.weights = weights
        
        # 验证权重
        if abs(sum(self.weights) - 1.0) > 0.001:
            raise ValueError(f"权重总和必须为1.0，当前为{sum(self.weights):.4f}")
        
        self.rebalance_frequency = rebalance_frequency
        self.last_rebalance_date = None
        
        # 绩效跟踪
        self.strategy_returns = {name: [] for name in self.strategy_names}
        self.weight_history = {name: [] for name in self.strategy_names}
    
    def on_bar(self, bar):
        """
        处理K线数据
        
        Args:
            bar: K线数据
        
        Returns:
            TradeSignal or None: 组合交易信号
        """
        signals = []
        
        # 收集各策略信号
        for strategy, weight in zip(self.strategies, self.weights):
            signal = strategy.on_bar(bar)
            if signal:
                # 根据权重调整交易量
                adjusted_signal = signal.copy()
                adjusted_signal.quantity = int(signal.quantity * weight)
                signals.append(adjusted_signal)
        
        # 检查再平衡
        current_date = bar.get('date', datetime.now())
        if self._should_rebalance(current_date):
            rebalance_signals = self._rebalance_portfolio(bar)
            signals.extend(rebalance_signals)
            self.last_rebalance_date = current_date
        
        # 合并信号
        if signals:
            return self._merge_signals(signals)
        
        return None
    
    def _should_rebalance(self, current_date):
        """检查是否需要再平衡"""
        if self.last_rebalance_date is None:
            return True
        
        if self.rebalance_frequency == 'D':
            return current_date.date() > self.last_rebalance_date.date()
        elif self.rebalance_frequency == 'W':
            return current_date.isocalendar()[1] > self.last_rebalance_date.isocalendar()[1]
        elif self.rebalance_frequency == 'M':
            return current_date.month > self.last_rebalance_date.month
        
        return False
    
    def _rebalance_portfolio(self, bar):
        """执行组合再平衡"""
        signals = []
        
        # 这里可以实现复杂的再平衡逻辑
        # 例如：根据策略表现动态调整权重
        
        return signals
    
    def _merge_signals(self, signals):
        """合并多个交易信号"""
        if not signals:
            return None
        
        # 简单合并：取第一个信号
        # 实际应用中可以实现更复杂的合并逻辑
        return signals[0]
    
    def get_strategy_contributions(self):
        """获取各策略贡献度"""
        contributions = {}
        total_return = 0
        
        for name, returns in self.strategy_returns.items():
            if returns:
                strategy_return = sum(returns)
                contributions[name] = strategy_return
                total_return += strategy_return
        
        # 归一化
        if total_return != 0:
            for name in contributions:
                contributions[name] /= total_return
        
        return contributions
    
    def update_weights(self, new_weights):
        """更新策略权重"""
        if len(new_weights) != len(self.strategies):
            raise ValueError("权重数量必须与策略数量一致")
        
        if abs(sum(new_weights) - 1.0) > 0.001:
            raise ValueError(f"权重总和必须为1.0，当前为{sum(new_weights):.4f}")
        
        self.weights = new_weights
        
        # 记录权重历史
        for i, name in enumerate(self.strategy_names):
            self.weight_history[name].append(new_weights[i])
```

## 📈 指标模块

### `BaseIndicator` - 指标基类

```python
class BaseIndicator:
    """
    技术指标基类
    
    所有技术指标的基类，定义了指标的基本接口。
    """
    
    def __init__(self, name="BaseIndicator", **kwargs):
        self.name = name
        self.params = kwargs
        self.value = None
        self.history = []
    
    def update(self, price):
        """
        更新指标值
        
        Args:
            price: 当前价格
        
        Returns:
            float or tuple: 指标值
        """
        raise NotImplementedError("子类必须实现update方法")
    
    def reset(self):
        """重置指标"""
        self.value = None
        self.history = []
    
    def get_history(self):
        """获取历史值"""
        return self.history.copy()
    
    def __str__(self):
        return f"{self.name}(value={self.value})"
```

### `SMA` - 简单移动平均

```python
class SMA(BaseIndicator):
    """
    简单移动平均 (Simple Moving Average)
    """
    
    def __init__(self, period=20):
        super().__init__(name=f"SMA({period})", period=period)
        self.period = period
        self.prices = []
    
    def update(self, price):
        """
        更新SMA值
        
        Args:
            price: 当前价格
        
        Returns:
            float or None: SMA值，数据不足时返回None
        """
        self.prices.append(price)
        
        if len(self.prices) > self.period:
            self.prices.pop(0)
        
        if len(self.prices) == self.period:
            self.value = sum(self.prices) / self.period
            self.history.append(self.value)
            return self.value
        
        return None
```

### `EMA` - 指数移动平均

```python
class EMA(BaseIndicator):
    """
    指数移动平均 (Exponential Moving Average)
    """
    
    def __init__(self, period=20, smoothing=2):
        super().__init__(name=f"EMA({period})", period=period)
        self.period = period
        self.smoothing = smoothing
        self.multiplier = smoothing / (period + 1)
        self.prev_ema = None
        self.count = 0
    
    def update(self, price):
        """
        更新EMA值
        
        Args:
            price: 当前价格
        
        Returns:
            float or None: EMA值
        """
        self.count += 1
        
        if self.count < self.period:
            # 数据不足，使用SMA
            if not hasattr(self, '_sma_buffer'):
                self._sma_buffer = []
            
            self._sma_buffer.append(price)
            
            if len(self._sma_buffer) == self.period:
                self.prev_ema = sum(self._sma_buffer) / self.period
                self.value = self.prev_ema
                self.history.append(self.value)
                return self.value
            
            return None
        
        elif self.count == self.period:
            # 第一次计算EMA
            if self.prev_ema is None:
                self.prev_ema = price
            
            self.value = price
            self.history.append(self.value)
            return self.value
        
        else:
            # 正常计算EMA
            ema = price * self.multiplier + self.prev_ema * (1 - self.multiplier)
            self.prev_ema = ema
            self.value = ema
            self.history.append(self.value)
            return self.value
```

### `MACD` - 移动平均收敛发散

```python
class MACD(BaseIndicator):
    """
    移动平均收敛发散指标 (Moving Average Convergence Divergence)
    """
    
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        super().__init__(name=f"MACD({fast_period},{slow_period},{signal_period})",
                        fast_period=fast_period, slow_period=slow_period, 
                        signal_period=signal_period)
        
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
        self.fast_ema = EMA(period=fast_period)
        self.slow_ema = EMA(period=slow_period)
        self.signal_ema = EMA(period=signal_period)
        
        self.macd_line = None
        self.signal_line = None
        self.histogram = None
    
    def update(self, price):
        """
        更新MACD值
        
        Args:
            price: 当前价格
        
        Returns:
            tuple: (MACD线, 信号线, 柱状图) 或 (None, None, None)
        """
        # 更新EMA
        fast_value = self.fast_ema.update(price)
        slow_value = self.slow_ema.update(price)
        
        if fast_value is None or slow_value is None:
            return None, None, None
        
        # 计算MACD线
        self.macd_line = fast_value - slow_value
        
        # 计算信号线
        self.signal_line = self.signal_ema.update(self.macd_line)
        
        if self.signal_line is None:
            return None, None, None
        
        # 计算柱状图
        self.histogram = self.macd_line - self.signal_line
        
        # 保存历史
        self.history.append((self.macd_line, self.signal_line, self.histogram))
        
        return self.macd_line, self.signal_line, self.histogram
    
    def get_cross_signal(self):
        """
        获取交叉信号
        
        Returns:
            str or None: 'golden'金叉, 'dead'死叉, None无信号
        """
        if len(self.history) < 2:
            return None
        
        prev_macd, prev_signal, _ = self.history[-2]
        curr_macd, curr_signal, _ = self.history[-1]
        
        if prev_macd <= prev_signal and curr_macd > curr_signal:
            return 'golden'  # 金叉
        elif prev_macd >= prev_signal and curr_macd < curr_signal:
            return 'dead'    # 死叉
        
        return None
```

### `RSI` - 相对强弱指数

```python
class RSI(BaseIndicator):
    """
    相对强弱指数 (Relative Strength Index)
    """
    
    def __init__(self, period=14):
        super().__init__(name=f"RSI({period})", period=period)
        self.period = period
        self.gains = []
        self.losses = []
        self.prev_price = None
        self.avg_gain = None
        self.avg_loss = None
    
    def update(self, price):
        """
        更新RSI值
        
        Args:
            price: 当前价格
        
        Returns:
            float or None: RSI值 (0-100)
        """
        if self.prev_price is None:
            self.prev_price = price
            return None
        
        # 计算价格变化
        change = price - self.prev_price
        
        if change > 0:
            gain = change
            loss = 0
        else:
            gain = 0
            loss = abs(change)
        
        self.gains.append(gain)
        self.losses.append(loss)
        
        # 保持窗口大小
        if len(self.gains) > self.period:
            self.gains.pop(0)
            self.losses.pop(0)
        
        if len(self.gains) < self.period:
            self.prev_price = price
            return None
        
        # 计算平均增益和平均损失
        if self.avg_gain is None or self.avg_loss is None:
            # 第一次计算
            self.avg_gain = sum(self.gains) / self.period
            self.avg_loss = sum(self.losses) / self.period
        else:
            # 平滑更新
            self.avg_gain = (self.avg_gain * (self.period - 1) + gain) / self.period
            self.avg_loss = (self.avg_loss * (self.period - 1) + loss) / self.period
        
        # 计算RSI
        if self.avg_loss == 0:
            self.value = 100
        else:
            rs = self.avg_gain / self.avg_loss
            self.value = 100 - (100 / (1 + rs))
        
        self.history.append(self.value)
        self.prev_price = price
        
        return self.value
```

## 🔄 回测模块

### `BacktestEngine` - 回测引擎

```python
class BacktestEngine:
    """
    回测引擎
    
    执行策略回测，计算绩效指标。
    """
    
    def __init__(self, data_source, strategy, 
                 initial_capital=100000, commission_rate=0.0003,
                 tax_rate=0.001, slippage=0.0001, **kwargs):
        """
        初始化回测引擎
        
        Args:
            data_source: 数据源对象
            strategy: 交易策略对象
            initial_capital: 初始资金
            commission_rate: 佣金率
            tax_rate: 印花税率
            slippage: 滑点
            **kwargs: 其他参数
                - start_date: 开始日期
                - end_date: 结束日期
                - benchmark: 基准代码
                - verbose: 是否显示详细日志
        """
        pass
    
    def run(self):
        """
        运行回测
        
        Returns:
            BacktestResults: 回测结果对象
        """
        pass
    
    def run_step_by_step(self):
        """
        逐步运行回测（用于调试）
        
        Yields:
            dict: 每一步的回测状态
        """
        pass
    
    def get_current_status(self):
        """
        获取当前回测状态
        
        Returns:
            dict: 状态信息
        """
        pass
```

### `BacktestResults` - 回测结果

```python
class BacktestResults:
    """
    回测结果
    
    包含回测的所有统计信息和交易记录。
    """
    
    def __init__(self):
        # 基本统计
        self.total_return = 0.0
        self.annual_return = 0.0
        self.max_drawdown = 0.0
        self.sharpe_ratio = 0.0
        self.sortino_ratio = 0.0
        self.calmar_ratio = 0.0
        
        # 交易统计
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.win_rate = 0.0
        self.avg_win = 0.0
        self.avg_loss = 0.0
        self.profit_loss_ratio = 0.0
        
        # 风险指标
        self.volatility = 0.0
        self.downside_risk = 0.0
        self.var_95 = 0.0
        self.cvar_95 = 0.0
        
        # 数据
        self.equity_curve = None
        self.drawdown_curve = None
        self.trade_history = []
        self.daily_returns = None
    
    def generate_report(self, title="回测报告", **kwargs):
        """
        生成回测报告
        
        Args:
            title: 报告标题
            **kwargs: 报告选项
        
        Returns:
            Report: 报告对象
        """
        pass
    
    def export_to_excel(self, filepath):
        """
        导出到Excel
        
        Args:
            filepath: Excel文件路径
        """
        pass
    
    def plot(self, save_path=None):
        """
        绘制回测图表
        
        Args:
            save_path: 保存路径，None则显示
        """
        pass
    
    def compare_with_benchmark(self, benchmark_returns):
        """
        与基准比较
        
        Args:
            benchmark_returns: 基准收益率序列
        
        Returns:
            dict: 比较结果
        """
        pass
```

## ⚡ 交易模块

### `Exchange` - 交易所接口

```python
class Exchange:
    """
    交易所接口基类
    
    定义交易所的基本操作接口。
    """
    
    def __init__(self, name="Exchange"):
        self.name = name
        self.connected = False
    
    def connect(self):
        """连接交易所"""
        pass
    
    def disconnect(self):
        """断开连接"""
        pass
    
    def get_balance(self):
        """
        获取账户余额
        
        Returns:
            dict: 各币种余额
        """
        pass
    
    def get_position(self, symbol):
        """
        获取持仓
        
        Args:
            symbol: 交易标的
        
        Returns:
            Position: 持仓信息
        """
        pass
    
    def place_order(self, order):
        """
        下单
        
        Args:
            order: 订单对象
        
        Returns:
            OrderResult: 订单结果
        """
        pass
    
    def cancel_order(self, order_id):
        """
        撤单
        
        Args:
            order_id: 订单ID
        
        Returns:
            bool: 是否成功
        """
        pass
    
    def get_order_status(self, order_id):
        """
        获取订单状态
        
        Args:
            order_id: 订单ID
        
        Returns:
            OrderStatus: 订单状态
        """
        pass
```

### `SimulatedExchange` - 模拟交易所

```python
class SimulatedExchange(Exchange):
    """
    模拟交易所
    
    用于回测和模拟交易的虚拟交易所。
    """
    
    def __init__(self, initial_capital=100000, commission_rate=0.0003,
                 tax_rate=0.001, slippage=0.0001, **kwargs):
        """
        初始化模拟交易所
        
        Args:
            initial_capital: 初始资金
            commission_rate: 佣金率
            tax_rate: 印花税率
            slippage: 滑点
            **kwargs: 其他参数
        """
        super().__init__(name="SimulatedExchange")
        
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.tax_rate = tax_rate
        self.slippage = slippage
        
        # 账户状态
        self.cash = initial_capital
        self.positions = {}  # symbol -> Position
        self.trade_history = []
        self.order_history = []
        
        # 统计信息
        self.total_trades = 0
        self.total_commission = 0
        self.total_tax = 0
        self.total_pnl = 0
    
    def place_order(self, order):
        """
        执行模拟订单
        
        Args:
            order: 订单对象
        
        Returns:
            OrderResult: 订单执行结果
        """
        # 模拟订单执行
        executed_price = self._simulate_execution(order)
        
        # 计算费用
        commission = order.quantity * executed_price * self.commission_rate
        tax = order.quantity * executed_price * self.tax_rate if order.side == 'SELL' else 0
        
        # 检查资金是否充足
        if order.side == 'BUY':
            total_cost = order.quantity * executed_price + commission + tax
            if self.cash < total_cost:
                raise InsufficientFunds(f"资金不足: 需要{total_cost:.2f}, 可用{self.cash:.2f}")
            
            # 更新现金
            self.cash -= total_cost
            
            # 更新持仓
            if order.symbol not in self.positions:
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_cost=executed_price
                )
            else:
                position = self.positions[order.symbol]
                new_quantity = position.quantity + order.quantity
                new_avg_cost = (position.quantity * position.avg_cost + 
                               order.quantity * executed_price) / new_quantity
                position.quantity = new_quantity
                position.avg_cost = new_avg_cost
        
        elif order.side == 'SELL':
            if order.symbol not in self.positions:
                raise InvalidOrder(f"没有{order.symbol}的持仓")
            
            position = self.positions[order.symbol]
            if position.quantity < order.quantity:
                raise InvalidOrder(f"持仓不足: 持有{position.quantity}, 卖出{order.quantity}")
            
            # 更新持仓
            position.quantity -= order.quantity
            if position.quantity == 0:
                del self.positions[order.symbol]
            
            # 更新现金
            proceeds = order.quantity * executed_price - commission - tax
            self.cash += proceeds
            
            # 计算盈亏
            pnl = order.quantity * (executed_price - position.avg_cost) - commission - tax
            self.total_pnl += pnl
        
        # 记录交易
        trade = Trade(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=executed_price,
            commission=commission,
            tax=tax,
            pnl=pnl if order.side == 'SELL' else 0
        )
        self.trade_history.append(trade)
        self.total_trades += 1
        self.total_commission += commission
        self.total_tax += tax
        
        return OrderResult(
            order_id=order.order_id,
            status='FILLED',
            filled_quantity=order.quantity,
            filled_price=executed_price,
            commission=commission,
            tax=tax
        )
    
    def _simulate_execution(self, order):
        """
        模拟订单执行
        
        Args:
            order: 订单对象
        
        Returns:
            float: 执行价格
        """
        # 基础价格
        base_price = order.price
        
        # 应用滑点
        if order.side == 'BUY':
            # 买入时价格偏高
            executed_price = base_price * (1 + self.slippage)
        else:
            # 卖出时价格偏低
            executed_price = base_price * (1 - self.slippage)
        
        return executed_price
    
    def get_total_assets(self, current_prices=None):
        """
        获取总资产
        
        Args:
            current_prices: 当前价格字典
        
        Returns:
            float: 总资产
        """
        total = self.cash
        
        for symbol, position in self.positions.items():
            if current_prices and symbol in current_prices:
                price = current_prices[symbol]
            else:
                # 如果没有提供当前价格，使用成本价
                price = position.avg_cost
            
            total += position.quantity * price
        
        return total
    
    def get_statistics(self):
        """
        获取交易统计
        
        Returns:
            dict: 统计信息
        """
        return {
            'total_trades': self.total_trades,
            'total_commission': self.total_commission,
            'total_tax': self.total_tax,
            'total_pnl': self.total_pnl,
            'win_rate': self._calculate_win_rate(),
            'avg_win': self._calculate_avg_win(),
            'avg_loss': self._calculate_avg_loss()
        }
    
    def _calculate_win_rate(self):
        """计算胜率"""
        if self.total_trades == 0:
            return 0.0
        
        winning_trades = sum(1 for trade in self.trade_history if trade.pnl > 0)
        return winning_trades / self.total_trades
```

### `LiveTrader` - 实时交易器

```python
class LiveTrader:
    """
    实时交易器
    
    管理实时交易执行和风险控制。
    """
    
    def __init__(self, exchange, strategy, data_stream, **kwargs):
        """
        初始化实时交易器
        
        Args:
            exchange: 交易所对象
            strategy: 交易策略对象
            data_stream: 数据流对象
            **kwargs: 其他参数
                - max_position: 最大仓位比例
                - max_daily_loss: 最大日亏损比例
                - trade_throttle: 交易频率限制（秒）
                - auto_stop_loss: 自动止损比例
                - auto_take_profit: 自动止盈比例
        """
        pass
    
    def start(self):
        """启动交易器"""
        pass
    
    def stop(self):
        """停止交易器"""
        pass
    
    def pause(self):
        """暂停交易"""
        pass
    
    def resume(self):
        """恢复交易"""
        pass
    
    def get_status(self):
        """获取交易器状态"""
        pass
    
    def set_callbacks(self, on_trade=None, on_signal=None, on_error=None):
        """
        设置回调函数
        
        Args:
            on_trade: 交易执行回调
            on_signal: 交易信号回调
            on_error: 错误回调
        """
        pass
```

## 🛡️ 风险管理

### `RiskManager` - 风险管理器

```python
class RiskManager:
    """
    风险管理器
    
    监控和控制交易风险。
    """
    
    def __init__(self, initial_capital, **kwargs):
        """
        初始化风险管理器
        
        Args:
            initial_capital: 初始资金
            **kwargs: 风险参数
                - max_position_risk: 最大单笔风险比例
                - max_portfolio_risk: 最大组合风险比例
                - max_drawdown_limit: 最大回撤限制
                - var_confidence: VaR置信度
        """
        pass
    
    def check_trade_risk(self, trade):
        """
        检查交易风险
        
        Args:
            trade: 交易计划
        
        Returns:
            bool: 是否通过风险检查
        """
        pass
    
    def calculate_position_size(self, entry_price, stop_loss):
        """
        计算头寸规模
        
        Args:
            entry_price: 入场价格
            stop_loss: 止损价格
        
        Returns:
            int: 建议交易数量
        """
        pass
    
    def update_risk_metrics(self, portfolio_value, returns):
        """
        更新风险指标
        
        Args:
            portfolio_value: 组合价值
            returns: 收益率序列
        """
        pass
    
    def get_risk_report(self):
        """
        获取风险报告
        
        Returns:
            dict: 风险指标
        """
        pass
```

### `PositionSizer` - 头寸规模计算

```python
class PositionSizer:
    """
    头寸规模计算器
    
    基于风险预算计算合适的交易规模。
    """
    
    def __init__(self, risk_per_trade=0.01, risk_method='fixed'):
        """
        初始化头寸规模计算器
        
        Args:
            risk_per_trade: 每笔交易风险比例
            risk_method: 风险计算方法 ('fixed', 'kelly', 'optimal')
        """
        pass
    
    def calculate(self, account_size, entry_price, stop_loss, **kwargs):
        """
        计算头寸规模
        
        Args:
            account_size: 账户规模
            entry_price: 入场价格
            stop_loss: 止损价格
            **kwargs: 其他参数
                - win_rate: 胜率（Kelly公式需要）
                - avg_win: 平均盈利（Kelly公式需要）
                - avg_loss: 平均亏损（Kelly公式需要）
        
        Returns:
            int: 交易数量
        """
        pass
```

## 🛠️ 工具函数

### 数据工具

```python
# 数据下载
ppt.download_stock_data(symbol, start_date, end_date, **kwargs)
ppt.batch_download(symbols, start_date, end_date, **kwargs)

# 数据清洗
ppt.clean_data(df, **kwargs)
ppt.handle_missing_values(df, method='ffill')
ppt.remove_outliers(df, threshold=3)

# 特征工程
ppt.add_technical_indicators(df, indicators=['sma', 'rsi', 'macd'])
ppt.create_lagged_features(df, lags=[1, 2, 3, 5, 10])
ppt.add_volume_features(df)
```

### 性能分析

```python
# 回测分析
ppt.analyze_backtest(results, benchmark=None)
ppt.compare_strategies(strategy_results, benchmark_returns)
ppt.calculate_performance_metrics(returns, risk_free_rate=0.02)

# 可视化
ppt.plot_equity_curve(equity_curve, benchmark=None, title="资金曲线")
ppt.plot_drawdown(drawdown_curve, title="回撤曲线")
ppt.plot_monthly_returns(monthly_returns, title="月度收益")
ppt.plot_trade_distribution(trades, title="交易分布")
```

### 工具类

```python
# 日志记录
logger = ppt.get_logger(name, level=logging.INFO)
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")

# 配置管理
config = ppt.load_config(filepath="config.yaml")
ppt.save_config(config, filepath="config.yaml")

# 缓存管理
cache = ppt.CacheManager(max_size=1000, ttl=3600)
cache.set(key, value)
value = cache.get(key)
cache.clear()

# 进度显示
with ppt.ProgressBar(total=100, desc="处理进度") as pbar:
    for i in range(100):
        # 处理逻辑
        pbar.update(1)
```

## 📚 数据类型

### 基本数据类型

```python
# K线数据
Bar = {
    'timestamp': datetime,  # 时间戳
    'open': float,          # 开盘价
    'high': float,          # 最高价
    'low': float,           # 最低价
    'close': float,         # 收盘价
    'volume': float,        # 成交量
    'amount': float         # 成交额
}

# 交易信号
TradeSignal = {
    'symbol': str,          # 交易标的
    'side': str,            # 方向 ('BUY'/'SELL')
    'quantity': int,        # 数量
    'price': float,         # 价格
    'reason': str,          # 原因
    'timestamp': datetime   # 时间
}

# 订单
Order = {
    'order_id': str,        # 订单ID
    'symbol': str,          # 交易标的
    'side': str,            # 方向
    'quantity': int,        # 数量
    'price': float,         # 价格
    'order_type': str,      # 类型 ('LIMIT'/'MARKET')
    'time_in_force': str    # 有效期 ('GTC'/'IOC'/'FOK')
}

# 持仓
Position = {
    'symbol': str,          # 交易标的
    'quantity': int,        # 数量
    'avg_cost': float,      # 平均成本
    'market_value': float,  # 市值
    'unrealized_pnl': float # 浮动盈亏
}

# 交易记录
Trade = {
    'trade_id': str,        # 交易ID
    'order_id': str,        # 订单ID
    'symbol': str,          # 交易标的
    'side': str,            # 方向
    'quantity': int,        # 数量
    'price': float,         # 价格
    'commission': float,    # 佣金
    'tax': float,           # 税费
    'pnl': float,           # 盈亏
    'timestamp': datetime   # 时间
}
```

## 🔧 错误处理

### 异常类型

```python
# 基础异常
class PlusPlusTraderError(Exception):
    """所有PlusPlusTrader异常的基类"""
    pass

# 数据异常
class DataError(PlusPlusTraderError):
    """数据相关错误"""
    pass

class DataNotFoundError(DataError):
    """数据未找到"""
    pass

class DataFormatError(DataError):
    """数据格式错误"""
    pass

# 交易异常
class TradingError(PlusPlusTraderError):
    """交易相关错误"""
    pass

class InsufficientFunds(TradingError):
    """资金不足"""
    pass

class InvalidOrder(TradingError):
    """无效订单"""
    pass

class OrderRejected(TradingError):
    """订单被拒绝"""
    pass

# 网络异常
class NetworkError(PlusPlusTraderError):
    """网络错误"""
    pass

class TimeoutError(NetworkError):
    """超时错误"""
    pass

class ConnectionError(NetworkError):
    """连接错误"""
    pass

# 配置异常
class ConfigError(PlusPlusTraderError):
    """配置错误"""
    pass

class InvalidConfig(ConfigError):
    """无效配置"""
    pass

class MissingConfig(ConfigError):
    """缺少配置"""
    pass
```

### 错误处理示例

```python
try:
    # 尝试执行交易
    result = exchange.place_order(order)
    
except InsufficientFunds as e:
    print(f"资金不足: {e}")
    # 减少交易数量或取消交易
    
except InvalidOrder as e:
    print(f"无效订单: {e}")
    # 检查订单参数
    
except NetworkError as e:
    print(f"网络错误: {e}")
    # 重试或等待网络恢复
    
except Exception as e:
    print(f"未知错误: {e}")
    # 记录错误并通知管理员
    logger.error(f"交易错误: {e}", exc_info=True)
```

## 🎯 最佳实践

### 代码组织

```python
# 项目结构建议
project/
├── strategies/          # 策略目录
│   ├── __init__.py
│   ├── trend.py        # 趋势策略
│   ├── mean_reversion.py # 均值回归策略
│   └── ml_strategies.py # 机器学习策略
├── indicators/          # 指标目录
│   ├── __init__.py
│   ├── custom_indicators.py # 自定义指标
│   └── advanced_indicators.py # 高级指标
├── utils/              # 工具函数
│   ├── data_utils.py   # 数据工具
│   ├── risk_utils.py   # 风险工具
│   └── visualization.py # 可视化工具
├── configs/            # 配置文件
│   ├── trading.yaml    # 交易配置
│   └── risk.yaml       # 风险配置
└── tests/              # 测试目录
    ├── test_strategies.py
    └── test_indicators.py
```

### 性能优化

```python
# 使用向量化操作
import numpy as np

# 不好：循环
sma_values = []
for i in range(window, len(prices)):
    sma = np.mean(prices[i-window:i])
    sma_values.append(sma)

# 好：向量化
sma_values = np.convolve(prices, np.ones(window)/window, mode='valid')

# 使用C++扩展
from pplustrader.core import fast_calculate

# Python实现慢
result = slow_python_function(data)

# C++实现快
result = fast_calculate(data)

# 内存优化
# 使用生成器处理大数据
def process_large_file(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield process_line(line)  # 逐行处理，不加载全部到内存

# 使用适当的数据类型
import pandas as pd

# 使用合适的数据类型减少内存
df['price'] = df['price'].astype('float32')  # 32位浮点数
df['volume'] = df['volume'].astype('int32')  # 32位整数
```

### 测试策略

```python
import unittest
import pplustrader as ppt

class TestStrategies(unittest.TestCase):
    def setUp(self):
        """测试准备"""
        self.data = ppt.CSVDataSource("test_data.csv")
        self.initial_capital = 100000
    
    def test_macross_strategy(self):
        """测试均线交叉策略"""
        strategy = ppt.MACrossStrategy(short_period=10, long_period=30)
        backtest = ppt.BacktestEngine(
            data_source=self.data,
            strategy=strategy,
            initial_capital=self.initial_capital
        )
        
        results = backtest.run()
        
        # 断言测试
        self.assertGreater(results.total_return, -0.5)  # 亏损不超过50%
        self.assertLess(results.max_drawdown, 0.3)      # 最大回撤小于30%
        self.assertGreater(results.sharpe_ratio, 0)     # 夏普比率为正
    
    def test_rsi_strategy(self):
        """测试RSI策略"""
        strategy = ppt.RSIStrategy(period=14, oversold=30, overbought=70)
        backtest = ppt.BacktestEngine(
            data_source=self.data,
            strategy=strategy,
            initial_capital=self.initial_capital
        )
        
        results = backtest.run()
        
        # 检查交易次数
        self.assertGreater(results.trade_count, 0)
        
        # 检查胜率合理性
        self.assertGreaterEqual(results.win_rate, 0.0)
        self.assertLessEqual(results.win_rate, 1.0)
    
    def tearDown(self):
        """测试清理"""
        pass

if __name__ == '__main__':
    unittest.main()
```

## 📖 版本历史

### v1.0.0 (2026-03-22)
- 初始发布版本
- 完整的量化交易框架
- C++核心引擎
- Python完整接口
- Web监控界面
- 丰富的示例和文档

### v0.9.0 (2026-03-15)
- Beta测试版本
- 核心功能完成
- 基础文档
- 示例代码

### v0.5.0 (2026-03-01)
- Alpha测试版本
- 基本框架
- 核心模块
- 初步测试

## 📞 支持与反馈

### 获取帮助
1. 查看[文档](https://github.com/WangBreeze/PlusPlusTrader/wiki)
2. 查看[示例代码](https://github.com/WangBreeze/PlusPlusTrader/tree/main/examples)
3. 搜索[常见问题](https://github.com/WangBreeze/PlusPlusTrader/wiki/FAQ)

### 报告问题
1. 在[GitHub Issues](https://github.com/WangBreeze/PlusPlusTrader/issues)报告bug
2. 提供复现步骤和错误信息
3. 包含系统环境和版本信息

### 贡献代码
1. Fork项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

### 联系方式
- 邮箱: support@pplustrader.com
- GitHub: [@WangBreeze](https://github.com/WangBreeze)
- 文档: https://pplustrader.readthedocs.io/

---

**感谢使用 PlusPlusTrader!** 🚀

希望这个API参考文档对你有所帮助。如果有任何问题或建议，请随时联系我们。

Happy Trading! 📈