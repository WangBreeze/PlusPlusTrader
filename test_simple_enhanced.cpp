#include <iostream>
#include <memory>
#include "src/indicators/EnhancedIndicator.h"

// 简单的测试类
class TestEnhancedIndicator : public pplustrader::indicators::EnhancedIndicator {
private:
    std::string name_;
    double value_;
    bool ready_;
    std::map<std::string, double> params_;
    
public:
    TestEnhancedIndicator(const std::string& name = "TestIndicator") 
        : name_(name), value_(0.0), ready_(false) {}
    
    // 基础Indicator接口
    void initialize() override {
        ready_ = true;
    }
    
    void update(const pplustrader::core::TickData& tick) override {
        value_ = tick.close;
        ready_ = true;
    }
    
    std::string name() const override {
        return name_;
    }
    
    double value() const override {
        return value_;
    }
    
    std::vector<double> history(size_t n) const override {
        return std::vector<double>(n, value_);
    }
    
    void reset() override {
        value_ = 0.0;
        ready_ = false;
    }
    
    bool is_ready() const override {
        return ready_;
    }
    
    // EnhancedIndicator接口
    void set_parameters(const std::map<std::string, double>& params) override {
        params_ = params;
    }
    
    std::map<std::string, double> get_parameters() const override {
        return params_;
    }
    
    std::map<std::string, std::string> get_parameter_descriptions() const override {
        return {{"test_param", "测试参数"}};
    }
    
    pplustrader::indicators::IndicatorSignal signal() const override {
        return pplustrader::indicators::IndicatorSignal::NEUTRAL;
    }
    
    double signal_strength() const override {
        return 0.5;
    }
    
    std::string signal_description() const override {
        return "测试信号";
    }
    
    void add_child(std::shared_ptr<EnhancedIndicator> child) override {
        // 简单实现
    }
    
    void remove_child(const std::string& child_name) override {
        // 简单实现
    }
    
    std::vector<std::shared_ptr<EnhancedIndicator>> get_children() const override {
        return {};
    }
    
    size_t child_count() const override {
        return 0;
    }
    
    std::string status() const override {
        return ready_ ? "就绪" : "未就绪";
    }
    
    bool has_error() const override {
        return false;
    }
    
    std::string error_message() const override {
        return "";
    }
    
    void clear_error() override {
        // 无操作
    }
    
    std::string to_json() const override {
        return "{\"name\":\"" + name_ + "\",\"value\":" + std::to_string(value_) + "}";
    }
    
    void from_json(const std::string& json_str) override {
        // 简单实现
    }
    
    size_t calculation_count() const override {
        return 1;
    }
    
    double average_calculation_time() const override {
        return 0.0;
    }
    
    void reset_performance_stats() override {
        // 无操作
    }
};

int main() {
    std::cout << "=== 测试增强指标基类 ===" << std::endl;
    
    // 创建测试指标
    auto indicator = std::make_shared<TestEnhancedIndicator>("MyCustomIndicator");
    
    std::cout << "1. 基础信息:" << std::endl;
    std::cout << "名称: " << indicator->name() << std::endl;
    std::cout << "状态: " << indicator->status() << std::endl;
    std::cout << "就绪: " << (indicator->is_ready() ? "是" : "否") << std::endl;
    
    // 设置参数
    std::cout << "\n2. 设置参数:" << std::endl;
    indicator->set_parameters({
        {"period", 20.0},
        {"threshold", 0.01}
    });
    
    auto params = indicator->get_parameters();
    std::cout << "参数数量: " << params.size() << std::endl;
    for (const auto& p : params) {
        std::cout << "  " << p.first << " = " << p.second << std::endl;
    }
    
    // 测试信号
    std::cout << "\n3. 信号测试:" << std::endl;
    std::cout << "信号: " << indicator->signal_description() << std::endl;
    std::cout << "信号强度: " << indicator->signal_strength() << std::endl;
    
    // 测试JSON
    std::cout << "\n4. JSON序列化:" << std::endl;
    std::cout << "JSON: " << indicator->to_json() << std::endl;
    
    // 测试工厂模式
    std::cout << "\n5. 工厂模式测试:" << std::endl;
    
    // 注册测试指标
    pplustrader::indicators::IndicatorFactory::instance().register_indicator(
        "TestIndicator",
        "测试指标",
        []() -> std::shared_ptr<pplustrader::indicators::EnhancedIndicator> {
            return std::make_shared<TestEnhancedIndicator>();
        }
    );
    
    // 创建指标
    auto factory_indicator = pplustrader::indicators::IndicatorFactory::instance().create("TestIndicator");
    if (factory_indicator) {
        std::cout << "工厂创建成功: " << factory_indicator->name() << std::endl;
        
        // 设置参数
        factory_indicator->set_parameters({{"custom_param", 42.0}});
        
        auto factory_params = factory_indicator->get_parameters();
        std::cout << "工厂指标参数: ";
        for (const auto& p : factory_params) {
            std::cout << p.first << "=" << p.second << " ";
        }
        std::cout << std::endl;
    } else {
        std::cout << "工厂创建失败" << std::endl;
    }
    
    // 列出可用指标
    std::cout << "\n6. 可用指标列表:" << std::endl;
    auto indicators = pplustrader::indicators::IndicatorFactory::instance().available_indicators();
    for (const auto& name : indicators) {
        std::cout << "- " << name << std::endl;
    }
    
    std::cout << "\n=== 测试完成 ===" << std::endl;
    
    return 0;
}