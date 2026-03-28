// 简单功能测试：验证C++核心功能
#include <iostream>
#include <vector>
#include <chrono>
#include "src/indicators/MA.h"
#include "src/indicators/MACD.h"
#include "src/indicators/RSI.h"

using namespace std;
using namespace pplustrader::indicators;

// 创建TickData的辅助函数
pplustrader::core::TickData create_tick(const string& symbol, double price, int seconds_offset = 0) {
    pplustrader::core::TickData tick;
    tick.symbol = symbol;
    tick.timestamp = std::chrono::system_clock::now() + std::chrono::seconds(seconds_offset);
    tick.last_price = price;
    tick.bid_price = price - 0.01;
    tick.ask_price = price + 0.01;
    tick.bid_size = 100.0;
    tick.ask_size = 100.0;
    tick.last_size = 1000.0;
    tick.volume = 1000.0;
    tick.open_interest = 0.0;
    return tick;
}

int main() {
    cout << "==========================================" << endl;
    cout << "C++核心指标功能测试" << endl;
    cout << "==========================================" << endl;
    
    // 1. 测试简单移动平均线
    cout << "\n1. 测试简单移动平均线(SMA)..." << endl;
    SimpleMovingAverage sma(20);
    
    vector<double> test_prices = {100.0, 101.0, 102.0, 103.0, 104.0, 
                                  105.0, 106.0, 107.0, 108.0, 109.0,
                                  110.0, 111.0, 112.0, 113.0, 114.0,
                                  115.0, 116.0, 117.0, 118.0, 119.0};
    
    for (size_t i = 0; i < test_prices.size(); ++i) {
        auto tick = create_tick("TEST", test_prices[i], i);
        sma.update(tick);
        cout << "  价格 " << test_prices[i] 
             << " -> SMA: " << sma.value()
             << " (就绪: " << (sma.is_ready() ? "是" : "否") << ")" << endl;
    }
    
    // 2. 测试指数移动平均线
    cout << "\n2. 测试指数移动平均线(EMA)..." << endl;
    ExponentialMovingAverage ema(20);
    
    for (size_t i = 0; i < 10; ++i) {
        auto tick = create_tick("TEST", 120.0 + i, i + 20);
        ema.update(tick);
        cout << "  价格 " << (120.0 + i) 
             << " -> EMA: " << ema.value() << endl;
    }
    
    // 3. 测试MACD
    cout << "\n3. 测试MACD指标..." << endl;
    MACD macd(12, 26, 9);
    
    for (size_t i = 0; i < 30; ++i) {
        auto tick = create_tick("TEST", 130.0 + i * 0.5, i + 30);
        macd.update(tick);
        if (macd.is_ready()) {
            cout << "  价格 " << (130.0 + i * 0.5) 
                 << " -> MACD: " << macd.value() 
                 << ", Signal: " << macd.signal() 
                 << ", Histogram: " << macd.histogram() << endl;
        }
    }
    
    // 4. 测试RSI
    cout << "\n4. 测试RSI指标..." << endl;
    RSI rsi(14);
    
    for (size_t i = 0; i < 20; ++i) {
        auto tick = create_tick("TEST", 140.0 + (i % 3) * 0.2, i + 60);
        rsi.update(tick);
        if (rsi.is_ready()) {
            cout << "  价格 " << tick.last_price 
                 << " -> RSI: " << rsi.value() << endl;
        }
    }
    
    cout << "\n==========================================" << endl;
    cout << "测试完成" << endl;
    cout << "==========================================" << endl;
    
    return 0;
}