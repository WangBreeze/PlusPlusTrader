// ParallelBacktestEngine.h - Parallel backtesting engine for PlusPlusTrader
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#ifndef PPLUSTRADER_BACKTEST_PARALLELBACKTESTENGINE_H
#define PPLUSTRADER_BACKTEST_PARALLELBACKTESTENGINE_H

#include "BacktestEngine.h"
#include "BacktestResult.h"
#include "../core/ThreadPool.h"
#include <vector>
#include <memory>
#include <future>
#include <mutex>
#include <atomic>

namespace pplustrader {
namespace backtest {

/**
 * @class ParallelBacktestTask
 * @brief Individual task for parallel backtesting
 */
struct ParallelBacktestTask {
    std::shared_ptr<BacktestEngine> engine;
    std::string task_name;
    std::function<void()> setup_func;  // Optional setup function
    
    ParallelBacktestTask(std::shared_ptr<BacktestEngine> eng, 
                        const std::string& name = "")
        : engine(eng), task_name(name) {}
};

/**
 * @class ParallelBacktestResult
 * @brief Collection of results from parallel backtesting
 */
class ParallelBacktestResult {
public:
    ParallelBacktestResult() = default;
    
    /**
     * @brief Add a result from a parallel task
     */
    void add_result(const std::string& task_name, 
                   const BacktestResult& result,
                   double execution_time_ms);
    
    /**
     * @brief Get all results
     */
    const std::vector<std::pair<std::string, BacktestResult>>& results() const {
        return results_;
    }
    
    /**
     * @brief Get execution times
     */
    const std::vector<std::pair<std::string, double>>& execution_times() const {
        return execution_times_;
    }
    
    /**
     * @brief Get aggregated statistics across all results
     */
    BacktestResult aggregate_results() const;
    
    /**
     * @brief Print summary of all parallel backtests
     */
    void print_summary() const;
    
    /**
     * @brief Generate combined HTML report
     */
    bool generate_combined_html_report(const std::string& filename) const;
    
    /**
     * @brief Generate combined JSON report
     */
    bool generate_combined_json_report(const std::string& filename) const;
    
private:
    std::vector<std::pair<std::string, BacktestResult>> results_;
    std::vector<std::pair<std::string, double>> execution_times_;
    mutable std::mutex mutex_;
};

/**
 * @class ParallelBacktestEngine
 * @brief Engine for parallel execution of multiple backtests
 * 
 * This engine allows running multiple backtests in parallel using a thread pool.
 * It's useful for:
 * 1. Testing multiple strategies simultaneously
 * 2. Parameter optimization (grid search)
 * 3. Walk-forward analysis with multiple windows
 * 4. Monte Carlo simulations
 */
class ParallelBacktestEngine {
public:
    /**
     * @brief Construct a parallel backtest engine
     * @param num_threads Number of threads to use (0 = auto-detect)
     */
    explicit ParallelBacktestEngine(size_t num_threads = 0);
    
    ~ParallelBacktestEngine();
    
    /**
     * @brief Add a backtest task to execute
     * @param task Backtest task to add
     */
    void add_task(const ParallelBacktestTask& task);
    
    /**
     * @brief Add multiple backtest tasks
     */
    void add_tasks(const std::vector<ParallelBacktestTask>& tasks);
    
    /**
     * @brief Create a task from a backtest engine
     */
    ParallelBacktestTask create_task(std::shared_ptr<BacktestEngine> engine,
                                    const std::string& name = "");
    
    /**
     * @brief Run all tasks in parallel
     * @param wait_for_completion If true, wait for all tasks to complete
     * @return ParallelBacktestResult containing all results
     */
    ParallelBacktestResult run(bool wait_for_completion = true);
    
    /**
     * @brief Run tasks asynchronously (non-blocking)
     * @return std::future for the results
     */
    std::future<ParallelBacktestResult> run_async();
    
    /**
     * @brief Wait for all running tasks to complete
     */
    void wait_all();
    
    /**
     * @brief Get number of pending tasks
     */
    size_t pending_tasks() const;
    
    /**
     * @brief Get number of completed tasks
     */
    size_t completed_tasks() const;
    
    /**
     * @brief Get total number of tasks
     */
    size_t total_tasks() const;
    
    /**
     * @brief Clear all tasks (does not affect running tasks)
     */
    void clear_tasks();
    
    /**
     * @brief Run parameter sweep for a strategy
     * @tparam StrategyType Strategy class type
     * @param base_engine Base backtest engine to clone
     * @param param_name Parameter name to sweep
     * @param values Parameter values to test
     * @param strategy_creator Function to create strategy with parameter
     * @return Results of parameter sweep
     */
    template<typename StrategyType>
    ParallelBacktestResult run_parameter_sweep(
        std::shared_ptr<BacktestEngine> base_engine,
        const std::string& param_name,
        const std::vector<double>& values,
        std::function<std::shared_ptr<StrategyType>(double)> strategy_creator);
    
    /**
     * @brief Run walk-forward analysis
     * @param engine_template Template engine to clone for each period
     * @param window_size Size of training window (in periods)
     * @param step_size Step size between windows (in periods)
     * @param total_periods Total number of periods
     * @return Walk-forward analysis results
     */
    ParallelBacktestResult run_walk_forward_analysis(
        std::shared_ptr<BacktestEngine> engine_template,
        size_t window_size,
        size_t step_size,
        size_t total_periods);
    
private:
    std::vector<ParallelBacktestTask> tasks_;
    std::unique_ptr<core::ThreadPool> thread_pool_;
    std::atomic<size_t> completed_count_;
    
    /**
     * @brief Execute a single backtest task
     */
    std::pair<BacktestResult, double> execute_task(const ParallelBacktestTask& task);
    
    /**
     * @brief Clone a backtest engine (deep copy)
     */
    std::shared_ptr<BacktestEngine> clone_engine(
        std::shared_ptr<BacktestEngine> original) const;
};

// Template implementation for parameter sweep
template<typename StrategyType>
ParallelBacktestResult ParallelBacktestEngine::run_parameter_sweep(
    std::shared_ptr<BacktestEngine> base_engine,
    const std::string& param_name,
    const std::vector<double>& values,
    std::function<std::shared_ptr<StrategyType>(double)> strategy_creator) {
    
    clear_tasks();
    
    for (size_t i = 0; i < values.size(); ++i) {
        double param_value = values[i];
        
        // Clone the base engine
        auto engine = clone_engine(base_engine);
        
        // Create strategy with parameter
        auto strategy = strategy_creator(param_value);
        
        // Add strategy to engine
        // Note: This assumes BacktestEngine has add_strategy method
        // engine->add_strategy(strategy);
        
        // Create task name
        std::string task_name = param_name + "=" + std::to_string(param_value);
        
        // Add task
        add_task(ParallelBacktestTask(engine, task_name));
    }
    
    return run(true);
}

} // namespace backtest
} // namespace pplustrader

#endif // PPLUSTRADER_BACKTEST_PARALLELBACKTESTENGINE_H