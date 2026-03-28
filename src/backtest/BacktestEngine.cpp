// BacktestEngine.cpp - 回测引擎实现
#include "BacktestEngine.h"
#include "SimulatedExchange.h"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <random>

namespace pplustrader {
namespace backtest {

// 前向声明
class BacktestEngine::Impl {
public:
    Impl() : progress_(0.0), is_running_(false) {}
    
    ~Impl() {
        stop();
    }
    
    void set_config(const BacktestConfig& config) {
        config_ = config;
    }
    
    void add_strategy(const std::shared_ptr<core::Strategy>& strategy) {
        strategies_.push_back(strategy);
    }
    
    bool load_data() {
        // 简单实现：从CSV文件加载数据
        // TODO: 实现实际的数据加载逻辑
        std::ifstream file(config_.data_path);
        if (!file.is_open()) {
            std::cerr << "无法打开数据文件: " << config_.data_path << std::endl;
            return false;
        }
        
        std::string line;
        bool first_line = true;
        
        while (std::getline(file, line)) {
            if (first_line) {
                // 跳过标题行
                first_line = false;
                continue;
            }
            
            // 解析CSV行
            // 格式: timestamp,open,high,low,close,volume
            std::istringstream ss(line);
            std::string token;
            std::vector<std::string> tokens;
            
            while (std::getline(ss, token, ',')) {
                tokens.push_back(token);
            }
            
            if (tokens.size() < 6) {
                continue;
            }
            
            // 创建TickData
            core::TickData tick;
            tick.symbol = config_.symbol;
            
            // 解析时间戳（简化处理）
            // TODO: 实现实际的时间戳解析
            tick.timestamp = std::chrono::system_clock::now();
            
            // 使用收盘价作为last_price
            tick.last_price = std::stod(tokens[4]);
            tick.volume = std::stod(tokens[5]);
            
            // 假设买卖价相同（简化）
            tick.bid_price = tick.last_price;
            tick.ask_price = tick.last_price;
            
            historical_data_.push_back(tick);
        }
        
        std::cout << "加载了 " << historical_data_.size() << " 条历史数据" << std::endl;
        return !historical_data_.empty();
    }
    
    BacktestResult run() {
        if (strategies_.empty()) {
            std::cerr << "没有添加策略，无法运行回测" << std::endl;
            return BacktestResult();
        }
        
        if (historical_data_.empty() && !load_data()) {
            std::cerr << "无法加载历史数据" << std::endl;
            return BacktestResult();
        }
        
        is_running_ = true;
        
        // 创建模拟交易所
        exchange_ = std::make_unique<SimulatedExchange>(
            config_.initial_capital,
            config_.commission_rate,
            config_.slippage
        );
        
        // 初始化策略
        for (auto& strategy : strategies_) {
            strategy->initialize();
        }
        
        // 初始化回测结果
        result_.initial_capital = config_.initial_capital;
        
        // 按时间顺序处理数据
        std::sort(historical_data_.begin(), historical_data_.end(),
                  [](const core::TickData& a, const core::TickData& b) {
                      return a.timestamp < b.timestamp;
                  });
        
        // 过滤日期范围
        auto start_it = std::find_if(historical_data_.begin(), historical_data_.end(),
                                     [this](const core::TickData& tick) {
                                         return tick.timestamp >= config_.start_date;
                                     });
        
        auto end_it = std::find_if(historical_data_.begin(), historical_data_.end(),
                                   [this](const core::TickData& tick) {
                                       return tick.timestamp > config_.end_date;
                                   });
        
        std::vector<core::TickData> filtered_data(start_it, end_it);
        
        // 主回测循环
        for (size_t i = 0; i < filtered_data.size(); ++i) {
            if (!is_running_) {
                break;
            }
            
            const auto& tick = filtered_data[i];
            
            // 更新交易所市场数据
            exchange_->set_market_data(tick);
            
            // 撮合未完成订单
            exchange_->match_orders();
            
            // 调用策略处理tick
            for (auto& strategy : strategies_) {
                strategy->on_tick(tick);
            }
            
            // 记录组合价值
            double total_value = exchange_->get_total_value();
            result_.portfolio_values.push_back(total_value);
            result_.timestamps.push_back(tick.timestamp);
            
            // 更新进度
            progress_ = static_cast<double>(i + 1) / filtered_data.size();
        }
        
        // 清理策略
        for (auto& strategy : strategies_) {
            strategy->cleanup();
        }
        
        // 计算最终结果
        calculate_results();
        
        is_running_ = false;
        return result_;
    }
    
