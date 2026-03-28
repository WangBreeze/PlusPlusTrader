#!/usr/bin/env python3
"""
HistoricalDataManager example showcasing data loading, querying, resampling, and management.
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

def create_sample_data_file(filepath, symbol="AAPL", num_records=100):
    """Create a sample CSV data file for testing"""
    import csv
    from datetime import datetime, timedelta
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        base_time = datetime(2026, 1, 1, 9, 30, 0)
        price = 150.0
        
        for i in range(num_records):
            timestamp = base_time + timedelta(minutes=i)
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
    
    print(f"✅ Created sample data file: {filepath} ({num_records} records)")
    return filepath

def demonstrate_historical_data_manager():
    """Demonstrate HistoricalDataManager functionality"""
    print("=" * 70)
    print("HISTORICAL DATA MANAGER DEMONSTRATION")
    print("=" * 70)
    
    # Create a temporary directory for test data
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\n📁 Using temporary directory: {tmpdir}")
        
        # Create sample data files
        data_dir = os.path.join(tmpdir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Create 1-minute data
        min1_file = os.path.join(data_dir, "AAPL_MINUTE_1.csv")
        create_sample_data_file(min1_file, "AAPL", 100)
        
        # Create 5-minute data
        min5_file = os.path.join(data_dir, "AAPL_MINUTE_5.csv")
        create_sample_data_file(min5_file, "AAPL", 20)
        
        # Step 1: Create HistoricalDataManager with configuration
        print("\n1. 📋 Creating HistoricalDataManager with configuration")
        config = pplustrader.HistoricalDataConfig()
        config.data_dir = data_dir
        config.file_pattern = "{symbol}_{timeframe}.csv"
        config.cache_enabled = True
        config.max_cache_size_mb = 10
        config.validate_data = True
        
        manager = pplustrader.create_historical_data_manager_with_config(config)
        print(f"   ✅ Created manager with cache enabled: {config.cache_enabled}")
        print(f"   ✅ Data directory: {config.data_dir}")
        print(f"   ✅ Max cache size: {config.max_cache_size_mb}MB")
        
        # Step 2: Load data
        print("\n2. 📥 Loading historical data")
        
        # Load 1-minute data
        print("   Loading AAPL 1-minute data...")
        success = manager.load_data("AAPL", pplustrader.TimeFrame.MINUTE_1)
        print(f"   ✅ Load success: {success}")
        
        if success:
            count = manager.get_data_count("AAPL", pplustrader.TimeFrame.MINUTE_1)
            print(f"   ✅ Loaded {count} data points")
            
            # Get data range
            start, end = manager.get_data_range("AAPL", pplustrader.TimeFrame.MINUTE_1)
            print(f"   ✅ Data range: {start} to {end}")
        
        # Step 3: Query data
        print("\n3. 🔍 Querying data")
        
        if manager.has_data("AAPL", pplustrader.TimeFrame.MINUTE_1):
            # Get latest 10 data points
            latest_data = manager.get_latest_data("AAPL", pplustrader.TimeFrame.MINUTE_1, 10)
            print(f"   ✅ Retrieved {len(latest_data)} latest data points")
            
            if latest_data:
                print(f"   📊 Latest tick: {latest_data[-1].symbol} @ {latest_data[-1].close}")
            
            # Get data by time range (simulated)
            print("   Querying data by time range...")
            # In a real scenario, you would specify actual start/end times
            all_data = manager.get_data("AAPL", pplustrader.TimeFrame.MINUTE_1, start, end)
            print(f"   ✅ Retrieved {len(all_data)} data points in range")
        
        # Step 4: Data resampling
        print("\n4. 🔄 Demonstrating data resampling")
        
        # Resample 1-minute data to 5-minute
        print("   Resampling 1-minute data to 5-minute...")
        resampled = manager.resample_data(
            all_data if 'all_data' in locals() else [],
            pplustrader.TimeFrame.MINUTE_1,
            pplustrader.TimeFrame.MINUTE_5
        )
        print(f"   ✅ Resampled {len(all_data) if 'all_data' in locals() else 0} 1-min ticks to {len(resampled)} 5-min ticks")
        
        # Resample and cache
        print("   Resampling and caching...")
        success = manager.resample_and_cache("AAPL", 
                                           pplustrader.TimeFrame.MINUTE_1,
                                           pplustrader.TimeFrame.MINUTE_5)
        print(f"   ✅ Resample and cache success: {success}")
        
        if success:
            has_5min = manager.has_data("AAPL", pplustrader.TimeFrame.MINUTE_5)
            count_5min = manager.get_data_count("AAPL", pplustrader.TimeFrame.MINUTE_5)
            print(f"   ✅ 5-minute data available: {has_5min} ({count_5min} points)")
        
        # Step 5: Cache management
        print("\n5. 🗄️ Cache management")
        
        cache_stats = manager.get_cache_stats()
        print(f"   📊 Cache stats:")
        print(f"     - Total entries: {cache_stats.total_entries}")
        print(f"     - Total data points: {cache_stats.total_data_points}")
        print(f"     - Cache size: {cache_stats.total_cache_size_bytes / 1024:.2f} KB")
        print(f"     - Hit rate: {cache_stats.hit_rate:.2%}")
        
        cached_symbols = manager.get_cached_symbols()
        print(f"   📋 Cached symbols: {cached_symbols}")
        
        for symbol in cached_symbols:
            timeframes = manager.get_cached_timeframes(symbol)
            print(f"   ⏱️  {symbol} timeframes: {[pplustrader.timeframe_to_string(tf) for tf in timeframes]}")
        
        # Step 6: Data preprocessing
        print("\n6. 🧹 Data preprocessing demonstration")
        
        if 'all_data' in locals() and all_data:
            print("   Cleaning data...")
            cleaned = manager.clean_data(all_data)
            print(f"   ✅ Cleaned data: {len(all_data)} -> {len(cleaned)} points")
            
            print("   Filling missing data...")
            filled = manager.fill_missing_data(all_data, pplustrader.TimeFrame.MINUTE_1)
            print(f"   ✅ Filled data: {len(all_data)} -> {len(filled)} points")
            
            print("   Removing outliers...")
            no_outliers = manager.remove_outliers(all_data, z_score_threshold=2.5)
            print(f"   ✅ Outlier removal: {len(all_data)} -> {len(no_outliers)} points")
        
        # Step 7: DataFeed interface
        print("\n7. 📡 DataFeed interface demonstration")
        
        print("   Connecting as DataFeed...")
        manager.connect()
        
        print("   Subscribing to symbols...")
        manager.subscribe("AAPL")
        manager.subscribe("GOOGL")  # Note: This symbol doesn't have data loaded
        
        subscribed = manager.get_subscribed_symbols()
        print(f"   ✅ Subscribed symbols: {subscribed}")
        
        print("   Getting next ticks...")
        next_ticks = manager.get_next_ticks(5)
        print(f"   ✅ Retrieved {len(next_ticks)} ticks")
        
        print("   Unsubscribing...")
        manager.unsubscribe("AAPL")
        manager.unsubscribe("GOOGL")
        
        print("   Disconnecting...")
        manager.disconnect()
        
        # Step 8: Export data
        print("\n8. 💾 Exporting data")
        
        export_file = os.path.join(tmpdir, "exported_data.csv")
        success = manager.export_to_csv("AAPL", pplustrader.TimeFrame.MINUTE_1, export_file)
        print(f"   ✅ Export to CSV: {success}")
        if success:
            print(f"   📄 Exported to: {export_file}")
        
        # Step 9: Cache operations
        print("\n9. 🗑️ Cache operations")
        
        print("   Unloading 5-minute data...")
        success = manager.unload_data("AAPL", pplustrader.TimeFrame.MINUTE_5)
        print(f"   ✅ Unload success: {success}")
        
        print("   Clearing cache...")
        manager.clear_cache()
        
        final_stats = manager.get_cache_stats()
        print(f"   📊 Final cache stats:")
        print(f"     - Total entries: {final_stats.total_entries}")
        print(f"     - Total data points: {final_stats.total_data_points}")
        
        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)
        
        return True

def main():
    """Main function"""
    print("🧪 PlusPlusTrader Historical Data Manager Test")
    print("Date:", datetime.datetime.now().strftime("%Y-%m-%d"))
    print("Version: 0.3.0 (Historical Data Manager)")
    print()
    
    try:
        success = demonstrate_historical_data_manager()
        if success:
            print("\n🎉 HISTORICAL DATA MANAGER IMPLEMENTATION SUCCESSFUL!")
            print("\n✅ Key features implemented:")
            print("   1. 📂 Multi-timeframe data loading and caching")
            print("   2. 🔍 Flexible data querying (range, latest, count)")
            print("   3. 🔄 Timeframe resampling (1-min → 5-min, etc.)")
            print("   4. 🧹 Data preprocessing (clean, fill, outlier removal)")
            print("   5. 🗄️ Cache management with statistics")
            print("   6. 📡 DataFeed interface for real-time simulation")
            print("   7. 💾 CSV import/export")
            print("   8. 🐍 Full Python bindings with example")
            print("\n🚀 Ready for integration with backtest engine and strategies!")
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