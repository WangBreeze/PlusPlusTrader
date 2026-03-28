/**
 * Minimal Python bindings for PlusPlusTrader
 */

#include <pybind11/pybind11.h>

namespace py = pybind11;

// Minimal bindings for testing
PYBIND11_MODULE(pplustrader, m) {
    m.doc() = "PlusPlusTrader Python bindings";
    
    // Simple version info
    m.attr("__version__") = "0.1.0";
    m.attr("__author__") = "PlusPlusTrader Team";
    
    // Simple test function
    m.def("hello", []() -> std::string {
        return "Hello from PlusPlusTrader! Python bindings are working.";
    });
    
    m.def("add", [](int a, int b) -> int {
        return a + b;
    }, "Add two numbers");
    
    m.def("get_version", []() -> std::string {
        return "PlusPlusTrader v0.1.0 (Python bindings test)";
    });
}