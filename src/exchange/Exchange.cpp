#include "exchange/Exchange.h"
#include <iostream>
#include <random>
#include <chrono>
#include <thread>
#include <vector>

namespace pplustrader {
namespace exchange {

bool Exchange::initialize(const ExchangeConfig& config) {
    config_ = config;
    
    std::cout << "Exchange initializing, type: ";
    switch (config.type) {
        case ExchangeType::BINANCE_SPOT:
            std::cout << "BINANCE_SPOT";
            break;
        case ExchangeType::BINANCE_FUTURES:
            std::cout << "BINANCE_FUTURES";
            break;
        case ExchangeType::OKX_SPOT:
            std::cout << "OKX_SPOT";
            break;
        case ExchangeType::OKX_FUTURES:
            std::cout << "OKX_FUTURES";
            break;
        case ExchangeType::STOCK_A:
            std::cout << "STOCK_A";
            break;
        case ExchangeType::STOCK_EU:
            std::cout << "STOCK_EU";
            break;
        case ExchangeType::FOREX:
            std::cout << "FOREX";
            break;
        case ExchangeType::CRYPTO:
            std::cout << "CRYPTO";
            break;
    }
    std::cout << ", endpoint: " << config.endpoint
              << ", testnet: " << (config.testnet ? "true" : "false") << std::endl;
    
    return true;
}

bool Exchange::connect() {
    std::cout << "Exchange connecting..." << std::endl;
    
    // 模拟连接延迟
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    connected_ = true;
    std::cout << "Exchange connected" << std::endl;
    return true;
}

void Exchange::disconnect() {
    if (connected_) {
        std::cout << "Exchange disconnecting..." << std::endl;
        connected_ = false;
        std::cout << "Exchange disconnected" << std::endl;
    }
}

AccountInfo Exchange::get_account_info() {
    std::cout << "Getting account info..." << std::endl;
    
    AccountInfo info;
    
    if (config_.type == ExchangeType::BINANCE_SPOT ||
        config_.type == ExchangeType::OKX_SPOT ||
        config_.type == ExchangeType::CRYPTO) {
        
        // 模拟加密货币账户
        info.total_balance = 10000.0;
        info.available_balance = 8000.0;
        info.locked_balance = 2000.0;
        
        info.positions = {
            {"BTC", 0.5},
            {"ETH", 5.0},
            {"USDT", 5000.0}
        };
        
    } else if (config_.type == ExchangeType::STOCK_A) {
        
        // 模拟A股账户
        info.total_balance = 500000.0;
        info.available_balance = 300000.0;
        info.locked_balance = 200000.0;
        
        info.positions = {
            {"600519.SH", 100},  // 贵州茅台
            {"000858.SZ", 500},  // 五粮液
            {"601318.SH", 200}   // 中国平安
        };
        
    } else if (config_.type == ExchangeType::FOREX) {
        
        // 模拟外汇账户
        info.total_balance = 100000.0;
        info.available_balance = 100000.0;
        info.locked_balance = 0.0;
        
        info.positions = {
            {"EUR/USD", 50000.0},
            {"USD/JPY", 30000.0},
            {"GBP/USD", 20000.0}
        };
    }
    
    std::cout << "Account balance: " << info.total_balance
              << " (available: " << info.available_balance
              << ", locked: " << info.locked_balance << ")" << std::endl;
    
    return info;
}

bool Exchange::get_depth(const std::string& symbol, int limit) {
    std::cout << "Getting depth for " << symbol << " (limit: " << limit << ")..." << std::endl;
    
    // 模拟市场深度数据
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> price_dist(90.0, 110.0);
    std::uniform_real_distribution<> volume_dist(100.0, 1000.0);
    
    std::vector<std::pair<double, double>> bids;
    std::vector<std::pair<double, double>> asks;
    
    double bid_price = price_dist(gen);
    double ask_price = bid_price * 1.01;  // 卖价比买价高1%
    
    for (int i = 0; i < limit/2; i++) {
        bids.push_back({bid_price - i * 0.1, volume_dist(gen)});
        asks.push_back({ask_price + i * 0.1, volume_dist(gen)});
    }
    
    std::cout << "Market depth for " << symbol << ":" << std::endl;
    std::cout << "Bids: ";
    for (const auto& bid : bids) {
        std::cout << bid.first << "(" << bid.second << ") ";
    }
    std::cout << std::endl;
    
    std::cout << "Asks: ";
    for (const auto& ask : asks) {
        std::cout << ask.first << "(" << ask.second << ") ";
    }
    std::cout << std::endl;
    
    return true;
}

bool Exchange::get_klines(const std::string& symbol,
                         core::MarketDataType interval,
                         const std::chrono::system_clock::time_point& start_time,
                         const std::chrono::system_clock::time_point& end_time) {
    
    std::cout << "Getting klines for " << symbol 
              << ", interval: " << static_cast<int>(interval)
              << ", from " << std::chrono::system_clock::to_time_t(start_time)
              << " to " << std::chrono::system_clock::to_time_t(end_time) << std::endl;
    
    return true;
}

std::string Exchange::place_order(const core::Order& order) {
    static int order_counter = 0;
    std::string order_id = "EX_" + std::to_string(++order_counter);
    
    std::cout << "Placing order: " << order_id
              << ", Symbol: " << order.symbol
              << ", Side: " << (order.side == core::OrderSide::BUY ? "BUY" : "SELL")
              << ", Type: ";
    
    switch (order.type) {
        case core::OrderType::LIMIT:
            std::cout << "LIMIT";
            break;
        case core::OrderType::MARKET:
            std::cout << "MARKET";
            break;
        case core::OrderType::STOP:
            std::cout << "STOP";
            break;
        case core::OrderType::STOP_LIMIT:
            std::cout << "STOP_LIMIT";
            break;
    }
    
    std::cout << ", Price: " << order.price
              << ", Quantity: " << order.quantity << std::endl;
    
    // 模拟订单处理
    if (order_callback_) {
        core::Order updated_order = order;
        updated_order.order_id = order_id;
        updated_order.status = core::OrderStatus::SUBMITTED;
        updated_order.created_at = std::chrono::system_clock::now();
        
        // 稍后模拟订单成交
        std::thread([this, updated_order]() {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
            
            core::Order filled_order = updated_order;
            filled_order.status = core::OrderStatus::FILLED;
            filled_order.updated_at = std::chrono::system_clock::now();
            
            if (order_callback_) {
                order_callback_(filled_order);
            }
        }).detach();
    }
    
    return order_id;
}

bool Exchange::cancel_order(const std::string& order_id) {
    std::cout << "Cancelling order: " << order_id << std::endl;
    return true;
}

core::Order Exchange::query_order(const std::string& order_id) {
    std::cout << "Querying order: " << order_id << std::endl;
    
    core::Order order;
    order.order_id = order_id;
    order.status = core::OrderStatus::FILLED;
    order.symbol = "BTCUSDT";
    order.side = core::OrderSide::BUY;
    order.type = core::OrderType::LIMIT;
    order.price = 50000.0;
    order.quantity = 0.1;
    
    return order;
}

std::vector<core::Order> Exchange::query_orders(const std::string& symbol) {
    std::cout << "Querying orders for symbol: " << (symbol.empty() ? "ALL" : symbol) << std::endl;
    
    std::vector<core::Order> orders;
    
    // 模拟一些订单
    for (int i = 1; i <= 3; i++) {
        core::Order order;
        order.order_id = "ORDER_" + std::to_string(i);
        order.status = (i % 2 == 0) ? core::OrderStatus::FILLED : core::OrderStatus::SUBMITTED;
        order.symbol = symbol.empty() ? "BTCUSDT" : symbol;
        order.side = (i % 2 == 0) ? core::OrderSide::BUY : core::OrderSide::SELL;
        order.type = core::OrderType::LIMIT;
        order.price = 50000.0 + i * 100;
        order.quantity = 0.1 * i;
        order.created_at = std::chrono::system_clock::now() - std::chrono::hours(i);
        
        orders.push_back(order);
    }
    
    return orders;
}

// 交易所工厂实现
std::shared_ptr<Exchange> ExchangeFactory::create_exchange(ExchangeType type) {
    auto exchange = std::make_shared<Exchange>();
    
    ExchangeConfig config;
    config.type = type;
    
    switch (type) {
        case ExchangeType::BINANCE_SPOT:
            config.endpoint = "https://api.binance.com";
            break;
        case ExchangeType::BINANCE_FUTURES:
            config.endpoint = "https://fapi.binance.com";
            break;
        case ExchangeType::OKX_SPOT:
            config.endpoint = "https://www.okx.com";
            break;
        case ExchangeType::OKX_FUTURES:
            config.endpoint = "https://www.okx.com";
            break;
        case ExchangeType::STOCK_A:
            config.endpoint = "simulator://a-stock";
            break;
        case ExchangeType::STOCK_EU:
            config.endpoint = "simulator://eu-stock";
            break;
        case ExchangeType::FOREX:
            config.endpoint = "simulator://forex";
            break;
        case ExchangeType::CRYPTO:
            config.endpoint = "simulator://crypto";
            break;
    }
    
    exchange->initialize(config);
    return exchange;
}

std::shared_ptr<Exchange> ExchangeFactory::create_binance(bool futures, bool testnet) {
    ExchangeConfig config;
    config.type = futures ? ExchangeType::BINANCE_FUTURES : ExchangeType::BINANCE_SPOT;
    config.testnet = testnet;
    
    if (testnet) {
        config.endpoint = futures ? "https://testnet.binancefuture.com" : "https://testnet.binance.vision";
    } else {
        config.endpoint = futures ? "https://fapi.binance.com" : "https://api.binance.com";
    }
    
    auto exchange = std::make_shared<Exchange>();
    exchange->initialize(config);
    return exchange;
}

std::shared_ptr<Exchange> ExchangeFactory::create_okx(bool futures, bool testnet) {
    ExchangeConfig config;
    config.type = futures ? ExchangeType::OKX_FUTURES : ExchangeType::OKX_SPOT;
    config.testnet = testnet;
    
    if (testnet) {
        config.endpoint = "https://www.okx.com";
    } else {
        config.endpoint = "https://www.okx.com";
    }
    
    auto exchange = std::make_shared<Exchange>();
    exchange->initialize(config);
    return exchange;
}

std::shared_ptr<Exchange> ExchangeFactory::create_a_stock_simulator() {
    ExchangeConfig config;
    config.type = ExchangeType::STOCK_A;
    config.endpoint = "simulator://a-stock";
    config.testnet = true;
    
    auto exchange = std::make_shared<Exchange>();
    exchange->initialize(config);
    return exchange;
}

std::shared_ptr<Exchange> ExchangeFactory::create_forex_simulator() {
    ExchangeConfig config;
    config.type = ExchangeType::FOREX;
    config.endpoint = "simulator://forex";
    config.testnet = true;
    
    auto exchange = std::make_shared<Exchange>();
    exchange->initialize(config);
    return exchange;
}

} // namespace exchange
} // namespace pplustrader