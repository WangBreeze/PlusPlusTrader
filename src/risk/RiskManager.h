#ifndef PLUSPLUSTRADER_RISKMANAGER_H
#define PLUSPLUSTRADER_RISKMANAGER_H

#include "../core/Engine.h"
#include <memory>
#include <string>
#include <unordered_map>

namespace pplustrader {
namespace risk {

// 风险限制类型
enum class RiskLimitType {
    MAX_POSITION_SIZE,      // 最大持仓规模
    MAX_DAILY_LOSS,         // 最大单日亏损
    MAX_DRAWDOWN,           // 最大回撤
    STOP_LOSS,              // 止损
    TAKE_PROFIT,            // 止盈
    TRAILING_STOP,          // 移动止损
    POSITION_SIZING         // 仓位大小
};

// 风险检查结果
struct RiskCheckResult {
    bool passed = true;                 // 是否通过检查
    std::string reason;                 // 失败原因
    double suggested_quantity = 0.0;    // 建议数量（如果有限制）
};

// 风险管理器基类
class RiskManager {
public:
    virtual ~RiskManager() = default;
    
    // 检查订单风险
    virtual RiskCheckResult check_order(const core::Order& order, 
                                       const core::AccountInfo& account,
                                       const core::TickData& market) = 0;
    
    // 更新市场数据
    virtual void update_market(const core::TickData& tick) = 0;
    
    // 更新持仓信息
    virtual void update_position(const std::string& symbol, double quantity, double avg_price) = 0;
    
    // 检查账户整体风险
    virtual RiskCheckResult check_account(const core::AccountInfo& account) = 0;
    
    // 获取风险指标
    virtual double get_risk_metric(const std::string& metric) const = 0;
    
    // 重置风险状态
    virtual void reset() = 0;
    
    // 获取管理器名称
    virtual std::string name() const = 0;
};

} // namespace risk
} // namespace pplustrader

#endif // PLUSPLUSTRADER_RISKMANAGER_H