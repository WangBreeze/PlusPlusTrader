// ParallelBacktestEngine.cpp - Parallel backtesting engine implementation
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#include "ParallelBacktestEngine.h"
#include <chrono>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <numeric>

using namespace std::chrono;

namespace pplustrader {
namespace backtest {

// ParallelBacktestResult implementation
void ParallelBacktestResult::add_result(const std::string& task_name,
                                       const BacktestResult& result,
                                       double execution_time_ms) {
    std::lock_guard<std::mutex> lock(mutex_);
    results_.emplace_back(task_name, result);
    execution_times_.emplace_back(task_name, execution_time_ms);
}

BacktestResult ParallelBacktestResult::aggregate_results() const {
    if (results_.empty()) {
        return BacktestResult();
    }
    
    // Simple aggregation: use the first result as base
    BacktestResult aggregated = results_[0].second;
    
    // For now, return the first result
    // In a more complete implementation, we could:
    // 1. Combine equity curves
    // 2. Aggregate trade statistics
    // 3. Calculate meta-statistics across all runs
    
    return aggregated;
}

void ParallelBacktestResult::print_summary() const {
    std::lock_guard<std::mutex> lock(mutex_);
    
    std::cout << "\n========================================" << std::endl;
    std::cout << "Parallel Backtest Summary" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "Total tasks: " << results_.size() << std::endl;
    
    if (results_.empty()) {
        std::cout << "No results to display." << std::endl;
        return;
    }
    
    // Display execution times
    std::cout << "\nExecution Times:" << std::endl;
    std::cout << std::setw(30) << std::left << "Task Name"
              << std::setw(15) << std::right << "Time (ms)"
              << std::setw(15) << "Return %" << std::endl;
    
    double total_time = 0.0;
    for (size_t i = 0; i < results_.size(); ++i) {
        const auto& [name, result] = results_[i];
        double time_ms = execution_times_[i].second;
        total_time += time_ms;
        
        std::cout << std::setw(30) << std::left << name
                  << std::setw(15) << std::right << std::fixed << std::setprecision(1) << time_ms
                  << std::setw(15) << std::fixed << std::setprecision(2) << result.total_return_
                  << std::endl;
    }
    
    std::cout << "\nTotal execution time: " << std::fixed << std::setprecision(1) 
              << total_time << " ms" << std::endl;
    
    if (results_.size() > 1) {
        double avg_time = total_time / results_.size();
        std::cout << "Average per task: " << std::fixed << std::setprecision(1) 
                  << avg_time << " ms" << std::endl;
        
        // Find best and worst performers
        auto max_it = std::max_element(results_.begin(), results_.end(),
            [](const auto& a, const auto& b) {
                return a.second.total_return_ < b.second.total_return_;
            });
        
        auto min_it = std::min_element(results_.begin(), results_.end(),
            [](const auto& a, const auto& b) {
                return a.second.total_return_ < b.second.total_return_;
            });
        
        std::cout << "\nBest performer: " << max_it->first 
                  << " (" << std::fixed << std::setprecision(2) 
                  << max_it->second.total_return_ << "%)" << std::endl;
        
        std::cout << "Worst performer: " << min_it->first 
                  << " (" << std::fixed << std::setprecision(2) 
                  << min_it->second.total_return_ << "%)" << std::endl;
    }
}

bool ParallelBacktestResult::generate_combined_html_report(const std::string& filename) const {
    std::lock_guard<std::mutex> lock(mutex_);
    
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }
    
