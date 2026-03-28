#ifndef PLUSPLUSTRADER_ENGINE_H
#define PLUSPLUSTRADER_ENGINE_H

#include <memory>
#include <string>
#include <vector>
#include <chrono>

namespace pplustrader {
namespace core {

// 市场数据类型
enum class MarketDataType {
    TICK,
    BAR_1S,
    BAR_1M,
    BAR_5M,
    BAR_15M,
    BAR_1H,
    BAR_4H,
    BAR_1D
};

// Tick数据结构
struct TickData {
    std::string symbol;
    std::chrono::system_clock::time_point timestamp;
    double bid_price;
    double ask_price;
    double bid_size;
    double ask_size;
    double last_price;
    double last_size;
    double volume;
    double open_interest;
    
    TickData() 
        : bid_price(0.0), ask_price(0.0), bid_size(0.0), ask_size(0.0),
          last_price(0.0), last_size(0.0), volume(0.0), open_interest(0.0) {}
};

// 订单类型
enum class OrderType {
    MARKET,
    LIMIT,
    STOP,
    STOP_LIMIT
};

// 订单方向
enum class OrderSide {
    BUY,
    SELL
};

// 订单状态
enum class OrderStatus {
    UNKNOWN,
    PENDING,
    SUBMITTED,
    FILLED,
    PARTIALLY_FILLED,
    CANCELLED,
    REJECTED
};

// 订单结构
struct Order {
    std::string order_id;
    std::string symbol;
    OrderType type;
    OrderSide side;
    double price;
    double quantity;
    OrderStatus status;
    std::chrono::system_clock::time_point created_at;
    std::chrono::system_clock::time_point updated_at;
    
    Order()
        : price(0.0), quantity(0.0), status(OrderStatus::PENDING) {}
};

// 账户信息
struct AccountInfo {
    std::string account_id;
    double equity;
    double margin;
    double free_margin;
    double margin_level;
    double realized_pnl;
    double unrealized_pnl;
    std::vector<Order> open_orders;
    std::vector<Order> position_orders;
    
    AccountInfo()
        : equity(0.0), margin(0.0), free_margin(0.0), margin_level(0.0),
          realized_pnl(0.0), unrealized_pnl(0.0) {}
};

// 策略接口
class Strategy {
public:
    virtual ~Strategy() = default;
    
    // 初始化
    virtual void initialize() = 0;
    
    // 处理Tick数据
    virtual void on_tick(const TickData& tick) = 0;
    
    // 处理订单事件
    virtual void on_order(const Order& order) = 0;
    
    // 清理
    virtual void cleanup() = 0;
};

// 交易引擎
class TradingEngine {
public:
    TradingEngine();
    ~TradingEngine();
    
    // 初始化引擎
    bool initialize(const std::string& config_path);
    
    // 启动引擎
    void start();
    
    // 停止引擎
    void stop();
    
    // 添加策略
    void add_strategy(const std::shared_ptr<Strategy>& strategy);
    
    // 提交订单
    std::string submit_order(const Order& order);
    
    // 取消订单
    bool cancel_order(const std::string& order_id);
    
    // 获取订单状态
    OrderStatus get_order_status(const std::string& order_id);
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace core
} // namespace pplustrader

#endif // PLUSPLUSTRADER_ENGINE_H