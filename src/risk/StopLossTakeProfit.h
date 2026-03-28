#ifndef PLUSPLUSTRADER_STOPLOSSTAKEPROFIT_H
#define PLUSPLUSTRADER_STOPLOSSTAKEPROFIT_H

#include "RiskManager.h"
#include <unordered_map>
#include <deque>

namespace pplustrader {
namespace risk {

// 止损止盈类型
enum class SLTPType {
    FIXED,           // 固定价格
    PERCENTAGE,      // 百分比
    TRAILING,        // 移动止损
    ATR_BASED        // ATR基准
};

// 止损止盈管理器
class StopLossTakeProfit : public RiskManager {
public:
    struct PositionRisk {
        std::string symbol;
        double entry_price = 0.0;
        double quantity = 0.0;
        double stop_loss_price = 0.0;
        double take_profit_price = 0.0;
        double trailing_stop_price = 0.0;
        double highest_price = 0.0;      // 用于移动止损的最高价
        double lowest_price = 0.0;       // 用于移动止损的最低价
        SLTPType sl_type = SLTPType::PERCENTAGE;
        SLTPType tp_type = SLTPType::PERCENTAGE;
        double sl_value = 0.02;          // 默认2%止损
        double tp_value = 0.04;          // 默认4%止盈
        double trailing_distance = 0.01; // 移动止损距离（1%）
    };
    
    StopLossTakeProfit(double default_stop_loss = 0.02,  // 2%
                       double default_take_profit = 0.04, // 4%
                       double max_position_risk = 0.02);  // 单笔最大风险2%
    
    RiskCheckResult check_order(const core::Order& order,
                               const core::AccountInfo& account,
                               const core::TickData& market) override;
    
    void update_market(const core::TickData& tick) override;
    
    void update_position(const std::string& symbol, double quantity, double avg_price) override;
    
    RiskCheckResult check_account(const core::AccountInfo& account) override;
    
    double get_risk_metric(const std::string& metric) const override;
    
    void reset() override;
    
    std::string name() const override { return "StopLossTakeProfit"; }
    
    // 检查是否有止损/止盈信号
    bool check_stop_loss(const std::string& symbol, double current_price, 
                        double& stop_price, std::string& reason);
    
    bool check_take_profit(const std::string& symbol, double current_price,
                          double& take_price, std::string& reason);
    
    // 设置特定标的的止损止盈
    void set_position_risk(const std::string& symbol, 
                          double stop_loss, 
                          double take_profit,
                          SLTPType sl_type = SLTPType::PERCENTAGE,
                          SLTPType tp_type = SLTPType::PERCENTAGE);
    
    // 设置移动止损
    void set_trailing_stop(const std::string& symbol, double distance);
    
private:
    // 计算止损价格
    double calculate_stop_loss(double entry_price, double quantity, 
                              SLTPType type, double value, 
                              const core::TickData* market = nullptr) const;
    
    // 计算止盈价格
    double calculate_take_profit(double entry_price, double quantity,
                                SLTPType type, double value,
                                const core::TickData* market = nullptr) const;
    
    // 更新移动止损
    void update_trailing_stop(const std::string& symbol, double current_price);
    
    std::unordered_map<std::string, PositionRisk> positions_;
    std::unordered_map<std::string, std::deque<double>> price_history_;
    
    double default_stop_loss_;
    double default_take_profit_;
    double max_position_risk_;
    
    // 风险指标
    double total_risk_exposure_ = 0.0;
    double max_drawdown_ = 0.0;
    double current_drawdown_ = 0.0;
    double peak_equity_ = 0.0;
};

} // namespace risk
} // namespace pplustrader

#endif // PLUSPLUSTRADER_STOPLOSSTAKEPROFIT_H