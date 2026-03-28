#ifndef PLUSPLUSTRADER_RSI_H
#define PLUSPLUSTRADER_RSI_H

#include "Indicator.h"
#include <deque>
#include <cmath>
#include <stdexcept>

namespace pplustrader {
namespace indicators {

// 相对强弱指标
class RSI : public Indicator {
public:
    RSI(int period = 14) : period_(period), ready_(false) {
        if (period <= 0) {
            throw std::invalid_argument("Period must be positive");
        }
    }
    
    void initialize() override {
        reset();
    }
    
    void update(const core::TickData& tick) override {
        double current_price = tick.last_price;
        
        if (!std::isnan(previous_price_)) {
            // 计算价格变化
            double change = current_price - previous_price_;
            
            // 计算涨幅和跌幅
            double gain = (change > 0) ? change : 0.0;
            double loss = (change < 0) ? -change : 0.0;
            
            // 添加到历史
            gains_.push_back(gain);
            losses_.push_back(loss);
            
            // 保持最多period个数据点
            if (gains_.size() > static_cast<size_t>(period_)) {
                gains_.pop_front();
                losses_.pop_front();
            }
            
            // 计算平均涨幅和跌幅
            if (gains_.size() == static_cast<size_t>(period_)) {
                calculate();
                ready_ = true;
            } else {
                ready_ = false;
            }
        }
        
        previous_price_ = current_price;
    }
    
    std::string name() const override {
        return "RSI(" + std::to_string(period_) + ")";
    }
    
    double value() const override {
        return current_rsi_;
    }
    
    std::vector<double> history(size_t n) const override {
        std::vector<double> result;
        size_t count = std::min(n, rsi_history_.size());
        auto it = rsi_history_.rbegin();
        for (size_t i = 0; i < count; ++i) {
            result.push_back(*it);
            ++it;
        }
        return result;
    }
    
    void reset() override {
        gains_.clear();
        losses_.clear();
        rsi_history_.clear();
        previous_price_ = std::nan("");
        current_rsi_ = 50.0;  // 中性值
        ready_ = false;
    }
    
    bool is_ready() const override {
        return ready_;
    }
    
private:
    void calculate() {
        // 计算平均涨幅和跌幅
        double avg_gain = 0.0;
        double avg_loss = 0.0;
        
        for (size_t i = 0; i < gains_.size(); ++i) {
            avg_gain += gains_[i];
            avg_loss += losses_[i];
        }
        
        avg_gain /= gains_.size();
        avg_loss /= losses_.size();
        
        // 防止除零
        if (avg_loss < 1e-10) {
            current_rsi_ = 100.0;
        } else {
            double rs = avg_gain / avg_loss;
            current_rsi_ = 100.0 - (100.0 / (1.0 + rs));
        }
        
        // 存储历史值
        rsi_history_.push_back(current_rsi_);
        
        // 限制历史记录长度
        const size_t max_history = 100;
        if (rsi_history_.size() > max_history) {
            rsi_history_.pop_front();
        }
    }
    
    int period_;
    std::deque<double> gains_;
    std::deque<double> losses_;
    std::deque<double> rsi_history_;
    double previous_price_;
    double current_rsi_;
    bool ready_;
};

} // namespace indicators
} // namespace pplustrader

#endif // PLUSPLUSTRADER_RSI_H