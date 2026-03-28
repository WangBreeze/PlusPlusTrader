#ifndef PPLUSTRADER_CORE_TYPES_H
#define PPLUSTRADER_CORE_TYPES_H

#include <string>
#include <vector>

namespace pplustrader {
namespace core {

// 交易方向
enum class Side {
    BUY = 0,
    SELL = 1
};

// 订单类型
enum class OrderType {
    LIMIT = 0,      // 限价单
    MARKET = 1,     // 市价单
    STOP = 2,       // 止损单
    STOP_LIMIT = 3  // 止损限价单
};

// 订单状态
enum class OrderStatus {
    NEW = 0,                // 新建
    PARTIALLY_FILLED = 1,   // 部分成交
    FILLED = 2,             // 完全成交
    CANCELED = 3,           // 已取消
    REJECTED = 4,           // 被拒绝
    EXPIRED = 5             // 已过期
};

// Tick数据结构
struct TickData {
    std::string symbol;       // 标的代码
    double timestamp;         // 时间戳 (Unix秒，毫秒精度)
    double last_price;        // 最新价
    double volume;           // 成交量
    double amount;           // 成交额
    double bid_price;        // 买一价
    double ask_price;        // 卖一价
    int bid_volume;          // 买一量
    int ask_volume;          // 卖一量
    
    // 默认构造函数
    TickData() = default;
    
    // 带参构造函数
    TickData(const std::string& sym, double ts, double price, 
             double vol = 0.0, double amt = 0.0,
             double bid = 0.0, double ask = 0.0,
             int bid_vol = 0, int ask_vol = 0)
        : symbol(sym), timestamp(ts), last_price(price),
          volume(vol), amount(amt), bid_price(bid), ask_price(ask),
          bid_volume(bid_vol), ask_volume(ask_vol) {}
};

// BarData结构 (K线)
struct BarData {
    std::string symbol;
    double timestamp;         // K线开始时间
    double open;
    double high;
    double low;
    double close;
    double volume;
    double amount;
    int frequency;           // 频率 (秒): 60=1分钟, 300=5分钟, 900=15分钟
    
    // 默认构造函数
    BarData() = default;
    
    // 带参构造函数
    BarData(const std::string& sym, double ts, double o, double h, double l, double c,
            double vol = 0.0, double amt = 0.0, int freq = 60)
        : symbol(sym), timestamp(ts), open(o), high(h), low(l), close(c),
          volume(vol), amount(amt), frequency(freq) {}
};

// 订单结构
struct Order {
    std::string order_id;    // 订单ID
    std::string symbol;
    Side side;               // 交易方向
    OrderType order_type;    // 订单类型
    double price;            // 限价单价格
    double quantity;         // 数量
    double filled_quantity;  // 已成交数量
    OrderStatus status;      // 订单状态
    double timestamp;        // 创建时间
    double update_time;      // 最后更新时间
    
    // 默认构造函数
    Order() = default;
    
    // 带参构造函数
    Order(const std::string& id, const std::string& sym, Side sd, 
          OrderType ot, double pr, double qty, double ts)
        : order_id(id), symbol(sym), side(sd), order_type(ot),
          price(pr), quantity(qty), filled_quantity(0.0),
          status(OrderStatus::NEW), timestamp(ts), update_time(ts) {}
};

// 持仓结构
struct Position {
    std::string symbol;
    double quantity;          // 持仓数量
    double avg_price;         // 平均成本价
    double market_price;      // 市价
    double unrealized_pnl;    // 未实现盈亏
    double realized_pnl;      // 已实现盈亏
    
    // 默认构造函数
    Position() = default;
    
    // 带参构造函数
    Position(const std::string& sym, double qty = 0.0, double avg = 0.0,
             double market = 0.0)
        : symbol(sym), quantity(qty), avg_price(avg), market_price(market),
          unrealized_pnl(0.0), realized_pnl(0.0) {}
};

// 策略配置
struct StrategyConfig {
    std::string strategy_name;
    std::string strategy_class;
    std::string config_path;
    double initial_capital;
    std::vector<std::string> symbols;
    
    // 默认构造函数
    StrategyConfig() = default;
    
    // 带参构造函数
    StrategyConfig(const std::string& name, const std::string& cls,
                   const std::string& cfg_path, double capital)
        : strategy_name(name), strategy_class(cls),
          config_path(cfg_path), initial_capital(capital) {}
};

} // namespace core
} // namespace pplustrader

#endif // PPLUSTRADER_CORE_TYPES_H