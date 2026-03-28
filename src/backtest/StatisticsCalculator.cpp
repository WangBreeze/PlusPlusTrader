// StatisticsCalculator.cpp - Advanced statistical calculations implementation
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#include "StatisticsCalculator.h"
#include <sstream>
#include <iomanip>
#include <cmath>
#include <algorithm>
#include <numeric>

namespace pplustrader {
namespace backtest {

// Helper function implementations
double StatisticsCalculator::mean(const std::vector<double>& values) {
    if (values.empty()) return 0.0;
    return std::accumulate(values.begin(), values.end(), 0.0) / values.size();
}

double StatisticsCalculator::stddev(const std::vector<double>& values, bool population) {
    if (values.size() < 2) return 0.0;
    
    double m = mean(values);
    double sum_sq = 0.0;
    for (double v : values) {
        double diff = v - m;
        sum_sq += diff * diff;
    }
    
    double variance = sum_sq / (population ? values.size() : values.size() - 1);
    return std::sqrt(variance);
}

double StatisticsCalculator::downside_deviation(const std::vector<double>& returns,
                                               double minimum_acceptable_return) {
    if (returns.empty()) return 0.0;
    
    std::vector<double> downside_returns;
    for (double r : returns) {
        if (r < minimum_acceptable_return) {
            downside_returns.push_back(r - minimum_acceptable_return);
        }
    }
    
    if (downside_returns.empty()) return 0.0;
    
    return stddev(downside_returns, true);
}

double StatisticsCalculator::annualized_return(const std::vector<double>& returns,
                                              int periods_per_year) {
    if (returns.empty()) return 0.0;
    
    // Calculate cumulative return
    double cumulative_return = 1.0;
    for (double r : returns) {
        cumulative_return *= (1.0 + r / 100.0);  // Assuming returns in percentage
    }
    
    double total_return = (cumulative_return - 1.0) * 100.0;
    double years = returns.size() / static_cast<double>(periods_per_year);
    
    if (years <= 0.0) return 0.0;
    
    // Annualized return: (1 + total_return)^(1/years) - 1
    double annualized = (std::pow(1.0 + total_return / 100.0, 1.0 / years) - 1.0) * 100.0;
    return annualized;
}

std::vector<double> StatisticsCalculator::returns_to_equity(const std::vector<double>& returns,
                                                           double initial_capital) {
    std::vector<double> equity_curve;
    double equity = initial_capital;
    
    for (double r : returns) {
        equity *= (1.0 + r / 100.0);  // Assuming returns in percentage
        equity_curve.push_back(equity);
    }
    
    return equity_curve;
}

// Public function implementations
double StatisticsCalculator::calculate_sharpe_ratio(const std::vector<double>& returns,
                                                   double risk_free_rate) {
    if (returns.empty()) return 0.0;
    
    double avg_return = mean(returns);
    double std_dev = stddev(returns);
    
    if (std_dev == 0.0) return 0.0;
    
    // Convert risk-free rate from annual to period rate
    double period_risk_free = risk_free_rate / 252.0;  // Assuming daily returns
    
    return (avg_return - period_risk_free) / std_dev * std::sqrt(252.0);
}

double StatisticsCalculator::calculate_sortino_ratio(const std::vector<double>& returns,
                                                    double risk_free_rate) {
    if (returns.empty()) return 0.0;
    
    double avg_return = mean(returns);
    double downside_dev = downside_deviation(returns, risk_free_rate / 252.0);
    
    if (downside_dev == 0.0) return 0.0;
    
    return (avg_return - risk_free_rate / 252.0) / downside_dev * std::sqrt(252.0);
}

double StatisticsCalculator::calculate_max_drawdown(const std::vector<double>& equity_curve) {
    if (equity_curve.empty()) return 0.0;
    
    double peak = equity_curve[0];
    double max_dd = 0.0;
    
    for (double equity : equity_curve) {
        if (equity > peak) {
            peak = equity;
        }
        
        double drawdown = (peak - equity) / peak * 100.0;
        if (drawdown > max_dd) {
            max_dd = drawdown;
        }
    }
    
    return max_dd;
}

void StatisticsCalculator::calculate_max_drawdown_details(const std::vector<double>& equity_curve,
                                                         double& drawdown,
                                                         size_t& duration,
                                                         size_t& start_idx,
                                                         size_t& end_idx) {
    drawdown = 0.0;
    duration = 0;
    start_idx = 0;
    end_idx = 0;
    
    if (equity_curve.empty()) return;
    
    double peak = equity_curve[0];
    size_t peak_idx = 0;
    double current_dd = 0.0;
    size_t current_start = 0;
    size_t current_duration = 0;
    
    for (size_t i = 0; i < equity_curve.size(); ++i) {
        if (equity_curve[i] > peak) {
            peak = equity_curve[i];
            peak_idx = i;
            current_dd = 0.0;
            current_start = i;
            current_duration = 0;
        } else {
            current_dd = (peak - equity_curve[i]) / peak * 100.0;
            current_duration = i - peak_idx;
            
            if (current_dd > drawdown) {
                drawdown = current_dd;
                start_idx = peak_idx;
                end_idx = i;
                duration = current_duration;
            }
        }
    }
}

double StatisticsCalculator::calculate_calmar_ratio(double annualized_return,
                                                   double max_drawdown) {
    if (max_drawdown == 0.0) return 0.0;
    
    return annualized_return / max_drawdown;
}

double StatisticsCalculator::calculate_volatility(const std::vector<double>& returns,
                                                 int periods_per_year) {
    if (returns.empty()) return 0.0;
    
    double std_dev = stddev(returns);
    return std_dev * std::sqrt(static_cast<double>(periods_per_year));
}

double StatisticsCalculator::calculate_var(const std::vector<double>& returns,
                                          double confidence_level) {
    if (returns.empty()) return 0.0;
    
    std::vector<double> sorted_returns = returns;
    std::sort(sorted_returns.begin(), sorted_returns.end());
    
    size_t index = static_cast<size_t>(std::floor((1.0 - confidence_level) * sorted_returns.size()));
    if (index >= sorted_returns.size()) index = sorted_returns.size() - 1;
    
    return sorted_returns[index];
}

double StatisticsCalculator::calculate_ulcer_index(const std::vector<double>& equity_curve) {
    if (equity_curve.size() < 2) return 0.0;
    
    std::vector<double> drawdowns;
    double peak = equity_curve[0];
    
    for (double equity : equity_curve) {
        if (equity > peak) {
            peak = equity;
        }
        
        double drawdown = (peak - equity) / peak * 100.0;
        drawdowns.push_back(drawdown);
    }
    
    double sum_sq = 0.0;
    for (double dd : drawdowns) {
        sum_sq += dd * dd;
    }
    
    return std::sqrt(sum_sq / drawdowns.size());
}

void StatisticsCalculator::calculate_trade_statistics(const std::vector<double>& trade_returns,
                                                     PortfolioMetrics& metrics) {
    metrics.total_trades = trade_returns.size();
    metrics.winning_trades = 0;
    metrics.losing_trades = 0;
    
    double total_win = 0.0;
    double total_loss = 0.0;
    
    for (double ret : trade_returns) {
        if (ret > 0.0) {
            metrics.winning_trades++;
            total_win += ret;
        } else if (ret < 0.0) {
            metrics.losing_trades++;
            total_loss += std::abs(ret);
        }
    }
    
    if (metrics.total_trades > 0) {
        metrics.win_rate = static_cast<double>(metrics.winning_trades) / metrics.total_trades * 100.0;
    }
    
    if (metrics.winning_trades > 0) {
        metrics.average_win = total_win / metrics.winning_trades;
    }
    
    if (metrics.losing_trades > 0) {
        metrics.average_loss = total_loss / metrics.losing_trades;
    }
    
    if (metrics.average_loss != 0.0) {
        metrics.avg_win_loss_ratio = metrics.average_win / metrics.average_loss;
    }
    
    if (total_loss != 0.0) {
        metrics.profit_factor = total_win / total_loss;
    }
}

PortfolioMetrics StatisticsCalculator::calculate_comprehensive_metrics(
    const std::vector<double>& equity_curve,
    const std::vector<double>& trade_returns,
    int periods_per_year) {
    
    PortfolioMetrics metrics;
    metrics.reset();
    
    if (equity_curve.empty()) return metrics;
    
    // Calculate returns from equity curve
    std::vector<double> returns;
    for (size_t i = 1; i < equity_curve.size(); ++i) {
        double ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] * 100.0;
        returns.push_back(ret);
    }
    
