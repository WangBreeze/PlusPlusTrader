// test_backtest_units.cpp - Unit tests for backtest statistics
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#include "test/TestUtils.h"
#include "backtest/StatisticsCalculator.h"
#include "backtest/BacktestResult.h"
#include <vector>
#include <cmath>
#include <algorithm>

using namespace pplustrader;
using namespace pplustrader::backtest;
using namespace pplustrader::test;

// Test case for StatisticsCalculator
TEST_CASE_BEGIN(TestStatisticsCalculator)
    void test_sharpe_ratio() {
        // Test with simple returns
        std::vector<double> returns = {0.01, 0.02, -0.01, 0.03, 0.01};  // 5 days
        
        double sharpe = StatisticsCalculator::calculate_sharpe_ratio(returns, 0.0);
        
        // Manual calculation check
        double mean_return = (0.01 + 0.02 - 0.01 + 0.03 + 0.01) / 5.0;
        double variance = 0.0;
        for (double r : returns) {
            variance += (r - mean_return) * (r - mean_return);
        }
        variance /= 4.0;  // sample variance
        double std_dev = std::sqrt(variance);
        double expected_sharpe = mean_return / std_dev * std::sqrt(252.0);
        
        ASSERT_DOUBLE_EQUAL(expected_sharpe, sharpe, 0.001, 
                           "Sharpe ratio calculation should be correct");
        
        // Test with zero returns
        std::vector<double> zero_returns(10, 0.0);
        double zero_sharpe = StatisticsCalculator::calculate_sharpe_ratio(zero_returns);
        ASSERT_DOUBLE_EQUAL(0.0, zero_sharpe, 0.001, 
                           "Sharpe ratio should be 0 for zero returns");
    }
    
    void test_max_drawdown() {
        // Simple equity curve with known drawdown
        std::vector<double> equity_curve = {100.0, 110.0, 105.0, 120.0, 90.0, 100.0, 130.0};
        
        // Peaks: 100, 110, 110, 120, 120, 120, 130
        // Drawdowns: 0%, 0%, 4.55%, 0%, 25%, 16.67%, 0%
        // Max drawdown: 25%
        
        double max_dd = StatisticsCalculator::calculate_max_drawdown(equity_curve);
        ASSERT_DOUBLE_EQUAL(25.0, max_dd, 0.001, 
                           "Max drawdown should be 25%");
        
        // Test with ascending equity (no drawdown)
        std::vector<double> ascending = {100.0, 110.0, 120.0, 130.0, 140.0};
        double ascending_dd = StatisticsCalculator::calculate_max_drawdown(ascending);
        ASSERT_DOUBLE_EQUAL(0.0, ascending_dd, 0.001,
                           "Max drawdown should be 0 for ascending equity");
        
        // Test with descending equity
        std::vector<double> descending = {100.0, 90.0, 80.0, 70.0, 60.0};
        double descending_dd = StatisticsCalculator::calculate_max_drawdown(descending);
        ASSERT_DOUBLE_EQUAL(40.0, descending_dd, 0.001,
                           "Max drawdown should be 40% for descending equity");
    }
    
    void test_volatility() {
        std::vector<double> returns = {0.01, -0.02, 0.03, -0.01, 0.02};
        
        double volatility = StatisticsCalculator::calculate_volatility(returns, 252);
        
        // Manual calculation
        double mean_return = (0.01 - 0.02 + 0.03 - 0.01 + 0.02) / 5.0;
        double sum_sq = 0.0;
        for (double r : returns) {
            sum_sq += (r - mean_return) * (r - mean_return);
        }
        double sample_variance = sum_sq / 4.0;
        double daily_vol = std::sqrt(sample_variance);
        double expected_vol = daily_vol * std::sqrt(252.0);
        
        ASSERT_DOUBLE_EQUAL(expected_vol, volatility, 0.001,
                           "Volatility calculation should be correct");
    }
    
    void test_var_calculation() {
        std::vector<double> returns = {
            0.01, -0.02, 0.03, -0.01, 0.02,
            -0.03, 0.01, 0.02, -0.01, -0.02
        };
        
        // For 95% VaR with 10 samples, we take the 5th worst (sorted ascending)
        // Sorted: -0.03, -0.02, -0.02, -0.01, -0.01, 0.01, 0.01, 0.02, 0.02, 0.03
        // 95% VaR = 5th worst = -0.01
        
        double var_95 = StatisticsCalculator::calculate_var(returns, 0.95);
        ASSERT_DOUBLE_EQUAL(-0.01, var_95, 0.001,
                           "95% VaR should be -0.01");
        
        // 90% VaR (10 samples * 0.1 = 1st worst)
        double var_90 = StatisticsCalculator::calculate_var(returns, 0.90);
        ASSERT_DOUBLE_EQUAL(-0.03, var_90, 0.001,
                           "90% VaR should be -0.03");
    }
    
    void test_portfolio_metrics() {
        // Create a simple equity curve
        std::vector<double> equity_curve = {100000.0, 105000.0, 103000.0, 110000.0, 115000.0};
        
        // Create some trade returns
        std::vector<double> trade_returns = {2.5, -1.5, 3.2, 1.8, -0.5, 2.1};
        
        PortfolioMetrics metrics = StatisticsCalculator::calculate_comprehensive_metrics(
            equity_curve, trade_returns, 252);
        
        // Verify basic calculations
        double total_return = (115000.0 - 100000.0) / 100000.0 * 100.0;
        ASSERT_DOUBLE_EQUAL(total_return, metrics.total_return, 0.1,
                           "Total return should be calculated correctly");
        
        // Trade statistics
        ASSERT_EQUAL(6, metrics.total_trades, "Should have 6 trades");
        ASSERT_IN_RANGE(metrics.win_rate, 0.0, 100.0, "Win rate should be in [0, 100]");
        
        // Max drawdown from equity curve [100, 105, 103, 110, 115]
        // Peak: 100, 105, 105, 110, 115
        // Drawdown: 0%, 0%, 1.9%, 0%, 0%
        // Max drawdown should be ~1.9%
        ASSERT_IN_RANGE(metrics.max_drawdown, 0.0, 5.0, 
                       "Max drawdown should be around 1.9%");
    }
    
    void run_tests() override {
        test_sharpe_ratio();
        test_max_drawdown();
        test_volatility();
        test_var_calculation();
        test_portfolio_metrics();
    }
