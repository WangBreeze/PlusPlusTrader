#ifndef PLUSPLUSTRADER_SIMULATEDEXCHANGE_H
#define PLUSPLUSTRADER_SIMULATEDEXCHANGE_H

#include "../core/Engine.h"
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

namespace pplustrader {
namespace backtest {

// 模拟账户
struct SimulatedAccount {
    double cash = 0.0;                  // 现金
    std::unordered_map<std::string, double> positions;  // 持仓（标的 -> 数量）
    std::unordered_map<std::string, double> avg_prices; // 持仓平均价格
    
    // 计算总资产价值（现金 + 持仓市值）
    double total_value(const std::string& symbol, double current_price) const;
    
    // 更新持仓
    void update_position(const std::string& symbol, double quantity, double price);
    
    // 获取持仓数量
    double get_position(const std::string& symbol) const;
    
    // 获取可用现金
    double get_cash() const { return cash; }
};

// 模拟交易所
class SimulatedExchange {
public:
    SimulatedExchange(double initial_capital = 100000.0,
                      double commission_rate = 0.0005,
                      double slippage = 0.0001);
    ~SimulatedExchange();
    
    // 设置当前市场数据
    void set_market_data(const core::TickData& tick);
    
    // 提交订单（返回订单ID）
    std::string submit_order(const core::Order& order);
    
    // 取消订单
    bool cancel_order(const std::string& order_id);
    
    // 获取订单状态
    core::OrderStatus get_order_status(const std::string& order_id);
    
    // 获取账户信息
    const SimulatedAccount& get_account() const;
    
    // 获取所有未平仓订单
    std::vector<core::Order> get_open_orders() const;
    
    // 撮合引擎（处理当前市场数据下的订单）
    void match_orders();
    
    // 获取当前资产总值
    double get_total_value() const;
    
    // 获取持仓
    double get_position(const std::string& symbol) const;
    
    // 获取交易记录
    struct TradeRecord {
        std::string order_id;
        std::string symbol;
        core::OrderSide side;
        double price;
        double quantity;
        double commission;
        std::chrono::system_clock::time_point timestamp;
    };
    
    const std::vector<TradeRecord>& get_trade_records() const;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace backtest
} // namespace pplustrader

#endif // PLUSPLUSTRADER_SIMULATEDEXCHANGE_H