// SimulatedExchange.cpp - 模拟交易所实现
#include "SimulatedExchange.h"
#include <algorithm>
#include <random>

namespace pplustrader {
namespace backtest {

// SimulatedAccount 实现
double SimulatedAccount::total_value(const std::string& symbol, double current_price) const {
    double position_value = 0.0;
    auto pos_it = positions.find(symbol);
    if (pos_it != positions.end()) {
        position_value = pos_it->second * current_price;
    }
    return cash + position_value;
}

void SimulatedAccount::update_position(const std::string& symbol, double quantity, double price) {
    if (std::abs(quantity) < 1e-10) {
        return;
    }
    
    auto pos_it = positions.find(symbol);
    auto avg_it = avg_prices.find(symbol);
    
    if (pos_it == positions.end()) {
        // 新持仓
        positions[symbol] = quantity;
        avg_prices[symbol] = price;
    } else {
        // 更新持仓
        double old_position = pos_it->second;
        double old_avg_price = avg_it->second;
        double old_value = old_position * old_avg_price;
        
        double new_quantity = quantity;
        double new_value = new_quantity * price;
        
        if (std::abs(old_position + new_quantity) < 1e-10) {
            // 平仓
            positions.erase(symbol);
            avg_prices.erase(symbol);
        } else {
            // 更新平均价格
            double total_value = old_value + new_value;
            double total_quantity = old_position + new_quantity;
            
            positions[symbol] = total_quantity;
            avg_prices[symbol] = total_value / total_quantity;
        }
    }
}

double SimulatedAccount::get_position(const std::string& symbol) const {
    auto it = positions.find(symbol);
    return (it != positions.end()) ? it->second : 0.0;
}

// SimulatedExchange::Impl 定义
class SimulatedExchange::Impl {
public:
    Impl(double initial_capital, double commission_rate, double slippage)
        : commission_rate_(commission_rate),
          slippage_(slippage),
          order_id_counter_(0) {
        account_.cash = initial_capital;
    }
    
    void set_market_data(const core::TickData& tick) {
        current_tick_ = tick;
    }
    
    std::string submit_order(const core::Order& order) {
        // 生成订单ID
        std::string order_id = "order_" + std::to_string(++order_id_counter_);
        
        // 复制订单并设置ID
        core::Order new_order = order;
        new_order.order_id = order_id;
        new_order.status = core::OrderStatus::PENDING;
        
        // 添加到待处理订单
        pending_orders_[order_id] = new_order;
        
        return order_id;
    }
    
    bool cancel_order(const std::string& order_id) {
        auto it = pending_orders_.find(order_id);
        if (it != pending_orders_.end()) {
            it->second.status = core::OrderStatus::CANCELLED;
            // 移动到已取消订单
            cancelled_orders_[order_id] = it->second;
            pending_orders_.erase(it);
            return true;
        }
        return false;
    }
    
    core::OrderStatus get_order_status(const std::string& order_id) {
        // 检查各种订单列表
        auto pending_it = pending_orders_.find(order_id);
        if (pending_it != pending_orders_.end()) {
            return pending_it->second.status;
        }
        
        auto filled_it = filled_orders_.find(order_id);
        if (filled_it != filled_orders_.end()) {
            return core::OrderStatus::FILLED;
        }
        
        auto cancelled_it = cancelled_orders_.find(order_id);
        if (cancelled_it != cancelled_orders_.end()) {
            return core::OrderStatus::CANCELLED;
        }
        
        auto rejected_it = rejected_orders_.find(order_id);
        if (rejected_it != rejected_orders_.end()) {
            return core::OrderStatus::REJECTED;
        }
        
        return core::OrderStatus::UNKNOWN;
    }
    
    const SimulatedAccount& get_account() const {
        return account_;
    }
    
    std::vector<core::Order> get_open_orders() const {
        std::vector<core::Order> open_orders;
        for (const auto& pair : pending_orders_) {
            if (pair.second.status == core::OrderStatus::PENDING ||
                pair.second.status == core::OrderStatus::PARTIALLY_FILLED) {
                open_orders.push_back(pair.second);
            }
        }
        return open_orders;
    }
    
