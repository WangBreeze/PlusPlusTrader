#pragma once

#include <vector>
#include <string>
#include <chrono>
#include <memory>
#include <map>

namespace pplustrader {
namespace backtest {

class BacktestResult {
public:
    // Performance metrics
    struct Metrics {
        // Basic metrics
        double total_return = 0.0;           // Total return in percentage
        double annualized_return = 0.0;      // Annualized return in percentage
        double sharpe_ratio = 0.0;           // Sharpe ratio (risk-free rate assumed 0)
        double sortino_ratio = 0.0;          // Sortino ratio
        double max_drawdown = 0.0;           // Maximum drawdown in percentage
        double max_drawdown_duration = 0.0;  // Maximum drawdown duration in days
        
        // Risk metrics
        double volatility = 0.0;             // Portfolio volatility (standard deviation)
        double beta = 0.0;                   // Beta to benchmark
        double alpha = 0.0;                  // Alpha (excess return)
        double information_ratio = 0.0;      // Information ratio
        
        // Trade metrics
        int total_trades = 0;                // Total number of trades
        int winning_trades = 0;              // Number of winning trades
        int losing_trades = 0;               // Number of losing trades
        double win_rate = 0.0;               // Win rate in percentage
        double avg_win = 0.0;                // Average profit of winning trades
        double avg_loss = 0.0;               // Average loss of losing trades
        double profit_factor = 0.0;          // Gross profit / gross loss
        double avg_trade_return = 0.0;       // Average return per trade
        
        // Time metrics
        std::chrono::seconds total_duration{0};  // Total backtest duration
        double avg_holding_period = 0.0;     // Average holding period in days
        
        // Portfolio metrics
        double final_portfolio_value = 0.0;  // Final portfolio value
        double initial_portfolio_value = 0.0; // Initial portfolio value
        double peak_portfolio_value = 0.0;   // Peak portfolio value
        double trough_portfolio_value = 0.0; // Trough portfolio value
        
        // Benchmark comparison
        double benchmark_return = 0.0;       // Benchmark total return
        double excess_return = 0.0;          // Excess return over benchmark
    };
    
    // Trade record
    struct TradeRecord {
        std::string trade_id;
        std::string symbol;
        std::chrono::system_clock::time_point entry_time;
        std::chrono::system_clock::time_point exit_time;
        double entry_price = 0.0;
        double exit_price = 0.0;
        double quantity = 0.0;
        double profit_loss = 0.0;           // Absolute P&L
        double return_pct = 0.0;            // Return in percentage
        bool is_winning = false;
        std::string notes;
    };
    
    // Portfolio snapshot at a point in time
    struct PortfolioSnapshot {
        std::chrono::system_clock::time_point timestamp;
        double portfolio_value = 0.0;
        double cash = 0.0;
        double positions_value = 0.0;
        double unrealized_pnl = 0.0;
        double realized_pnl = 0.0;
        std::map<std::string, double> positions; // symbol -> quantity
    };
    
    // Constructor
    BacktestResult() = default;
    
    // Add a trade record
    void add_trade_record(const TradeRecord& record);
    
    // Add a portfolio snapshot
    void add_portfolio_snapshot(const PortfolioSnapshot& snapshot);
    
    // Calculate all performance metrics
    void calculate_metrics();
    
    // Get metrics
    const Metrics& get_metrics() const { return metrics_; }
    
    // Get trade records
    const std::vector<TradeRecord>& get_trade_records() const { return trade_records_; }
    
    // Get portfolio snapshots
    const std::vector<PortfolioSnapshot>& get_portfolio_snapshots() const { return portfolio_snapshots_; }
    
    // Get drawdown series
    const std::vector<double>& get_drawdown_series() const { return drawdown_series_; }
    
    // Get equity curve
    const std::vector<double>& get_equity_curve() const { return equity_curve_; }
    
    // Get returns series
    const std::vector<double>& get_returns_series() const { return returns_series_; }
    
    // Set benchmark data
    void set_benchmark_data(const std::vector<double>& benchmark_prices);
    
    // Generate summary report as string
    std::string generate_summary_report() const;
    
    // Generate detailed report as string
    std::string generate_detailed_report() const;
    
    // Export to CSV
    bool export_to_csv(const std::string& filepath) const;
    
    // Export to JSON
    bool export_to_json(const std::string& filepath) const;
    
    // Clear all data
    void clear();
    
private:
    Metrics metrics_;
    std::vector<TradeRecord> trade_records_;
    std::vector<PortfolioSnapshot> portfolio_snapshots_;
    std::vector<double> drawdown_series_;
    std::vector<double> equity_curve_;
    std::vector<double> returns_series_;
    std::vector<double> benchmark_prices_;
    
    // Helper methods for calculations
    void calculate_basic_metrics();
    void calculate_risk_metrics();
    void calculate_trade_metrics();
    void calculate_portfolio_metrics();
    void calculate_drawdown();
    void calculate_equity_curve();
    void calculate_returns_series();
};

} // namespace backtest
} // namespace pplustrader