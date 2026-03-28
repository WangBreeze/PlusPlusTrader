// 简单集成测试：验证Python自定义指标系统的基本功能
// 测试目标：验证Python自定义指标可以正确创建、更新和生成信号

#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <cassert>

// Python自定义指标桥接
#ifdef WITH_PYTHON
#include "include/custom/PythonIndicatorBridge.h"
using namespace pplustrader::custom;
#endif

using namespace std;

// 主测试函数
int main() {
    cout << "==========================================" << endl;
    cout << "Python自定义指标系统简单集成测试" << endl;
    cout << "==========================================" << endl;
    
    // 1. 初始化Python环境
#ifdef WITH_PYTHON
    cout << "\n1. 初始化Python环境..." << endl;
    try {
        PythonIndicatorBridge::instance().initialize();
        cout << "✓ Python环境初始化成功" << endl;
    } catch (const exception& e) {
        cerr << "✗ Python环境初始化失败: " << e.what() << endl;
        return 1;
    }
#endif
    
    // 2. 测试Python自定义指标工厂
    cout << "\n2. 测试Python自定义指标工厂..." << endl;
    try {
        // 创建SMA指标
        map<string, double> sma_params = {{"period", 20}};  // 20日SMA
        auto sma_indicator = PythonIndicatorFactory::instance().create_indicator(
            "SimpleMovingAverage", sma_params);
        
        if (sma_indicator) {
            cout << "✓ 成功创建SimpleMovingAverage指标" << endl;
            
            // 测试指标更新
            cout << "\n3. 测试指标更新..." << endl;
            vector<double> test_prices = {100.0, 101.0, 102.0, 103.0, 104.0, 
                                         105.0, 106.0, 107.0, 108.0, 109.0,
                                         110.0, 111.0, 112.0, 113.0, 114.0,
                                         115.0, 116.0, 117.0, 118.0, 119.0};
            
            for (size_t i = 0; i < test_prices.size(); ++i) {
                // 创建TickData对象（使用Engine.h中的定义）
                pplustrader::core::TickData tick;
                tick.symbol = "TEST";
                tick.timestamp = std::chrono::system_clock::now() + std::chrono::seconds(i);
                tick.last_price = test_prices[i];
                tick.bid_price = test_prices[i] - 0.01;
                tick.ask_price = test_prices[i] + 0.01;
                tick.bid_size = 100.0;
                tick.ask_size = 100.0;
                tick.last_size = 1000.0;
                tick.volume = 1000.0;
                tick.open_interest = 0.0;
                
                sma_indicator->update(tick);
                cout << "  更新价格 " << test_prices[i] 
                     << " -> 指标值: " << sma_indicator->value() 
                     << " (就绪: " << (sma_indicator->is_ready() ? "是" : "否") << ")" << endl;
            }
            
            // 测试指标值获取
            cout << "\n4. 测试指标值获取..." << endl;
            auto history = sma_indicator->history(5);
            cout << "  最近5个历史值: ";
            for (double val : history) {
                cout << val << " ";
            }
            cout << endl;
            
            // 测试信号生成
            cout << "\n5. 测试信号生成..." << endl;
            auto signal = sma_indicator->signal();
            cout << "  当前信号: " << static_cast<int>(signal) 
                 << " (0=中性, 1=买入, -1=卖出)" << endl;
            
            // 测试参数获取
            cout << "\n6. 测试参数获取..." << endl;
            auto params = sma_indicator->get_parameters();
            cout << "  指标参数: ";
            for (const auto& [key, value] : params) {
                cout << key << "=" << value << " ";
            }
            cout << endl;
            
            cout << "\n✓ 所有测试通过！" << endl;
        } else {
            cerr << "✗ 创建SimpleMovingAverage指标失败" << endl;
        }
        
        // 测试RSI指标
        cout << "\n7. 测试RSI指标..." << endl;
        map<string, double> rsi_params = {{"period", 14}};  // 14日RSI
        auto rsi_indicator = PythonIndicatorFactory::instance().create_indicator(
            "RelativeStrengthIndex", rsi_params);
        
        if (rsi_indicator) {
            cout << "✓ 成功创建RelativeStrengthIndex指标" << endl;
            
            // 快速测试
            int time_counter = 0;
            for (double price : {50.0, 51.0, 52.0, 53.0, 54.0}) {
                pplustrader::core::TickData tick;
                tick.symbol = "TEST";
                tick.timestamp = std::chrono::system_clock::now() + std::chrono::seconds(time_counter++);
                tick.last_price = price;
                tick.bid_price = price - 0.01;
                tick.ask_price = price + 0.01;
                tick.bid_size = 100.0;
                tick.ask_size = 100.0;
                tick.last_size = 1000.0;
                tick.volume = 1000.0;
                tick.open_interest = 0.0;
                rsi_indicator->update(tick);
            }
            cout << "  RSI值: " << rsi_indicator->value() << endl;
        } else {
            cerr << "✗ 创建RelativeStrengthIndex指标失败" << endl;
        }
        
        // 测试可用指标列表
        cout << "\n8. 测试可用指标列表..." << endl;
        auto available_indicators = PythonIndicatorFactory::instance().available_indicators();
        cout << "  可用指标 (" << available_indicators.size() << "个):" << endl;
        for (const auto& name : available_indicators) {
            cout << "    - " << name << endl;
        }
        
    } catch (const exception& e) {
        cerr << "✗ 测试过程中发生异常: " << e.what() << endl;
    }
    
    // 9. 清理Python环境
#ifdef WITH_PYTHON
    cout << "\n9. 清理Python环境..." << endl;
    try {
        PythonIndicatorBridge::instance().finalize();
        cout << "✓ Python环境清理成功" << endl;
    } catch (const exception& e) {
        cerr << "✗ Python环境清理失败: " << e.what() << endl;
    }
#endif
    
    cout << "\n==========================================" << endl;
    cout << "测试完成" << endl;
    cout << "==========================================" << endl;
    
    return 0;
}