    void match_orders() {
        // 简化撮合：所有订单以当前价格立即成交
        std::vector<std::string> to_remove;
        
        for (auto& pair : pending_orders_) {
            auto& order = pair.second;
            
            // 检查订单是否可执行
            if (order.status != core::OrderStatus::PENDING &&
                order.status != core::OrderStatus::PARTIALLY_FILLED) {
                continue;
            }
            
            // 计算成交价格（考虑滑点）
            double execution_price = calculate_execution_price(order);
            
            // 计算佣金
            double commission = order.quantity * execution_price * commission_rate_;
            
            // 检查资金是否充足（仅限买入订单）
            if (order.side == core::OrderSide::BUY) {
                double total_cost = order.quantity * execution_price + commission;
                if (account_.cash < total_cost) {
                    // 资金不足，拒绝订单
                    order.status = core::OrderStatus::REJECTED;
                    rejected_orders_[order.order_id] = order;
                    to_remove.push_back(order.order_id);
                    continue;
                }
            }
            
            // 检查持仓是否充足（仅限卖出订单）
            if (order.side == core::OrderSide::SELL) {
                double current_position = account_.get_position(order.symbol);
                if (current_position < order.quantity) {
                    // 持仓不足，拒绝订单
                    order.status = core::OrderStatus::REJECTED;
                    rejected_orders_[order.order_id] = order;
                    to_remove.push_back(order.order_id);
                    continue;
                }
            }
            
            // 执行订单
            execute_order(order, execution_price, commission);
            
            // 记录交易
            TradeRecord trade;
            trade.order_id = order.order_id;
            trade.symbol = order.symbol;
            trade.side = order.side;
            trade.price = execution_price;
            trade.quantity = order.quantity;
            trade.commission = commission;
            trade.timestamp = std::chrono::system_clock::now();
            trade_records_.push_back(trade);
            
            // 更新订单状态
            order.status = core::OrderStatus::FILLED;
            filled_orders_[order.order_id] = order;
            to_remove.push_back(order.order_id);
        }
        
        // 移除已处理的订单
        for (const auto& order_id : to_remove) {
            pending_orders_.erase(order_id);
        }
    }
    
    double get_total_value() const {
        if (current_tick_.symbol.empty()) {
            return account_.cash;
        }
        return account_.total_value(current_tick_.symbol, current_tick_.last_price);
    }
    
    double get_position(const std::string& symbol) const {
        return account_.get_position(symbol);
    }
    
    const std::vector<TradeRecord>& get_trade_records() const {
        return trade_records_;
    }
    
private:
    double calculate_execution_price(const core::Order& order) {
        double base_price = current_tick_.last_price;
        
        // 应用滑点
        // 买入订单：在卖价上加滑点
        // 卖出订单：在买价上减滑点
        if (order.side == core::OrderSide::BUY) {
            return base_price * (1.0 + slippage_);
        } else {
            return base_price * (1.0 - slippage_);
        }
    }
    
    void execute_order(const core::Order& order, double price, double commission) {
        // 计算交易金额
        double trade_value = order.quantity * price;
        
        if (order.side == core::OrderSide::BUY) {
            // 买入：减少现金，增加持仓
            account_.cash -= (trade_value + commission);
            account_.update_position(order.symbol, order.quantity, price);
        } else {
            // 卖出：增加现金，减少持仓
            account_.cash += (trade_value - commission);
            account_.update_position(order.symbol, -order.quantity, price);
        }
    }
    
    double commission_rate_;
    double slippage_;
    
    SimulatedAccount account_;
    core::TickData current_tick_;
    
    std::unordered_map<std::string, core::Order> pending_orders_;
    std::unordered_map<std::string, core::Order> filled_orders_;
    std::unordered_map<std::string, core::Order> cancelled_orders_;
    std::unordered_map<std::string, core::Order> rejected_orders_;
    
    std::vector<TradeRecord> trade_records_;
    unsigned long order_id_counter_;
};

// SimulatedExchange 公共接口实现
SimulatedExchange::SimulatedExchange(double initial_capital, double commission_rate, double slippage)
    : impl_(std::make_unique<Impl>(initial_capital, commission_rate, slippage)) {}

SimulatedExchange::~SimulatedExchange() = default;

void SimulatedExchange::set_market_data(const core::TickData& tick) {
    impl_->set_market_data(tick);
}

std::string SimulatedExchange::submit_order(const core::Order& order) {
    return impl_->submit_order(order);
}

bool SimulatedExchange::cancel_order(const std::string& order_id) {
    return impl_->cancel_order(order_id);
}

core::OrderStatus SimulatedExchange::get_order_status(const std::string& order_id) {
    return impl_->get_order_status(order_id);
}

const SimulatedAccount& SimulatedExchange::get_account() const {
    return impl_->get_account();
}

std::vector<core::Order> SimulatedExchange::get_open_orders() const {
    return impl_->get_open_orders();
}

void SimulatedExchange::match_orders() {
    impl_->match_orders();
}

double SimulatedExchange::get_total_value() const {
    return impl_->get_total_value();
}

double SimulatedExchange::get_position(const std::string& symbol) const {
    return impl_->get_position(symbol);
}

const std::vector<SimulatedExchange::TradeRecord>& SimulatedExchange::get_trade_records() const {
    return impl_->get_trade_records();
}

} // namespace backtest
} // namespace pplustrader