    file << "<!DOCTYPE html>\n";
    file << "<html lang=\"zh-CN\">\n";
    file << "<head>\n";
    file << "    <meta charset=\"UTF-8\">\n";
    file << "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n";
    file << "    <title>Parallel Backtest Report</title>\n";
    file << "    <style>\n";
    file << "        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }\n";
    file << "        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }\n";
    file << "        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }\n";
    file << "        h2 { color: #34495e; margin-top: 30px; }\n";
    file << "        table { width: 100%; border-collapse: collapse; margin: 20px 0; }\n";
    file << "        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }\n";
    file << "        th { background-color: #f2f2f2; }\n";
    file << "        tr:hover { background-color: #f5f5f5; }\n";
    file << "        .good { color: #27ae60; }\n";
    file << "        .bad { color: #e74c3c; }\n";
    file << "        .summary { background: #e8f4fc; padding: 20px; border-radius: 5px; margin: 20px 0; }\n";
    file << "        .metric-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }\n";
    file << "        .metric-card { background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }\n";
    file << "    </style>\n";
    file << "</head>\n";
    file << "<body>\n";
    file << "    <div class=\"container\">\n";
    file << "        <h1>📊 Parallel Backtest Report</h1>\n";
    
    // Summary
    file << "        <div class=\"summary\">\n";
    file << "            <p><strong>Total Tasks:</strong> " << results_.size() << "</p>\n";
    
    if (!results_.empty()) {
        double total_time = 0.0;
        for (const auto& time : execution_times_) {
            total_time += time.second;
        }
        
        file << "            <p><strong>Total Execution Time:</strong> " 
             << std::fixed << std::setprecision(1) << total_time << " ms</p>\n";
        
        if (results_.size() > 1) {
            double avg_time = total_time / results_.size();
            file << "            <p><strong>Average Time per Task:</strong> "
                 << std::fixed << std::setprecision(1) << avg_time << " ms</p>\n";
        }
    }
    file << "        </div>\n";
    
    // Results table
    if (!results_.empty()) {
        file << "        <h2>Results Summary</h2>\n";
        file << "        <table>\n";
        file << "            <tr>\n";
        file << "                <th>Task Name</th>\n";
        file << "                <th>Execution Time (ms)</th>\n";
        file << "                <th>Total Return</th>\n";
        file << "                <th>Sharpe Ratio</th>\n";
        file << "                <th>Max Drawdown</th>\n";
        file << "            </tr>\n";
        
        for (size_t i = 0; i < results_.size(); ++i) {
            const auto& [name, result] = results_[i];
            double time_ms = execution_times_[i].second;
            double sharpe = result.calculate_sharpe_ratio();
            double max_dd = result.calculate_max_drawdown();
            
            std::string return_class = result.total_return_ >= 0 ? "good" : "bad";
            std::string dd_class = max_dd < 20.0 ? "good" : (max_dd < 40.0 ? "" : "bad");
            
            file << "            <tr>\n";
            file << "                <td>" << name << "</td>\n";
            file << "                <td>" << std::fixed << std::setprecision(1) << time_ms << "</td>\n";
            file << "                <td class=\"" << return_class << "\">" 
                 << std::fixed << std::setprecision(2) << result.total_return_ << "%</td>\n";
            file << "                <td>" << std::fixed << std::setprecision(3) << sharpe << "</td>\n";
            file << "                <td class=\"" << dd_class << "\">"
                 << std::fixed << std::setprecision(2) << max_dd << "%</td>\n";
            file << "            </tr>\n";
        }
        
        file << "        </table>\n";
        
        // Key metrics
        file << "        <h2>Key Metrics Summary</h2>\n";
        file << "        <div class=\"metric-grid\">\n";
        
        if (results_.size() > 1) {
            // Calculate statistics across all runs
            std::vector<double> returns;
            std::vector<double> sharpe_ratios;
            std::vector<double> max_drawdowns;
            
            for (const auto& [name, result] : results_) {
                returns.push_back(result.total_return_);
                sharpe_ratios.push_back(result.calculate_sharpe_ratio());
                max_drawdowns.push_back(result.calculate_max_drawdown());
            }
            
            auto avg_return = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
            auto avg_sharpe = std::accumulate(sharpe_ratios.begin(), sharpe_ratios.end(), 0.0) / sharpe_ratios.size();
            auto avg_dd = std::accumulate(max_drawdowns.begin(), max_drawdowns.end(), 0.0) / max_drawdowns.size();
            
            auto max_return = *std::max_element(returns.begin(), returns.end());
            auto min_return = *std::min_element(returns.begin(), returns.end());
            
            file << "            <div class=\"metric-card\">\n";
            file << "                <h3>Average Return</h3>\n";
            file << "                <p style=\"font-size: 24px; color: " 
                 << (avg_return >= 0 ? "#27ae60" : "#e74c3c") << ";\">"
                 << std::fixed << std::setprecision(2) << avg_return << "%</p>\n";
            file << "            </div>\n";
            
            file << "            <div class=\"metric-card\">\n";
            file << "                <h3>Best Return</h3>\n";
            file << "                <p style=\"font-size: 24px; color: #27ae60;\">"
                 << std::fixed << std::setprecision(2) << max_return << "%</p>\n";
            file << "            </div>\n";
            
            file << "            <div class=\"metric-card\">\n";
            file << "                <h3>Worst Return</h3>\n";
            file << "                <p style=\"font-size: 24px; color: #e74c3c;\">"
                 << std::fixed << std::setprecision(2) << min_return << "%</p>\n";
            file << "            </div>\n";
            
            file << "            <div class=\"metric-card\">\n";
            file << "                <h3>Average Sharpe</h3>\n";
            file << "                <p style=\"font-size: 24px;\">"
                 << std::fixed << std::setprecision(3) << avg_sharpe << "</p>\n";
            file << "            </div>\n";
        }
        
        file << "        </div>\n";
    }
    
