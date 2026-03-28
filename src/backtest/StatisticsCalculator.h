// StatisticsCalculator.h - Advanced statistical calculations for backtesting
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#ifndef PPLUSTRADER_BACKTEST_STATISTICSCALCULATOR_H
#define PPLUSTRADER_BACKTEST_STATISTICSCALCULATOR_H

#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <stdexcept>
#include <string>

namespace pplustrader {
namespace backtest {

/**
 * @struct PortfolioMetrics
 * @brief Comprehensive portfolio performance metrics
 */
struct PortfolioMetrics {
    // Basic metrics
    double total_return;           ///< Total return percentage
    double annualized_return;      ///< Annualized return percentage
    double volatility;             ///< Annualized volatility (standard deviation)
    
    // Risk-adjusted metrics
    double sharpe_ratio;           ///< Sharpe ratio (risk-free rate assumed 0)
    double sortino_ratio;          ///< Sortino ratio (downside deviation)
    double calmar_ratio;           ///< Calmar ratio (return / max drawdown)
    
    // Drawdown metrics
    double max_drawdown;           ///< Maximum drawdown percentage
    double max_drawdown_duration;  ///< Duration of max drawdown in days
    
    // Trade statistics
    size_t total_trades;           ///< Total number of trades
    size_t winning_trades;         ///< Number of winning trades
    size_t losing_trades;          ///< Number of losing trades
    double win_rate;               ///< Winning trade percentage
    double profit_factor;          ///< Gross profit / gross loss
    double average_win;            ///< Average winning trade return
    double average_loss;           ///< Average losing trade return
    double avg_win_loss_ratio;     ///< Average win / average loss ratio
    
    // Additional metrics
    double beta;                   ///< Beta relative to benchmark
    double alpha;                  ///< Alpha (excess return)
    double information_ratio;      ///< Information ratio
    double value_at_risk;          ///< Value at Risk (95% confidence)
    
    // Timing metrics
    double recovery_factor;        ///< Total return / max drawdown
    double ulcer_index;            ///< Ulcer index (measure of downside risk)
    
    /**
     * @brief Reset all metrics to default values
     */
    void reset() {
        total_return = 0.0;
        annualized_return = 0.0;
        volatility = 0.0;
        sharpe_ratio = 0.0;
        sortino_ratio = 0.0;
        calmar_ratio = 0.0;
        max_drawdown = 0.0;
        max_drawdown_duration = 0;
        total_trades = 0;
        winning_trades = 0;
        losing_trades = 0;
        win_rate = 0.0;
        profit_factor = 0.0;
        average_win = 0.0;
        average_loss = 0.0;
        avg_win_loss_ratio = 0.0;
        beta = 0.0;
        alpha = 0.0;
        information_ratio = 0.0;
        value_at_risk = 0.0;
        recovery_factor = 0.0;
        ulcer_index = 0.0;
    }
    
    /**
     * @brief Get a formatted string representation of metrics
     * @return Formatted metrics string
     */
    std::string to_string() const;
};

/**
 * @class StatisticsCalculator
 * @brief Advanced statistical calculator for portfolio analysis
 * 
 * This class provides comprehensive statistical calculations for
 * backtesting results, including risk-adjusted returns, drawdown
 * analysis, and trade statistics.
 */
class StatisticsCalculator {
public:
    /**
     * @brief Calculate Sharpe ratio
     * @param returns Vector of periodic returns (e.g., daily returns)
     * @param risk_free_rate Annual risk-free rate (default: 0.0)
     * @return Sharpe ratio
     */
    static double calculate_sharpe_ratio(const std::vector<double>& returns,
                                        double risk_free_rate = 0.0);
    
    /**
     * @brief Calculate Sortino ratio
     * @param returns Vector of periodic returns
     * @param risk_free_rate Annual risk-free rate (default: 0.0)
     * @return Sortino ratio
     */
    static double calculate_sortino_ratio(const std::vector<double>& returns,
                                         double risk_free_rate = 0.0);
    
    /**
     * @brief Calculate maximum drawdown
     * @param equity_curve Vector of equity values over time
     * @return Maximum drawdown percentage (0-100)
     */
    static double calculate_max_drawdown(const std::vector<double>& equity_curve);
    
