cmake_minimum_required(VERSION 3.10)
project(PlusPlusTrader VERSION 0.1.0 LANGUAGES CXX)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 编译选项
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_options(-g -O0 -Wall -Wextra -Wpedantic)
    add_definitions(-DDEBUG)
else()
    add_compile_options(-O3 -Wall -Wextra)
    add_definitions(-DNDEBUG)
endif()

# 包含目录
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# 添加子目录
add_subdirectory(src)

# 测试（暂时全部禁用以专注于Python绑定）
# enable_testing()
# if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/tests)
#     add_subdirectory(tests)
# endif()

# 所有测试程序暂时禁用
# add_executable(test_mfi src/test/test_mfi.cpp)
# target_link_libraries(test_mfi cpptrader)
# 
# add_executable(test_backtest_stats src/test/test_backtest_stats.cpp)
# target_link_libraries(test_backtest_stats cpptrader)
# 
# add_executable(test_indicators src/test/test_indicators.cpp)
# target_link_libraries(test_indicators cpptrader)
# 
# add_executable(test_backtest_units src/test/test_backtest_units.cpp)
# target_link_libraries(test_backtest_units cpptrader)

# 集成测试：Python自定义指标与回测引擎
option(BUILD_INTEGRATION_TEST "Build integration test for Python custom indicators" ON)
if(BUILD_INTEGRATION_TEST AND BUILD_PYTHON_BINDINGS)
    message(STATUS "Building integration test for Python custom indicators...")
    
    # 查找Python开发库
    find_package(Python3 COMPONENTS Development REQUIRED)
    
    # 简单集成测试
    add_executable(test_simple_integration test_simple_integration.cpp)
    target_link_libraries(test_simple_integration 
        pplustrader_core
        pplustrader_indicators
        pplustrader_custom
        ${Python3_LIBRARIES}
    )
    target_include_directories(test_simple_integration PRIVATE
        ${Python3_INCLUDE_DIRS}
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_SOURCE_DIR}/include/custom
    )
    target_compile_definitions(test_simple_integration PRIVATE WITH_PYTHON)
    
    message(STATUS "Added test_simple_integration executable")
    
    # 完整集成测试（暂时禁用）
    # add_executable(test_integration_python_backtest test_integration_python_backtest.cpp)
    # target_link_libraries(test_integration_python_backtest 
    #     pplustrader_core
    #     pplustrader_indicators
    #     pplustrader_backtest
    #     pplustrader_data
    #     pplustrader_exchange
    #     pplustrader_risk
    #     ${Python3_LIBRARIES}
    # )
    # target_include_directories(test_integration_python_backtest PRIVATE
    #     ${Python3_INCLUDE_DIRS}
    #     ${CMAKE_CURRENT_SOURCE_DIR}/include
    #     ${CMAKE_CURRENT_SOURCE_DIR}/include/custom
    # )
    # target_compile_definitions(test_integration_python_backtest PRIVATE WITH_PYTHON)
    # 
    # message(STATUS "Added test_integration_python_backtest executable")
endif()

# Python绑定（可选）
option(BUILD_PYTHON_BINDINGS "Build Python bindings" ON)
if(BUILD_PYTHON_BINDINGS)
    if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/python/bindings)
        message(STATUS "Building Python bindings...")
        add_subdirectory(python/bindings)
    else()
        message(WARNING "Python bindings directory not found: ${CMAKE_CURRENT_SOURCE_DIR}/python/bindings")
    endif()
endif()

# 并行回测测试程序（暂时禁用）
# add_executable(test_parallel_backtest src/test/test_parallel_backtest.cpp)
# target_link_libraries(test_parallel_backtest cpptrader)
# message(STATUS "Added test_parallel_backtest executable")

# Python绑定（暂时禁用以专注C++核心开发）
# find_package(Python3 COMPONENTS Development)
# if(Python3_FOUND)
#     message(STATUS "Found Python3: ${Python3_EXECUTABLE}")
#     add_subdirectory(python/bindings)
# else()
#     message(WARNING "Python3 development not found, Python bindings disabled")
# endif()
message(STATUS "Python bindings temporarily disabled for core development")