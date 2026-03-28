// test_backtest.cpp - 回测引擎测试程序
#include "src/core/Engine.h"
#include "src/strategies/MACrossStrategy.h"
#include "src/backtest/BacktestEngine.h"
#include <iostream>
#include <fstream>
#include <random>
#include <chrono>

// 生成模拟价格数据
void generate_test_data(const std::string& filename, int num_points = 1000) {
    std::ofstream file(filename);
    file << "timestamp,open,high,low,close,volume\n";
    
    std::default_random_engine generator;
    std::normal_distribution<double> returns(0.0001, 0.01);  // 日收益率
    double price = 100.0;
    
    auto start_time = std::chrono::system_clock::now();
    
    for (int i = 0; i < num_points; ++i) {
        // 生成价格
        double ret = returns(generator);
        price *= (1.0 + ret);
        
        // 生成OHLC数据（简化：假设价格变化很小）
        double open = price;
        double close = price * (1.0 + returns(generator) * 0.1);
        double high = std::max(open, close) * (1.0 + std::abs(returns(generator)) * 0.05);
        double low = std::min(open, close) * (1.0 - std::abs(returns(generator)) * 0.05);
        double volume = 1000000.0 * (1.0 + returns(generator));
        
        // 时间戳（每天一个点）
        auto timestamp = start_time + std::chrono::hours(24 * i);
        std::time_t tt = std::chrono::system_clock::to_time_t(timestamp);
        std::tm* tm = std::gmtime(&tt);
        char time_str[100];
        std::strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", tm);
        
        file << time_str << ","
             << open << "," << high << "," << low << "," << close << ","
             << volume << "\n";
    }
    
    file.close();
    std::cout << "生成测试数据: " << filename << " (" << num_points << " 条记录)" << std::endl;
}

int main() {
    std::cout << "=== PlusPlusTrader 回测引擎测试 ===\n" << std::endl;
    
    // 生成测试数据
    const std::string data_file = "test_data.csv";
    generate_test_data(data_file, 500);
    
    try {
        // 创建回测引擎
        pplustrader::backtest::BacktestEngine backtest;
        
        // 配置回测
        pplustrader::backtest::BacktestConfig config;
        config.symbol = "TEST";
        config.start_date = std::chrono::system_clock::now() - std::chrono::hours(24 * 365);
        config.end_date = std::chrono::system_clock::now();
        config.initial_capital = 100000.0;
        config.commission_rate = 0.0005;  // 0.05%
        config.slippage = 0.0001;         // 0.01%
        config.data_source = "csv";
        config.data_path = data_file;
        
        backtest.set_config(config);
        
        // 添加策略
        auto strategy = std::make_shared<pplustrader::strategies::MACrossStrategy>(5, 20);
        backtest.add_strategy(strategy);
        
        std::cout << "开始运行回测..." << std::endl;
        
        // 运行回测
        auto result = backtest.run();
        
        std::cout << "\n=== 回测结果 ===\n" << std::endl;
        std::cout << "初始资金: " << result.initial_capital << std::endl;
        std::cout << "最终资金: " << result.final_capital << std::endl;
        std::cout << "总收益率: " << (result.total_return * 100.0) << "%" << std::endl;
        std::cout << "最大回撤: " << (result.max_drawdown * 100.0) << "%" << std::endl;
        std::cout << "总交易次数: " << result.total_trades << std::endl;
        std::cout << "盈利交易次数: " << result.winning_trades << std::endl;
        std::cout << "亏损交易次数: " << result.losing_trades << std::endl;
        std::cout << "胜率: " << (result.win_rate * 100.0) << "%" << std::endl;
        std::cout << "盈亏比: " << result.profit_factor << std::endl;
        
        if (!result.trades.empty()) {
            std::cout << "\n=== 最近5笔交易 ===" << std::endl;
            int count = std::min(5, static_cast<int>(result.trades.size()));
            for (int i = 0; i < count; ++i) {
                const auto& trade = result.trades[result.trades.size() - 1 - i];
                std::cout << "交易 " << (i + 1) << ": "
                          << (trade.is_long ? "多头" : "空头") << " "
                          << trade.quantity << " 手 @ "
                          << trade.entry_price << " -> "
                          << trade.exit_price << " P&L: "
                          << trade.pnl << std::endl;
            }
        }
        
        // 生成简单图表（文本）
        if (!result.portfolio_values.empty()) {
            std::cout << "\n=== 组合价值曲线 ===" << std::endl;
            size_t step = result.portfolio_values.size() / 20;
            if (step == 0) step = 1;
            
            for (size_t i = 0; i < result.portfolio_values.size(); i += step) {
                double value = result.portfolio_values[i];
                int bar_length = static_cast<int>((value / result.initial_capital - 1.0) * 100.0) + 50;
                bar_length = std::max(0, std::min(100, bar_length));
                
                std::cout << "[" << std::string(bar_length, '=') << ">] "
                          << value << std::endl;
            }
        }
        
        // 删除测试文件
        std::remove(data_file.c_str());
        
    } catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
        return 1;
    }
    
    std::cout << "\n测试完成!" << std::endl;
    return 0;
}