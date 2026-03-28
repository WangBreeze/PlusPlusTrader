#ifndef PLUSPLUSTRADER_ENHANCEDMA_H
#define PLUSPLUSTRADER_ENHANCEDMA_H

#include "EnhancedIndicator.h"
#include "MA.h"
#include <chrono>

namespace pplustrader {
namespace indicators {

// 增强的移动平均线类
class EnhancedSMA : public BaseEnhancedIndicator<SimpleMovingAverage> {
public:
    EnhancedSMA(int period = 20) {
        parameters_["period"] = static_cast<double>(period);
        parameters_["price_type"] = 0.0;  // 0:close, 1:open, 2:high, 3:low, 4:volume
        parameters_["signal_threshold"] = 0.01;  // 信号阈值
        base_indicator_ = std::make_shared<SimpleMovingAverage>(period);
    }
    
    std::string name() const override {
        return "EnhancedSMA(" + std::to_string(static_cast<int>(parameters_.at("period"))) + ")";
    }
    
    std::map<std::string, std::string> get_parameter_descriptions() const override {
        return {
            {"period", "移动平均周期 (正整数)"},
            {"price_type", "价格类型: 0=收盘价, 1=开盘价, 2=最高价, 3=最低价, 4=成交量"},
            {"signal_threshold", "信号阈值 (百分比变化)"}
        };
    }
    
    void set_parameters(const std::map<std::string, double>& params) override {
        BaseEnhancedIndicator::set_parameters(params);
        
        // 应用参数到基础指标
        auto period_it = params.find("period");
        if (period_it != params.end() && period_it->second > 0) {
            int new_period = static_cast<int>(period_it->second);
            if (new_period != static_cast<int>(parameters_["period"])) {
                // 周期改变，重新创建基础指标
                base_indicator_ = std::make_shared<SimpleMovingAverage>(new_period);
                reset();
            }
        }
    }
    
    IndicatorSignal signal() const override {
        if (!is_ready() || child_count() == 0) {
            // 如果没有子指标，使用默认信号逻辑
            return BaseEnhancedIndicator::signal();
        }
        
        // 如果有子指标，可以基于子指标组合生成信号
        // 这里实现一个简单的多MA交叉信号
        
        // 获取所有子指标的值
        std::vector<double> child_values;
        for (const auto& child : children_) {
            if (child->is_ready()) {
                child_values.push_back(child->value());
            }
        }
        
        if (child_values.size() < 2) {
            return BaseEnhancedIndicator::signal();
        }
        
        // 检查MA交叉
        double fast_ma = child_values[0];  // 假设第一个是快速MA
        double slow_ma = child_values[1];  // 假设第二个是慢速MA
        
        double threshold = parameters_.at("signal_threshold");
        
        if (fast_ma > slow_ma * (1.0 + threshold)) {
            return IndicatorSignal::BUY;
        } else if (fast_ma < slow_ma * (1.0 - threshold)) {
            return IndicatorSignal::SELL;
        }
        
        return IndicatorSignal::NEUTRAL;
    }
    
    double signal_strength() const override {
        if (!is_ready() || child_count() < 2) {
            return BaseEnhancedIndicator::signal_strength();
        }
        
        // 基于MA交叉的强度计算
        auto child_values = get_children_values();
        if (child_values.size() < 2) {
            return 0.0;
        }
        
        double fast_ma = child_values[0];
        double slow_ma = child_values[1];
        double diff = std::abs(fast_ma - slow_ma);
        double avg = (fast_ma + slow_ma) / 2.0;
        
        if (avg == 0.0) {
            return 0.0;
        }
        
        double strength = diff / avg;
        return std::min(strength * 10.0, 1.0);  // 标准化到0-1
    }
    
    std::string signal_description() const override {
        auto sig = signal();
        double strength = signal_strength();
        
        std::string desc = BaseEnhancedIndicator::signal_description();
        
        if (child_count() >= 2) {
            auto child_values = get_children_values();
            if (child_values.size() >= 2) {
                desc += " [MA交叉: " + std::to_string(child_values[0]) + " vs " + 
                        std::to_string(child_values[1]) + "]";
            }
        }
        
        return desc;
    }
    
