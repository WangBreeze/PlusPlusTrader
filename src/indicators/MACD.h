#ifndef PLUSPLUSTRADER_MACD_H
#define PLUSPLUSTRADER_MACD_H

#include "MA.h"
#include <deque>

namespace pplustrader {
namespace indicators {

// MACD指标
class MACD : public Indicator {
public:
    MACD(int fast_period = 12, int slow_period = 26, int signal_period = 9)
        : fast_period_(fast_period),
          slow_period_(slow_period),
          signal_period_(signal_period),
          fast_ema_(fast_period),
          slow_ema_(slow_period),
          signal_ema_(signal_period),
          ready_(false) {}
    
    void initialize() override {
        reset();
    }
    
    void update(const core::TickData& tick) override {
        // 更新快慢EMA
        fast_ema_.update(tick);
        slow_ema_.update(tick);
        
        // 检查快慢EMA是否就绪
        if (!fast_ema_.is_ready() || !slow_ema_.is_ready()) {
            ready_ = false;
            return;
        }
        
        // 计算MACD值
        double fast_val = fast_ema_.value();
        double slow_val = slow_ema_.value();
        double macd_val = fast_val - slow_val;
        
        // 存储MACD值
        macd_values_.push_back(macd_val);
        
        // 保持最多signal_period个MACD值用于信号线计算
        if (macd_values_.size() > static_cast<size_t>(signal_period_)) {
            macd_values_.pop_front();
        }
        
        // 计算信号线（使用信号周期的EMA）
        // 我们需要模拟一个EMA计算，使用MACD值作为输入
        // 创建一个临时的TickData来传递MACD值
        core::TickData macd_tick;
        macd_tick.last_price = macd_val;
        signal_ema_.update(macd_tick);
        
        // 存储当前值
        current_macd_ = macd_val;
        current_signal_ = signal_ema_.value();
        current_histogram_ = current_macd_ - current_signal_;
        
        // 检查信号EMA是否就绪
        ready_ = signal_ema_.is_ready();
        
        // 存储历史值（用于history方法）
        if (ready_) {
            macd_history_.push_back(current_macd_);
            signal_history_.push_back(current_signal_);
            histogram_history_.push_back(current_histogram_);
            
            // 限制历史记录长度
            const size_t max_history = 100;
            if (macd_history_.size() > max_history) {
                macd_history_.pop_front();
                signal_history_.pop_front();
                histogram_history_.pop_front();
            }
        }
    }
    
    std::string name() const override {
        return "MACD(" + std::to_string(fast_period_) + "," + 
               std::to_string(slow_period_) + "," + 
               std::to_string(signal_period_) + ")";
    }
    
    double value() const override {
        // 返回MACD值
        return current_macd_;
    }
    
    // MACD特有方法：获取信号线和直方图
    double signal() const {
        return current_signal_;
    }
    
    double histogram() const {
        return current_histogram_;
    }
    
    std::vector<double> history(size_t n) const override {
        // 返回最近n个MACD值
        std::vector<double> result;
        size_t count = std::min(n, macd_history_.size());
        auto it = macd_history_.rbegin();
        for (size_t i = 0; i < count; ++i) {
            result.push_back(*it);
            ++it;
        }
        return result;
    }
    
    // 获取信号线历史
    std::vector<double> signal_history(size_t n) const {
        std::vector<double> result;
        size_t count = std::min(n, signal_history_.size());
        auto it = signal_history_.rbegin();
        for (size_t i = 0; i < count; ++i) {
            result.push_back(*it);
            ++it;
        }
        return result;
    }
    
    // 获取直方图历史
    std::vector<double> histogram_history(size_t n) const {
        std::vector<double> result;
        size_t count = std::min(n, histogram_history_.size());
        auto it = histogram_history_.rbegin();
        for (size_t i = 0; i < count; ++i) {
            result.push_back(*it);
            ++it;
        }
        return result;
    }
    
    void reset() override {
        fast_ema_.reset();
        slow_ema_.reset();
        signal_ema_.reset();
        macd_values_.clear();
        macd_history_.clear();
        signal_history_.clear();
        histogram_history_.clear();
        current_macd_ = 0.0;
        current_signal_ = 0.0;
        current_histogram_ = 0.0;
        ready_ = false;
    }
    
    bool is_ready() const override {
        return ready_;
    }
    
private:
    int fast_period_;
    int slow_period_;
    int signal_period_;
    ExponentialMovingAverage fast_ema_;
    ExponentialMovingAverage slow_ema_;
    ExponentialMovingAverage signal_ema_;
    
    std::deque<double> macd_values_;  // 用于信号线计算的MACD值
    std::deque<double> macd_history_;     // MACD历史值
    std::deque<double> signal_history_;   // 信号线历史值
    std::deque<double> histogram_history_; // 直方图历史值
    
    double current_macd_;
    double current_signal_;
    double current_histogram_;
    bool ready_;
};

} // namespace indicators
} // namespace pplustrader

#endif // PLUSPLUSTRADER_MACD_H