    file << "        <hr>\n";
    file << "        <p style=\"text-align: center; color: #7f8c8d; font-size: 12px;\">\n";
    file << "            Report generated: " << __DATE__ << " " << __TIME__ 
         << " | ParallelBacktestEngine\n";
    file << "        </p>\n";
    file << "    </div>\n";
    file << "</body>\n";
    file << "</html>\n";
    
    file.close();
    return true;
}

bool ParallelBacktestResult::generate_combined_json_report(const std::string& filename) const {
    std::lock_guard<std::mutex> lock(mutex_);
    
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }
    
    file << "{\n";
    file << "  \"parallel_backtest_report\": {\n";
    file << "    \"total_tasks\": " << results_.size() << ",\n";
    
    if (!results_.empty()) {
        double total_time = 0.0;
        for (const auto& time : execution_times_) {
            total_time += time.second;
        }
        
        file << "    \"total_execution_time_ms\": " << std::fixed << std::setprecision(1) << total_time << ",\n";
        
        if (results_.size() > 1) {
            double avg_time = total_time / results_.size();
            file << "    \"average_time_per_task_ms\": " << std::fixed << std::setprecision(1) << avg_time << ",\n";
        }
        
        file << "    \"tasks\": [\n";
        
        for (size_t i = 0; i < results_.size(); ++i) {
            const auto& [name, result] = results_[i];
            double time_ms = execution_times_[i].second;
            
            file << "      {\n";
            file << "        \"name\": \"" << name << "\",\n";
            file << "        \"execution_time_ms\": " << std::fixed << std::setprecision(1) << time_ms << ",\n";
            file << "        \"total_return\": " << std::fixed << std::setprecision(2) << result.total_return_ << ",\n";
            file << "        \"sharpe_ratio\": " << std::fixed << std::setprecision(3) << result.calculate_sharpe_ratio() << ",\n";
            file << "        \"max_drawdown\": " << std::fixed << std::setprecision(2) << result.calculate_max_drawdown() << "\n";
            
            if (i < results_.size() - 1) {
                file << "      },\n";
            } else {
                file << "      }\n";
            }
        }
        
        file << "    ]\n";
    } else {
        file << "    \"tasks\": []\n";
    }
    
    file << "  }\n";
    file << "}\n";
    
    file.close();
    return true;
}

// ParallelBacktestEngine implementation
ParallelBacktestEngine::ParallelBacktestEngine(size_t num_threads)
    : completed_count_(0) {
    
    thread_pool_ = std::make_unique<core::ThreadPool>(num_threads);
}

