#include "EnhancedIndicator.h"
#include "EnhancedMA.h"
#include <iostream>

namespace pplustrader {
namespace indicators {

// 全局指标工厂实例
IndicatorFactory& IndicatorFactory::instance() {
    static IndicatorFactory factory;
    return factory;
}

// 静态初始化：注册内置指标
static bool register_builtin_indicators() {
    // 注册增强型SMA
    IndicatorFactory::instance().register_indicator(
        "EnhancedSMA",
        "增强型简单移动平均线",
        []() -> std::shared_ptr<EnhancedIndicator> {
            return std::make_shared<EnhancedSMA>();
        }
    );
    
    // 注册增强型EMA
    IndicatorFactory::instance().register_indicator(
        "EnhancedEMA",
        "增强型指数移动平均线",
        []() -> std::shared_ptr<EnhancedIndicator> {
            return std::make_shared<EnhancedEMA>();
        }
    );
    
    // 注册增强型MACD（待实现）
    IndicatorFactory::instance().register_indicator(
        "EnhancedMACD",
        "增强型MACD指标",
        []() -> std::shared_ptr<EnhancedIndicator> {
            // 返回一个基础增强指标作为占位符
            auto indicator = std::make_shared<BaseEnhancedIndicator<SimpleMovingAverage>>();
            indicator->set_parameters({{"period", 12.0}});
            return indicator;
        }
    );
    
    // 注册增强型RSI（待实现）
    IndicatorFactory::instance().register_indicator(
        "EnhancedRSI",
        "增强型RSI指标",
        []() -> std::shared_ptr<EnhancedIndicator> {
            auto indicator = std::make_shared<BaseEnhancedIndicator<SimpleMovingAverage>>();
            indicator->set_parameters({{"period", 14.0}});
            return indicator;
        }
    );
    
    return true;
}

// 静态变量确保注册函数被调用
static bool registered = register_builtin_indicators();

// 工具函数：创建指标并设置参数
std::shared_ptr<EnhancedIndicator> create_indicator_with_params(
    const std::string& name, 
    const std::map<std::string, double>& params) {
    
    auto indicator = IndicatorFactory::instance().create(name);
    if (indicator) {
        indicator->set_parameters(params);
    }
    return indicator;
}

// 工具函数：创建指标组合
std::shared_ptr<EnhancedIndicator> create_indicator_combo(
    const std::string& name,
    const std::vector<std::pair<std::string, std::map<std::string, double>>>& children) {
    
    auto indicator = IndicatorFactory::instance().create(name);
    if (!indicator) {
        return nullptr;
    }
    
    for (const auto& child_spec : children) {
        auto child = create_indicator_with_params(child_spec.first, child_spec.second);
        if (child) {
            indicator->add_child(child);
        }
    }
    
    return indicator;
}

// 工具函数：打印指标信息
void print_indicator_info(const std::shared_ptr<EnhancedIndicator>& indicator) {
    if (!indicator) {
        std::cout << "指标为空" << std::endl;
        return;
    }
    
    std::cout << "=== 指标信息 ===" << std::endl;
    std::cout << "名称: " << indicator->name() << std::endl;
    std::cout << "状态: " << indicator->status() << std::endl;
    std::cout << "值: " << indicator->value() << std::endl;
    std::cout << "就绪: " << (indicator->is_ready() ? "是" : "否") << std::endl;
    
    auto signal = indicator->signal();
    std::string signal_str;
    switch (signal) {
        case IndicatorSignal::BUY: signal_str = "买入"; break;
        case IndicatorSignal::SELL: signal_str = "卖出"; break;
        case IndicatorSignal::NEUTRAL: signal_str = "中性"; break;
    }
    std::cout << "信号: " << signal_str << " (强度: " << indicator->signal_strength() << ")" << std::endl;
    std::cout << "信号描述: " << indicator->signal_description() << std::endl;
    
    auto params = indicator->get_parameters();
    if (!params.empty()) {
        std::cout << "参数:" << std::endl;
        for (const auto& param : params) {
            std::cout << "  " << param.first << ": " << param.second << std::endl;
        }
    }
    
    auto param_descs = indicator->get_parameter_descriptions();
    if (!param_descs.empty()) {
        std::cout << "参数描述:" << std::endl;
        for (const auto& desc : param_descs) {
            std::cout << "  " << desc.first << ": " << desc.second << std::endl;
        }
    }
    
    std::cout << "子指标数量: " << indicator->child_count() << std::endl;
    if (indicator->child_count() > 0) {
        std::cout << "子指标:" << std::endl;
        auto children = indicator->get_children();
        for (size_t i = 0; i < children.size(); ++i) {
            std::cout << "  [" << i << "] " << children[i]->name() 
                      << " = " << children[i]->value() << std::endl;
        }
    }
    
    std::cout << "计算次数: " << indicator->calculation_count() << std::endl;
    std::cout << "平均计算时间: " << indicator->average_calculation_time() << " μs" << std::endl;
    
    if (indicator->has_error()) {
        std::cout << "错误: " << indicator->error_message() << std::endl;
    }
    
    std::cout << "JSON: " << indicator->to_json() << std::endl;
    std::cout << "=================" << std::endl;
}

// 工具函数：列出所有可用指标
void list_available_indicators() {
    auto& factory = IndicatorFactory::instance();
    auto indicators = factory.available_indicators();
    
    std::cout << "=== 可用指标列表 ===" << std::endl;
    for (const auto& name : indicators) {
        std::cout << "- " << name << ": " << factory.get_description(name) << std::endl;
    }
    std::cout << "总计: " << indicators.size() << " 个指标" << std::endl;
    std::cout << "====================" << std::endl;
}

// 工具函数：创建MA交叉策略指标
std::shared_ptr<EnhancedIndicator> create_ma_crossover_strategy(
    int fast_period = 10,
    int slow_period = 30,
    double threshold = 0.01) {
    
    // 创建快速MA
    auto fast_ma = std::make_shared<EnhancedSMA>(fast_period);
    fast_ma->set_parameters({{"period", static_cast<double>(fast_period)}});
    
    // 创建慢速MA
    auto slow_ma = std::make_shared<EnhancedSMA>(slow_period);
    slow_ma->set_parameters({{"period", static_cast<double>(slow_period)}});
    
    // 创建策略指标（使用快速MA作为基础）
    auto strategy = std::make_shared<EnhancedSMA>(fast_period);
    strategy->set_parameters({
        {"period", static_cast<double>(fast_period)},
        {"signal_threshold", threshold}
    });
    
    // 添加子指标
    strategy->add_child(fast_ma);
    strategy->add_child(slow_ma);
    
    return strategy;
}

// 工具函数：创建EMA趋势策略指标
std::shared_ptr<EnhancedIndicator> create_ema_trend_strategy(
    int period = 20,
    double trend_threshold = 0.005) {
    
    auto ema = std::make_shared<EnhancedEMA>(period);
    ema->set_parameters({
        {"period", static_cast<double>(period)},
        {"trend_threshold", trend_threshold}
    });
    
    return ema;
}

// 工具函数：批量更新指标
void update_indicators(const std::vector<std::shared_ptr<EnhancedIndicator>>& indicators,
                      const core::TickData& tick) {
    for (auto& indicator : indicators) {
        indicator->update(tick);
    }
}

// 工具函数：获取指标信号摘要
std::string get_signals_summary(const std::vector<std::shared_ptr<EnhancedIndicator>>& indicators) {
    int buy_count = 0;
    int sell_count = 0;
    int neutral_count = 0;
    
    for (const auto& indicator : indicators) {
        if (!indicator->is_ready()) {
            continue;
        }
        
        auto signal = indicator->signal();
        switch (signal) {
            case IndicatorSignal::BUY: buy_count++; break;
            case IndicatorSignal::SELL: sell_count++; break;
            case IndicatorSignal::NEUTRAL: neutral_count++; break;
        }
    }
    
    return "信号统计: 买入=" + std::to_string(buy_count) + 
           ", 卖出=" + std::to_string(sell_count) + 
           ", 中性=" + std::to_string(neutral_count);
}

} // namespace indicators
} // namespace pplustrader