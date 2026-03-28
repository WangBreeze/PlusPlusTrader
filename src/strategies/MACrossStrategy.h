#ifndef PLUSPLUSTRADER_MACROSSSTRATEGY_H
#define PLUSPLUSTRADER_MACROSSSTRATEGY_H

#include "../core/Engine.h"
#include "../indicators/MA.h"
#include <memory>
#include <iostream>

namespace pplustrader {
namespace strategies {

// 移动平均线交叉策略
class MACrossStrategy : public core::Strategy {
public:
    MACrossStrategy(int fast_period = 5, int slow_period = 20)
        : fast_ma_(fast_period),
          slow_ma_(slow_period),
          position_(0.0),
          last_cross_(CrossType::NONE) {}
    
    void initialize() override {
        fast_ma_.initialize();
        slow_ma_.initialize();
    }
    
    void on_tick(const core::TickData& tick) override {
        // 更新指标
        fast_ma_.update(tick);
        slow_ma_.update(tick);
        
        // 检查是否就绪
        if (!fast_ma_.is_ready() || !slow_ma_.is_ready()) {
            return;
        }
        
        // 检测交叉信号
        CrossType cross = detect_cross();
        
        // 根据交叉信号交易
        if (cross != last_cross_) {
            handle_cross_signal(cross, tick);
            last_cross_ = cross;
        }
    }
    
    void cleanup() override {
        // 平仓所有持仓
        if (std::abs(position_) > 1e-10) {
            core::Order order;
            order.symbol = last_symbol_;
            order.side = (position_ > 0) ? core::OrderSide::SELL : core::OrderSide::BUY;
            order.quantity = std::abs(position_);
            order.type = core::OrderType::MARKET;
            
            engine_->submit_order(order);
        }
    }
    
    // 处理订单事件
    void on_order(const core::Order& order) override {
        // 简单实现：记录订单状态变化
        std::cout << "订单更新: " << order.order_id << " 状态: " 
                  << static_cast<int>(order.status) << std::endl;
    }
    
    // 设置引擎
    void set_engine(core::TradingEngine* engine) {
        engine_ = engine;
    }
    
private:
    enum class CrossType {
        NONE,
        GOLDEN_CROSS,    // 金叉：快线上穿慢线
        DEAD_CROSS       // 死叉：快线下穿慢线
    };
    
    CrossType detect_cross() {
        double fast_value = fast_ma_.value();
        double slow_value = slow_ma_.value();
        
        // 获取历史值判断趋势
        if (fast_history_.empty()) {
            fast_history_.push_back(fast_value);
            slow_history_.push_back(slow_value);
            return CrossType::NONE;
        }
        
        double prev_fast = fast_history_.back();
        double prev_slow = slow_history_.back();
        
        // 更新历史值
        fast_history_.push_back(fast_value);
        slow_history_.push_back(slow_value);
        
        // 限制历史记录长度
        const size_t max_history = 10;
        if (fast_history_.size() > max_history) {
            fast_history_.pop_front();
            slow_history_.pop_front();
        }
        
        // 检测交叉
        if (prev_fast <= prev_slow && fast_value > slow_value) {
            return CrossType::GOLDEN_CROSS;
        } else if (prev_fast >= prev_slow && fast_value < slow_value) {
            return CrossType::DEAD_CROSS;
        }
        
        return CrossType::NONE;
    }
    
    void handle_cross_signal(CrossType cross, const core::TickData& tick) {
        if (!engine_) {
            return;
        }
        
        last_symbol_ = tick.symbol;
        
        switch (cross) {
            case CrossType::GOLDEN_CROSS:
                // 金叉：买入
                if (position_ <= 0) {
                    // 平空头仓位（如果有）
                    if (position_ < 0) {
                        core::Order close_order;
                        close_order.symbol = tick.symbol;
                        close_order.side = core::OrderSide::BUY;
                        close_order.quantity = std::abs(position_);
                        close_order.type = core::OrderType::MARKET;
                        engine_->submit_order(close_order);
                    }
                    
                    // 开多头仓位
                    core::Order buy_order;
                    buy_order.symbol = tick.symbol;
                    buy_order.side = core::OrderSide::BUY;
                    buy_order.quantity = 1.0;  // 固定数量（简化）
                    buy_order.type = core::OrderType::MARKET;
                    engine_->submit_order(buy_order);
                    
                    position_ = 1.0;
                }
                break;
                
            case CrossType::DEAD_CROSS:
                // 死叉：卖出
                if (position_ >= 0) {
                    // 平多头仓位（如果有）
                    if (position_ > 0) {
                        core::Order close_order;
                        close_order.symbol = tick.symbol;
                        close_order.side = core::OrderSide::SELL;
                        close_order.quantity = position_;
                        close_order.type = core::OrderType::MARKET;
                        engine_->submit_order(close_order);
                    }
                    
                    // 开空头仓位
                    core::Order sell_order;
                    sell_order.symbol = tick.symbol;
                    sell_order.side = core::OrderSide::SELL;
                    sell_order.quantity = 1.0;  // 固定数量（简化）
                    sell_order.type = core::OrderType::MARKET;
                    engine_->submit_order(sell_order);
                    
                    position_ = -1.0;
                }
                break;
                
            case CrossType::NONE:
                // 无操作
                break;
        }
    }
    
    indicators::SimpleMovingAverage fast_ma_;
    indicators::SimpleMovingAverage slow_ma_;
    
    std::deque<double> fast_history_;
    std::deque<double> slow_history_;
    
    core::TradingEngine* engine_ = nullptr;
    std::string last_symbol_;
    double position_;  // 当前持仓数量（正数：多头，负数：空头）
    CrossType last_cross_;
};

} // namespace strategies
} // namespace pplustrader

#endif // PLUSPLUSTRADER_MACROSSSTRATEGY_H