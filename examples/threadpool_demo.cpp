// threadpool_demo.cpp - Demonstration of ThreadPool usage
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-16

#include "../src/core/ThreadPool.h"
#include <iostream>
#include <vector>
#include <future>
#include <chrono>
#include <cmath>

using namespace pplustrader::core;
using namespace std::chrono;

// Simple function to simulate work
double calculate_technical_indicator(int iterations) {
    double result = 0.0;
    for (int i = 0; i < iterations; ++i) {
        result += std::sin(i * 0.01) * std::cos(i * 0.005);
    }
    return result;
}

// Demo 1: Basic ThreadPool usage
void demo_basic_usage() {
    std::cout << "=== Demo 1: Basic ThreadPool Usage ===" << std::endl;
    
    // Create thread pool with auto-detected threads
    ThreadPool pool;
    std::cout << "Created ThreadPool with " << pool.thread_count() 
              << " worker threads" << std::endl;
    
    // Submit tasks
    std::vector<std::future<double>> futures;
    const int num_tasks = 8;
    const int work_per_task = 1000000;
    
    auto start_time = high_resolution_clock::now();
    
    for (int i = 0; i < num_tasks; ++i) {
        auto future = pool.submit(calculate_technical_indicator, work_per_task);
        futures.push_back(std::move(future));
    }
    
    // Collect results
    double total_result = 0.0;
    for (int i = 0; i < num_tasks; ++i) {
        total_result += futures[i].get();
    }
    
    auto end_time = high_resolution_clock::now();
    auto duration = duration_cast<milliseconds>(end_time - start_time).count();
    
    std::cout << "Completed " << num_tasks << " tasks in " 
              << duration << " ms" << std::endl;
    std::cout << "Total result: " << total_result << std::endl;
    std::cout << "Average time per task: " 
              << static_cast<double>(duration) / num_tasks << " ms" << std::endl;
}

// Demo 2: Parallel parameter sweep simulation
void demo_parameter_sweep() {
    std::cout << "\n=== Demo 2: Parallel Parameter Sweep ===" << std::endl;
    
    ThreadPool pool(4);  // Use 4 threads
    
    // Simulate testing different strategy parameters
    std::vector<double> parameters = {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0};
    std::vector<std::future<std::pair<double, double>>> futures;
    
    // Function to test a parameter value
    auto test_parameter = [](double param) -> std::pair<double, double> {
        // Simulate backtest with this parameter
        std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(100 * param)));
        
        // Simulate return based on parameter (simple quadratic function)
        double return_rate = -10.0 * (param - 0.5) * (param - 0.5) + 2.5;
        
        return {param, return_rate};
    };
    
    auto start_time = high_resolution_clock::now();
    
    // Submit all parameter tests
    for (double param : parameters) {
        futures.push_back(pool.submit(test_parameter, param));
    }
    
    // Collect and analyze results
    std::cout << "\nParameter sweep results:" << std::endl;
    std::cout << "Parameter | Return % | Status" << std::endl;
    std::cout << "----------|----------|--------" << std::endl;
    
    double best_return = -1000.0;
    double best_param = 0.0;
    
    for (size_t i = 0; i < futures.size(); ++i) {
        auto [param, return_rate] = futures[i].get();
        
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "    " << std::setw(5) << param << "  | "
                  << std::setw(7) << return_rate << "% | ";
        
        if (return_rate > best_return) {
            best_return = return_rate;
            best_param = param;
            std::cout << "New Best!" << std::endl;
        } else {
            std::cout << "OK" << std::endl;
        }
    }
    
    auto end_time = high_resolution_clock::now();
    auto duration = duration_cast<milliseconds>(end_time - start_time).count();
    
    std::cout << "\nOptimization complete in " << duration << " ms" << std::endl;
    std::cout << "Best parameter: " << best_param 
              << " with return: " << best_return << "%" << std::endl;
}

