#ifndef PLUSPLUSTRADER_PYTHONINDICATORBRIDGE_FIXED_H
#define PLUSPLUSTRADER_PYTHONINDICATORBRIDGE_FIXED_H

#include <string>
#include <vector>
#include <memory>
#include <map>
#include "indicators/EnhancedIndicator.h"

namespace pplustrader {
namespace custom {

// Python指标桥接类
class PythonIndicatorBridge {
public:
    // 单例模式
    static PythonIndicatorBridge& instance() {
        static PythonIndicatorBridge bridge;
        return bridge;
    }
    
    // 初始化Python环境
    bool initialize();
    
    // 清理Python环境
    void finalize();
    
    // 检查Python是否可用
    bool isAvailable() const { return pythonInitialized_; }
    
    // 创建Python指标
    std::shared_ptr<indicators::EnhancedIndicator> create_indicator(
        const std::string& name,
        const std::map<std::string, double>& params = {});
    
    // 获取可用指标列表
    std::vector<std::string> available_indicators() const;
    
    // 获取指标信息
    std::string get_indicator_info(const std::string& instanceId) const;
    
private:
    PythonIndicatorBridge() : pythonInitialized_(false) {}
    ~PythonIndicatorBridge() { finalize(); }
    
    bool pythonInitialized_;
    
    // 禁止拷贝
    PythonIndicatorBridge(const PythonIndicatorBridge&) = delete;
    PythonIndicatorBridge& operator=(const PythonIndicatorBridge&) = delete;
};

// Python包装的指标类
class PythonWrappedIndicator : public indicators::EnhancedIndicator {
public:
    PythonWrappedIndicator(PythonIndicatorBridge& bridge,
                          const std::string& instanceId,
                          const std::string& name);
    
    virtual ~PythonWrappedIndicator();
    
    // EnhancedIndicator接口实现
    virtual void initialize() override;
    virtual void update(const core::TickData& tick) override;
    virtual std::string name() const override;
    virtual double value() const override;
    virtual std::vector<double> history(size_t n) const override;
    virtual void reset() override;
    virtual bool is_ready() const override;
    
    // EnhancedIndicator新增接口
    virtual void set_parameters(const std::map<std::string, double>& params) override;
    virtual std::map<std::string, double> get_parameters() const override;
    virtual std::map<std::string, std::string> get_parameter_descriptions() const override;
    
    virtual indicators::IndicatorSignal signal() const override;
    virtual double signal_strength() const override;
    virtual std::string signal_description() const override;
    
    virtual void add_child(std::shared_ptr<EnhancedIndicator> child) override;
    virtual void remove_child(const std::string& child_name) override;
    virtual std::vector<std::shared_ptr<EnhancedIndicator>> get_children() const override;
    virtual size_t child_count() const override;
    
    virtual std::string status() const override;
    virtual bool has_error() const override;
    virtual std::string error_message() const override;
    virtual void clear_error() override;
    
    virtual std::string to_json() const override;
    virtual void from_json(const std::string& json_str) override;
    
    virtual size_t calculation_count() const override;
    virtual double average_calculation_time() const override;
    virtual void reset_performance_stats() override;
    
    // 特定功能
    std::string get_python_instance_id() const { return instanceId_; }
    bool is_python_available() const { return bridge_.isAvailable(); }
    
private:
    PythonIndicatorBridge& bridge_;
    std::string instanceId_;
    std::string name_;
    mutable std::vector<double> cachedValues_;
    mutable std::vector<indicators::IndicatorSignal> cachedSignals_;
    mutable std::map<std::string, double> cachedParams_;
    mutable std::string cachedStatus_;
    mutable bool hasError_ = false;
    mutable std::string errorMessage_;
    size_t calcCount_ = 0;
    double totalCalcTime_ = 0.0;
    
    // 从Python获取最新数据并缓存
    void refresh_cache() const;
    
    // 转换信号类型
    static indicators::IndicatorSignal signal_from_string(const std::string& signalStr);
    static std::string signal_to_string(indicators::IndicatorSignal signal);
};

// Python指标工厂类
class PythonIndicatorFactory {
public:
    // 单例模式
    static PythonIndicatorFactory& instance() {
        static PythonIndicatorFactory factory;
        return factory;
    }
    
    // 创建指标实例
    std::shared_ptr<indicators::EnhancedIndicator> create_indicator(
        const std::string& name,
        const std::map<std::string, double>& params = {}) {
        return PythonIndicatorBridge::instance().create_indicator(name, params);
    }
    
    // 获取可用指标列表
    std::vector<std::string> available_indicators() const {
        return PythonIndicatorBridge::instance().available_indicators();
    }
    
private:
    PythonIndicatorFactory() = default;
    ~PythonIndicatorFactory() = default;
};

} // namespace custom
} // namespace pplustrader

#endif // PLUSPLUSTRADER_PYTHONINDICATORBRIDGE_FIXED_H