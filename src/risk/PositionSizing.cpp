// PositionSizing.cpp - 仓位管理实现
#include "PositionSizing.h"
#include <algorithm>
#include <numeric>
#include <cmath>

namespace pplustrader {
namespace risk {

PositionSizing::PositionSizing(PositionSizingMethod method,
                               double risk_per_trade,
                               double max_portfolio_risk,
                               double kelly_fraction)
    : method_(method),
      risk_per_trade_(std::max(0.001, std::min(0.5, risk_per_trade))),
      max_portfolio_risk_(std::max(0.01, std::min(1.0, max_portfolio_risk))),
      kelly_fraction_(std::max(0.1, std::min(1.0, kelly_fraction))) {
    reset();
}

RiskCheckResult PositionSizing::check_order(const core::Order& order,
                                           const core::AccountInfo& account,
                                           const core::TickData& market) {
    RiskCheckResult result;
    
    if (order.symbol.empty() || order.quantity <= 0 || account.equity <= 0) {
        result.passed = false;
        result.reason = "无效的参数";
        return result;
    }
    
    // 计算建议仓位大小
    double stop_loss_price = 0.0;
    // TODO: 从止损止盈管理器获取止损价格
    
    double suggested_size = calculate_position_size(order.symbol,
                                                   market.last_price,
                                                   stop_loss_price,
                                                   account.equity,
                                                   current_risk_exposure_);
    
    // 检查订单数量是否超过建议
    double order_value = order.quantity * market.last_price;
    double max_value = suggested_size * account.equity;
    
    if (order_value > max_value) {
        result.passed = false;
        result.reason = "订单规模超过风险管理限制";
        result.suggested_quantity = suggested_size;
    }
    
    // 检查组合总风险
    double new_risk_exposure = current_risk_exposure_ + (order_value / account.equity);
    if (new_risk_exposure > max_portfolio_risk_) {
        result.passed = false;
        result.reason = "组合风险超过限制: " + std::to_string(new_risk_exposure * 100) + "%";
        
        // 计算允许的最大数量
        double allowed_risk = max_portfolio_risk_ - current_risk_exposure_;
        if (allowed_risk > 0) {
            double allowed_value = allowed_risk * account.equity;
            result.suggested_quantity = allowed_value / market.last_price;
        }
    }
    
    return result;
}

void PositionSizing::update_market(const core::TickData& tick) {
    // 更新价格收益率历史（用于波动率计算）
    auto& returns = price_returns_[tick.symbol];
    
    if (!returns.empty()) {
        double prev_price = returns.back();
        if (prev_price > 0) {
            double ret = std::log(tick.last_price / prev_price);
            returns.push_back(ret);
            
            // 保持最近252个收益率（约1年交易日）
            const size_t max_returns = 252;
            if (returns.size() > max_returns) {
                returns.pop_front();
            }
        }
    } else {
        // 第一个价格，存储为价格本身（不是收益率）
        returns.push_back(tick.last_price);
    }
    
    // 更新组合波动率
    // TODO: 实现实际波动率计算
}

void PositionSizing::update_position(const std::string& symbol,
                                    double quantity,
                                    double avg_price) {
    // 更新当前风险敞口
    double position_value = std::abs(quantity) * avg_price;
    
    if (total_account_equity_ > 0) {
        double risk_ratio = position_value / total_account_equity_;
        
        if (quantity == 0) {
            // 平仓，减少风险敞口
            current_risk_exposure_ = std::max(0.0, current_risk_exposure_ - risk_ratio);
        } else {
            // 开仓或加仓，增加风险敞口
            current_risk_exposure_ += risk_ratio;
        }
    }
}

RiskCheckResult PositionSizing::check_account(const core::AccountInfo& account) {
    RiskCheckResult result;
    
    total_account_equity_ = account.equity;
    
    // 检查组合风险
    if (current_risk_exposure_ > max_portfolio_risk_) {
        result.passed = false;
        result.reason = "组合风险过高: " + std::to_string(current_risk_exposure_ * 100) + "%";
    }
    
    return result;
}

double PositionSizing::get_risk_metric(const std::string& metric) const {
    if (metric == "current_risk_exposure") {
        return current_risk_exposure_;
    } else if (metric == "portfolio_volatility") {
        return portfolio_volatility_;
    } else if (metric == "max_portfolio_risk") {
        return max_portfolio_risk_;
    } else if (metric == "risk_per_trade") {
        return risk_per_trade_;
    }
    return 0.0;
}

void PositionSizing::reset() {
    symbol_stats_.clear();
    price_returns_.clear();
    total_account_equity_ = 0.0;
    current_risk_exposure_ = 0.0;
    portfolio_volatility_ = 0.0;
}

double PositionSizing::calculate_position_size(const std::string& symbol,
                                              double entry_price,
                                              double stop_loss_price,
                                              double account_equity,
                                              double current_risk_exposure) const {
    if (account_equity <= 0 || entry_price <= 0) {
        return 0.0;
    }
    
    double position_size = 0.0;
    
    switch (method_) {
        case PositionSizingMethod::FIXED_FRACTIONAL: {
            if (stop_loss_price > 0) {
                double risk_per_share = std::abs(entry_price - stop_loss_price);
                if (risk_per_share > 0) {
                    double risk_amount = account_equity * risk_per_trade_;
                    position_size = risk_amount / risk_per_share;
                }
            } else {
                // 没有止损价，使用固定比例
                position_size = (account_equity * risk_per_trade_) / entry_price;
            }
            break;
        }
            
        case PositionSizingMethod::KELLY_CRITERION: {
            auto it = symbol_stats_.find(symbol);
            if (it != symbol_stats_.end()) {
                const auto& stats = it->second;
                double win_rate = stats.win_rate();
                double avg_win = stats.avg_win();
                double avg_loss = stats.avg_loss();
                
                if (avg_loss > 0) {
                    double kelly_f = win_rate - (1.0 - win_rate) / (avg_win / avg_loss);
                    kelly_f = std::max(0.0, std::min(0.25, kelly_f));  // 限制在0-25%
                    kelly_f *= kelly_fraction_;  // 使用半凯利或其他分数
                    
                    position_size = (account_equity * kelly_f) / entry_price;
                }
            } else {
                // 没有历史数据，退回固定分数法
                position_size = (account_equity * risk_per_trade_) / entry_price;
            }
            break;
        }
            
        case PositionSizingMethod::VOLATILITY_BASED: {
            double volatility = estimate_volatility(symbol);
            double target_volatility = 0.01;  // 目标波动率1%
            position_size = volatility_based_size(account_equity, volatility, target_volatility);
            break;
        }
            
        case PositionSizingMethod::EQUAL_WEIGHT: {
            // 等权重：每个标的分配相同资金
            double target_position_value = account_equity * risk_per_trade_;
            position_size = target_position_value / entry_price;
            break;
        }
            
        case PositionSizingMethod::RISK_PARITY: {
            // 风险平价：根据波动率调整权重
            double volatility = estimate_volatility(symbol);
            if (volatility > 0) {
                double risk_weight = 1.0 / volatility;
                double total_risk_weight = 1.0;  // 简化：假设只有一个标的
                double weight = risk_weight / total_risk_weight;
                position_size = (account_equity * weight) / entry_price;
            }
            break;
        }
    }
    
    // 考虑当前风险敞口
    double available_risk = max_portfolio_risk_ - current_risk_exposure;
    if (available_risk <= 0) {
        return 0.0;
    }
    
    double max_position_by_risk = (account_equity * available_risk) / entry_price;
    return std::min(position_size, max_position_by_risk);
}

double PositionSizing::estimate_volatility(const std::string& symbol, int period) const {
    auto it = price_returns_.find(symbol);
    if (it == price_returns_.end() || it->second.size() < 2) {
        return 0.1;  // 默认10%波动率
    }
    
    const auto& returns = it->second;
    size_t count = std::min(static_cast<size_t>(period), returns.size());
    
    // 计算平均收益率
    double sum = 0.0;
    size_t valid_count = 0;
    for (size_t i = returns.size() - count; i < returns.size(); ++i) {
        sum += returns[i];
        valid_count++;
    }
    
    if (valid_count <= 1) {
        return 0.1;
    }
    
    double mean = sum / valid_count;
    
    // 计算标准差
    double sum_sq = 0.0;
    for (size_t i = returns.size() - count; i < returns.size(); ++i) {
        double diff = returns[i] - mean;
        sum_sq += diff * diff;
    }
    
    double variance = sum_sq / (valid_count - 1);
    double volatility = std::sqrt(variance);
    
    // 年化波动率（假设252个交易日）
    return volatility * std::sqrt(252.0);
}

double PositionSizing::fixed_fractional_size(double account_equity,
                                            double risk_per_trade,
                                            double entry_price,
                                            double stop_loss_price) const {
    if (stop_loss_price > 0) {
        double risk_per_share = std::abs(entry_price - stop_loss_price);
        if (risk_per_share > 0) {
            double risk_amount = account_equity * risk_per_trade;
            return risk_amount / risk_per_share;
        }
    }
    
    // 没有止损价，使用固定比例
    return (account_equity * risk_per_trade) / entry_price;
}

double PositionSizing::kelly_criterion_size(double win_rate,
                                           double avg_win,
                                           double avg_loss,
                                           double account_equity) const {
    if (avg_loss <= 0) {
        return 0.0;
    }
    
    double b = avg_win / avg_loss;  // 盈亏比
    double kelly_f = win_rate - (1.0 - win_rate) / b;
    
    // 限制凯利分数在合理范围内
    kelly_f = std::max(0.0, std::min(0.25, kelly_f));
    kelly_f *= kelly_fraction_;  // 使用分数凯利
    
    return account_equity * kelly_f;
}

double PositionSizing::volatility_based_size(double account_equity,
                                            double volatility,
                                            double target_volatility) const {
    if (volatility <= 0) {
        return 0.0;
    }
    
    // 计算达到目标波动率所需的仓位
    double weight = target_volatility / volatility;
    weight = std::min(weight, 1.0);  // 不超过100%仓位
    
    return account_equity * weight;
}

} // namespace risk
} // namespace pplustrader