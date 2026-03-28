// ThreadPool.h - Simple thread pool implementation for PlusPlusTrader
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#ifndef PPLUSTRADER_CORE_THREADPOOL_H
#define PPLUSTRADER_CORE_THREADPOOL_H

#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <future>
#include <functional>
#include <memory>
#include <stdexcept>
#include <atomic>

namespace pplustrader {
namespace core {

/**
 * @class ThreadPool
 * @brief Simple thread pool implementation for parallel backtesting
 * 
 * This thread pool allows submitting tasks (callable objects) that are
 * executed by worker threads. It's useful for parallelizing backtesting
 * of multiple strategies or parameter sweeps.
 */
class ThreadPool {
public:
    /**
     * @brief Construct a thread pool with specified number of threads
     * @param num_threads Number of worker threads (0 = hardware_concurrency)
     */
    explicit ThreadPool(size_t num_threads = 0);
    
    /**
     * @brief Destructor - waits for all tasks to complete
     */
    ~ThreadPool();
    
    // Delete copy and move constructors
    ThreadPool(const ThreadPool&) = delete;
    ThreadPool& operator=(const ThreadPool&) = delete;
    ThreadPool(ThreadPool&&) = delete;
    ThreadPool& operator=(ThreadPool&&) = delete;
    
    /**
     * @brief Submit a task to the thread pool
     * @tparam F Function type
     * @tparam Args Argument types
     * @param f Callable object (function, lambda, etc.)
     * @param args Arguments to pass to the callable
     * @return std::future for the task result
     */
    template<typename F, typename... Args>
    auto submit(F&& f, Args&&... args) 
        -> std::future<typename std::invoke_result<F, Args...>::type>;
    
    /**
     * @brief Get number of worker threads
     * @return Number of threads in the pool
     */
    size_t thread_count() const { return workers_.size(); }
    
    /**
     * @brief Get number of pending tasks
     * @return Number of tasks waiting in the queue
     */
    size_t pending_tasks() const;
    
    /**
     * @brief Wait for all tasks to complete
     */
    void wait_all();
    
    /**
     * @brief Check if thread pool is stopped
     * @return True if stopped
     */
    bool stopped() const { return stop_.load(); }
    
    /**
     * @brief Stop the thread pool (waits for current tasks to complete)
     */
    void stop();
    
    /**
     * @brief Get recommended thread count for the system
     * @return Recommended number of threads (hardware_concurrency - 1)
     */
    static size_t recommended_thread_count();
    
private:
    // Worker threads
    std::vector<std::thread> workers_;
    
    // Task queue
    std::queue<std::function<void()>> tasks_;
    
    // Synchronization
    mutable std::mutex queue_mutex_;
    std::condition_variable condition_;
    
    // Stop flag
    std::atomic<bool> stop_;
    
    // Pending task counter
    std::atomic<size_t> pending_count_;
    
    /**
     * @brief Worker thread function
     */
    void worker_loop();
};

// Template implementation
template<typename F, typename... Args>
auto ThreadPool::submit(F&& f, Args&&... args) 
    -> std::future<typename std::invoke_result<F, Args...>::type> {
    
    using return_type = typename std::invoke_result<F, Args...>::type;
    
    // Create a packaged_task with the function and arguments
    auto task = std::make_shared<std::packaged_task<return_type()>>(
        std::bind(std::forward<F>(f), std::forward<Args>(args)...)
    );
    
    // Get future for the task result
    std::future<return_type> result = task->get_future();
    
    {
        // Lock the queue
        std::unique_lock<std::mutex> lock(queue_mutex_);
        
        // Check if pool is stopped
        if (stop_.load()) {
            throw std::runtime_error("ThreadPool is stopped, cannot submit tasks");
        }
        
        // Add task to queue
        tasks_.emplace([task]() { (*task)(); });
        pending_count_.fetch_add(1, std::memory_order_relaxed);
    }
    
    // Notify one worker thread
    condition_.notify_one();
    
    return result;
}

} // namespace core
} // namespace pplustrader

#endif // PPLUSTRADER_CORE_THREADPOOL_H