#ifndef PLUSPLUSTRADER_MA_H
#define PLUSPLUSTRADER_MA_H

#include "Indicator.h"
#include <deque>
#include <numeric>
#include <stdexcept>

namespace pplustrader {
namespace indicators {

// 移动平均线类型
enum class MAType {
    SMA,    // 简单移动平均线
    EMA,    // 指数移动平均线
    WMA     // 加权移动平均线
};

// 移动平均线基类
class MovingAverage : public Indicator {
public:
    MovingAverage(int period) : period_(period), ready_(false) {
        if (period <= 0) {
            throw std::invalid_argument("Period must be positive");
        }
    }
    
    virtual ~MovingAverage() = default;
    
    void initialize() override {
        reset();
    }
    
    void update(const core::TickData& tick) override {
        double price = get_price(tick);
        prices_.push_back(price);
        
        // 保持最多period个数据点
        if (prices_.size() > static_cast<size_t>(period_)) {
            prices_.pop_front();
        }
        
        // 计算新的移动平均值
        calculate();
        
        // 检查是否就绪
        ready_ = (prices_.size() == static_cast<size_t>(period_));
    }
    
    bool is_ready() const override {
        return ready_;
    }
    
    void reset() override {
        prices_.clear();
        current_value_ = 0.0;
        ready_ = false;
    }
    
    std::vector<double> history(size_t n) const override {
        // 简单实现：返回最近n个值（实际上我们只存储当前值）
        // 在实际实现中，需要存储历史值
        std::vector<double> result;
        if (n > 0 && ready_) {
            result.push_back(current_value_);
        }
        return result;
    }
    
    virtual std::string name() const override = 0;
    
protected:
    virtual double get_price(const core::TickData& tick) const {
        // 默认使用最后成交价
        return tick.last_price;
    }
    
    virtual void calculate() = 0;
    
    int period_;
    std::deque<double> prices_;
    double current_value_;
    bool ready_;
};

// 简单移动平均线
class SimpleMovingAverage : public MovingAverage {
public:
    SimpleMovingAverage(int period) : MovingAverage(period) {}
    
    std::string name() const override {
        return "SMA(" + std::to_string(period_) + ")";
    }
    
    double value() const override {
        return current_value_;
    }
    
protected:
    void calculate() override {
        if (prices_.empty()) {
            current_value_ = 0.0;
            return;
        }
        
        double sum = std::accumulate(prices_.begin(), prices_.end(), 0.0);
        current_value_ = sum / prices_.size();
    }
};

// 指数移动平均线
class ExponentialMovingAverage : public MovingAverage {
public:
    ExponentialMovingAverage(int period) : MovingAverage(period) {
        alpha_ = 2.0 / (period + 1.0);
    }
    
    std::string name() const override {
        return "EMA(" + std::to_string(period_) + ")";
    }
    
    double value() const override {
        return current_value_;
    }
    
    void reset() override {
        MovingAverage::reset();
        previous_ema_ = 0.0;
    }
    
protected:
    void calculate() override {
        if (prices_.empty()) {
            current_value_ = 0.0;
            return;
        }
        
        if (prices_.size() == 1) {
            // 第一个值，使用价格本身
            current_value_ = prices_.back();
            previous_ema_ = current_value_;
            return;
        }
        
        double price = prices_.back();
        if (!ready_) {
            // 数据不足period个，使用简单平均
            double sum = std::accumulate(prices_.begin(), prices_.end(), 0.0);
            current_value_ = sum / prices_.size();
            previous_ema_ = current_value_;
        } else {
            // 标准EMA计算: EMA = alpha * price + (1 - alpha) * previous_EMA
            current_value_ = alpha_ * price + (1.0 - alpha_) * previous_ema_;
            previous_ema_ = current_value_;
        }
    }
    
private:
    double alpha_;
    double previous_ema_;
};

// 兼容性别名
using MA = SimpleMovingAverage;

} // namespace indicators
} // namespace pplustrader

#endif // PLUSPLUSTRADER_MA_H