    /**
     * @brief Calculate maximum drawdown with duration
     * @param equity_curve Vector of equity values
     * @param drawdown Output maximum drawdown percentage
     * @param duration Output duration of maximum drawdown
     * @param start_idx Output start index of drawdown
     * @param end_idx Output end index of drawdown
     */
    static void calculate_max_drawdown_details(const std::vector<double>& equity_curve,
                                              double& drawdown,
                                              size_t& duration,
                                              size_t& start_idx,
                                              size_t& end_idx);
    
    /**
     * @brief Calculate Calmar ratio
     * @param annualized_return Annualized return percentage
     * @param max_drawdown Maximum drawdown percentage
     * @return Calmar ratio
     */
    static double calculate_calmar_ratio(double annualized_return,
                                        double max_drawdown);
    
    /**
     * @brief Calculate volatility (annualized standard deviation)
     * @param returns Vector of periodic returns
     * @param periods_per_year Number of periods in a year (e.g., 252 for daily)
     * @return Annualized volatility
     */
    static double calculate_volatility(const std::vector<double>& returns,
                                      int periods_per_year = 252);
    
    /**
     * @brief Calculate Value at Risk (VaR)
     * @param returns Vector of returns
     * @param confidence_level Confidence level (e.g., 0.95 for 95%)
     * @return Value at Risk (negative value represents loss)
     */
    static double calculate_var(const std::vector<double>& returns,
                               double confidence_level = 0.95);
    
    /**
     * @brief Calculate Ulcer Index
     * @param equity_curve Vector of equity values
     * @return Ulcer Index
     */
    static double calculate_ulcer_index(const std::vector<double>& equity_curve);
    
    /**
     * @brief Calculate trade statistics
     * @param trade_returns Vector of individual trade returns (percentage)
     * @param metrics Output portfolio metrics structure
     */
    static void calculate_trade_statistics(const std::vector<double>& trade_returns,
                                          PortfolioMetrics& metrics);
    
    /**
     * @brief Calculate comprehensive portfolio metrics
     * @param equity_curve Vector of equity values over time
     * @param trade_returns Vector of individual trade returns
     * @param periods_per_year Number of periods in a year
     * @return Complete portfolio metrics
     */
    static PortfolioMetrics calculate_comprehensive_metrics(
        const std::vector<double>& equity_curve,
        const std::vector<double>& trade_returns = {},
        int periods_per_year = 252);
    
    /**
     * @brief Calculate beta and alpha (relative to benchmark)
     * @param portfolio_returns Portfolio returns
     * @param benchmark_returns Benchmark returns
     * @param risk_free_rate Risk-free rate
     * @param beta Output beta value
     * @param alpha Output alpha value
     */
    static void calculate_beta_alpha(const std::vector<double>& portfolio_returns,
                                    const std::vector<double>& benchmark_returns,
                                    double risk_free_rate,
                                    double& beta,
                                    double& alpha);
    
    /**
     * @brief Calculate Information Ratio
     * @param portfolio_returns Portfolio returns
     * @param benchmark_returns Benchmark returns
     * @return Information Ratio
     */
    static double calculate_information_ratio(
        const std::vector<double>& portfolio_returns,
        const std::vector<double>& benchmark_returns);
    
private:
    /**
     * @brief Calculate mean of a vector
     */
    static double mean(const std::vector<double>& values);
    
    /**
     * @brief Calculate standard deviation of a vector
     */
    static double stddev(const std::vector<double>& values, bool population = false);
    
    /**
     * @brief Calculate downside deviation (for Sortino ratio)
     */
    static double downside_deviation(const std::vector<double>& returns,
                                    double minimum_acceptable_return = 0.0);
    
    /**
     * @brief Calculate annualized return
     */
    static double annualized_return(const std::vector<double>& returns,
                                   int periods_per_year);
    
    /**
     * @brief Convert daily returns to cumulative equity curve
     */
    static std::vector<double> returns_to_equity(const std::vector<double>& returns,
                                                double initial_capital = 1.0);
};

} // namespace backtest
} // namespace pplustrader

#endif // PPLUSTRADER_BACKTEST_STATISTICSCALCULATOR_H