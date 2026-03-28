#include "core/BaseStrategy.h"
#include <iostream>
#include <memory>
#include <cmath>
#include <vector>

namespace pplustrader {
namespace example {

// 简单移动平均策略
class SimpleMovingAverageStrategy : public core::BaseStrategyImpl {
public:
    SimpleMovingAverageStrategy(const std::string& name, 
                               const std::string& symbol,
                               int short_period,
                               int long_period)
        : BaseStrategyImpl(name)
        , symbol_(symbol)
        , short_period_(short_period)
        , long_period_(long_period) {
        
        std::cout << "Creating SMA Strategy '" << name 
                  << "' for " << symbol
                  << " (short=" << short_period
                  << ", long=" << long_period << ")" << std::endl;
    }
    
    void initialize() override {
        BaseStrategyImpl::initialize();
        
        std::cout << "[" << name_ << "] Initializing SMA strategy" << std::endl;
        
        // 初始化移动平均线缓冲区
        short_ma_buffer_.reserve(short_period_);
        long_ma_buffer_.reserve(long_period_);
        
        // 重置状态
        position_ = 0.0;
        cash_ = 100000.0;  // 初始资金
        
        std::cout << "[" << name_ << "] Initial position: " << position_
                  << ", cash: " << cash_ << std::endl;
    }
    
    void on_tick(const core::TickData& tick) override {
        if (!initialized_ || tick.symbol != symbol_) return;
        
        // 记录价格
        double price = tick.last_price;
        prices_.push_back(price);
        
        // 保持缓冲区大小
        if (prices_.size() > static_cast<size_t>(long_period_)) {
            prices_.erase(prices_.begin());
        }
        
        // 计算移动平均
        if (prices_.size() >= static_cast<size_t>(long_period_)) {
            // 计算短期均线
            double short_ma = 0.0;
            size_t start_idx_short = prices_.size() - static_cast<size_t>(short_period_);
            for (size_t i = start_idx_short; i < prices_.size(); ++i) {
                short_ma += prices_[i];
            }
            short_ma /= short_period_;
            
            // 计算长期均线
            double long_ma = 0.0;
            size_t start_idx_long = prices_.size() - static_cast<size_t>(long_period_);
            for (size_t i = start_idx_long; i < prices_.size(); ++i) {
                long_ma += prices_[i];
            }
            long_ma /= long_period_;
            
            // 记录到缓冲区
            short_ma_buffer_.push_back(short_ma);
            long_ma_buffer_.push_back(long_ma);
            
            if (short_ma_buffer_.size() > 5) {
                short_ma_buffer_.erase(short_ma_buffer_.begin());
            }
            if (long_ma_buffer_.size() > 5) {
                long_ma_buffer_.erase(long_ma_buffer_.begin());
            }
            
            // 生成交易信号
            generate_signal(price, short_ma, long_ma);
        }
    }
    
    void on_order_filled(const core::Order& order) override {
        BaseStrategyImpl::on_order_filled(order);
        
        // 更新持仓和现金
        double trade_value = order.price * order.quantity;
        
        if (order.side == core::OrderSide::BUY) {
            position_ += order.quantity;
            cash_ -= trade_value;
            std::cout << "[" << name_ << "] Bought " << order.quantity 
                      << " " << order.symbol << " at " << order.price
                      << ", new position: " << position_
                      << ", cash: " << cash_ << std::endl;
        } else {
            position_ -= order.quantity;
            cash_ += trade_value;
            std::cout << "[" << name_ << "] Sold " << order.quantity 
                      << " " << order.symbol << " at " << order.price
                      << ", new position: " << position_
                      << ", cash: " << cash_ << std::endl;
        }
        
        // 计算总资产
        double total_assets = cash_ + (position_ * last_price_);
        std::cout << "[" << name_ << "] Total assets: " << total_assets << std::endl;
    }
    
    void cleanup() override {
        std::cout << "[" << name_ << "] Finalizing SMA strategy" << std::endl;
        std::cout << "[" << name_ << "] Final position: " << position_
                  << ", cash: " << cash_ << std::endl;
        
        BaseStrategyImpl::cleanup();
    }
    
private:
    void generate_signal(double price, double short_ma, double long_ma) {
        last_price_ = price;
        
        // 金叉：短线上穿长线，买入信号
        // 死叉：短线下穿长线，卖出信号
        bool golden_cross = false;
        bool death_cross = false;
        
        if (short_ma_buffer_.size() >= 2 && long_ma_buffer_.size() >= 2) {
            double prev_short_ma = short_ma_buffer_[short_ma_buffer_.size() - 2];
            double prev_long_ma = long_ma_buffer_[long_ma_buffer_.size() - 2];
            
            golden_cross = (prev_short_ma <= prev_long_ma) && (short_ma > long_ma);
            death_cross = (prev_short_ma >= prev_long_ma) && (short_ma < long_ma);
        }
        
        if (golden_cross && position_ <= 0.0) {
            // 买入信号
            std::cout << "[" << name_ << "] GOLDEN CROSS! Short MA(" << short_ma 
                      << ") > Long MA(" << long_ma << ")" << std::endl;
            
            if (position_ < 0.0) {
                // 如果有空头持仓，先平仓
                create_order(core::OrderSide::BUY, std::abs(position_));
            } else {
                // 开多头仓位
                double quantity = (cash_ * 0.2) / price;  // 使用20%资金
                create_order(core::OrderSide::BUY, quantity);
            }
        } else if (death_cross && position_ >= 0.0) {
            // 卖出信号
            std::cout << "[" << name_ << "] DEATH CROSS! Short MA(" << short_ma 
                      << ") < Long MA(" << long_ma << ")" << std::endl;
            
            if (position_ > 0.0) {
                // 如果有多头持仓，先平仓
                create_order(core::OrderSide::SELL, std::abs(position_));
            } else {
                // 开空头仓位
                double quantity = (cash_ * 0.2) / price;  // 使用20%资金
                create_order(core::OrderSide::SELL, quantity);
            }
        }
    }
    
    void create_order(core::OrderSide side, double quantity) {
        core::Order order;
        order.symbol = symbol_;
        order.side = side;
        order.type = core::OrderType::LIMIT;
        order.price = last_price_;
        order.quantity = quantity;
        
        std::cout << "[" << name_ << "] Creating order: "
                  << (side == core::OrderSide::BUY ? "BUY" : "SELL")
                  << " " << quantity << " " << symbol_
                  << " at " << last_price_ << std::endl;
        
        // 这里应该调用引擎的submit_order
        // 为了示例，我们只打印
    }
    
private:
    std::string symbol_;
    int short_period_;
    int long_period_;
    
    double position_{0.0};
    double cash_{0.0};
    double last_price_{0.0};
    
    std::vector<double> prices_;
    std::vector<double> short_ma_buffer_;
    std::vector<double> long_ma_buffer_;
};

} // namespace example
} // namespace pplustrader