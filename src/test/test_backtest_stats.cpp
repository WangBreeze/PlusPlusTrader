// test_backtest_stats.cpp - Test program for backtest statistics
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#include "backtest/BacktestResult.h"
#include "backtest/StatisticsCalculator.h"
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <random>

using namespace pplustrader;
using namespace pplustrader::backtest;

// Generate sample equity curve with trend and volatility
std::vector<double> generate_sample_equity_curve(double initial_capital = 100000.0,
                                                 int days = 252,
                                                 double annual_return = 0.15,
                                                 double volatility = 0.20) {
    std::vector<double> equity_curve;
    std::mt19937 rng(42);  // Fixed seed for reproducibility
    std::normal_distribution<double> dist(0.0, 1.0);
    
    double equity = initial_capital;
    double daily_return = annual_return / 252.0;
    double daily_vol = volatility / std::sqrt(252.0);
    
    equity_curve.push_back(equity);
    
    for (int i = 0; i < days; ++i) {
        double random_shock = dist(rng);
        double daily_change = daily_return + daily_vol * random_shock;
        equity *= (1.0 + daily_change);
        equity_curve.push_back(equity);
    }
    
    return equity_curve;
}

// Generate sample trades
std::vector<BacktestResult::TradeRecord> generate_sample_trades(int count = 50) {
    std::vector<BacktestResult::TradeRecord> trades;
    std::mt19937 rng(123);
    std::uniform_real_distribution<double> price_dist(100.0, 200.0);
    std::uniform_int_distribution<int> quantity_dist(100, 1000);
    std::uniform_int_distribution<int> dir_dist(0, 1);
    std::uniform_real_distribution<double> pl_dist(-500.0, 1000.0);
    
    for (int i = 0; i < count; ++i) {
        BacktestResult::TradeRecord trade;
        trade.timestamp = "2026-01-" + std::to_string((i % 30) + 1);
        trade.symbol = "600519.SH";  // 茅台
        trade.direction = dir_dist(rng) == 0 ? core::OrderDirection::BUY : core::OrderDirection::SELL;
        trade.price = price_dist(rng);
        trade.quantity = quantity_dist(rng);
        trade.profit_loss = pl_dist(rng);
        
        trades.push_back(trade);
    }
    
    return trades;
}

void test_statistics_calculator() {
    std::cout << "=== Testing StatisticsCalculator ===" << std::endl;
    
    // Generate sample returns
    std::vector<double> returns;
    std::mt19937 rng(42);
    std::normal_distribution<double> dist(0.001, 0.02);  // 0.1% mean, 2% std
    
    for (int i = 0; i < 100; ++i) {
        returns.push_back(dist(rng) * 100.0);  // Convert to percentage
    }
    
    // Test individual calculations
    double sharpe = StatisticsCalculator::calculate_sharpe_ratio(returns);
    double sortino = StatisticsCalculator::calculate_sortino_ratio(returns);
    double volatility = StatisticsCalculator::calculate_volatility(returns);
    double var = StatisticsCalculator::calculate_var(returns, 0.95);
    
    std::cout << "Sharpe Ratio: " << std::fixed << std::setprecision(3) << sharpe << std::endl;
    std::cout << "Sortino Ratio: " << std::fixed << std::setprecision(3) << sortino << std::endl;
    std::cout << "Volatility: " << std::fixed << std::setprecision(2) << volatility << "%" << std::endl;
    std::cout << "VaR (95%): " << std::fixed << std::setprecision(2) << var << "%" << std::endl;
    
    // Test max drawdown calculation
    std::vector<double> equity_curve = {100.0, 110.0, 105.0, 120.0, 90.0, 100.0, 130.0};
    double max_dd = StatisticsCalculator::calculate_max_drawdown(equity_curve);
    std::cout << "Max Drawdown: " << std::fixed << std::setprecision(2) << max_dd << "%" << std::endl;
    
    // Test comprehensive metrics
    auto metrics = StatisticsCalculator::calculate_comprehensive_metrics(equity_curve, {}, 252);
    std::cout << "\nComprehensive Metrics:\n";
    std::cout << "Total Return: " << std::fixed << std::setprecision(2) << metrics.total_return << "%" << std::endl;
    std::cout << "Max Drawdown: " << std::fixed << std::setprecision(2) << metrics.max_drawdown << "%" << std::endl;
    std::cout << "Ulcer Index: " << std::fixed << std::setprecision(2) << metrics.ulcer_index << std::endl;
}

