/**
 * Complete Python bindings for PlusPlusTrader
 * Simplified version with core functionality
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

namespace py = pybind11;

// Forward declarations
namespace pplustrader {
    namespace core {
        struct TickData;
        struct Order;
        enum class OrderType;
        enum class OrderSide;
        enum class OrderStatus;
        struct AccountInfo;
        class BaseStrategy;
    }
    
    namespace indicators {
        class Indicator;
        class MA;
    }
    
    namespace backtest {
        class BacktestEngine;
        struct BacktestConfig;
    }
    
    namespace data {
        class CSVDataSource;
        struct DataSourceConfig;
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
        .def_readwrite("volume", &pplustrader::core::TickData::volume);
    
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
        .def_readwrite("updated_at", &pplustrader::core::Order::updated_at);
    
    // AccountInfo struct
    py::class_<pplustrader::core::AccountInfo>(core, "AccountInfo")
        .def(py::init<>())
        .def_readwrite("account_id", &pplustrader::core::AccountInfo::account_id)
        .def_readwrite("equity", &pplustrader::core::AccountInfo::equity)
        .def_readwrite("margin", &pplustrader::core::AccountInfo::margin)
        .def_readwrite("free_margin", &pplustrader::core::AccountInfo::free_margin)
        .def_readwrite("margin_level", &pplustrader::core::AccountInfo::margin_level)
        .def_readwrite("realized_pnl", &pplustrader::core::AccountInfo::realized_pnl)
        .def_readwrite("unrealized_pnl", &pplustrader::core::AccountInfo::unrealized_pnl);
    
    // BaseStrategy (abstract base class)
    py::class_<pplustrader::core::BaseStrategy, std::shared_ptr<pplustrader::core::BaseStrategy>>(core, "BaseStrategy")
        .def("initialize", &pplustrader::core::BaseStrategy::initialize)
        .def("on_tick", &pplustrader::core::BaseStrategy::on_tick)
        .def("on_order", &pplustrader::core::BaseStrategy::on_order)
        .def("get_name", &pplustrader::core::BaseStrategy::get_name);
    
    // Indicators module
    auto indicators = m.def_submodule("indicators", "Technical indicators module");
    
    // Indicator base class
    py::class_<pplustrader::indicators::Indicator, std::shared_ptr<pplustrader::indicators::Indicator>>(indicators, "Indicator")
        .def("update", &pplustrader::indicators::Indicator::update)
        .def("is_ready", &pplustrader::indicators::Indicator::is_ready)
        .def("get_value", &pplustrader::indicators::Indicator::get_value);
    
    // MA (Moving Average)
    py::class_<pplustrader::indicators::MA, pplustrader::indicators::Indicator, std::shared_ptr<pplustrader::indicators::MA>>(indicators, "MA")
        .def(py::init<int>())
        .def("get_period", &pplustrader::indicators::MA::get_period);
    
    // Backtest module
    auto backtest = m.def_submodule("backtest", "Backtesting engine module");
    
    // BacktestConfig
    py::class_<pplustrader::backtest::BacktestConfig>(backtest, "BacktestConfig")
        .def(py::init<>())
        .def_readwrite("symbol", &pplustrader::backtest::BacktestConfig::symbol)
        .def_readwrite("start_date", &pplustrader::backtest::BacktestConfig::start_date)
        .def_readwrite("end_date", &pplustrader::backtest::BacktestConfig::end_date)
        .def_readwrite("initial_capital", &pplustrader::backtest::BacktestConfig::initial_capital)
        .def_readwrite("commission_rate", &pplustrader::backtest::BacktestConfig::commission_rate)
        .def_readwrite("slippage", &pplustrader::backtest::BacktestConfig::slippage);
    
    // BacktestEngine
    py::class_<pplustrader::backtest::BacktestEngine>(backtest, "BacktestEngine")
        .def(py::init<>())
        .def("run", &pplustrader::backtest::BacktestEngine::run)
        .def("get_results", &pplustrader::backtest::BacktestEngine::get_results);
    
    // Data module
    auto data = m.def_submodule("data", "Data source module");
    
    // DataSourceConfig
    py::class_<pplustrader::data::DataSourceConfig>(data, "DataSourceConfig")
        .def(py::init<>())
        .def_readwrite("symbol", &pplustrader::data::DataSourceConfig::symbol)
        .def_readwrite("file_path", &pplustrader::data::DataSourceConfig::file_path);
    
    // CSVDataSource
    py::class_<pplustrader::data::CSVDataSource, std::shared_ptr<pplustrader::data::CSVDataSource>>(data, "CSVDataSource")
        .def(py::init<>())
        .def("load_data", &pplustrader::data::CSVDataSource::load_data)
        .def("get_next", &pplustrader::data::CSVDataSource::get_next);
    
    // Utility functions
    m.def("create_tick_data", []() -> pplustrader::core::TickData {
        return pplustrader::core::TickData();
    }, "Create a new TickData object");
    
    m.def("create_order", []() -> pplustrader::core::Order {
        return pplustrader::core::Order();
    }, "Create a new Order object");
    
    m.def("create_account_info", []() -> pplustrader::core::AccountInfo {
        return pplustrader::core::AccountInfo();
    }, "Create a new AccountInfo object");
}