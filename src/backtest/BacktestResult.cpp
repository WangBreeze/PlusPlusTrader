// BacktestResult.cpp - Implementation of advanced backtest statistics
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#include "BacktestResult.h"
#include <fstream>
#include <iomanip>
#include <sstream>
#include <cmath>
#include <algorithm>

namespace pplustrader {
namespace backtest {

// 计算夏普比率
double BacktestResult::calculate_sharpe_ratio(double risk_free_rate) const {
    if (equity_curve_.size() < 2) return 0.0;
    
    // 从净值曲线计算日收益率
    std::vector<double> returns;
    for (size_t i = 1; i < equity_curve_.size(); ++i) {
        double ret = (equity_curve_[i] - equity_curve_[i-1]) / equity_curve_[i-1];
        returns.push_back(ret);
    }
    
    return StatisticsCalculator::calculate_sharpe_ratio(returns, risk_free_rate);
}

// 计算索提诺比率
double BacktestResult::calculate_sortino_ratio(double risk_free_rate) const {
    if (equity_curve_.size() < 2) return 0.0;
    
    std::vector<double> returns;
    for (size_t i = 1; i < equity_curve_.size(); ++i) {
        double ret = (equity_curve_[i] - equity_curve_[i-1]) / equity_curve_[i-1];
        returns.push_back(ret);
    }
    
    return StatisticsCalculator::calculate_sortino_ratio(returns, risk_free_rate);
}

// 计算最大回撤
double BacktestResult::calculate_max_drawdown() const {
    if (equity_curve_.empty()) return 0.0;
    
    return StatisticsCalculator::calculate_max_drawdown(equity_curve_);
}

// 计算波动率
double BacktestResult::calculate_volatility(int periods_per_year) const {
    if (equity_curve_.size() < 2) return 0.0;
    
    std::vector<double> returns;
    for (size_t i = 1; i < equity_curve_.size(); ++i) {
        double ret = (equity_curve_[i] - equity_curve_[i-1]) / equity_curve_[i-1];
        returns.push_back(ret);
    }
    
    return StatisticsCalculator::calculate_volatility(returns, periods_per_year);
}

// 计算卡玛比率
double BacktestResult::calculate_calmar_ratio() const {
    if (equity_curve_.empty()) return 0.0;
    
    // 计算年化收益率
    double initial_equity = equity_curve_[0];
    double final_equity = equity_curve_.back();
    double total_return = (final_equity - initial_equity) / initial_equity;
    
    // 假设252个交易日
    double years = equity_curve_.size() / 252.0;
    double annualized_return = (std::pow(1.0 + total_return, 1.0 / years) - 1.0);
    
    // 计算最大回撤
    double max_dd = calculate_max_drawdown() / 100.0;  // 转换为小数
    
    if (max_dd == 0.0) return 0.0;
    
    return annualized_return / max_dd;
}

// 计算价值风险（VaR）
double BacktestResult::calculate_var(double confidence_level) const {
    if (equity_curve_.size() < 2) return 0.0;
    
    std::vector<double> returns;
    for (size_t i = 1; i < equity_curve_.size(); ++i) {
        double ret = (equity_curve_[i] - equity_curve_[i-1]) / equity_curve_[i-1];
        returns.push_back(ret);
    }
    
    return StatisticsCalculator::calculate_var(returns, confidence_level);
}

// 计算综合投资组合指标
PortfolioMetrics BacktestResult::calculate_comprehensive_metrics(int periods_per_year) const {
    if (equity_curve_.empty()) {
        return PortfolioMetrics();
    }
    
    // 从净值曲线计算收益率
    std::vector<double> returns;
    for (size_t i = 1; i < equity_curve_.size(); ++i) {
        double ret = (equity_curve_[i] - equity_curve_[i-1]) / equity_curve_[i-1] * 100.0;
        returns.push_back(ret);
    }
    
    // 如果有交易记录，计算交易收益率
    std::vector<double> trade_returns;
    if (!trades_.empty()) {
        for (const auto& trade : trades_) {
            if (trade.profit_loss != 0.0 && trade.quantity != 0.0) {
                double ret = trade.profit_loss / (trade.price * trade.quantity) * 100.0;
                trade_returns.push_back(ret);
            }
        }
    }
    
    return StatisticsCalculator::calculate_comprehensive_metrics(
        equity_curve_, trade_returns, periods_per_year);
}

// 生成HTML回测报告
bool BacktestResult::generate_html_report(const std::string& filename) const {
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }
    
    // 计算综合指标
    PortfolioMetrics metrics = calculate_comprehensive_metrics();
    
