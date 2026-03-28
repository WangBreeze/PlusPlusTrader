#ifndef PLUSPLUSTRADER_BASE_STRATEGY_H
#define PLUSPLUSTRADER_BASE_STRATEGY_H

#include "Engine.h"
#include <iostream>
#include <memory>
#include <chrono>
#include <vector>

namespace pplustrader {
namespace core {

// 基础策略实现类
class BaseStrategyImpl : public Strategy {
public:
    BaseStrategyImpl(const std::string& name) : name_(name), initialized_(false) {}
    
    virtual ~BaseStrategyImpl() = default;
    
    void initialize() override {
        if (initialized_) return;
        
        std::cout << "Strategy '" << name_ << "' initializing..." << std::endl;
        
        // 初始化指标
        // 订阅行情
        // 设置回调
        
        initialized_ = true;
        std::cout << "Strategy '" << name_ << "' initialized" << std::endl;
    }
    
    void on_tick(const TickData& tick) override {
        if (!initialized_) return;
        
        // 简单的日志输出
        std::cout << "[" << name_ << "] Tick: " << tick.symbol 
                  << " Price: " << tick.last_price
                  << " Time: " << std::chrono::system_clock::to_time_t(tick.timestamp) << std::endl;
        
        // 这里应该实现具体的交易逻辑
        // 例如：均线策略、动量策略等
    }
    
    void on_order(const Order& order) override {
        if (!initialized_) return;
        
        std::cout << "[" << name_ << "] Order update: " << order.order_id
                  << " Status: ";
        
        switch (order.status) {
            case OrderStatus::UNKNOWN:
                std::cout << "UNKNOWN";
                break;
            case OrderStatus::PENDING:
                std::cout << "PENDING";
                break;
            case OrderStatus::SUBMITTED:
                std::cout << "SUBMITTED";
                break;
            case OrderStatus::FILLED:
                std::cout << "FILLED";
                // 订单成交后的处理
                on_order_filled(order);
                break;
            case OrderStatus::PARTIALLY_FILLED:
                std::cout << "PARTIALLY_FILLED";
                break;
            case OrderStatus::CANCELLED:
                std::cout << "CANCELLED";
                break;
            case OrderStatus::REJECTED:
                std::cout << "REJECTED";
                break;
        }
        std::cout << std::endl;
    }
    
    void cleanup() override {
        if (!initialized_) return;
        
        std::cout << "Strategy '" << name_ << "' cleaning up..." << std::endl;
        
        // 清理资源
        // 取消订阅
        // 平仓
        
        initialized_ = false;
        std::cout << "Strategy '" << name_ << "' cleaned up" << std::endl;
    }
    
    virtual void on_order_filled(const Order& order) {
        // 子类可以重写这个方法
        std::cout << "[" << name_ << "] Order filled: " << order.order_id
                  << " Symbol: " << order.symbol
                  << " Side: " << (order.side == OrderSide::BUY ? "BUY" : "SELL")
                  << " Price: " << order.price
                  << " Quantity: " << order.quantity << std::endl;
    }
    
protected:
    std::string name_;
    bool initialized_;
};

} // namespace core
} // namespace pplustrader

#endif // PLUSPLUSTRADER_BASE_STRATEGY_H