#include "core/Engine.h"
#include <iostream>
#include <memory>
#include <unordered_map>
#include <mutex>
#include <thread>
#include <chrono>

namespace pplustrader {
namespace core {

// 引擎实现类
class TradingEngine::Impl {
public:
    Impl() : running_(false) {}
    ~Impl() { stop(); }
    
    bool initialize(const std::string& config_path) {
        std::lock_guard<std::mutex> lock(mutex_);
        std::cout << "TradingEngine initializing with config: " << config_path << std::endl;
        // TODO: 加载配置文件
        return true;
    }
    
    void start() {
        if (running_) return;
        
        running_ = true;
        std::cout << "TradingEngine starting..." << std::endl;
        
        // 启动策略
        for (auto& strategy : strategies_) {
            strategy->initialize();
        }
        
        // TODO: 启动数据源和交易所连接
        // 暂时模拟运行
        worker_thread_ = std::thread([this]() {
            while (running_) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                // TODO: 处理数据事件
            }
        });
    }
    
    void stop() {
        if (!running_) return;
        
        running_ = false;
        std::cout << "TradingEngine stopping..." << std::endl;
        
        if (worker_thread_.joinable()) {
            worker_thread_.join();
        }
        
        // 清理策略
        for (auto& strategy : strategies_) {
            strategy->cleanup();
        }
    }
    
    void add_strategy(const std::shared_ptr<Strategy>& strategy) {
        std::lock_guard<std::mutex> lock(mutex_);
        strategies_.push_back(strategy);
        std::cout << "Strategy added, total: " << strategies_.size() << std::endl;
    }
    
    std::string submit_order(const Order& order) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        // 生成订单ID
        static int order_counter = 0;
        std::string order_id = "ORDER_" + std::to_string(++order_counter);
        
        // 这里应该调用交易所接口
        // 暂时模拟成功
        std::cout << "Order submitted: " << order_id 
                  << " Symbol: " << order.symbol
                  << " Side: " << (order.side == OrderSide::BUY ? "BUY" : "SELL")
                  << " Price: " << order.price
                  << " Quantity: " << order.quantity << std::endl;
        
        // 存储订单
        orders_[order_id] = order;
        orders_[order_id].order_id = order_id;
        orders_[order_id].status = OrderStatus::SUBMITTED;
        orders_[order_id].created_at = std::chrono::system_clock::now();
        
        return order_id;
    }
    
    bool cancel_order(const std::string& order_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        auto it = orders_.find(order_id);
        if (it == orders_.end()) {
            std::cout << "Order not found: " << order_id << std::endl;
            return false;
        }
        
        it->second.status = OrderStatus::CANCELLED;
        it->second.updated_at = std::chrono::system_clock::now();
        
        std::cout << "Order cancelled: " << order_id << std::endl;
        return true;
    }
    
    OrderStatus get_order_status(const std::string& order_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        auto it = orders_.find(order_id);
        if (it == orders_.end()) {
            return OrderStatus::REJECTED;
        }
        
        return it->second.status;
    }
    
private:
    bool running_;
    std::mutex mutex_;
    std::thread worker_thread_;
    std::vector<std::shared_ptr<Strategy>> strategies_;
    std::unordered_map<std::string, Order> orders_;
};

// TradingEngine 公共接口实现
TradingEngine::TradingEngine() : impl_(std::make_unique<Impl>()) {}
TradingEngine::~TradingEngine() = default;

bool TradingEngine::initialize(const std::string& config_path) {
    return impl_->initialize(config_path);
}

void TradingEngine::start() {
    impl_->start();
}

void TradingEngine::stop() {
    impl_->stop();
}

void TradingEngine::add_strategy(const std::shared_ptr<Strategy>& strategy) {
    impl_->add_strategy(strategy);
}

std::string TradingEngine::submit_order(const Order& order) {
    return impl_->submit_order(order);
}

bool TradingEngine::cancel_order(const std::string& order_id) {
    return impl_->cancel_order(order_id);
}

OrderStatus TradingEngine::get_order_status(const std::string& order_id) {
    return impl_->get_order_status(order_id);
}

} // namespace core
} // namespace pplustrader