    std::string to_json() const override {
        std::string json = BaseEnhancedIndicator::to_json();
        
        // 移除最后的}
        json.pop_back();
        
        // 添加MA特定信息
        json += ",\"ma_type\":\"SMA\"";
        json += ",\"period\":" + std::to_string(static_cast<int>(parameters_.at("period")));
        json += ",\"children\":" + std::to_string(child_count());
        
        // 添加子指标信息
        if (child_count() > 0) {
            json += ",\"child_values\":[";
            auto child_values = get_children_values();
            for (size_t i = 0; i < child_values.size(); ++i) {
                if (i > 0) json += ",";
                json += std::to_string(child_values[i]);
            }
            json += "]";
        }
        
        json += "}";
        return json;
    }
    
private:
    std::vector<double> get_children_values() const {
        std::vector<double> values;
        for (const auto& child : children_) {
            if (child->is_ready()) {
                values.push_back(child->value());
            }
        }
        return values;
    }
};

// 增强的指数移动平均线
class EnhancedEMA : public BaseEnhancedIndicator<ExponentialMovingAverage> {
public:
    EnhancedEMA(int period = 20) {
        parameters_["period"] = static_cast<double>(period);
        parameters_["smoothing_factor"] = 2.0;  // EMA平滑因子
        parameters_["trend_threshold"] = 0.005;  // 趋势阈值
        base_indicator_ = std::make_shared<ExponentialMovingAverage>(period);
    }
    
    std::string name() const override {
        return "EnhancedEMA(" + std::to_string(static_cast<int>(parameters_.at("period"))) + ")";
    }
    
    std::map<std::string, std::string> get_parameter_descriptions() const override {
        return {
            {"period", "EMA周期 (正整数)"},
            {"smoothing_factor", "平滑因子 (通常为2.0)"},
            {"trend_threshold", "趋势检测阈值"}
        };
    }
    
    void set_parameters(const std::map<std::string, double>& params) override {
        BaseEnhancedIndicator::set_parameters(params);
        
        auto period_it = params.find("period");
        if (period_it != params.end() && period_it->second > 0) {
            int new_period = static_cast<int>(period_it->second);
            if (new_period != static_cast<int>(parameters_["period"])) {
                base_indicator_ = std::make_shared<ExponentialMovingAverage>(new_period);
                reset();
            }
        }
    }
    
    IndicatorSignal signal() const override {
        if (!is_ready()) {
            return IndicatorSignal::NEUTRAL;
        }
        
        // EMA特有的信号逻辑：基于趋势和加速度
        auto hist = history(5);
        if (hist.size() < 3) {
            return BaseEnhancedIndicator::signal();
        }
        
        double current = hist.back();
        double prev1 = hist[hist.size() - 2];
        double prev2 = hist[hist.size() - 3];
        
        // 计算趋势和加速度
        double trend = current - prev1;
        double acceleration = (current - prev1) - (prev1 - prev2);
        
        double threshold = parameters_.at("trend_threshold");
        
        // 趋势向上且加速
        if (trend > threshold && acceleration > 0) {
            return IndicatorSignal::BUY;
        }
        // 趋势向下且加速
        else if (trend < -threshold && acceleration < 0) {
            return IndicatorSignal::SELL;
        }
        
        return IndicatorSignal::NEUTRAL;
    }
    
    double signal_strength() const override {
        if (!is_ready()) {
            return 0.0;
        }
        
        auto hist = history(5);
        if (hist.size() < 3) {
            return BaseEnhancedIndicator::signal_strength();
        }
        
        double current = hist.back();
        double prev1 = hist[hist.size() - 2];
        double prev2 = hist[hist.size() - 3];
        
        double trend = std::abs(current - prev1);
        double acceleration = std::abs((current - prev1) - (prev1 - prev2));
        
        // 结合趋势和加速度计算强度
        double avg_price = (current + prev1 + prev2) / 3.0;
        if (avg_price == 0.0) {
            return 0.0;
        }
        
        double strength = (trend + acceleration * 0.5) / avg_price;
        return std::min(strength * 20.0, 1.0);
    }
    
    std::string signal_description() const override {
        auto sig = signal();
        double strength = signal_strength();
        
        std::string desc = BaseEnhancedIndicator::signal_description();
        
        if (is_ready()) {
            auto hist = history(3);
            if (hist.size() >= 3) {
                double trend = hist.back() - hist[hist.size() - 2];
                desc += " [趋势: " + std::to_string(trend) + "]";
            }
        }
        
        return desc;
    }
    
    std::string to_json() const override {
        std::string json = BaseEnhancedIndicator::to_json();
        
        json.pop_back();
        json += ",\"ma_type\":\"EMA\"";
        json += ",\"period\":" + std::to_string(static_cast<int>(parameters_.at("period")));
        json += ",\"smoothing_factor\":" + std::to_string(parameters_.at("smoothing_factor"));
        
        if (is_ready()) {
            auto hist = history(3);
            if (hist.size() >= 3) {
                json += ",\"trend\":" + std::to_string(hist.back() - hist[hist.size() - 2]);
            }
        }
        
        json += "}";
        return json;
    }
};

// 注册宏
REGISTER_INDICATOR(EnhancedSMA, "EnhancedSMA", "增强型简单移动平均线");
REGISTER_INDICATOR(EnhancedEMA, "EnhancedEMA", "增强型指数移动平均线");

} // namespace indicators
} // namespace pplustrader

#endif // PLUSPLUSTRADER_ENHANCEDMA_H