    // Basic metrics
    double initial_equity = equity_curve[0];
    double final_equity = equity_curve.back();
    metrics.total_return = (final_equity - initial_equity) / initial_equity * 100.0;
    
    // Annualized return
    if (!returns.empty()) {
        metrics.annualized_return = annualized_return(returns, periods_per_year);
    }
    
    // Volatility
    metrics.volatility = calculate_volatility(returns, periods_per_year);
    
    // Drawdown metrics
    metrics.max_drawdown = calculate_max_drawdown(equity_curve);
    
    size_t duration, start_idx, end_idx;
    calculate_max_drawdown_details(equity_curve, metrics.max_drawdown,
                                  duration, start_idx, end_idx);
    metrics.max_drawdown_duration = duration;
    
    // Risk-adjusted metrics
    metrics.sharpe_ratio = calculate_sharpe_ratio(returns);
    metrics.sortino_ratio = calculate_sortino_ratio(returns);
    metrics.calmar_ratio = calculate_calmar_ratio(metrics.annualized_return,
                                                 metrics.max_drawdown);
    
    // Additional metrics
    if (!returns.empty()) {
        metrics.value_at_risk = calculate_var(returns, 0.95);
        metrics.ulcer_index = calculate_ulcer_index(equity_curve);
        metrics.recovery_factor = metrics.total_return / 
                                 (metrics.max_drawdown > 0.0 ? metrics.max_drawdown : 1.0);
    }
    
