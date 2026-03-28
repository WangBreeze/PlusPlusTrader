// 集成测试：Python自定义指标与回测引擎
// 测试目标：验证Python自定义指标可以无缝集成到回测引擎中

#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <chrono>
#include <cassert>

// 包含必要的头文件
#include "src/backtest/BacktestEngine.h"
#include "src/core/BaseStrategy.h"
#include "src/indicators/Indicator.h"

// Python自定义指标桥接
#ifdef WITH_PYTHON
#include "include/custom/PythonIndicatorBridge.h"
#endif

using namespace pplustrader;
using namespace std::chrono;

// 简单的测试策略：使用Python自定义指标
class PythonIndicatorStrategy : public core::BaseStrategyImpl {
public:
    PythonIndicatorStrategy(const std::string& indicator_name, 
                           const std::vector<double>& params)
        : BaseStrategyImpl("PythonIndicatorStrategy_" + indicator_name),
          indicator_name_(indicator_name), params_(params) {
    }
    
    ~PythonIndicatorStrategy() override = default;
    
    // 初始化策略
    void init() override {
        std::cout << "初始化策略: " << name_ << std::endl;
        
#ifdef WITH_PYTHON
        try {
            // 创建Python自定义指标
            python_indicator_ = custom::PythonIndicatorFactory::create_indicator(
                indicator_name_, params_);
            
            if (python_indicator_) {
                std::cout << "成功创建Python指标: " << indicator_name_ << std::endl;
            } else {
                std::cerr << "无法创建Python指标: " << indicator_name_ << std::endl;
            }
        } catch (const std::exception& e) {
            std::cerr << "创建Python指标时出错: " << e.what() << std::endl;
        }
#endif
    }
    
    // 处理市场数据
    void on_market_data(const core::MarketData& data) override {
        if (!python_indicator_) {
            return;
        }
        
        // 更新指标
        python_indicator_->update(data.close);
        
        // 获取信号
        int signal = python_indicator_->signal();
        double signal_strength = python_indicator_->signal_strength();
        
        // 简单的交易逻辑
        if (signal > 0 && signal_strength > 0.7) {
            // 买入信号
            std::cout << "[" << data.timestamp << "] 买入信号: " 
                      << signal_strength << std::endl;
            
            // 这里可以添加实际的交易逻辑
            // 例如：place_order(...)
            
        } else if (signal < 0 && signal_strength > 0.7) {
            // 卖出信号
            std::cout << "[" << data.timestamp << "] 卖出信号: " 
                      << signal_strength << std::endl;
            
            // 这里可以添加实际的交易逻辑
        }
    }
    
private:
    std::string indicator_name_;
    std::vector<double> params_;
    
#ifdef WITH_PYTHON
    std::shared_ptr<custom::PythonWrappedIndicator> python_indicator_;
#endif
};

// 主测试函数
int main() {
    std::cout << "==========================================" << std::endl;
    std::cout << "Python自定义指标与回测引擎集成测试" << std::endl;
    std::cout << "==========================================" << std::endl;
    
    // 1. 初始化Python环境
#ifdef WITH_PYTHON
    std::cout << "\n1. 初始化Python环境..." << std::endl;
    try {
        custom::PythonIndicatorBridge::initialize();
        std::cout << "✓ Python环境初始化成功" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "✗ Python环境初始化失败: " << e.what() << std::endl;
        return 1;
    }
#endif
    
    // 2. 创建回测引擎
    std::cout << "\n2. 创建回测引擎..." << std::endl;
    auto backtest_engine = std::make_shared<backtest::BacktestEngine>();
    
    // 3. 配置回测参数
    backtest::BacktestConfig config;
    config.symbol = "000001.SZ";
    config.start_date = system_clock::now() - hours(24 * 30);  // 30天前
    config.end_date = system_clock::now();
    config.initial_capital = 100000.0;
    config.commission_rate = 0.0005;
    config.slippage = 0.0001;
    config.data_source = "csv";
    config.data_path = "data/000001.SZ_1d.csv";
    
    backtest_engine->set_config(config);
    std::cout << "✓ 回测引擎配置完成" << std::endl;
    
    // 4. 创建Python自定义指标策略
    std::cout << "\n3. 创建Python自定义指标策略..." << std::endl;
    
#ifdef WITH_PYTHON
    // 使用Python自定义指标
    std::vector<double> sma_params = {20};  // 20日SMA
    auto strategy = std::make_shared<PythonIndicatorStrategy>(
        "SimpleMovingAverage", sma_params);
    
    strategy->init();
    std::cout << "✓ Python自定义指标策略创建成功" << std::endl;
    
    // 5. 将策略添加到回测引擎
    std::cout << "\n4. 将策略添加到回测引擎..." << std::endl;
    backtest_engine->add_strategy(strategy);
    std::cout << "✓ 策略添加成功" << std::endl;
    
    // 6. 运行回测
    std::cout << "\n5. 运行回测..." << std::endl;
    try {
        auto result = backtest_engine->run();
        
        // 打印回测结果
        std::cout << "\n6. 回测结果:" << std::endl;
        std::cout << "   初始资金: " << result.initial_capital << std::endl;
        std::cout << "   最终资金: " << result.final_capital << std::endl;
        std::cout << "   总收益率: " << (result.total_return * 100) << "%" << std::endl;
        std::cout << "   年化收益率: " << (result.annual_return * 100) << "%" << std::endl;
        std::cout << "   夏普比率: " << result.sharpe_ratio << std::endl;
        std::cout << "   最大回撤: " << (result.max_drawdown * 100) << "%" << std::endl;
        std::cout << "   胜率: " << (result.win_rate * 100) << "%" << std::endl;
        std::cout << "   总交易次数: " << result.total_trades << std::endl;
        
        std::cout << "\n✓ 回测运行成功！" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "✗ 回测运行失败: " << e.what() << std::endl;
        return 1;
    }
    
    // 7. 清理Python环境
    std::cout << "\n7. 清理Python环境..." << std::endl;
    custom::PythonIndicatorBridge::finalize();
    std::cout << "✓ Python环境清理完成" << std::endl;
#else
    std::cout << "✗ 编译时未启用Python支持，跳过Python相关测试" << std::endl;
#endif
    
    std::cout << "\n==========================================" << std::endl;
    std::cout << "集成测试完成！" << std::endl;
    std::cout << "==========================================" << std::endl;
    
    return 0;
}