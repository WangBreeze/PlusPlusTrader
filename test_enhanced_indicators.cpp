#include <iostream>
#include <memory>
#include <vector>
#include "src/indicators/EnhancedIndicator.h"
#include "src/indicators/EnhancedMA.h"
#include "src/core/TickData.h"

using namespace pplustrader;

int main() {
    std::cout << "=== 测试增强型技术指标 ===" << std::endl;
    
    // 1. 列出可用指标
    std::cout << "\n1. 列出可用指标:" << std::endl;
    indicators::list_available_indicators();
    
    // 2. 创建增强型SMA
    std::cout << "\n2. 创建增强型SMA(20):" << std::endl;
    auto sma20 = std::make_shared<indicators::EnhancedSMA>(20);
    indicators::print_indicator_info(sma20);
    
    // 3. 创建增强型EMA
    std::cout << "\n3. 创建增强型EMA(20):" << std::endl;
    auto ema20 = std::make_shared<indicators::EnhancedEMA>(20);
    indicators::print_indicator_info(ema20);
    
    // 4. 创建MA交叉策略
    std::cout << "\n4. 创建MA交叉策略(快线10, 慢线30):" << std::endl;
    auto ma_crossover = indicators::create_ma_crossover_strategy(10, 30, 0.01);
    indicators::print_indicator_info(ma_crossover);
    
    // 5. 模拟tick数据更新
    std::cout << "\n5. 模拟tick数据更新:" << std::endl;
    
    std::vector<std::shared_ptr<indicators::EnhancedIndicator>> all_indicators = {
        sma20, ema20, ma_crossover
    };
    
    // 生成模拟tick数据
    std::vector<core::TickData> ticks;
    double price = 100.0;
    for (int i = 0; i < 50; ++i) {
        core::TickData tick;
        tick.symbol = "AAPL";
        tick.timestamp = i * 1000.0;
        tick.open = price;
        tick.high = price + 1.0;
        tick.low = price - 1.0;
        tick.close = price + (i % 3 == 0 ? 0.5 : -0.3);
        tick.volume = 1000000 + i * 10000;
        
        ticks.push_back(tick);
        price = tick.close;
    }
    
    // 更新指标
    for (size_t i = 0; i < ticks.size(); ++i) {
        indicators::update_indicators(all_indicators, ticks[i]);
        
        if (i == 19 || i == 29 || i == 49) {
            std::cout << "\n更新 " << (i + 1) << " 个tick后:" << std::endl;
            std::cout << "价格: " << ticks[i].close << std::endl;
            std::cout << indicators::get_signals_summary(all_indicators) << std::endl;
        }
    }
    
    // 6. 最终结果
    std::cout << "\n6. 最终指标状态:" << std::endl;
    
    std::cout << "\nSMA(20):" << std::endl;
    indicators::print_indicator_info(sma20);
    
    std::cout << "\nEMA(20):" << std::endl;
    indicators::print_indicator_info(ema20);
    
    std::cout << "\nMA交叉策略:" << std::endl;
    indicators::print_indicator_info(ma_crossover);
    
    // 7. 测试参数修改
    std::cout << "\n7. 测试参数修改:" << std::endl;
    
    std::cout << "修改SMA周期从20到50:" << std::endl;
    sma20->set_parameters({{"period", 50.0}});
    indicators::print_indicator_info(sma20);
    
    // 8. 测试错误处理
    std::cout << "\n8. 测试错误处理:" << std::endl;
    
    // 创建无效参数
    auto invalid_sma = std::make_shared<indicators::EnhancedSMA>(-5);
    indicators::print_indicator_info(invalid_sma);
    
    // 9. 测试工厂创建
    std::cout << "\n9. 测试工厂创建:" << std::endl;
    
    auto factory_sma = indicators::IndicatorFactory::instance().create("EnhancedSMA");
    if (factory_sma) {
        factory_sma->set_parameters({{"period", 25.0}});
        indicators::print_indicator_info(factory_sma);
    }
    
    auto factory_ema = indicators::IndicatorFactory::instance().create("EnhancedEMA");
    if (factory_ema) {
        factory_ema->set_parameters({{"period", 25.0}, {"trend_threshold", 0.01}});
        indicators::print_indicator_info(factory_ema);
    }
    
    // 10. 测试JSON序列化
    std::cout << "\n10. 测试JSON序列化:" << std::endl;
    
    std::cout << "SMA JSON: " << sma20->to_json() << std::endl;
    std::cout << "EMA JSON: " << ema20->to_json() << std::endl;
    std::cout << "MA交叉策略 JSON: " << ma_crossover->to_json() << std::endl;
    
    std::cout << "\n=== 测试完成 ===" << std::endl;
    
    return 0;
}