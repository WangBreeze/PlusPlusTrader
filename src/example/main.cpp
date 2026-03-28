#include "core/Engine.h"
#include "data/DataFeed.h"
#include "exchange/Exchange.h"
#include "example/SimpleStrategy.cpp"
#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <random>
#include <vector>

using namespace pplustrader;

// 模拟tick数据生成
void simulate_market_data([[maybe_unused]] core::TradingEngine& engine, const std::string& symbol, double base_price) {
    std::cout << "Starting market data simulation for " << symbol << std::endl;
    
    double price = base_price;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<> price_change(0.0, 0.5);  // 正态分布，标准差0.5
    
    for (int i = 0; i < 100; i++) {
        price += price_change(gen);
        if (price < 0) price = 1.0;  // 确保价格为正
        
        core::TickData tick;
        tick.symbol = symbol;
        tick.last_price = price;
        tick.bid_price = price - 0.1;
        tick.ask_price = price + 0.1;
        tick.bid_size = 100.0;
        tick.ask_size = 100.0;
        tick.volume = 1000.0;
        tick.timestamp = std::chrono::system_clock::now();
        
        // 这里应该通过引擎传递给策略
        // 为了示例，我们直接打印
        if (i % 10 == 0) {
            std::cout << "Tick " << i << ": " << symbol << " = " << price << std::endl;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

int main() {
    std::cout << "=== PlusPlusTrader 量化交易系统示例 ===" << std::endl;
    std::cout << std::endl;
    
    // 1. 创建交易引擎
    auto engine = std::make_unique<core::TradingEngine>();
    
    std::cout << "步骤1: 初始化交易引擎" << std::endl;
    if (!engine->initialize("config.json")) {
        std::cerr << "引擎初始化失败" << std::endl;
        return 1;
    }
    
    // 2. 创建数据源
    std::cout << "\n步骤2: 创建数据源" << std::endl;
    auto data_feed = data::DataFeedFactory::create_a_stock_feed(
        data::DataSourceType::REALTIME_API);
    
    if (!data_feed->connect()) {
        std::cerr << "数据源连接失败" << std::endl;
        return 1;
    }
    
    std::vector<std::string> symbols = {"600519.SH", "000858.SZ"};
    if (!data_feed->subscribe(symbols)) {
        std::cerr << "数据订阅失败" << std::endl;
        return 1;
    }
    
    // 3. 创建交易所连接
    std::cout << "\n步骤3: 创建交易所连接" << std::endl;
    auto exchange = exchange::ExchangeFactory::create_a_stock_simulator();
    
    if (!exchange->connect()) {
        std::cerr << "交易所连接失败" << std::endl;
        return 1;
    }
    
    // 获取账户信息
    auto account_info = exchange->get_account_info();
    std::cout << "账户总资产: " << account_info.total_balance << std::endl;
    std::cout << "可用资金: " << account_info.available_balance << std::endl;
    
    // 4. 创建策略
    std::cout << "\n步骤4: 创建交易策略" << std::endl;
    
    // 创建茅台股票的双均线策略
    std::shared_ptr<core::Strategy> strategy1 = std::make_shared<example::SimpleMovingAverageStrategy>(
        "茅台双均线策略", "600519.SH", 10, 30);
    
    // 创建五粮液股票的双均线策略
    std::shared_ptr<core::Strategy> strategy2 = std::make_shared<example::SimpleMovingAverageStrategy>(
        "五粮液双均线策略", "000858.SZ", 5, 20);
    
    // 添加策略到引擎
    engine->add_strategy(strategy1);
    engine->add_strategy(strategy2);
    
    // 5. 启动引擎
    std::cout << "\n步骤5: 启动交易引擎" << std::endl;
    engine->start();
    
    // 6. 模拟市场数据
    std::cout << "\n步骤6: 开始市场数据模拟" << std::endl;
    std::thread market_thread1([&engine]() {
        simulate_market_data(*engine, "600519.SH", 1700.0);  // 茅台
    });
    
    std::thread market_thread2([&engine]() {
        simulate_market_data(*engine, "000858.SZ", 150.0);   // 五粮液
    });
    
    // 7. 模拟交易操作
    std::cout << "\n步骤7: 模拟交易操作" << std::endl;
    
    // 等待策略初始化
    std::this_thread::sleep_for(std::chrono::seconds(1));
    
    // 提交一个测试订单
    core::Order test_order;
    test_order.symbol = "600519.SH";
    test_order.side = core::OrderSide::BUY;
    test_order.type = core::OrderType::LIMIT;
    test_order.price = 1680.0;
    test_order.quantity = 100;
    // test_order.time_in_force = core::TimeInForce::GTC; // TimeInForce not defined
    
    std::string order_id = engine->submit_order(test_order);
    std::cout << "测试订单提交: " << order_id << std::endl;
    
    // 检查订单状态
    std::this_thread::sleep_for(std::chrono::seconds(2));
    auto status = engine->get_order_status(order_id);
    std::cout << "测试订单状态: " << static_cast<int>(status) << std::endl;
    
    // 8. 运行一段时间
    std::cout << "\n步骤8: 运行交易系统 (10秒)" << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(10));
    
    // 9. 停止系统
    std::cout << "\n步骤9: 停止交易系统" << std::endl;
    
    // 取消测试订单
    if (engine->cancel_order(order_id)) {
        std::cout << "订单已取消: " << order_id << std::endl;
    }
    
    // 停止引擎
    engine->stop();
    
    // 等待市场数据线程结束
    market_thread1.join();
    market_thread2.join();
    
    // 断开连接
    data_feed->disconnect();
    exchange->disconnect();
    
    std::cout << "\n=== 交易系统运行完成 ===" << std::endl;
    std::cout << "总结:" << std::endl;
    std::cout << "1. 交易引擎已成功启动和停止" << std::endl;
    std::cout << "2. 数据源和交易所连接已建立和断开" << std::endl;
    std::cout << "3. 双均线策略已创建和初始化" << std::endl;
    std::cout << "4. 模拟了100次市场数据tick" << std::endl;
    std::cout << "5. 测试了订单提交和状态查询" << std::endl;
    
    return 0;
}