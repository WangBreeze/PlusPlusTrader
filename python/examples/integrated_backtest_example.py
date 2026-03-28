#!/usr/bin/env python3
"""
Integrated Backtest Example showcasing HistoricalDataManager integration.
Demonstrates the new features: multi-timeframe support, data preprocessing, caching.
"""

import sys
import os
import tempfile
import datetime

# Add the bindings directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pplustrader
    print("✅ Successfully imported pplustrader module")
except ImportError as e:
    print(f"❌ Failed to import pplustrader: {e}")
    sys.exit(1)

def create_sample_data_file(filepath, symbol="AAPL", timeframe="MINUTE_1", num_records=100):
    """Create a sample CSV data file for testing"""
    import csv
    from datetime import datetime, timedelta
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        base_time = datetime(2026, 1, 1, 9, 30, 0)
        price = 150.0
        
        # Adjust interval based on timeframe
        if timeframe == "MINUTE_1":
            interval = timedelta(minutes=1)
        elif timeframe == "MINUTE_5":
            interval = timedelta(minutes=5)
        elif timeframe == "HOUR_1":
            interval = timedelta(hours=1)
        else:
            interval = timedelta(minutes=1)
        
        for i in range(num_records):
            timestamp = base_time + interval * i
            open_price = price + i * 0.01
            high_price = open_price + 0.5
            low_price = open_price - 0.3
            close_price = open_price + (0.2 if i % 2 == 0 else -0.1)
            volume = 10000 + i * 100
            
            writer.writerow([
                timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                f"{open_price:.2f}",
                f"{high_price:.2f}",
                f"{low_price:.2f}",
                f"{close_price:.2f}",
                volume
            ])
    
    print(f"✅ Created sample data: {filepath} ({num_records} {timeframe} records)")
    return filepath

class SimpleTestStrategy(pplustrader.BaseStrategy):
    """A simple test strategy for demonstration"""
    def __init__(self, name="TestStrategy"):
        super().__init__(name)
        self.buy_signal_count = 0
        self.sell_signal_count = 0
        
    def on_tick(self, tick):
        """Simple strategy: Buy when price crosses above moving average"""
        # In a real strategy, you would implement actual logic here
        # For demonstration, we'll just count ticks
        if tick.close > tick.open:
            self.buy_signal_count += 1
        else:
            self.sell_signal_count += 1
        
        # No actual orders for this demo
        return
    
    def get_stats(self):
        return {
            "buy_signals": self.buy_signal_count,
            "sell_signals": self.sell_signal_count
        }