    double get_progress() const {
        return progress_;
    }
    
    void stop() {
        is_running_ = false;
    }
    
private:
    void calculate_results() {
        if (result_.portfolio_values.empty()) {
            return;
        }
        
        result_.final_capital = result_.portfolio_values.back();
        result_.total_return = (result_.final_capital / result_.initial_capital) - 1.0;
        
        // 计算回撤
        double peak = result_.initial_capital;
        for (double value : result_.portfolio_values) {
            if (value > peak) {
                peak = value;
            }
            double drawdown = (peak - value) / peak;
            result_.drawdowns.push_back(drawdown);
            
            if (drawdown > result_.max_drawdown) {
                result_.max_drawdown = drawdown;
            }
        }
        
        // 计算交易统计
        result_.total_trades = result_.trades.size();
        result_.winning_trades = 0;
        result_.losing_trades = 0;
        double total_profit = 0.0;
        double total_loss = 0.0;
        
        // 简化：假设每笔交易的盈亏就是佣金（因为我们的策略立即平仓）
        for (auto& trade : result_.trades) {
            // 在实际中，这里应该计算实际盈亏
            // 现在我们使用一个简单的方法：随机生成盈亏用于演示
            static std::default_random_engine generator;
            static std::normal_distribution<double> pnl_dist(0.0, 10.0);
            
            trade.pnl = pnl_dist(generator) - trade.commission;
            
            if (trade.pnl > 0) {
                result_.winning_trades++;
                total_profit += trade.pnl;
            } else {
                result_.losing_trades++;
                total_loss += std::abs(trade.pnl);
            }
        }
        
        // 计算胜率和盈亏比
        if (result_.total_trades > 0) {
            result_.win_rate = static_cast<double>(result_.winning_trades) / result_.total_trades;
            if (total_loss > 0) {
                result_.profit_factor = total_profit / total_loss;
            }
        }
        
        // 计算年化收益率（简化：假设回测期为1年）
        result_.annual_return = result_.total_return;
        
        // 计算夏普比率（简化：假设无风险利率为0，波动率为10%）
        double volatility = 0.1;  // 10%波动率
        if (volatility > 0) {
            result_.sharpe_ratio = result_.annual_return / volatility;
        }
    }
    
    BacktestConfig config_;
    std::vector<std::shared_ptr<core::Strategy>> strategies_;
    std::vector<core::TickData> historical_data_;
    std::unique_ptr<SimulatedExchange> exchange_;
    BacktestResult result_;
    double progress_;
    bool is_running_;
};

// BacktestEngine 公共接口实现
BacktestEngine::BacktestEngine() : impl_(std::make_unique<Impl>()) {}
BacktestEngine::~BacktestEngine() = default;

void BacktestEngine::set_config(const BacktestConfig& config) {
    impl_->set_config(config);
}

void BacktestEngine::add_strategy(const std::shared_ptr<core::Strategy>& strategy) {
    impl_->add_strategy(strategy);
}

bool BacktestEngine::load_data() {
    return impl_->load_data();
}

BacktestResult BacktestEngine::run() {
    return impl_->run();
}

double BacktestEngine::get_progress() const {
    return impl_->get_progress();
}

void BacktestEngine::stop() {
    impl_->stop();
}

} // namespace backtest
} // namespace pplustrader