    file << "<!DOCTYPE html>\n";
    file << "<html lang=\"zh-CN\">\n";
    file << "<head>\n";
    file << "    <meta charset=\"UTF-8\">\n";
    file << "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n";
    file << "    <title>PlusPlusTrader 回测报告</title>\n";
    file << "    <style>\n";
    file << "        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }\n";
    file << "        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }\n";
    file << "        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }\n";
    file << "        h2 { color: #34495e; margin-top: 30px; }\n";
    file << "        .metric-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }\n";
    file << "        .metric-card { background: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; border-radius: 5px; }\n";
    file << "        .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }\n";
    file << "        .metric-label { color: #7f8c8d; font-size: 14px; margin-top: 5px; }\n";
    file << "        .good { color: #27ae60; }\n";
    file << "        .bad { color: #e74c3c; }\n";
    file << "        .neutral { color: #f39c12; }\n";
    file << "        table { width: 100%; border-collapse: collapse; margin: 20px 0; }\n";
    file << "        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }\n";
    file << "        th { background-color: #f2f2f2; }\n";
    file << "        tr:hover { background-color: #f5f5f5; }\n";
    file << "        .summary { background: #e8f4fc; padding: 20px; border-radius: 5px; margin: 20px 0; }\n";
    file << "    </style>\n";
    file << "</head>\n";
    file << "<body>\n";
    file << "    <div class=\"container\">\n";
    file << "        <h1>📊 PlusPlusTrader 回测报告</h1>\n";
    file << "        <div class=\"summary\">\n";
    file << "            <p><strong>策略名称:</strong> " << strategy_name_ << "</p>\n";
    file << "            <p><strong>回测期间:</strong> " << start_time_ << " 至 " << end_time_ << "</p>\n";
    file << "            <p><strong>初始资金:</strong> ¥" << std::fixed << std::setprecision(2) << initial_capital_ << "</p>\n";
    file << "            <p><strong>最终资金:</strong> ¥" << std::fixed << std::setprecision(2) << final_capital_ << "</p>\n";
    file << "            <p><strong>总收益率:</strong> <span class=\"" << (total_return_ > 0 ? "good" : "bad") << "\">" << std::fixed << std::setprecision(2) << total_return_ << "%</span></p>\n";
    file << "        </div>\n";
    
    // 关键指标
    file << "        <h2>📈 关键绩效指标</h2>\n";
    file << "        <div class=\"metric-grid\">\n";
    
    auto add_metric = [&](const std::string& label, double value, const std::string& unit = "", const std::string& cls = "neutral") {
        file << "            <div class=\"metric-card\">\n";
        file << "                <div class=\"metric-value " << cls << "\">" << std::fixed << std::setprecision(2) << value << unit << "</div>\n";
        file << "                <div class=\"metric-label\">" << label << "</div>\n";
        file << "            </div>\n";
    };
    
    add_metric("夏普比率", metrics.sharpe_ratio, "", metrics.sharpe_ratio > 1.0 ? "good" : (metrics.sharpe_ratio > 0 ? "neutral" : "bad"));
    add_metric("最大回撤", metrics.max_drawdown, "%", metrics.max_drawdown < 20.0 ? "good" : (metrics.max_drawdown < 40.0 ? "neutral" : "bad"));
    add_metric("年化收益", metrics.annualized_return, "%", metrics.annualized_return > 10.0 ? "good" : (metrics.annualized_return > 0 ? "neutral" : "bad"));
    add_metric("波动率", metrics.volatility, "%", metrics.volatility < 20.0 ? "good" : (metrics.volatility < 40.0 ? "neutral" : "bad"));
    add_metric("胜率", metrics.win_rate, "%", metrics.win_rate > 50.0 ? "good" : "neutral");
    add_metric("盈亏比", metrics.profit_factor, "", metrics.profit_factor > 1.5 ? "good" : (metrics.profit_factor > 1.0 ? "neutral" : "bad"));
    add_metric("索提诺比率", metrics.sortino_ratio, "", metrics.sortino_ratio > 1.0 ? "good" : (metrics.sortino_ratio > 0 ? "neutral" : "bad"));
    add_metric("卡玛比率", metrics.calmar_ratio, "", metrics.calmar_ratio > 0.5 ? "good" : (metrics.calmar_ratio > 0 ? "neutral" : "bad"));
    
    file << "        </div>\n";
    
    // 交易统计
    file << "        <h2>💰 交易统计</h2>\n";
    file << "        <table>\n";
    file << "            <tr><th>指标</th><th>数值</th></tr>\n";
    file << "            <tr><td>总交易次数</td><td>" << metrics.total_trades << "</td></tr>\n";
    file << "            <tr><td>盈利交易</td><td>" << metrics.winning_trades << "</td></tr>\n";
    file << "            <tr><td>亏损交易</td><td>" << metrics.losing_trades << "</td></tr>\n";
    file << "            <tr><td>平均盈利</td><td>" << std::fixed << std::setprecision(2) << metrics.average_win << "%</td></tr>\n";
    file << "            <tr><td>平均亏损</td><td>" << std::fixed << std::setprecision(2) << metrics.average_loss << "%</td></tr>\n";
    file << "            <tr><td>最大连续盈利</td><td>" << max_consecutive_wins_ << "</td></tr>\n";
    file << "            <tr><td>最大连续亏损</td><td>" << max_consecutive_losses_ << "</td></tr>\n";
    file << "        </table>\n";
    
