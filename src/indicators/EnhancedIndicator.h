#ifndef PLUSPLUSTRADER_ENHANCEDINDICATOR_H
#define PLUSPLUSTRADER_ENHANCEDINDICATOR_H

#include "Indicator.h"
#include <map>
#include <vector>
#include <memory>
#include <functional>
#include <string>
#include <chrono>
#include <algorithm>

namespace pplustrader {
namespace indicators {

// 指标信号类型
enum class IndicatorSignal {
    SELL = -1,      // 卖出信号
    NEUTRAL = 0,    // 中性信号
    BUY = 1         // 买入信号
};

// 增强的指标基类，支持自定义功能
class EnhancedIndicator : public Indicator {
public:
    virtual ~EnhancedIndicator() = default;
    
    // ========== 新增功能：参数配置 ==========
    
    // 设置指标参数
    virtual void set_parameters(const std::map<std::string, double>& params) = 0;
    
    // 获取指标参数
    virtual std::map<std::string, double> get_parameters() const = 0;
    
    // 获取参数描述
    virtual std::map<std::string, std::string> get_parameter_descriptions() const = 0;
    
    // ========== 新增功能：指标信号 ==========
    
    // 获取当前信号（-1:卖出, 0:中性, 1:买入）
    virtual IndicatorSignal signal() const = 0;
    
    // 获取信号强度（0.0-1.0）
    virtual double signal_strength() const = 0;
    
    // 获取信号描述
    virtual std::string signal_description() const = 0;
    
    // ========== 新增功能：指标组合 ==========
    
    // 添加子指标
    virtual void add_child(std::shared_ptr<EnhancedIndicator> child) = 0;
    
    // 移除子指标
    virtual void remove_child(const std::string& child_name) = 0;
    
    // 获取所有子指标
    virtual std::vector<std::shared_ptr<EnhancedIndicator>> get_children() const = 0;
    
    // 获取子指标数量
    virtual size_t child_count() const = 0;
    
    // ========== 新增功能：状态管理 ==========
    
    // 获取指标状态
    virtual std::string status() const = 0;
    
    // 是否处于错误状态
    virtual bool has_error() const = 0;
    
    // 获取错误信息
    virtual std::string error_message() const = 0;
    
    // 清除错误状态
    virtual void clear_error() = 0;
    
    // ========== 新增功能：序列化 ==========
    
    // 序列化为JSON字符串
    virtual std::string to_json() const = 0;
    
    // 从JSON字符串反序列化
    virtual void from_json(const std::string& json_str) = 0;
    
    // ========== 新增功能：性能统计 ==========
    
    // 获取计算次数
    virtual size_t calculation_count() const = 0;
    
    // 获取平均计算时间（微秒）
    virtual double average_calculation_time() const = 0;
    
    // 重置性能统计
    virtual void reset_performance_stats() = 0;
};

// 指标工厂函数类型
using IndicatorCreator = std::function<std::shared_ptr<EnhancedIndicator>()>;

// 指标工厂类
class IndicatorFactory {
public:
    // 单例模式
    static IndicatorFactory& instance() {
        static IndicatorFactory factory;
        return factory;
    }
    
    // 注册指标
    void register_indicator(const std::string& name, 
                           const std::string& description,
                           IndicatorCreator creator) {
        creators_[name] = creator;
        descriptions_[name] = description;
    }
    
    // 创建指标实例
    std::shared_ptr<EnhancedIndicator> create(const std::string& name) const {
        auto it = creators_.find(name);
        if (it != creators_.end()) {
            return it->second();
        }
        return nullptr;
    }
    
    // 获取所有可用指标名称
    std::vector<std::string> available_indicators() const {
        std::vector<std::string> names;
        for (const auto& pair : creators_) {
            names.push_back(pair.first);
        }
        return names;
    }
    
    // 获取指标描述
    std::string get_description(const std::string& name) const {
        auto it = descriptions_.find(name);
        if (it != descriptions_.end()) {
            return it->second;
        }
        return "Unknown indicator";
    }
    
    // 检查指标是否存在
    bool has_indicator(const std::string& name) const {
        return creators_.find(name) != creators_.end();
    }
    
    // 清除所有注册的指标
    void clear() {
        creators_.clear();
        descriptions_.clear();
    }
    
private:
    IndicatorFactory() = default;
    ~IndicatorFactory() = default;
    
    std::map<std::string, IndicatorCreator> creators_;
    std::map<std::string, std::string> descriptions_;
};

// 指标注册辅助类
template<typename T>
class IndicatorRegistrar {
public:
    IndicatorRegistrar(const std::string& name, const std::string& description) {
        IndicatorFactory::instance().register_indicator(
            name, 
            description,
            []() -> std::shared_ptr<EnhancedIndicator> {
                return std::make_shared<T>();
            }
        );
    }
};

// 宏定义：简化指标注册
#define REGISTER_INDICATOR(ClassName, Name, Description) \
    static IndicatorRegistrar<ClassName> registrar_##ClassName(Name, Description)

// 基础增强指标实现（模板类）
template<typename BaseIndicator>
class BaseEnhancedIndicator : public EnhancedIndicator {
protected:
    std::shared_ptr<BaseIndicator> base_indicator_;
    std::map<std::string, double> parameters_;
    std::vector<std::shared_ptr<EnhancedIndicator>> children_;
    std::string error_msg_;
    size_t calc_count_ = 0;
    double total_calc_time_ = 0.0;
    
public:
    BaseEnhancedIndicator() : base_indicator_(std::make_shared<BaseIndicator>()) {}
    