ParallelBacktestEngine::~ParallelBacktestEngine() {
    wait_all();
}

void ParallelBacktestEngine::add_task(const ParallelBacktestTask& task) {
    tasks_.push_back(task);
}

void ParallelBacktestEngine::add_tasks(const std::vector<ParallelBacktestTask>& tasks) {
    tasks_.insert(tasks_.end(), tasks.begin(), tasks.end());
}

ParallelBacktestTask ParallelBacktestEngine::create_task(
    std::shared_ptr<BacktestEngine> engine,
    const std::string& name) {
    
    return ParallelBacktestTask(engine, name);
}

ParallelBacktestResult ParallelBacktestEngine::run(bool wait_for_completion) {
    ParallelBacktestResult all_results;
    std::vector<std::future<std::pair<BacktestResult, double>>> futures;
    
    // Reset completed count
    completed_count_.store(0);
    
    // Submit all tasks to thread pool
    for (const auto& task : tasks_) {
        auto future = thread_pool_->submit(
            [this, &task]() {
                return execute_task(task);
            }
        );
        futures.push_back(std::move(future));
    }
    
    if (wait_for_completion) {
        // Wait for all futures and collect results
        for (size_t i = 0; i < futures.size(); ++i) {
            try {
                auto [result, exec_time] = futures[i].get();
                std::string task_name = tasks_[i].task_name.empty() 
                                      ? "Task_" + std::to_string(i) 
                                      : tasks_[i].task_name;
                
                all_results.add_result(task_name, result, exec_time);
                completed_count_.fetch_add(1, std::memory_order_relaxed);
            } catch (const std::exception& e) {
                std::cerr << "Task " << i << " failed: " << e.what() << std::endl;
            }
        }
    } else {
        // For async execution, we need a different approach
        // This simple implementation doesn't support async collection
        // In a more complete implementation, we would store the futures
        // and provide a way to check completion and collect results later
        std::cerr << "Warning: Non-blocking run not fully implemented. "
                  << "Use run_async() instead." << std::endl;
    }
    
    return all_results;
}

std::future<ParallelBacktestResult> ParallelBacktestEngine::run_async() {
    // Return a future that will run in another thread
    return std::async(std::launch::async, [this]() {
        return run(true);
    });
}

void ParallelBacktestEngine::wait_all() {
    thread_pool_->wait_all();
}

size_t ParallelBacktestEngine::pending_tasks() const {
    return thread_pool_->pending_tasks();
}

size_t ParallelBacktestEngine::completed_tasks() const {
    return completed_count_.load(std::memory_order_relaxed);
}

size_t ParallelBacktestEngine::total_tasks() const {
    return tasks_.size();
}

void ParallelBacktestEngine::clear_tasks() {
    tasks_.clear();
}

std::pair<BacktestResult, double> ParallelBacktestEngine::execute_task(
    const ParallelBacktestTask& task) {
    
    auto start_time = high_resolution_clock::now();
    
    BacktestResult result;
    
    try {
        // Execute setup function if provided
        if (task.setup_func) {
            task.setup_func();
        }
        
        // Run the backtest
        // Note: This assumes BacktestEngine has a run() method
        // result = task.engine->run();
        
        // For now, create a dummy result
        result.total_return_ = 0.0;
        result.initial_capital_ = 100000.0;
        result.final_capital_ = 100000.0;
        
    } catch (const std::exception& e) {
        std::cerr << "Backtest execution failed: " << e.what() << std::endl;
    }
    
    auto end_time = high_resolution_clock::now();
    double exec_time_ms = duration_cast<duration<double, std::milli>>(
        end_time - start_time).count();
    
    return {result, exec_time_ms};
}

std::shared_ptr<BacktestEngine> ParallelBacktestEngine::clone_engine(
    std::shared_ptr<BacktestEngine> original) const {
    
    // Simple implementation: just return the original
    // In a real implementation, we would need to deep copy the engine
    return original;
}

} // namespace backtest
} // namespace pplustrader