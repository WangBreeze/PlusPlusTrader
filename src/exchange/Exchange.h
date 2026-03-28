#ifndef PLUSPLUSTRADER_EXCHANGE_H
#define PLUSPLUSTRADER_EXCHANGE_H

#include <memory>
#include <string>
#include <vector>
#include <functional>
#include <chrono>
#include "core/Engine.h"

namespace pplustrader {
namespace exchange {

// 交易所类型
enum class ExchangeType {
    BINANCE_SPOT,      // 币安现货
    BINANCE_FUTURES,   // 币安合约
    OKX_SPOT,          // 欧易现货
    OKX_FUTURES,       // 欧易合约
    STOCK_A,           // A股交易所
    STOCK_EU,          // 欧洲交易所
    FOREX,             // 外汇交易所
    CRYPTO             // 加密货币（通用）
};

// 账户信息
struct AccountInfo {
    double total_balance;      // 总余额
    double available_balance;  // 可用余额
    double locked_balance;     // 冻结余额
    std::vector<std::pair<std::string, double>> positions; // 持仓
    
    AccountInfo() : total_balance(0.0), available_balance(0.0), locked_balance(0.0) {}
};

// 交易所配置
struct ExchangeConfig {
    ExchangeType type;
    std::string api_key;
    std::string api_secret;
    std::string passphrase;    // 部分交易所需要
    std::string endpoint;
    bool testnet;              // 测试网络
    int rate_limit;            // 速率限制(毫秒)
    
    ExchangeConfig()
        : type(ExchangeType::BINANCE_SPOT),
          testnet(false),
          rate_limit(1000) {}
};

// 订单回调函数
using OrderCallback = std::function<void(const core::Order&)>;

// 交易所接口
class Exchange {
public:
    virtual ~Exchange() = default;
    
    // 初始化交易所
    virtual bool initialize(const ExchangeConfig& config);
    
    // 连接交易所
    virtual bool connect();
    
    // 断开连接
    virtual void disconnect();
    
    // 获取账户信息
    virtual AccountInfo get_account_info();
    
    // 获取市场深度
    virtual bool get_depth(const std::string& symbol, 
                          int limit = 20);
    
    // 获取K线数据
    virtual bool get_klines(const std::string& symbol,
                           core::MarketDataType interval,
                           const std::chrono::system_clock::time_point& start_time,
                           const std::chrono::system_clock::time_point& end_time);
    
    // 下单
    virtual std::string place_order(const core::Order& order);
    
    // 撤单
    virtual bool cancel_order(const std::string& order_id);
    
    // 查询订单
    virtual core::Order query_order(const std::string& order_id);
    
    // 查询所有订单
    virtual std::vector<core::Order> query_orders(const std::string& symbol = "");
    
    // 设置订单回调
    void set_order_callback(OrderCallback callback) {
        order_callback_ = std::move(callback);
    }
    
protected:
    OrderCallback order_callback_;
    ExchangeConfig config_;
    bool connected_ = false;
};

// 交易所工厂
class ExchangeFactory {
public:
    static std::shared_ptr<Exchange> create_exchange(ExchangeType type);
    
    // 创建币安交易所
    static std::shared_ptr<Exchange> create_binance(
        bool futures = false,
        bool testnet = false);
    
    // 创建欧易交易所
    static std::shared_ptr<Exchange> create_okx(
        bool futures = false,
        bool testnet = false);
    
    // 创建A股交易所模拟器
    static std::shared_ptr<Exchange> create_a_stock_simulator();
    
    // 创建外汇交易所模拟器
    static std::shared_ptr<Exchange> create_forex_simulator();
};

} // namespace exchange
} // namespace pplustrader

#endif // PLUSPLUSTRADER_EXCHANGE_H