    // Trade statistics
    if (!trade_returns.empty()) {
        calculate_trade_statistics(trade_returns, metrics);
    }
    
    return metrics;
}

void StatisticsCalculator::calculate_beta_alpha(const std::vector<double>& portfolio_returns,
                                               const std::vector<double>& benchmark_returns,
                                               double risk_free_rate,
                                               double& beta,
                                               double& alpha) {
    beta = 0.0;
    alpha = 0.0;
    
    if (portfolio_returns.size() != benchmark_returns.size() ||
        portfolio_returns.size() < 2) {
        return;
    }
    
    // Calculate covariance and variance
    double mean_port = mean(portfolio_returns);
    double mean_bench = mean(benchmark_returns);
    
    double covariance = 0.0;
    double variance_bench = 0.0;
    
    for (size_t i = 0; i < portfolio_returns.size(); ++i) {
        double port_diff = portfolio_returns[i] - mean_port;
        double bench_diff = benchmark_returns[i] - mean_bench;
        covariance += port_diff * bench_diff;
        variance_bench += bench_diff * bench_diff;
    }
    
    covariance /= (portfolio_returns.size() - 1);
    variance_bench /= (benchmark_returns.size() - 1);
    
    if (variance_bench != 0.0) {
        beta = covariance / variance_bench;
        
        // Alpha = portfolio_return - [risk_free_rate + beta * (benchmark_return - risk_free_rate)]
        double port_annual = mean_port * std::sqrt(252.0);
        double bench_annual = mean_bench * std::sqrt(252.0);
        alpha = port_annual - (risk_free_rate + beta * (bench_annual - risk_free_rate));
    }
}

double StatisticsCalculator::calculate_information_ratio(
    const std::vector<double>& portfolio_returns,
    const std::vector<double>& benchmark_returns) {
    
    if (portfolio_returns.size() != benchmark_returns.size() ||
        portfolio_returns.size() < 2) {
        return 0.0;
    }
    
    // Calculate active returns (portfolio - benchmark)
    std::vector<double> active_returns;
    for (size_t i = 0; i < portfolio_returns.size(); ++i) {
        active_returns.push_back(portfolio_returns[i] - benchmark_returns[i]);
    }
    
    double mean_active = mean(active_returns);
    double std_active = stddev(active_returns);
    
    if (std_active == 0.0) return 0.0;
    
    return mean_active / std_active * std::sqrt(252.0);
}

// PortfolioMetrics member functions
std::string PortfolioMetrics::to_string() const {
    std::ostringstream ss;
    ss << std::fixed << std::setprecision(2);
    
    ss << "=== Portfolio Performance Metrics ===\n";
    ss << "Basic Metrics:\n";
    ss << "  Total Return: " << total_return << "%\n";
    ss << "  Annualized Return: " << annualized_return << "%\n";
    ss << "  Volatility: " << volatility << "%\n\n";
    
    ss << "Risk-Adjusted Metrics:\n";
    ss << "  Sharpe Ratio: " << std::setprecision(3) << sharpe_ratio << "\n";
    ss << "  Sortino Ratio: " << sortino_ratio << "\n";
    ss << "  Calmar Ratio: " << calmar_ratio << "\n\n";
    
    ss << std::setprecision(2);
    ss << "Drawdown Analysis:\n";
    ss << "  Max Drawdown: " << max_drawdown << "%\n";
    ss << "  Max Drawdown Duration: " << max_drawdown_duration << " days\n";
    ss << "  Ulcer Index: " << ulcer_index << "\n";
    ss << "  Value at Risk (95%): " << value_at_risk << "%\n\n";
    
    ss << "Trade Statistics:\n";
    ss << "  Total Trades: " << total_trades << "\n";
    ss << "  Winning Trades: " << winning_trades << "\n";
    ss << "  Losing Trades: " << losing_trades << "\n";
    ss << "  Win Rate: " << win_rate << "%\n";
    ss << "  Profit Factor: " << std::setprecision(2) << profit_factor << "\n";
    ss << "  Average Win: " << average_win << "%\n";
    ss << "  Average Loss: " << average_loss << "%\n";
    ss << "  Win/Loss Ratio: " << avg_win_loss_ratio << "\n\n";
    
    ss << "Additional Metrics:\n";
    ss << "  Beta: " << std::setprecision(3) << beta << "\n";
    ss << "  Alpha: " << alpha << "%\n";
    ss << "  Information Ratio: " << information_ratio << "\n";
    ss << "  Recovery Factor: " << recovery_factor << "\n";
    
    return ss.str();
}

} // namespace backtest
} // namespace pplustrader