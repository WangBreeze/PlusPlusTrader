/**
 * Python bindings for PlusPlusTrader
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>

// Core headers
#include "core/Engine.h"
#include "core/BaseStrategy.h"
#include "indicators/Indicator.h"
#include "indicators/MA.h"
#include "indicators/MACD.h"
#include "indicators/RSI.h"
#include "data/DataFeed.h"
#include "data/CSVDataSource.h"
#include "backtest/BacktestEngine.h"
#include "backtest/SimulatedExchange.h"
#include "data/DataSource.h"

namespace py = pybind11;
using namespace pplustrader;

PYBIND11_MODULE(pplustrader, m) {
    m.doc() = "PlusPlusTrader - C++ algorithmic trading framework with Python bindings";
    
    // TickData
    py::class_<TickData>(m, "TickData")
        .def(py::init<>())
        .def_readwrite("symbol", &TickData::symbol)
        .def_readwrite("timestamp", &TickData::timestamp)
        .def_readwrite("open", &TickData::open)
        .def_readwrite("high", &TickData::high)
        .def_readwrite("low", &TickData::low)
        .def_readwrite("close", &TickData::close)
        .def_readwrite("volume", &TickData::volume);
    
    // OrderType enum
    py::enum_<OrderType>(m, "OrderType")
        .value("MARKET", OrderType::MARKET)
        .value("LIMIT", OrderType::LIMIT)
        .value("STOP", OrderType::STOP)
        .value("STOP_LIMIT", OrderType::STOP_LIMIT)
        .export_values();
    
    // OrderSide enum
    py::enum_<OrderSide>(m, "OrderSide")
        .value("BUY", OrderSide::BUY)
        .value("SELL", OrderSide::SELL)
        .export_values();
    
    // OrderStatus enum
    py::enum_<OrderStatus>(m, "OrderStatus")
        .value("UNKNOWN", OrderStatus::UNKNOWN)
        .value("PENDING", OrderStatus::PENDING)
        .value("SUBMITTED", OrderStatus::SUBMITTED)
        .value("FILLED", OrderStatus::FILLED)
        .value("PARTIALLY_FILLED", OrderStatus::PARTIALLY_FILLED)
        .value("CANCELLED", OrderStatus::CANCELLED)
        .value("REJECTED", OrderStatus::REJECTED)
        .export_values();
    
    // Order struct
    py::class_<Order>(m, "Order")
        .def(py::init<>())
        .def_readwrite("order_id", &Order::order_id)
        .def_readwrite("symbol", &Order::symbol)
        .def_readwrite("type", &Order::type)
        .def_readwrite("side", &Order::side)
        .def_readwrite("price", &Order::price)
        .def_readwrite("quantity", &Order::quantity)
        .def_readwrite("status", &Order::status)
        .def_readwrite("created_at", &Order::created_at)
        .def_readwrite("updated_at", &Order::updated_at);
    
    // AccountInfo struct
    py::class_<AccountInfo>(m, "AccountInfo")
        .def(py::init<>())
        .def_readwrite("account_id", &AccountInfo::account_id)
        .def_readwrite("equity", &AccountInfo::equity)
        .def_readwrite("margin", &AccountInfo::margin)
        .def_readwrite("free_margin", &AccountInfo::free_margin)
        .def_readwrite("margin_level", &AccountInfo::margin_level)
        .def_readwrite("realized_pnl", &AccountInfo::realized_pnl)
        .def_readwrite("unrealized_pnl", &AccountInfo::unrealized_pnl);
    
    // BaseStrategy (abstract base class)
    py::class_<BaseStrategy, std::shared_ptr<BaseStrategy>>(m, "BaseStrategy")
        .def("initialize", &BaseStrategy::initialize)
        .def("on_tick", &BaseStrategy::on_tick)
        .def("on_order", &BaseStrategy::on_order)
        .def("get_name", &BaseStrategy::get_name);
    
    // Indicator base class
    py::class_<indicators::Indicator, std::shared_ptr<indicators::Indicator>>(m, "Indicator")
        .def("update", &indicators::Indicator::update)
        .def("is_ready", &indicators::Indicator::is_ready)
        .def("get_value", &indicators::Indicator::get_value);
    
    // BacktestConfig (defined in BacktestEngine.h)
    py::class_<backtest::BacktestConfig>(m, "BacktestConfig")
        .def(py::init<>())
        .def_readwrite("symbol", &backtest::BacktestConfig::symbol)
        .def_readwrite("start_date", &backtest::BacktestConfig::start_date)
        .def_readwrite("end_date", &backtest::BacktestConfig::end_date)
        .def_readwrite("initial_capital", &backtest::BacktestConfig::initial_capital)
        .def_readwrite("commission_rate", &backtest::BacktestConfig::commission_rate)
        .def_readwrite("slippage", &backtest::BacktestConfig::slippage)
        .def_readwrite("data_source", &backtest::BacktestConfig::data_source)
        .def_readwrite("data_path", &backtest::BacktestConfig::data_path);
    
    // DataSourceConfig (defined in DataSource.h)
    py::class_<data::DataSourceConfig>(m, "DataSourceConfig")
        .def(py::init<>())
        .def_readwrite("symbol", &data::DataSourceConfig::symbol)
        .def_readwrite("frequency", &data::DataSourceConfig::frequency)
        .def_readwrite("start_date", &data::DataSourceConfig::start_date)
        .def_readwrite("end_date", &data::DataSourceConfig::end_date)
        .def_readwrite("fields", &data::DataSourceConfig::fields)
        .def_readwrite("include_volume", &data::DataSourceConfig::include_volume)
        .def_readwrite("include_ohlc", &data::DataSourceConfig::include_ohlc)
        .def_readwrite("file_path", &data::DataSourceConfig::file_path)
        .def_readwrite("db_connection", &data::DataSourceConfig::db_connection)
        .def_readwrite("api_endpoint", &data::DataSourceConfig::api_endpoint)
        .def_readwrite("api_key", &data::DataSourceConfig::api_key);
    
    // MA indicator
    py::class_<indicators::MA, indicators::Indicator, std::shared_ptr<indicators::MA>>(m, "MA")
        .def(py::init<int>())
        .def("get_period", &indicators::MA::get_period);
    
    // BacktestEngine
    py::class_<backtest::BacktestEngine>(m, "BacktestEngine")
        .def(py::init<>())
        .def("set_config", &backtest::BacktestEngine::set_config)
        .def("add_strategy", &backtest::BacktestEngine::add_strategy)
        .def("load_data", &backtest::BacktestEngine::load_data)
        .def("run", &backtest::BacktestEngine::run)
        .def("get_progress", &backtest::BacktestEngine::get_progress)
        .def("stop", &backtest::BacktestEngine::stop);
    
    // CSVDataSource
    py::class_<data::CSVDataSource, data::DataSource, std::shared_ptr<data::CSVDataSource>>(m, "CSVDataSource")
        .def(py::init<>())
        .def("initialize", &data::CSVDataSource::initialize)
        .def("load_historical_data", &data::CSVDataSource::load_historical_data)
        .def("get_latest_data", &data::CSVDataSource::get_latest_data)
        .def("is_available", &data::CSVDataSource::is_available)
        .def("name", &data::CSVDataSource::name)
        .def("supported_frequencies", &data::CSVDataSource::supported_frequencies)
        .def("available_symbols", &data::CSVDataSource::available_symbols);
    
    // Module functions
    m.def("create_moving_average", [](int period) -> std::shared_ptr<indicators::MA> {
        return std::make_shared<indicators::MA>(period);
    }, "Create a moving average indicator");
    
    m.def("create_csv_data_source", []() {
        return std::make_shared<data::CSVDataSource>();
    }, "Create a CSV data source");
    
    // Version info
    m.attr("__version__") = "0.1.0";
    m.attr("__author__") = "PlusPlusTrader Team";
}