#ifndef PLUSPLUSTRADER_BACKTESTENGINE_H
#define PLUSPLUSTRADER_BACKTESTENGINE_H

#include "../core/Engine.h"
#include <vector>
#include <memory>
#include <string>
#include <chrono>

namespace pplustrader {
namespace backtest {

// 回测配置
struct BacktestConfig {
    std::string symbol;
    std::chrono::system_clock::time_point start_date;
    std::chrono::system_clock::time_point end_date;
    double initial_capital = 100000.0;  // 初始资金
    double commission_rate = 0.0005;    // 佣金费率（0.05%）
    double slippage = 0.0001;           // 滑点（0.01%）
    
    // 数据源配置
    std::string data_source;            // 数据源类型（csv, database, etc.）
    std::string data_path;              // 数据文件路径
};

// 回测结果
struct BacktestResult {
    double initial_capital = 0.0;
    double final_capital = 0.0;
    double total_return = 0.0;          // 总收益率
    double annual_return = 0.0;         // 年化收益率
    double sharpe_ratio = 0.0;          // 夏普比率
    double max_drawdown = 0.0;          // 最大回撤
    double win_rate = 0.0;              // 胜率
    double profit_factor = 0.0;         // 盈亏比
    int total_trades = 0;               // 总交易次数
    int winning_trades = 0;             // 盈利交易次数
    int losing_trades = 0;              // 亏损交易次数
    
    // 交易记录
    struct TradeRecord {
        std::chrono::system_clock::time_point entry_time;
        std::chrono::system_clock::time_point exit_time;
        double entry_price = 0.0;
        double exit_price = 0.0;
        double quantity = 0.0;
        double pnl = 0.0;               // 盈亏
        double commission = 0.0;        // 佣金
        bool is_long = true;            // 是否多头
    };
    
    std::vector<TradeRecord> trades;    // 所有交易记录
    
    // 时间序列数据
    std::vector<std::chrono::system_clock::time_point> timestamps;
    std::vector<double> portfolio_values;  // 组合价值
    std::vector<double> drawdowns;         // 回撤序列
};

// 回测引擎
class BacktestEngine {
public:
    BacktestEngine();
    ~BacktestEngine();
    
    // 设置回测配置
    void set_config(const BacktestConfig& config);
    
    // 添加策略
    void add_strategy(const std::shared_ptr<core::Strategy>& strategy);
    
    // 加载历史数据
    bool load_data();
    
    // 运行回测
    BacktestResult run();
    
    // 获取回测进度（0.0 - 1.0）
    double get_progress() const;
    
    // 停止回测（异步）
    void stop();
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace backtest
} // namespace pplustrader

#endif // PLUSPLUSTRADER_BACKTESTENGINE_H