void test_backtest_result_enhancements() {
    std::cout << "\n=== Testing Enhanced BacktestResult ===" << std::endl;
    
    // Create a sample backtest result
    BacktestResult result;
    result.strategy_name_ = "双均线策略";
    result.start_time_ = "2026-01-01";
    result.end_time_ = "2026-12-31";
    result.initial_capital_ = 100000.0;
    result.final_capital_ = 125000.0;
    result.total_return_ = 25.0;
    result.max_consecutive_wins_ = 5;
    result.max_consecutive_losses_ = 3;
    
    // Generate sample equity curve and trades
    result.equity_curve_ = generate_sample_equity_curve(100000.0, 252, 0.15, 0.20);
    result.trades_ = generate_sample_trades(50);
    
    std::cout << "Strategy: " << result.strategy_name_ << std::endl;
    std::cout << "Period: " << result.start_time_ << " to " << result.end_time_ << std::endl;
    std::cout << "Initial Capital: ¥" << std::fixed << std::setprecision(2) << result.initial_capital_ << std::endl;
    std::cout << "Final Capital: ¥" << std::fixed << std::setprecision(2) << result.final_capital_ << std::endl;
    std::cout << "Total Return: " << std::fixed << std::setprecision(2) << result.total_return_ << "%" << std::endl;
    
    // Test new calculation methods
    std::cout << "\nAdvanced Statistics:" << std::endl;
    std::cout << "Sharpe Ratio: " << std::fixed << std::setprecision(3) << result.calculate_sharpe_ratio() << std::endl;
    std::cout << "Sortino Ratio: " << std::fixed << std::setprecision(3) << result.calculate_sortino_ratio() << std::endl;
    std::cout << "Max Drawdown: " << std::fixed << std::setprecision(2) << result.calculate_max_drawdown() << "%" << std::endl;
    std::cout << "Volatility: " << std::fixed << std::setprecision(2) << result.calculate_volatility() << "%" << std::endl;
    std::cout << "Calmar Ratio: " << std::fixed << std::setprecision(3) << result.calculate_calmar_ratio() << std::endl;
    std::cout << "VaR (95%): " << std::fixed << std::setprecision(2) << result.calculate_var() << "%" << std::endl;
    
    // Test comprehensive metrics
    auto metrics = result.calculate_comprehensive_metrics();
    std::cout << "\nComprehensive Metrics Summary:" << std::endl;
    std::cout << "Annualized Return: " << std::fixed << std::setprecision(2) << metrics.annualized_return << "%" << std::endl;
    std::cout << "Win Rate: " << std::fixed << std::setprecision(2) << metrics.win_rate << "%" << std::endl;
    std::cout << "Profit Factor: " << std::fixed << std::setprecision(2) << metrics.profit_factor << std::endl;
    std::cout << "Average Win: " << std::fixed << std::setprecision(2) << metrics.average_win << "%" << std::endl;
    std::cout << "Average Loss: " << std::fixed << std::setprecision(2) << metrics.average_loss << "%" << std::endl;
    
    // Test report generation
    std::cout << "\nGenerating reports..." << std::endl;
    
    bool html_success = result.generate_html_report("test_backtest_report.html");
    bool json_success = result.generate_json_report("test_backtest_report.json");
    
    std::cout << "HTML report generated: " << (html_success ? "Success" : "Failed") << std::endl;
    std::cout << "JSON report generated: " << (json_success ? "Success" : "Failed") << std::endl;
    
    if (html_success) {
        std::cout << "HTML report saved to: test_backtest_report.html" << std::endl;
    }
    if (json_success) {
        std::cout << "JSON report saved to: test_backtest_report.json" << std::endl;
    }
}

void test_portfolio_metrics_formatting() {
    std::cout << "\n=== Testing PortfolioMetrics Formatting ===" << std::endl;
    
    PortfolioMetrics metrics;
    metrics.total_return = 25.5;
    metrics.annualized_return = 15.2;
    metrics.volatility = 18.7;
    metrics.sharpe_ratio = 0.85;
    metrics.sortino_ratio = 1.12;
    metrics.calmar_ratio = 0.65;
    metrics.max_drawdown = 23.4;
    metrics.max_drawdown_duration = 45;
    metrics.total_trades = 120;
    metrics.winning_trades = 65;
    metrics.losing_trades = 55;
    metrics.win_rate = 54.2;
    metrics.profit_factor = 1.35;
    metrics.average_win = 2.1;
    metrics.average_loss = -1.5;
    metrics.avg_win_loss_ratio = 1.4;
    metrics.value_at_risk = -2.3;
    metrics.ulcer_index = 8.7;
    metrics.recovery_factor = 1.09;
    
    std::cout << metrics.to_string() << std::endl;
}

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "Backtest Statistics Test Program" << std::endl;
    std::cout << "Date: 2026-03-15" << std::endl;
    std::cout << "========================================" << std::endl;
    
    try {
        test_statistics_calculator();
        test_backtest_result_enhancements();
        test_portfolio_metrics_formatting();
        
        std::cout << "\n========================================" << std::endl;
        std::cout << "All tests completed successfully!" << std::endl;
        std::cout << "Backtest statistics system is working." << std::endl;
        std::cout << "========================================" << std::endl;
        
        return 0;
    } catch (const std::exception& e) {
        std::cout << "Test failed with error: " << e.what() << std::endl;
        return 1;
    }
}