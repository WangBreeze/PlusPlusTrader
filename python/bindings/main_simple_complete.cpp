/**
 * Simple but complete Python bindings for PlusPlusTrader
 * Core functionality only
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// Simple data structures
namespace pplustrader {
    namespace core {
        struct TickData {
            std::string symbol;
            double timestamp;
            double open;
            double high;
            double low;
            double close;
            double volume;
        };
        
        enum class OrderType {
            MARKET,
            LIMIT,
            STOP,
            STOP_LIMIT
        };
        
        enum class OrderSide {
            BUY,
            SELL
        };
        
        enum class OrderStatus {
            UNKNOWN,
            PENDING,
            SUBMITTED,
            FILLED,
            PARTIALLY_FILLED,
            CANCELLED,
            REJECTED
        };
        
        struct Order {
            std::string order_id;
            std::string symbol;
            OrderType type;
            OrderSide side;
            double price;
            double quantity;
            OrderStatus status;
            double created_at;
            double updated_at;
        };
        
        struct AccountInfo {
            std::string account_id;
            double equity;
            double margin;
            double free_margin;
            double margin_level;
            double realized_pnl;
            double unrealized_pnl;
        };
    }
}

PYBIND11_MODULE(pplustrader, m) {
    m.doc() = "PlusPlusTrader - C++ algorithmic trading framework with Python bindings";
    
    // Version info
    m.attr("__version__") = "0.1.0";
    m.attr("__author__") = "PlusPlusTrader Team";
    m.attr("__description__") = "High-performance algorithmic trading system";
    
    // Simple test functions
    m.def("hello", []() -> std::string {
        return "Hello from PlusPlusTrader! Complete Python bindings are working.";
    });
    
    m.def("get_version", []() -> std::string {
        return "PlusPlusTrader v0.1.0 (Complete Python bindings)";
    });
    
    // Core module
    auto core = m.def_submodule("core", "Core trading engine module");
    
    // TickData
    py::class_<pplustrader::core::TickData>(core, "TickData")
        .def(py::init<>())
        .def_readwrite("symbol", &pplustrader::core::TickData::symbol)
        .def_readwrite("timestamp", &pplustrader::core::TickData::timestamp)
        .def_readwrite("open", &pplustrader::core::TickData::open)
        .def_readwrite("high", &pplustrader::core::TickData::high)
        .def_readwrite("low", &pplustrader::core::TickData::low)
        .def_readwrite("close", &pplustrader::core::TickData::close)
        .def_readwrite("volume", &pplustrader::core::TickData::volume)
        .def("__repr__", [](const pplustrader::core::TickData &t) {
            return "TickData(symbol='" + t.symbol + "', close=" + std::to_string(t.close) + ")";
        });
    
    // OrderType enum
    py::enum_<pplustrader::core::OrderType>(core, "OrderType")
        .value("MARKET", pplustrader::core::OrderType::MARKET)
        .value("LIMIT", pplustrader::core::OrderType::LIMIT)
        .value("STOP", pplustrader::core::OrderType::STOP)
        .value("STOP_LIMIT", pplustrader::core::OrderType::STOP_LIMIT)
        .export_values();
    
    // OrderSide enum
    py::enum_<pplustrader::core::OrderSide>(core, "OrderSide")
        .value("BUY", pplustrader::core::OrderSide::BUY)
        .value("SELL", pplustrader::core::OrderSide::SELL)
        .export_values();
    
    // OrderStatus enum
    py::enum_<pplustrader::core::OrderStatus>(core, "OrderStatus")
        .value("UNKNOWN", pplustrader::core::OrderStatus::UNKNOWN)
        .value("PENDING", pplustrader::core::OrderStatus::PENDING)
        .value("SUBMITTED", pplustrader::core::OrderStatus::SUBMITTED)
        .value("FILLED", pplustrader::core::OrderStatus::FILLED)
        .value("PARTIALLY_FILLED", pplustrader::core::OrderStatus::PARTIALLY_FILLED)
        .value("CANCELLED", pplustrader::core::OrderStatus::CANCELLED)
        .value("REJECTED", pplustrader::core::OrderStatus::REJECTED)
        .export_values();
    
    // Order struct
    py::class_<pplustrader::core::Order>(core, "Order")
        .def(py::init<>())
        .def_readwrite("order_id", &pplustrader::core::Order::order_id)
        .def_readwrite("symbol", &pplustrader::core::Order::symbol)
        .def_readwrite("type", &pplustrader::core::Order::type)
        .def_readwrite("side", &pplustrader::core::Order::side)
        .def_readwrite("price", &pplustrader::core::Order::price)
        .def_readwrite("quantity", &pplustrader::core::Order::quantity)
        .def_readwrite("status", &pplustrader::core::Order::status)
        .def_readwrite("created_at", &pplustrader::core::Order::created_at)
        .def_readwrite("updated_at", &pplustrader::core::Order::updated_at)
        .def("__repr__", [](const pplustrader::core::Order &o) {
            return "Order(id='" + o.order_id + "', symbol='" + o.symbol + "', side=" + 
                   (o.side == pplustrader::core::OrderSide::BUY ? "BUY" : "SELL") + 
                   ", price=" + std::to_string(o.price) + ")";
        });
    
    // AccountInfo struct
    py::class_<pplustrader::core::AccountInfo>(core, "AccountInfo")
        .def(py::init<>())
        .def_readwrite("account_id", &pplustrader::core::AccountInfo::account_id)
        .def_readwrite("equity", &pplustrader::core::AccountInfo::equity)
        .def_readwrite("margin", &pplustrader::core::AccountInfo::margin)
        .def_readwrite("free_margin", &pplustrader::core::AccountInfo::free_margin)
        .def_readwrite("margin_level", &pplustrader::core::AccountInfo::margin_level)
        .def_readwrite("realized_pnl", &pplustrader::core::AccountInfo::realized_pnl)
        .def_readwrite("unrealized_pnl", &pplustrader::core::AccountInfo::unrealized_pnl)
        .def("__repr__", [](const pplustrader::core::AccountInfo &a) {
            return "AccountInfo(id='" + a.account_id + "', equity=" + std::to_string(a.equity) + ")";
        });
    
    // Utility functions
    m.def("create_tick_data", []() -> pplustrader::core::TickData {
        pplustrader::core::TickData td;
        td.symbol = "AAPL";
        td.timestamp = 0.0;
        td.open = 100.0;
        td.high = 105.0;
        td.low = 99.0;
        td.close = 102.5;
        td.volume = 1000000;
        return td;
    }, "Create a sample TickData object");
    
    m.def("create_order", []() -> pplustrader::core::Order {
        pplustrader::core::Order order;
        order.order_id = "ORD001";
        order.symbol = "AAPL";
        order.type = pplustrader::core::OrderType::MARKET;
        order.side = pplustrader::core::OrderSide::BUY;
        order.price = 102.5;
        order.quantity = 100;
        order.status = pplustrader::core::OrderStatus::PENDING;
        order.created_at = 0.0;
        order.updated_at = 0.0;
        return order;
    }, "Create a sample Order object");
    
    m.def("create_account_info", []() -> pplustrader::core::AccountInfo {
        pplustrader::core::AccountInfo ai;
        ai.account_id = "ACC001";
        ai.equity = 100000.0;
        ai.margin = 20000.0;
        ai.free_margin = 80000.0;
        ai.margin_level = 500.0;
        ai.realized_pnl = 5000.0;
        ai.unrealized_pnl = 2000.0;
        return ai;
    }, "Create a sample AccountInfo object");
    
    // Simple moving average function
    m.def("simple_moving_average", [](const std::vector<double>& prices, int period) -> std::vector<double> {
        if (prices.size() < period) return {};
        
        std::vector<double> sma;
        for (size_t i = period - 1; i < prices.size(); ++i) {
            double sum = 0.0;
            for (int j = 0; j < period; ++j) {
                sum += prices[i - j];
            }
            sma.push_back(sum / period);
        }
        return sma;
    }, "Calculate simple moving average");
    
    // Backtest simulation function
    m.def("simulate_backtest", [](double initial_capital, const std::vector<double>& prices) -> double {
        if (prices.empty()) return initial_capital;
        
        double capital = initial_capital;
        double position = 0.0;
        
        // Simple strategy: buy on first day, sell on last day
        double buy_price = prices[0];
        double sell_price = prices.back();
        
        // Calculate profit
        double profit = (sell_price - buy_price) / buy_price * capital * 0.1; // 10% position
        
        return capital + profit;
    }, "Simulate a simple backtest");
}