#ifndef PLUSPLUSTRADER_POSITIONSIZING_H
#define PLUSPLUSTRADER_POSITIONSIZING_H

#include "RiskManager.h"
#include <cmath>
#include <deque>
#include <unordered_map>

namespace pplustrader {
namespace risk {

// 仓位大小计算方法
enum class PositionSizingMethod {
    FIXED_FRACTIONAL,      // 固定分数法
    KELLY_CRITERION,       // 凯利公式
    VOLATILITY_BASED,      // 波动率基准
    EQUAL_WEIGHT,          // 等权重
    RISK_PARITY            // 风险平价
};

// 仓位管理器
class PositionSizing : public RiskManager {
public:
    PositionSizing(PositionSizingMethod method = PositionSizingMethod::FIXED_FRACTIONAL,
                   double risk_per_trade = 0.01,           // 每笔交易风险1%
                   double max_portfolio_risk = 0.20,       // 组合最大风险20%
                   double kelly_fraction = 0.5);           // 凯利分数（半凯利）
    
    RiskCheckResult check_order(const core::Order& order,
                               const core::AccountInfo& account,
                               const core::TickData& market) override;
    
    void update_market(const core::TickData& tick) override;
    
    void update_position(const std::string& symbol, double quantity, double avg_price) override;
    
    RiskCheckResult check_account(const core::AccountInfo& account) override;
    
    double get_risk_metric(const std::string& metric) const override;
    
    void reset() override;
    
    std::string name() const override { return "PositionSizing"; }
    
    // 计算建议仓位大小
    double calculate_position_size(const std::string& symbol,
                                  double entry_price,
                                  double stop_loss_price,
                                  double account_equity,
                                  double current_risk_exposure = 0.0) const;
    
    // 设置方法参数
    void set_method(PositionSizingMethod method) { method_ = method; }
    void set_risk_per_trade(double risk) { risk_per_trade_ = std::max(0.001, std::min(0.5, risk)); }
    void set_max_portfolio_risk(double risk) { max_portfolio_risk_ = std::max(0.01, std::min(1.0, risk)); }
    void set_kelly_fraction(double fraction) { kelly_fraction_ = std::max(0.1, std::min(1.0, fraction)); }
    
    // 估算波动率（基于历史数据）
    double estimate_volatility(const std::string& symbol, int period = 20) const;
    
private:
    // 固定分数法计算
    double fixed_fractional_size(double account_equity, 
                                double risk_per_trade,
                                double entry_price,
                                double stop_loss_price) const;
    
    // 凯利公式计算
    double kelly_criterion_size(double win_rate,
                               double avg_win,
                               double avg_loss,
                               double account_equity) const;
    
    // 波动率基准计算
    double volatility_based_size(double account_equity,
                                double volatility,
                                double target_volatility = 0.01) const;
    
    PositionSizingMethod method_;
    double risk_per_trade_;        // 每笔交易风险比例
    double max_portfolio_risk_;    // 组合最大风险比例
    double kelly_fraction_;        // 凯利分数
    
    // 交易统计数据（用于凯利公式）
    struct TradeStats {
        int total_trades = 0;
        int winning_trades = 0;
        double total_profit = 0.0;
        double total_loss = 0.0;
        double largest_win = 0.0;
        double largest_loss = 0.0;
        
        double win_rate() const {
            return total_trades > 0 ? static_cast<double>(winning_trades) / total_trades : 0.5;
        }
        
        double avg_win() const {
            return winning_trades > 0 ? total_profit / winning_trades : 1.0;
        }
        
        double avg_loss() const {
            int losing_trades = total_trades - winning_trades;
            return losing_trades > 0 ? total_loss / losing_trades : 1.0;
        }
        
        double profit_factor() const {
            return total_loss > 0 ? total_profit / total_loss : 1.0;
        }
    };
    
    std::unordered_map<std::string, TradeStats> symbol_stats_;
    std::unordered_map<std::string, std::deque<double>> price_returns_;
    
    double total_account_equity_ = 0.0;
    double current_risk_exposure_ = 0.0;
    double portfolio_volatility_ = 0.0;
};

} // namespace risk
} // namespace pplustrader

#endif // PLUSPLUSTRADER_POSITIONSIZING_H