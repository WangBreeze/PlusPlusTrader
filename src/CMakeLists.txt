# src/CMakeLists.txt

# 添加core库
add_library(pplustrader_core
    core/Engine.cpp
    core/BaseStrategy.cpp
)

# 添加data库（暂时空实现）
add_library(pplustrader_data
    data/DataFeed.cpp
)

# 添加indicators库
add_library(pplustrader_indicators
    indicators/Indicator.cpp
    indicators/MA.cpp
    indicators/MACD.cpp
    indicators/RSI.cpp
)

# 添加custom库（Python自定义指标桥接）
add_library(pplustrader_custom
    custom/PythonIndicatorBridge.cpp
)

# 添加backtest库
add_library(pplustrader_backtest
    backtest/BacktestEngine.cpp
    backtest/SimulatedExchange.cpp
)

# 添加risk库
add_library(pplustrader_risk
    risk/RiskManager.cpp
    risk/StopLossTakeProfit.cpp
    risk/PositionSizing.cpp
)

# 添加data库
add_library(pplustrader_data_src
    data/DataSource.cpp
    data/CSVDataSource.cpp
)

# 添加exchange库（暂时空实现）
add_library(pplustrader_exchange
    exchange/Exchange.cpp
)

# 创建主库（链接所有子库）
add_library(pplustrader
    $<TARGET_OBJECTS:pplustrader_core>
    $<TARGET_OBJECTS:pplustrader_data>
    $<TARGET_OBJECTS:pplustrader_exchange>
    $<TARGET_OBJECTS:pplustrader_indicators>
    $<TARGET_OBJECTS:pplustrader_backtest>
    $<TARGET_OBJECTS:pplustrader_risk>
    $<TARGET_OBJECTS:pplustrader_data_src>
    $<TARGET_OBJECTS:pplustrader_custom>
)

# 头文件目录
target_include_directories(pplustrader_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_include_directories(pplustrader_data PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/data
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_include_directories(pplustrader_exchange PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/exchange
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_include_directories(pplustrader_indicators PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/indicators
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_include_directories(pplustrader_custom PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/custom
    ${CMAKE_CURRENT_SOURCE_DIR}/core
    ${CMAKE_CURRENT_SOURCE_DIR}/indicators
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/custom
)

target_include_directories(pplustrader_backtest PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/backtest
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_include_directories(pplustrader_risk PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/risk
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_include_directories(pplustrader_data_src PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/data
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_include_directories(pplustrader PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# 创建示例程序
add_executable(example 
    example/main.cpp
    example/SimpleStrategy.cpp
)
target_link_libraries(example 
    pplustrader_core
    pplustrader_data
    pplustrader_exchange
    pthread
)

# 设置C++标准
set_target_properties(example PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
)