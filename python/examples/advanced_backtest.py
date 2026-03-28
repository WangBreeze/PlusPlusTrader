#!/usr/bin/env python3
"""
Advanced backtest example showcasing the improved backtest engine with detailed results.
"""

import sys
import os
import tempfile

# Add the bindings directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pplustrader
    print("✅ Successfully imported pplustrader module")
    print(f"✅ Available classes: {[x for x in dir(pplustrader) if not x.startswith('_')]}")
except ImportError as e:
    print(f"❌ Failed to import pplustrader: {e}")
    sys.exit(1)

def run_advanced_backtest():
    """Run an advanced backtest with detailed results analysis"""
    print("=" * 70)
    print("ADVANCED BACKTEST EXAMPLE")
    print("Demonstrating improved backtest engine with detailed performance metrics")
    print("=" * 70)
    
    # Create backtest engine
    engine = pplustrader.BacktestEngine()
    print("\n1. Created BacktestEngine")
    
    # Configure engine
    engine.set_initial_capital(100000.0)
    print(f"   Set initial capital: ${engine.get_initial_capital():,.2f}")
    
    # Create data source (simulated)
    data_source = pplustrader.create_csv_data_source()
    engine.set_data_source(data_source)
    print("   Set data source")
    
    # Note: In a real implementation, we would set a real exchange and strategy
    # For this example, we'll simulate a backtest run
    
    print("\n2. Running backtest simulation...")
    
    # Simulate running the backtest
    # In a real scenario, engine.run() would process actual data
    success = engine.run()
    
    if not success:
        print("❌ Backtest failed")
        return False
    
    print("✅ Backtest completed successfully")
    
    # Get results
    result = engine.get_result()
    print("\n3. Analyzing backtest results...")
    
    # Calculate metrics
    result.calculate_metrics()
    
    # Get performance metrics
    metrics = result.get_metrics()
    
    print("\n📊 PERFORMANCE METRICS:")
    print(f"   Total Return:        {metrics.total_return:.2f}%")
    print(f"   Annualized Return:   {metrics.annualized_return:.2f}%")
    print(f"   Sharpe Ratio:        {metrics.sharpe_ratio:.3f}")
    print(f"   Sortino Ratio:       {metrics.sortino_ratio:.3f}")
    print(f"   Max Drawdown:        {metrics.max_drawdown:.2f}%")
    print(f"   Volatility:          {metrics.volatility:.2f}%")
    
    print("\n📈 TRADE METRICS:")
    print(f"   Total Trades:        {metrics.total_trades}")
    print(f"   Winning Trades:      {metrics.winning_trades}")
    print(f"   Losing Trades:       {metrics.losing_trades}")
    print(f"   Win Rate:            {metrics.win_rate:.1f}%")
    print(f"   Avg Win:            ${metrics.avg_win:.2f}")
    print(f"   Avg Loss:           ${metrics.avg_loss:.2f}")
    print(f"   Profit Factor:       {metrics.profit_factor:.2f}")
    
    print("\n💰 PORTFOLIO METRICS:")
    print(f"   Initial Value:      ${metrics.initial_portfolio_value:,.2f}")
    print(f"   Final Value:        ${metrics.final_portfolio_value:,.2f}")
    
    # Generate and display summary report
    print("\n4. Generating summary report...")
    summary = result.generate_summary_report()
    print("\n" + "=" * 70)
    print("SUMMARY REPORT")
    print("=" * 70)
    print(summary)
    
    # Export results to files
    print("\n5. Exporting results...")
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "backtest_results.csv")
        json_path = os.path.join(tmpdir, "backtest_results.json")
        
        if result.export_to_csv(csv_path):
            print(f"   ✅ CSV export successful: {csv_path}")
        
        if result.export_to_json(json_path):
            print(f"   ✅ JSON export successful: {json_path}")
        
        # Read and display CSV content
        try:
            with open(csv_path, 'r') as f:
                csv_content = f.read()
                print(f"\n   📄 CSV Preview (first 10 lines):")
                lines = csv_content.strip().split('\n')
                for line in lines[:10]:
                    print(f"      {line}")
        except Exception as e:
            print(f"   ❌ Error reading CSV: {e}")
    
    # Test creating trade records
    print("\n6. Creating sample trade records...")
    
    # Create a sample trade record
    trade = pplustrader.TradeRecord()
    trade.trade_id = "TRADE_001"
    trade.symbol = "AAPL"
    trade.entry_price = 150.0
    trade.exit_price = 155.0
    trade.quantity = 100
    trade.profit_loss = (155.0 - 150.0) * 100
    trade.return_pct = ((155.0 - 150.0) / 150.0) * 100
    trade.is_winning = True
    
    print(f"   Created trade: {trade.symbol} {trade.quantity} shares")
    print(f"   P&L: ${trade.profit_loss:.2f} ({trade.return_pct:.2f}%)")
    
    # Create a sample portfolio snapshot
    snapshot = pplustrader.PortfolioSnapshot()
    snapshot.portfolio_value = 105000.0
    snapshot.cash = 50000.0
    snapshot.positions_value = 55000.0
    snapshot.realized_pnl = 5000.0
    snapshot.unrealized_pnl = 1000.0
    
    print(f"   Created portfolio snapshot: Value=${snapshot.portfolio_value:,.2f}")
    
    # Test BacktestEngine's report methods
    print("\n7. Testing engine report methods...")
    engine.print_report()
    
    print("\n" + "=" * 70)
    print("ADVANCED BACKTEST EXAMPLE COMPLETED")
    print("=" * 70)
    
    return True