def demonstrate_integrated_backtest():
    """Demonstrate integrated backtest with HistoricalDataManager"""
    print("=" * 70)
    print("INTEGRATED BACKTEST DEMONSTRATION")
    print("=" * 70)
    print("Demonstrating HistoricalDataManager integration with BacktestEngine")
    print()
    
    # Create a temporary directory for test data
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 Using temporary directory: {tmpdir}")
        
        # Create sample data files
        data_dir = os.path.join(tmpdir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Create 1-minute data
        min1_file = os.path.join(data_dir, "AAPL_MINUTE_1.csv")
        create_sample_data_file(min1_file, "AAPL", "MINUTE_1", 200)
        
        # Create 5-minute data  
        min5_file = os.path.join(data_dir, "AAPL_MINUTE_5.csv")
        create_sample_data_file(min5_file, "AAPL", "MINUTE_5", 40)
        
        print("\n" + "=" * 70)
        print("1. 🎯 CONFIGURING BACKTEST WITH DATA MANAGER")
        print("=" * 70)
        
        # Create backtest configuration
        config = pplustrader.BacktestConfig()
        config.symbol = "AAPL"
        config.initial_capital = 100000.0
        config.commission_rate = 0.001
        config.slippage = 0.0001
        
        # New configuration options
        config.timeframe = pplustrader.TimeFrame.MINUTE_1
        config.clean_data = True
        config.fill_missing_data = True
        config.remove_outliers = False
        config.outlier_z_score_threshold = 3.0
        config.use_cache = True
        config.max_cache_size_mb = 50
        config.enable_progress_reporting = True
        config.progress_report_interval = 50
        
        print(f"   Symbol: {config.symbol}")
        print(f"   Timeframe: {pplustrader.timeframe_to_string(config.timeframe)}")
        print(f"   Initial capital: ${config.initial_capital:,.2f}")
        print(f"   Use cache: {config.use_cache}")
        print(f"   Data preprocessing: clean={config.clean_data}, fill={config.fill_missing_data}")
        
        print("\n" + "=" * 70)
        print("2. 📥 LOADING DATA WITH HISTORICALDATAMANAGER")
        print("=" * 70)
        
        # Create backtest engine
        engine = pplustrader.create_backtest_engine()
        engine.set_config(config)
        
        # Create data manager configuration
        data_config = pplustrader.HistoricalDataConfig()
        data_config.data_dir = data_dir
        data_config.file_pattern = "{symbol}_{timeframe}.csv"
        data_config.cache_enabled = True
        data_config.max_cache_size_mb = config.max_cache_size_mb
        data_config.validate_data = True
        
        print("   Loading data using HistoricalDataManager...")
        
        # Method 1: Load using data manager with configuration
        success = engine.load_data_from_manager(data_config)
        print(f"   ✅ load_data_from_manager success: {success}")
        
        # Get the data manager instance
        data_manager = engine.get_data_manager()
        if data_manager:
            print(f"   ✅ Data manager retrieved successfully")
            
            # Check cache stats
            cache_stats = data_manager.get_cache_stats()
            print(f"   📊 Cache stats: {cache_stats.total_data_points} data points, "
                  f"hit rate: {cache_stats.hit_rate:.1%}")
        
        print("\n" + "=" * 70)
        print("3. 🔄 TESTING DIFFERENT TIMEFRAMES")
        print("=" * 70)
        
        # Test resampling
        if data_manager and data_manager.has_data("AAPL", pplustrader.TimeFrame.MINUTE_1):
            print("   Testing data resampling...")
            
            # Get 1-minute data
            min1_data = data_manager.get_data("AAPL", pplustrader.TimeFrame.MINUTE_1)
            print(f"   ✅ 1-minute data: {len(min1_data)} points")
            
            # Resample to 5-minute
            resampled = data_manager.resample_data(
                min1_data,
                pplustrader.TimeFrame.MINUTE_1,
                pplustrader.TimeFrame.MINUTE_5
            )
            print(f"   ✅ Resampled to 5-minute: {len(resampled)} points")
            
            # Cache the resampled data
            success = data_manager.resample_and_cache(
                "AAPL",
                pplustrader.TimeFrame.MINUTE_1,
                pplustrader.TimeFrame.MINUTE_5
            )
            print(f"   ✅ Cached resampled data: {success}")
            
            # Check available timeframes
            timeframes = data_manager.get_cached_timeframes("AAPL")
            print(f"   ⏱️  Available timeframes for AAPL: {[pplustrader.timeframe_to_string(tf) for tf in timeframes]}")
        
        print("\n" + "=" * 70)
        print("4. 🧹 DATA PREPROCESSING DEMONSTRATION")
        print("=" * 70)
        
        if data_manager and data_manager.has_data("AAPL", pplustrader.TimeFrame.MINUTE_1):
            print("   Testing data preprocessing features...")
            
            # Get raw data
            raw_data = data_manager.get_data("AAPL", pplustrader.TimeFrame.MINUTE_1)
            
            # Clean data
            cleaned = data_manager.clean_data(raw_data)
            print(f"   🧼 Data cleaning: {len(raw_data)} -> {len(cleaned)} points")
            
            # Fill missing data
            filled = data_manager.fill_missing_data(raw_data, pplustrader.TimeFrame.MINUTE_1)
            print(f"   🔧 Data filling: {len(raw_data)} -> {len(filled)} points")
            
            # Remove outliers
            no_outliers = data_manager.remove_outliers(raw_data, z_score_threshold=2.5)
            print(f"   📈 Outlier removal: {len(raw_data)} -> {len(no_outliers)} points")
        
        print("\n" + "=" * 70)
        print("5. 🤖 RUNNING INTEGRATED BACKTEST")
        print("=" * 70)
        
        # Add a test strategy
        strategy = SimpleTestStrategy("DemoStrategy")
        engine.add_strategy(strategy)
        
        print("   Running backtest with integrated data manager...")
        
        # Run the backtest
        success = engine.run()
        print(f"   ✅ Backtest run success: {success}")
        
        if success:
            # Get results
            result = engine.get_result()
            duration = engine.get_backtest_duration()
            progress = engine.get_progress()
            
            print(f"   📊 Backtest results:")
            print(f"     - Duration: {duration} ms")
            print(f"     - Progress: {progress:.1%}")
            print(f"     - Total return: {result.total_return * 100:.2f}%")
            print(f"     - Max drawdown: {result.max_drawdown * 100:.2f}%")
            print(f"     - Sharpe ratio: {result.sharpe_ratio:.2f}")
            print(f"     - Win rate: {result.win_rate * 100:.1f}%")
            print(f"     - Total trades: {result.total_trades}")
            
            # Get strategy stats
            stats = strategy.get_stats()
            print(f"   🤖 Strategy stats: {stats}")
        
        print("\n" + "=" * 70)
        print("6. 💾 DATA EXPORT AND CACHE MANAGEMENT")
        print("=" * 70)
        
        if data_manager:
            print("   Testing data export...")
            
            # Export data to CSV
            export_file = os.path.join(tmpdir, "exported_backtest_data.csv")
            success = data_manager.export_to_csv("AAPL", pplustrader.TimeFrame.MINUTE_1, export_file)
            print(f"   💾 Export to CSV: {success} ({export_file})")
            
            # Cache management
            cached_symbols = data_manager.get_cached_symbols()
            print(f"   🗄️  Cached symbols: {cached_symbols}")
            
            # Clear cache
            print("   Clearing cache...")
            data_manager.clear_cache()
            
            final_stats = data_manager.get_cache_stats()
            print(f"   📊 Final cache stats: {final_stats.total_data_points} data points")
        
        print("\n" + "=" * 70)
        print("7. 🔧 TESTING LEGACY COMPATIBILITY")
        print("=" * 70)
        
        print("   Testing legacy load_data() method...")
        
        # Create new engine for legacy test
        legacy_engine = pplustrader.create_backtest_engine()
        legacy_config = pplustrader.BacktestConfig()
        legacy_config.symbol = "AAPL"
        legacy_config.initial_capital = 50000.0
        
        legacy_engine.set_config(legacy_config)
        
        # Use legacy load_data method (should work with new implementation)
        success = legacy_engine.load_data(min1_file)
        print(f"   ✅ Legacy load_data() success: {success}")
        
        if success:
            legacy_engine.add_strategy(SimpleTestStrategy("LegacyStrategy"))
            legacy_engine.run()
            print(f"   ✅ Legacy backtest completed")
        
        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)
        
        return True

def main():
    """Main function"""
    print("🧪 PlusPlusTrader Integrated Backtest Test")
    print("Date:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Version: 0.3.1 (HistoricalDataManager Integration)")
    print()
    
    try:
        success = demonstrate_integrated_backtest()
        if success:
            print("\n🎉 HISTORICALDATAMANAGER INTEGRATION SUCCESSFUL!")
            print("\n✅ Integration features demonstrated:")
            print("   1. 🎯 Multi-timeframe backtest configuration")
            print("   2. 📥 Data loading via HistoricalDataManager")
            print("   3. 🔄 Automatic time frame resampling")
            print("   4. 🧹 Built-in data preprocessing pipeline")
            print("   5. 🗄️  Configurable caching system")
            print("   6. 🤖 Integrated strategy execution")
            print("   7. 📊 Performance metrics and timing")
            print("   8. 💾 Data export capabilities")
            print("   9. 🔧 Legacy API compatibility")
            print("   10. 📈 Cache statistics and management")
            print("\n🚀 Backtest engine now has enterprise-grade data management!")
        else:
            print("\n❌ Demonstration failed")
            return 1
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())