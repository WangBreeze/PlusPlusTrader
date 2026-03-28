// StopLossTakeProfit.cpp - 止损止盈管理器实现
#include "StopLossTakeProfit.h"
#include <algorithm>
#include <cmath>
#include <iostream>

namespace pplustrader {
namespace risk {

StopLossTakeProfit::StopLossTakeProfit(double default_stop_loss,
                                       double default_take_profit,
                                       double max_position_risk)
    : default_stop_loss_(std::max(0.001, std::min(0.5, default_stop_loss))),
      default_take_profit_(std::max(0.001, std::min(0.5, default_take_profit))),
      max_position_risk_(std::max(0.001, std::min(0.5, max_position_risk))) {
    reset();
}

RiskCheckResult StopLossTakeProfit::check_order(const core::Order& order,
                                               const core::AccountInfo& account,
                                               const core::TickData& market) {
    RiskCheckResult result;
    
    if (order.symbol.empty() || order.quantity <= 0) {
        result.passed = false;
        result.reason = "无效的订单参数";
        return result;
    }
    
    // 检查持仓风险
    auto pos_it = positions_.find(order.symbol);
    if (pos_it != positions_.end()) {
        const auto& pos_risk = pos_it->second;
        
        // 如果已经有持仓，检查是否违反风险管理规则
        if (order.side == core::OrderSide::BUY && pos_risk.quantity < 0) {
            // 空头平仓，允许
        } else if (order.side == core::OrderSide::SELL && pos_risk.quantity > 0) {
            // 多头平仓，允许
        } else {
            // 同向加仓，检查总风险
            double new_position = pos_risk.quantity + 
                                 (order.side == core::OrderSide::BUY ? order.quantity : -order.quantity);
            double position_value = std::abs(new_position) * market.last_price;
            double account_equity = account.equity;
            
            if (account_equity > 0) {
                double risk_ratio = position_value / account_equity;
                if (risk_ratio > max_position_risk_) {
                    result.passed = false;
                    result.reason = "持仓风险超过限制: " + std::to_string(risk_ratio * 100) + "%";
                    result.suggested_quantity = std::abs(max_position_risk_ * account_equity / market.last_price);
                }
            }
        }
    }
    
    return result;
}

void StopLossTakeProfit::update_market(const core::TickData& tick) {
    // 更新价格历史
    auto& history = price_history_[tick.symbol];
    history.push_back(tick.last_price);
    
    // 保持最近100个价格
    const size_t max_history = 100;
    if (history.size() > max_history) {
        history.pop_front();
    }
    
    // 更新持仓的最高/最低价（用于移动止损）
    auto pos_it = positions_.find(tick.symbol);
    if (pos_it != positions_.end()) {
        auto& pos_risk = pos_it->second;
        
        if (pos_risk.quantity > 0) {  // 多头持仓
            pos_risk.highest_price = std::max(pos_risk.highest_price, tick.last_price);
            pos_risk.lowest_price = std::min(pos_risk.lowest_price, tick.last_price);
        } else if (pos_risk.quantity < 0) {  // 空头持仓
            pos_risk.highest_price = std::max(pos_risk.highest_price, tick.last_price);
            pos_risk.lowest_price = std::min(pos_risk.lowest_price, tick.last_price);
        }
        
        // 更新移动止损
        update_trailing_stop(tick.symbol, tick.last_price);
    }
    
    // 更新账户风险指标
    // TODO: 实现实际的风险指标计算
}

void StopLossTakeProfit::update_position(const std::string& symbol,
                                        double quantity,
                                        double avg_price) {
    auto it = positions_.find(symbol);
    
    if (std::abs(quantity) < 1e-10) {
        // 平仓，移除持仓记录
        if (it != positions_.end()) {
            positions_.erase(it);
        }
        return;
    }
    
    if (it == positions_.end()) {
        // 新持仓
        PositionRisk risk;
        risk.symbol = symbol;
        risk.entry_price = avg_price;
        risk.quantity = quantity;
        risk.highest_price = avg_price;
        risk.lowest_price = avg_price;
        
        // 设置默认止损止盈
        set_position_risk(symbol, default_stop_loss_, default_take_profit_);
        
        positions_[symbol] = risk;
    } else {
        // 更新现有持仓
        auto& pos_risk = it->second;
        
        // 更新平均价格
        double old_value = pos_risk.quantity * pos_risk.entry_price;
        double new_value = quantity * avg_price;
        double total_quantity = pos_risk.quantity + quantity;
        
        if (std::abs(total_quantity) > 1e-10) {
            pos_risk.entry_price = (old_value + new_value) / total_quantity;
            pos_risk.quantity = total_quantity;
            
            // 更新最高/最低价
            pos_risk.highest_price = std::max(pos_risk.highest_price, avg_price);
            pos_risk.lowest_price = std::min(pos_risk.lowest_price, avg_price);
        } else {
            // 完全平仓
            positions_.erase(it);
        }
    }
}

RiskCheckResult StopLossTakeProfit::check_account(const core::AccountInfo& account) {
    RiskCheckResult result;
    
    // 检查总回撤
    if (account.equity > 0) {
        peak_equity_ = std::max(peak_equity_, account.equity);
        current_drawdown_ = (peak_equity_ - account.equity) / peak_equity_;
        max_drawdown_ = std::max(max_drawdown_, current_drawdown_);
        
        // 如果回撤过大，发出警告
        if (current_drawdown_ > max_position_risk_ * 2) {
            result.passed = false;
            result.reason = "账户回撤过大: " + std::to_string(current_drawdown_ * 100) + "%";
        }
    }
    
    return result;
}

double StopLossTakeProfit::get_risk_metric(const std::string& metric) const {
    if (metric == "max_drawdown") {
        return max_drawdown_;
    } else if (metric == "current_drawdown") {
        return current_drawdown_;
    } else if (metric == "total_risk_exposure") {
        return total_risk_exposure_;
    } else if (metric == "peak_equity") {
        return peak_equity_;
    }
    return 0.0;
}

void StopLossTakeProfit::reset() {
    positions_.clear();
    price_history_.clear();
    total_risk_exposure_ = 0.0;
    max_drawdown_ = 0.0;
    current_drawdown_ = 0.0;
    peak_equity_ = 0.0;
}

bool StopLossTakeProfit::check_stop_loss(const std::string& symbol,
                                        double current_price,
                                        double& stop_price,
                                        std::string& reason) {
    auto it = positions_.find(symbol);
    if (it == positions_.end()) {
        return false;
    }
    
    const auto& pos_risk = it->second;
    
    // 检查固定止损
    if (pos_risk.stop_loss_price > 0) {
        if ((pos_risk.quantity > 0 && current_price <= pos_risk.stop_loss_price) ||
            (pos_risk.quantity < 0 && current_price >= pos_risk.stop_loss_price)) {
            stop_price = pos_risk.stop_loss_price;
            reason = "触及固定止损价格";
            return true;
        }
    }
    
    // 检查移动止损
    if (pos_risk.trailing_stop_price > 0) {
        if ((pos_risk.quantity > 0 && current_price <= pos_risk.trailing_stop_price) ||
            (pos_risk.quantity < 0 && current_price >= pos_risk.trailing_stop_price)) {
            stop_price = pos_risk.trailing_stop_price;
            reason = "触及移动止损价格";
            return true;
        }
    }
    
    return false;
}

bool StopLossTakeProfit::check_take_profit(const std::string& symbol,
                                          double current_price,
                                          double& take_price,
                                          std::string& reason) {
    auto it = positions_.find(symbol);
    if (it == positions_.end()) {
        return false;
    }
    
    const auto& pos_risk = it->second;
    
    if (pos_risk.take_profit_price > 0) {
        if ((pos_risk.quantity > 0 && current_price >= pos_risk.take_profit_price) ||
            (pos_risk.quantity < 0 && current_price <= pos_risk.take_profit_price)) {
            take_price = pos_risk.take_profit_price;
            reason = "触及止盈价格";
            return true;
        }
    }
    
    return false;
}

void StopLossTakeProfit::set_position_risk(const std::string& symbol,
                                          double stop_loss,
                                          double take_profit,
                                          SLTPType sl_type,
                                          SLTPType tp_type) {
    auto it = positions_.find(symbol);
    if (it == positions_.end()) {
        return;
    }
    
    auto& pos_risk = it->second;
    pos_risk.sl_type = sl_type;
    pos_risk.tp_type = tp_type;
    pos_risk.sl_value = stop_loss;
    pos_risk.tp_value = take_profit;
    
    // 计算止损止盈价格
    if (sl_type == SLTPType::FIXED) {
        pos_risk.stop_loss_price = stop_loss;
    } else if (sl_type == SLTPType::PERCENTAGE) {
        if (pos_risk.quantity > 0) {  // 多头
            pos_risk.stop_loss_price = pos_risk.entry_price * (1.0 - stop_loss);
        } else {  // 空头
            pos_risk.stop_loss_price = pos_risk.entry_price * (1.0 + stop_loss);
        }
    }
    
    if (tp_type == SLTPType::FIXED) {
        pos_risk.take_profit_price = take_profit;
    } else if (tp_type == SLTPType::PERCENTAGE) {
        if (pos_risk.quantity > 0) {  // 多头
            pos_risk.take_profit_price = pos_risk.entry_price * (1.0 + take_profit);
        } else {  // 空头
            pos_risk.take_profit_price = pos_risk.entry_price * (1.0 - take_profit);
        }
    }
}

void StopLossTakeProfit::set_trailing_stop(const std::string& symbol, double distance) {
    auto it = positions_.find(symbol);
    if (it == positions_.end()) {
        return;
    }
    
    auto& pos_risk = it->second;
    pos_risk.trailing_distance = std::max(0.001, std::min(0.5, distance));
}

double StopLossTakeProfit::calculate_stop_loss(double entry_price,
                                              double quantity,
                                              SLTPType type,
                                              double value,
                                              [[maybe_unused]] const core::TickData* market) const {
    if (type == SLTPType::FIXED) {
        return value;
    } else if (type == SLTPType::PERCENTAGE) {
        if (quantity > 0) {  // 多头
            return entry_price * (1.0 - value);
        } else {  // 空头
            return entry_price * (1.0 + value);
        }
    }
    // TODO: 实现其他类型的止损计算
    return 0.0;
}

double StopLossTakeProfit::calculate_take_profit(double entry_price,
                                                double quantity,
                                                SLTPType type,
                                                double value,
                                                [[maybe_unused]] const core::TickData* market) const {
    if (type == SLTPType::FIXED) {
        return value;
    } else if (type == SLTPType::PERCENTAGE) {
        if (quantity > 0) {  // 多头
            return entry_price * (1.0 + value);
        } else {  // 空头
            return entry_price * (1.0 - value);
        }
    }
    // TODO: 实现其他类型的止盈计算
    return 0.0;
}

void StopLossTakeProfit::update_trailing_stop(const std::string& symbol, double current_price) {
    auto it = positions_.find(symbol);
    if (it == positions_.end()) {
        return;
    }
    
    auto& pos_risk = it->second;
    
    if (pos_risk.trailing_distance <= 0) {
        return;
    }
    
    if (pos_risk.quantity > 0) {  // 多头
        // 更新移动止损（从最高点回落）
        double new_stop = current_price * (1.0 - pos_risk.trailing_distance);
        pos_risk.trailing_stop_price = std::max(pos_risk.trailing_stop_price, new_stop);
    } else if (pos_risk.quantity < 0) {  // 空头
        // 更新移动止损（从最低点回升）
        double new_stop = current_price * (1.0 + pos_risk.trailing_distance);
        pos_risk.trailing_stop_price = std::min(pos_risk.trailing_stop_price, new_stop);
    }
}

} // namespace risk
} // namespace pplustrader