    // 风险指标
    file << "        <h2>⚠️ 风险指标</h2>\n";
    file << "        <table>\n";
    file << "            <tr><th>指标</th><th>数值</th><th>说明</th></tr>\n";
    file << "            <tr><td>VaR (95%)</td><td>" << std::fixed << std::setprecision(2) << metrics.value_at_risk << "%</td><td>95%置信度下最大单日损失</td></tr>\n";
    file << "            <tr><td>Ulcer指数</td><td>" << std::fixed << std::setprecision(2) << metrics.ulcer_index << "</td><td>下跌风险指标</td></tr>\n";
    file << "            <tr><td>恢复因子</td><td>" << std::fixed << std::setprecision(2) << metrics.recovery_factor << "</td><td>收益/最大回撤</td></tr>\n";
    file << "            <tr><td>最大回撤持续时间</td><td>" << metrics.max_drawdown_duration << " 天</td><td>最长恢复时间</td></tr>\n";
    file << "        </table>\n";
    
    // 交易明细（前20笔）
    if (!trades_.empty()) {
        file << "        <h2>📝 交易明细（前20笔）</h2>\n";
        file << "        <table>\n";
        file << "            <tr><th>时间</th><th>代码</th><th>方向</th><th>价格</th><th>数量</th><th>盈亏</th></tr>\n";
        
        size_t limit = std::min(trades_.size(), static_cast<size_t>(20));
        for (size_t i = 0; i < limit; ++i) {
            const auto& trade = trades_[i];
            file << "            <tr>\n";
            file << "                <td>" << trade.timestamp << "</td>\n";
            file << "                <td>" << trade.symbol << "</td>\n";
            file << "                <td>" << (trade.direction == core::OrderDirection::BUY ? "买入" : "卖出") << "</td>\n";
            file << "                <td>¥" << std::fixed << std::setprecision(2) << trade.price << "</td>\n";
            file << "                <td>" << trade.quantity << "</td>\n";
            file << "                <td class=\"" << (trade.profit_loss >= 0 ? "good" : "bad") << "\">¥" 
                 << std::fixed << std::setprecision(2) << trade.profit_loss << "</td>\n";
            file << "            </tr>\n";
        }
        file << "        </table>\n";
        file << "        <p><em>共 " << trades_.size() << " 笔交易，显示前 " << limit << " 笔</em></p>\n";
    }
    
    file << "        <hr>\n";
    file << "        <p style=\"text-align: center; color: #7f8c8d; font-size: 12px;\">\n";
    file << "            报告生成时间: " << __DATE__ << " " << __TIME__ << " | PlusPlusTrader v1.0.0\n";
    file << "        </p>\n";
    file << "    </div>\n";
    file << "</body>\n";
    file << "</html>\n";
    
    file.close();
    return true;
}

// 生成JSON回测报告（简化版，不使用外部JSON库）
bool BacktestResult::generate_json_report(const std::string& filename) const {
    PortfolioMetrics metrics = calculate_comprehensive_metrics();
    
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }
    
    file << "{\n";
    file << "  \"strategy_name\": \"" << strategy_name_ << "\",\n";
    file << "  \"start_time\": \"" << start_time_ << "\",\n";
    file << "  \"end_time\": \"" << end_time_ << "\",\n";
    file << "  \"initial_capital\": " << std::fixed << std::setprecision(2) << initial_capital_ << ",\n";
    file << "  \"final_capital\": " << std::fixed << std::setprecision(2) << final_capital_ << ",\n";
    file << "  \"total_return\": " << std::fixed << std::setprecision(2) << total_return_ << ",\n";
    file << "  \"annualized_return\": " << std::fixed << std::setprecision(2) << metrics.annualized_return << ",\n";
    file << "  \"volatility\": " << std::fixed << std::setprecision(2) << metrics.volatility << ",\n";
    file << "  \"sharpe_ratio\": " << std::fixed << std::setprecision(3) << metrics.sharpe_ratio << ",\n";
    file << "  \"sortino_ratio\": " << std::fixed << std::setprecision(3) << metrics.sortino_ratio << ",\n";
    file << "  \"calmar_ratio\": " << std::fixed << std::setprecision(3) << metrics.calmar_ratio << ",\n";
    file << "  \"max_drawdown\": " << std::fixed << std::setprecision(2) << metrics.max_drawdown << ",\n";
    file << "  \"max_drawdown_duration\": " << metrics.max_drawdown_duration << ",\n";
    file << "  \"win_rate\": " << std::fixed << std::setprecision(2) << metrics.win_rate << ",\n";
    file << "  \"total_trades\": " << metrics.total_trades << ",\n";
    file << "  \"winning_trades\": " << metrics.winning_trades << ",\n";
    file << "  \"losing_trades\": " << metrics.losing_trades << ",\n";
    file << "  \"max_consecutive_wins\": " << max_consecutive_wins_ << ",\n";
    file << "  \"max_consecutive_losses\": " << max_consecutive_losses_ << "\n";
    file << "}\n";
    
    file.close();
    return true;
}

} // namespace backtest
} // namespace pplustrader