TEST_CASE_END(TestStatisticsCalculator)

// Test case for PortfolioMetrics formatting
TEST_CASE_BEGIN(TestPortfolioMetrics)
    void test_to_string_formatting() {
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
        
        std::string formatted = metrics.to_string();
        
        // Check that all key metrics appear in the formatted string
        ASSERT_TRUE(formatted.find("25.5") != std::string::npos,
                   "Total return should appear in formatted string");
        ASSERT_TRUE(formatted.find("15.2") != std::string::npos,
                   "Annualized return should appear");
        ASSERT_TRUE(formatted.find("0.85") != std::string::npos,
                   "Sharpe ratio should appear");
        ASSERT_TRUE(formatted.find("23.4") != std::string::npos,
                   "Max drawdown should appear");
        ASSERT_TRUE(formatted.find("54.2") != std::string::npos,
                   "Win rate should appear");
        
        // Check section headers
        ASSERT_TRUE(formatted.find("Portfolio Performance Metrics") != std::string::npos,
                   "Should have main header");
        ASSERT_TRUE(formatted.find("Basic Metrics") != std::string::npos,
                   "Should have basic metrics section");
        ASSERT_TRUE(formatted.find("Risk-Adjusted Metrics") != std::string::npos,
                   "Should have risk-adjusted metrics section");
        ASSERT_TRUE(formatted.find("Drawdown Analysis") != std::string::npos,
                   "Should have drawdown analysis section");
        ASSERT_TRUE(formatted.find("Trade Statistics") != std::string::npos,
                   "Should have trade statistics section");
    }
    
    void test_reset_functionality() {
        PortfolioMetrics metrics;
        
        // Set some values
        metrics.total_return = 25.5;
        metrics.sharpe_ratio = 0.85;
        metrics.total_trades = 120;
        
        // Reset
        metrics.reset();
        
        // Check that all values are reset to 0
        ASSERT_DOUBLE_EQUAL(0.0, metrics.total_return, 0.001,
                           "Total return should be reset to 0");
        ASSERT_DOUBLE_EQUAL(0.0, metrics.sharpe_ratio, 0.001,
                           "Sharpe ratio should be reset to 0");
        ASSERT_EQUAL(0, metrics.total_trades,
                    "Total trades should be reset to 0");
        ASSERT_DOUBLE_EQUAL(0.0, metrics.win_rate, 0.001,
                           "Win rate should be reset to 0");
    }
    
    void run_tests() override {
        test_to_string_formatting();
        test_reset_functionality();
    }
TEST_CASE_END(TestPortfolioMetrics)

// Main test runner
int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "Backtest Statistics Unit Tests" << std::endl;
    std::cout << "Date: 2026-03-15" << std::endl;
    std::cout << "========================================" << std::endl;
    
    TestSuite suite("Backtest Statistics Test Suite");
    
    // Register test cases
    suite.add_test_case(&test_case_instance_TestStatisticsCalculator);
    suite.add_test_case(&test_case_instance_TestPortfolioMetrics);
    
    bool all_passed = suite.run_all();
    
    std::cout << "\n========================================" << std::endl;
    std::cout << "Test Run Completed" << std::endl;
    std::cout << "========================================" << std::endl;
    
    if (all_passed) {
        std::cout << "🎉 All backtest statistics tests passed!" << std::endl;
        return 0;
    } else {
        std::cout << "❌ Some backtest statistics tests failed." << std::endl;
        return 1;
    }
}