def create_custom_backtest_result():
    """Demonstrate creating and analyzing a custom backtest result"""
    print("\n" + "=" * 70)
    print("CUSTOM BACKTEST RESULT DEMO")
    print("=" * 70)
    
    # Create a new BacktestResult
    result = pplustrader.BacktestResult()
    
    # Note: In a real scenario, you would add actual trade records and snapshots
    # from your backtest. Here we'll just demonstrate the structure.
    
    print("✅ Created empty BacktestResult")
    
    # Generate report (will be empty)
    report = result.generate_summary_report()
    print(f"✅ Generated report (length: {len(report)} characters)")
    
    # Export empty result
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_path = f.name
    
    if result.export_to_csv(csv_path):
        print(f"✅ Exported empty result to: {csv_path}")
        os.unlink(csv_path)
    
    print("\n📋 BacktestResult API Overview:")
    print("   - calculate_metrics(): Calculate performance metrics from collected data")
    print("   - get_metrics(): Get performance metrics object")
    print("   - generate_summary_report(): Generate text summary")
    print("   - generate_detailed_report(): Generate detailed text report")
    print("   - export_to_csv(path): Export metrics to CSV")
    print("   - export_to_json(path): Export metrics to JSON")
    print("   - clear(): Clear all collected data")
    
    return result

if __name__ == "__main__":
    print("🧪 PlusPlusTrader Advanced Backtest Test")
    print("Date: 2026-03-12")
    print("Version: 0.3.0 (Enhanced Backtest Engine)")
    print()
    
    # Run advanced backtest demo
    success = run_advanced_backtest()
    
    if success:
        # Create custom result demo
        create_custom_backtest_result()
        
        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("\nKey improvements in the enhanced backtest engine:")
        print("1. 📊 Comprehensive performance metrics (Sharpe, Sortino, Max DD, etc.)")
        print("2. 📈 Detailed trade analysis (win rate, profit factor, etc.)")
        print("3. 💰 Portfolio tracking and snapshot system")
        print("4. 📁 Export capabilities (CSV, JSON)")
        print("5. 🐍 Full Python bindings for all result types")
        print("6. 📋 Automated report generation")
        print("\nNext steps:")
        print("  - Integrate with actual trading strategies")
        print("  - Add benchmark comparison functionality")
        print("  - Implement visualization tools")
        print("  - Add risk-adjusted performance measures")
    else:
        print("❌ Demonstration failed")