// TestUtils.h - Simple testing utilities for PlusPlusTrader
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#ifndef PPLUSTRADER_TEST_TESTUTILS_H
#define PPLUSTRADER_TEST_TESTUTILS_H

#include <iostream>
#include <string>
#include <cmath>
#include <sstream>

namespace pplustrader {
namespace test {

/**
 * @class TestCase
 * @brief Simple test case abstraction
 */
class TestCase {
public:
    TestCase(const std::string& name) : name_(name), passed_(0), failed_(0) {}
    
    virtual ~TestCase() = default;
    
    /**
     * @brief Run the test case
     * @return True if all tests passed
     */
    virtual bool run() {
        std::cout << "Running test case: " << name_ << std::endl;
        passed_ = 0;
        failed_ = 0;
        run_tests();
        print_summary();
        return failed_ == 0;
    }
    
    /**
     * @brief Get test case name
     */
    std::string name() const { return name_; }
    
    /**
     * @brief Get number of passed tests
     */
    int passed() const { return passed_; }
    
    /**
     * @brief Get number of failed tests
     */
    int failed() const { return failed_; }
    
protected:
    /**
     * @brief Implement test logic in derived classes
     */
    virtual void run_tests() = 0;
    
    /**
     * @brief Assert that condition is true
     */
    void assert_true(bool condition, const std::string& message) {
        if (condition) {
            ++passed_;
        } else {
            ++failed_;
            std::cout << "  FAIL: " << message << std::endl;
        }
    }
    
    /**
     * @brief Assert that condition is false
     */
    void assert_false(bool condition, const std::string& message) {
        assert_true(!condition, message);
    }
    
    /**
     * @brief Assert that two values are equal
     */
    template<typename T>
    void assert_equal(T expected, T actual, const std::string& message) {
        if (expected == actual) {
            ++passed_;
        } else {
            ++failed_;
            std::cout << "  FAIL: " << message 
                      << " (expected: " << expected 
                      << ", actual: " << actual << ")" << std::endl;
        }
    }
    
    /**
     * @brief Assert that two floating point values are equal within tolerance
     */
    void assert_double_equal(double expected, double actual, double tolerance, 
                           const std::string& message) {
        if (std::abs(expected - actual) <= tolerance) {
            ++passed_;
        } else {
            ++failed_;
            std::cout << "  FAIL: " << message 
                      << " (expected: " << expected 
                      << ", actual: " << actual 
                      << ", tolerance: " << tolerance << ")" << std::endl;
        }
    }
    
    /**
     * @brief Assert that value is within range
     */
    void assert_in_range(double value, double min, double max, 
                        const std::string& message) {
        if (value >= min && value <= max) {
            ++passed_;
        } else {
            ++failed_;
            std::cout << "  FAIL: " << message 
                      << " (value: " << value 
                      << ", range: [" << min << ", " << max << "])" << std::endl;
        }
    }
    
    /**
     * @brief Assert that code throws expected exception
     */
    template<typename ExceptionType>
    void assert_throws(void (*func)(), const std::string& message) {
        try {
            func();
            ++failed_;
            std::cout << "  FAIL: " << message 
                      << " (expected exception not thrown)" << std::endl;
        } catch (const ExceptionType&) {
            ++passed_;
        } catch (...) {
            ++failed_;
            std::cout << "  FAIL: " << message 
                      << " (wrong exception type thrown)" << std::endl;
        }
    }
    
private:
    void print_summary() const {
        std::cout << "  Summary: " << passed_ << " passed, " 
                  << failed_ << " failed" << std::endl;
        if (failed_ == 0) {
            std::cout << "  ✅ All tests passed!" << std::endl;
        } else {
            std::cout << "  ❌ " << failed_ << " test(s) failed!" << std::endl;
        }
    }
    
    std::string name_;
    int passed_;
    int failed_;
};

/**
 * @class TestSuite
 * @brief Collection of test cases
 */
class TestSuite {
public:
    TestSuite(const std::string& name) : name_(name), total_passed_(0), total_failed_(0) {}
    
    /**
     * @brief Add a test case to the suite
     */
    void add_test_case(TestCase* test_case) {
        test_cases_.push_back(test_case);
    }
    
    /**
     * @brief Run all test cases in the suite
     * @return True if all tests passed
     */
    bool run_all() {
        std::cout << "\n========================================" << std::endl;
        std::cout << "Running test suite: " << name_ << std::endl;
        std::cout << "========================================" << std::endl;
        
        total_passed_ = 0;
        total_failed_ = 0;
        
        for (auto* test_case : test_cases_) {
            if (test_case->run()) {
                total_passed_ += test_case->passed();
            } else {
                total_failed_ += test_case->failed();
            }
        }
        
        print_final_summary();
        return total_failed_ == 0;
    }
    
    /**
     * @brief Get total number of passed tests
     */
    int total_passed() const { return total_passed_; }
    
    /**
     * @brief Get total number of failed tests
     */
    int total_failed() const { return total_failed_; }
    
private:
    void print_final_summary() const {
        std::cout << "\n========================================" << std::endl;
        std::cout << "Test Suite Summary: " << name_ << std::endl;
        std::cout << "========================================" << std::endl;
        std::cout << "Total test cases: " << test_cases_.size() << std::endl;
        std::cout << "Total tests passed: " << total_passed_ << std::endl;
        std::cout << "Total tests failed: " << total_failed_ << std::endl;
        
        if (total_failed_ == 0) {
            std::cout << "\n🎉 All test suites passed successfully!" << std::endl;
        } else {
            std::cout << "\n❌ Some tests failed. Please review the failures." << std::endl;
        }
    }
    
    std::string name_;
    std::vector<TestCase*> test_cases_;
    int total_passed_;
    int total_failed_;
};

// Helper macros for easier test writing
#define TEST_CASE_BEGIN(name) class TestCase_##name : public pplustrader::test::TestCase { \
public: \
    TestCase_##name() : TestCase(#name) {} \
protected: \
    void run_tests() override {
    
#define TEST_CASE_END(name) } }; \
    static TestCase_##name test_case_instance_##name;

#define ASSERT_TRUE(cond, msg) assert_true(cond, msg)
#define ASSERT_FALSE(cond, msg) assert_false(cond, msg)
#define ASSERT_EQUAL(expected, actual, msg) assert_equal(expected, actual, msg)
#define ASSERT_DOUBLE_EQUAL(expected, actual, tolerance, msg) \
    assert_double_equal(expected, actual, tolerance, msg)
#define ASSERT_IN_RANGE(value, min, max, msg) assert_in_range(value, min, max, msg)

} // namespace test
} // namespace pplustrader

#endif // PPLUSTRADER_TEST_TESTUTILS_H