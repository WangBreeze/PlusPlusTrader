// ThreadPool.cpp - Thread pool implementation
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#include "ThreadPool.h"
#include <algorithm>
#include <iostream>

namespace pplustrader {
namespace core {

ThreadPool::ThreadPool(size_t num_threads) 
    : stop_(false), pending_count_(0) {
    
    // Determine number of threads
    size_t thread_count = num_threads;
    if (thread_count == 0) {
        thread_count = recommended_thread_count();
    }
    
    // Create worker threads
    workers_.reserve(thread_count);
    for (size_t i = 0; i < thread_count; ++i) {
        workers_.emplace_back(&ThreadPool::worker_loop, this);
    }
    
    // std::cout << "ThreadPool created with " << thread_count << " threads" << std::endl;
}

ThreadPool::~ThreadPool() {
    stop();
}

void ThreadPool::worker_loop() {
    while (true) {
        std::function<void()> task;
        
        {
            // Wait for a task or stop signal
            std::unique_lock<std::mutex> lock(queue_mutex_);
            condition_.wait(lock, [this]() {
                return stop_.load() || !tasks_.empty();
            });
            
            // Check if we should stop
            if (stop_.load() && tasks_.empty()) {
                return;
            }
            
            // Get the next task
            task = std::move(tasks_.front());
            tasks_.pop();
        }
        
        // Execute the task
        try {
            task();
            pending_count_.fetch_sub(1, std::memory_order_relaxed);
        } catch (const std::exception& e) {
            std::cerr << "ThreadPool task exception: " << e.what() << std::endl;
            pending_count_.fetch_sub(1, std::memory_order_relaxed);
        } catch (...) {
            std::cerr << "ThreadPool task unknown exception" << std::endl;
            pending_count_.fetch_sub(1, std::memory_order_relaxed);
        }
    }
}

size_t ThreadPool::pending_tasks() const {
    return pending_count_.load(std::memory_order_relaxed);
}

void ThreadPool::wait_all() {
    // Wait until no pending tasks
    while (pending_tasks() > 0) {
        std::this_thread::yield();
    }
}

void ThreadPool::stop() {
    // Set stop flag
    if (stop_.exchange(true)) {
        return;  // Already stopped
    }
    
    // Notify all threads
    condition_.notify_all();
    
    // Join all threads
    for (std::thread& worker : workers_) {
        if (worker.joinable()) {
            worker.join();
        }
    }
    
    // Clear any remaining tasks
    {
        std::unique_lock<std::mutex> lock(queue_mutex_);
        while (!tasks_.empty()) {
            tasks_.pop();
        }
    }
    
    pending_count_.store(0, std::memory_order_relaxed);
}

size_t ThreadPool::recommended_thread_count() {
    // Use hardware_concurrency, but leave one core for system
    size_t hw_threads = std::thread::hardware_concurrency();
    if (hw_threads == 0) {
        // If hardware_concurrency returns 0, use a reasonable default
        return 4;
    }
    
    // Leave at least one core for the system
    return std::max(static_cast<size_t>(1), hw_threads - 1);
}

} // namespace core
} // namespace pplustrader