// Demo 3: Exception handling in parallel tasks
void demo_exception_handling() {
    std::cout << "\n=== Demo 3: Exception Handling ===" << std::endl;
    
    ThreadPool pool(2);
    
    // Submit tasks, some of which throw exceptions
    auto future1 = pool.submit([]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        return 42;  // Normal task
    });
    
    auto future2 = pool.submit([]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(30));
        throw std::runtime_error("Simulated task failure!");
        return 0;
    });
    
    auto future3 = pool.submit([]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        return 100;  // Another normal task
    });
    
    // Try to get results
    try {
        int result1 = future1.get();
        std::cout << "Task 1 completed successfully: " << result1 << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Task 1 failed: " << e.what() << std::endl;
    }
    
    try {
        int result2 = future2.get();
        std::cout << "Task 2 completed successfully: " << result2 << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Task 2 failed (as expected): " << e.what() << std::endl;
    }
    
    try {
        int result3 = future3.get();
        std::cout << "Task 3 completed successfully: " << result3 << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Task 3 failed: " << e.what() << std::endl;
    }
    
    std::cout << "Exception handling demo completed." << std::endl;
}

// Demo 4: Performance comparison single vs multi-threaded
void demo_performance_comparison() {
    std::cout << "\n=== Demo 4: Performance Comparison ===" << std::endl;
    
    const int num_calculations = 10000000;
    const int num_tasks = 10;
    
    // Single-threaded execution
    std::cout << "Running single-threaded..." << std::endl;
    auto start_single = high_resolution_clock::now();
    
    double single_result = 0.0;
    for (int i = 0; i < num_tasks; ++i) {
        single_result += calculate_technical_indicator(num_calculations / num_tasks);
    }
    
    auto end_single = high_resolution_clock::now();
    auto single_time = duration_cast<milliseconds>(end_single - start_single).count();
    
    // Multi-threaded execution
    std::cout << "Running multi-threaded (4 threads)..." << std::endl;
    ThreadPool pool(4);
    
    auto start_multi = high_resolution_clock::now();
    
    std::vector<std::future<double>> futures;
    for (int i = 0; i < num_tasks; ++i) {
        futures.push_back(pool.submit(calculate_technical_indicator, num_calculations / num_tasks));
    }
    
    double multi_result = 0.0;
    for (auto& future : futures) {
        multi_result += future.get();
    }
    
    auto end_multi = high_resolution_clock::now();
    auto multi_time = duration_cast<milliseconds>(end_multi - start_multi).count();
    
    // Results comparison
    std::cout << "\nPerformance Comparison:" << std::endl;
    std::cout << "Single-threaded: " << single_time << " ms, Result: " << single_result << std::endl;
    std::cout << "Multi-threaded:  " << multi_time << " ms, Result: " << multi_result << std::endl;
    std::cout << "Speedup: " << std::fixed << std::setprecision(2) 
              << static_cast<double>(single_time) / multi_time << "x" << std::endl;
    std::cout << "Result difference: " << std::abs(single_result - multi_result) << std::endl;
}

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "ThreadPool Demonstration" << std::endl;
    std::cout << "PlusPlusTrader Parallel Computing Framework" << std::endl;
    std::cout << "Date: 2026-03-16" << std::endl;
    std::cout << "========================================" << std::endl;
    
    try {
        demo_basic_usage();
        demo_parameter_sweep();
        demo_exception_handling();
        demo_performance_comparison();
        
        std::cout << "\n========================================" << std::endl;
        std::cout << "All demonstrations completed successfully!" << std::endl;
        std::cout << "========================================" << std::endl;
        
        std::cout << "\n🎉 ThreadPool is ready for parallel backtesting!" << std::endl;
        std::cout << "\nKey Features Demonstrated:" << std::endl;
        std::cout << "✅ Automatic thread management" << std::endl;
        std::cout << "✅ Task submission with futures" << std::endl;
        std::cout << "✅ Exception safety and propagation" << std::endl;
        std::cout << "✅ Performance scaling with cores" << std::endl;
        std::cout << "✅ Real-world use case: parameter sweep" << std::endl;
        
        return 0;
    } catch (const std::exception& e) {
        std::cout << "Demonstration failed: " << e.what() << std::endl;
        return 1;
    }
}