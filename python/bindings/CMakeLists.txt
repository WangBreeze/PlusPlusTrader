# Python bindings CMakeLists.txt
# Force enable Python bindings

message(STATUS "=== Python bindings enabled ===")

# Set CMake policies for cross-directory linking
cmake_policy(SET CMP0079 NEW)

# First find Python3 with all required components
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

message(STATUS "Python3 found:")
message(STATUS "  Interpreter: ${Python3_EXECUTABLE}")
message(STATUS "  Include dirs: ${Python3_INCLUDE_DIRS}")
message(STATUS "  Libraries: ${Python3_LIBRARIES}")
message(STATUS "  Version: ${Python3_VERSION}")

# Find pybind11 from virtual environment
set(PYBIND11_PYTHON_VERSION 3)
find_package(pybind11 REQUIRED HINTS
    /home/wanglc/.openclaw/workspace/PlusPlusTrader/venv/lib/python3.13/site-packages/pybind11/share/cmake/pybind11
    ${PYBIND11_ROOT}/share/cmake/pybind11
)

message(STATUS "pybind11 found at: ${pybind11_INCLUDE_DIR}")

# Create Python module with unique name
pybind11_add_module(pplustrader_py
    main_simple_complete.cpp
)

message(STATUS "Python module target created: pplustrader_py")

# Link against the core library
target_link_libraries(pplustrader_py PRIVATE 
    pplustrader_core
    pplustrader_data
    pplustrader_exchange
    pplustrader_risk
    pplustrader_backtest
)

# Include directories
target_include_directories(pplustrader_py PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/src/core
    ${CMAKE_SOURCE_DIR}/src/indicators
    ${CMAKE_SOURCE_DIR}/src/data
    ${CMAKE_SOURCE_DIR}/src/exchange
    ${CMAKE_SOURCE_DIR}/src/backtest
    ${CMAKE_SOURCE_DIR}/src/risk
    ${CMAKE_SOURCE_DIR}/src/strategies
)

# Set output properties
set_target_properties(pplustrader_py PROPERTIES
    OUTPUT_NAME "pplustrader"
    SUFFIX "${PYTHON_MODULE_EXTENSION}"
    PREFIX ""
)

message(STATUS "Python module will be built as: pplustrader${PYTHON_MODULE_EXTENSION}")

# Install the module
install(TARGETS pplustrader_py
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/python3/site-packages
)

message(STATUS "=== Python bindings configuration complete ===")