    virtual ~BaseEnhancedIndicator() = default;
    
    // 基础Indicator接口实现
    void initialize() override {
        base_indicator_->initialize();
    }
    
    void update(const core::TickData& tick) override {
        auto start = std::chrono::high_resolution_clock::now();
        
        // 更新子指标
        for (auto& child : children_) {
            child->update(tick);
        }
        
        // 更新基础指标
        base_indicator_->update(tick);
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        calc_count_++;
        total_calc_time_ += duration.count();
    }
    
    std::string name() const override {
        return base_indicator_->name();
    }
    
    double value() const override {
        return base_indicator_->value();
    }
    
    std::vector<double> history(size_t n) const override {
        return base_indicator_->history(n);
    }
    
    void reset() override {
        base_indicator_->reset();
        for (auto& child : children_) {
            child->reset();
        }
        calc_count_ = 0;
        total_calc_time_ = 0.0;
        error_msg_.clear();
    }
    
    bool is_ready() const override {
        return base_indicator_->is_ready();
    }
    
    // EnhancedIndicator接口实现
    void set_parameters(const std::map<std::string, double>& params) override {
        parameters_ = params;
        // 子类可以重写此方法来应用参数
    }
    
    std::map<std::string, double> get_parameters() const override {
        return parameters_;
    }
    
    std::map<std::string, std::string> get_parameter_descriptions() const override {
        return {};  // 子类需要重写
    }
    
    IndicatorSignal signal() const override {
        // 默认实现：基于指标值变化判断信号
        if (!is_ready()) {
            return IndicatorSignal::NEUTRAL;
        }
        
        auto hist = history(3);
        if (hist.size() < 3) {
            return IndicatorSignal::NEUTRAL;
        }
        
        double current = hist.back();
        double prev = hist[hist.size() - 2];
        
        if (current > prev) {
            return IndicatorSignal::BUY;
        } else if (current < prev) {
            return IndicatorSignal::SELL;
        }
        
        return IndicatorSignal::NEUTRAL;
    }
    
    double signal_strength() const override {
        // 默认实现：基于变化幅度计算强度
        if (!is_ready()) {
            return 0.0;
        }
        
        auto hist = history(3);
        if (hist.size() < 3) {
            return 0.0;
        }
        
        double current = hist.back();
        double prev = hist[hist.size() - 2];
        double change = std::abs(current - prev);
        
        // 标准化到0-1范围（需要子类提供合适的阈值）
        return std::min(change / 10.0, 1.0);
    }
    
    std::string signal_description() const override {
        auto sig = signal();
        double strength = signal_strength();
        
        switch (sig) {
            case IndicatorSignal::BUY:
                return "买入信号 (强度: " + std::to_string(strength) + ")";
            case IndicatorSignal::SELL:
                return "卖出信号 (强度: " + std::to_string(strength) + ")";
            case IndicatorSignal::NEUTRAL:
                return "中性信号";
            default:
                return "未知信号";
        }
    }
    
    void add_child(std::shared_ptr<EnhancedIndicator> child) override {
        children_.push_back(child);
    }
    
    void remove_child(const std::string& child_name) override {
        children_.erase(
            std::remove_if(children_.begin(), children_.end(),
                [&child_name](const std::shared_ptr<EnhancedIndicator>& child) {
                    return child->name() == child_name;
                }),
            children_.end()
        );
    }
    
    std::vector<std::shared_ptr<EnhancedIndicator>> get_children() const override {
        return children_;
    }
    
    size_t child_count() const override {
        return children_.size();
    }
    
    std::string status() const override {
        if (has_error()) {
            return "错误: " + error_message();
        }
        if (is_ready()) {
            return "就绪";
        }
        return "初始化中";
    }
    
    bool has_error() const override {
        return !error_msg_.empty();
    }
    
    std::string error_message() const override {
        return error_msg_;
    }
    
    void clear_error() override {
        error_msg_.clear();
    }
    
    std::string to_json() const override {
        // 简化JSON实现
        std::string json = "{";
        json += "\"name\":\"" + name() + "\",";
        json += "\"value\":" + std::to_string(value()) + ",";
        json += "\"ready\":" + std::string(is_ready() ? "true" : "false") + ",";
        json += "\"signal\":" + std::to_string(static_cast<int>(signal())) + ",";
        json += "\"children_count\":" + std::to_string(child_count());
        json += "}";
        return json;
    }
    
    void from_json(const std::string& json_str) override {
        // 简化实现：只解析基本参数
        // 实际实现应该使用JSON库
        // 这里只是占位符实现
    }
    
    size_t calculation_count() const override {
        return calc_count_;
    }
    
    double average_calculation_time() const override {
        if (calc_count_ == 0) {
            return 0.0;
        }
        return total_calc_time_ / calc_count_;
    }
    
    void reset_performance_stats() override {
        calc_count_ = 0;
        total_calc_time_ = 0.0;
    }
    
protected:
    void set_error(const std::string& msg) {
        error_msg_ = msg;
    }
    
    std::shared_ptr<BaseIndicator> get_base_indicator() const {
        return base_indicator_;
    }
};

} // namespace indicators
} // namespace pplustrader

#endif // PLUSPLUSTRADER_ENHANCEDINDICATOR_H