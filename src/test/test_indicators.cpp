// test_indicators.cpp - Unit tests for technical indicators
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#include "test/TestUtils.h"
#include "indicators/MA.h"
#include "indicators/EMA.h"
#include "indicators/MACD.h"
#include "indicators/RSI.h"
#include "indicators/MFI.h"
#include "indicators/IndicatorFactory.h"
#include <vector>
#include <cmath>

using namespace pplustrader;
using namespace pplustrader::indicators;
using namespace pplustrader::test;

// Test case for Moving Average (MA)
TEST_CASE_BEGIN(TestMovingAverage)
    void test_basic_functionality() {
        MA ma(5);  // 5-period moving average
        
        ASSERT_FALSE(ma.ready(), "MA should not be ready initially");
        ASSERT_EQUAL(5, ma.period(), "Period should be 5");
        ASSERT_EQUAL("MA", ma.name(), "Name should be 'MA'");
        
        // Add values
        ma.update(10.0);
        ASSERT_FALSE(ma.ready(), "MA not ready after 1 value");
        
        ma.update(20.0);
        ma.update(30.0);
        ma.update(40.0);
        ma.update(50.0);  // 5th value
        
        ASSERT_TRUE(ma.ready(), "MA should be ready after 5 values");
        
        // Expected average: (10+20+30+40+50)/5 = 30.0
        ASSERT_DOUBLE_EQUAL(30.0, ma.value(), 0.001, "MA value should be 30.0");
        
        // Add another value, should drop the oldest
        ma.update(60.0);
        ASSERT_TRUE(ma.ready(), "MA should still be ready");
        // Now values: 20,30,40,50,60 = average 40.0
        ASSERT_DOUBLE_EQUAL(40.0, ma.value(), 0.001, "MA value should be 40.0 after update");
    }
    
    void test_reset_functionality() {
        MA ma(3);
        
        ma.update(10.0);
        ma.update(20.0);
        ma.update(30.0);
        
        ASSERT_TRUE(ma.ready(), "MA should be ready");
        ASSERT_DOUBLE_EQUAL(20.0, ma.value(), 0.001, "MA value should be 20.0");
        
        ma.reset();
        ASSERT_FALSE(ma.ready(), "MA should not be ready after reset");
        
        ma.update(100.0);
        ASSERT_FALSE(ma.ready(), "MA not ready after reset and 1 value");
    }
    
    void test_edge_cases() {
        // Test with period 1
        MA ma1(1);
        ma1.update(42.0);
        ASSERT_TRUE(ma1.ready(), "MA with period 1 should be ready after 1 value");
        ASSERT_DOUBLE_EQUAL(42.0, ma1.value(), 0.001, "MA with period 1 should return the value");
        
        // Test with invalid period (should use default)
        MA ma_default(0);
        ASSERT_EQUAL(10, ma_default.period(), "Invalid period should default to 10");
        
        // Test with negative values
        MA ma3(3);
        ma3.update(-10.0);
        ma3.update(-20.0);
        ma3.update(-30.0);
        ASSERT_DOUBLE_EQUAL(-20.0, ma3.value(), 0.001, "MA should handle negative values");
    }
    
    void run_tests() override {
        test_basic_functionality();
        test_reset_functionality();
        test_edge_cases();
    }
TEST_CASE_END(TestMovingAverage)

// Test case for Exponential Moving Average (EMA)
TEST_CASE_BEGIN(TestExponentialMovingAverage)
    void test_basic_functionality() {
        EMA ema(3);
        
        ASSERT_FALSE(ema.ready(), "EMA should not be ready initially");
        ASSERT_EQUAL(3, ema.period(), "Period should be 3");
        ASSERT_EQUAL("EMA", ema.name(), "Name should be 'EMA'");
        
        // Simple test with known values
        // For EMA with period 3, alpha = 2/(3+1) = 0.5
        // Values: 10, 20, 30
        ema.update(10.0);  // First value, EMA = 10
        ema.update(20.0);  // EMA = 0.5*20 + 0.5*10 = 15
        ema.update(30.0);  // EMA = 0.5*30 + 0.5*15 = 22.5
        
        ASSERT_TRUE(ema.ready(), "EMA should be ready after 3 values");
        ASSERT_DOUBLE_EQUAL(22.5, ema.value(), 0.001, "EMA value should be 22.5");
        
        // Next value
        ema.update(40.0);  // EMA = 0.5*40 + 0.5*22.5 = 31.25
        ASSERT_DOUBLE_EQUAL(31.25, ema.value(), 0.001, "EMA value should be 31.25");
    }
    
    void run_tests() override {
        test_basic_functionality();
    }
TEST_CASE_END(TestExponentialMovingAverage)

// Test case for RSI
TEST_CASE_BEGIN(TestRSI)
    void test_basic_functionality() {
        RSI rsi(14);  // Standard 14-period RSI
        
        ASSERT_EQUAL(14, rsi.period(), "Period should be 14");
        ASSERT_EQUAL("RSI", rsi.name(), "Name should be 'RSI'");
        
        // RSI should be in range [0, 100]
        std::vector<double> prices = {
            44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84,
            46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 46.41,
            46.22, 45.64, 46.21, 46.25, 45.71, 46.45, 45.78, 45.35, 44.03
        };
        
        for (size_t i = 0; i < prices.size(); ++i) {
            rsi.update(prices[i]);
            
            if (rsi.ready()) {
                double rsi_value = rsi.value();
                ASSERT_IN_RANGE(rsi_value, 0.0, 100.0, 
                               "RSI should be in range [0, 100]");
                
                // Check if RSI identifies overbought/oversold
                if (rsi_value > 70.0) {
                    // std::cout << "  Overbought signal at step " << i << ": " << rsi_value << std::endl;
                } else if (rsi_value < 30.0) {
                    // std::cout << "  Oversold signal at step " << i << ": " << rsi_value << std::endl;
                }
            }
        }
        
        // After all updates, RSI should be ready
        ASSERT_TRUE(rsi.ready(), "RSI should be ready after enough data");
        ASSERT_IN_RANGE(rsi.value(), 0.0, 100.0, "Final RSI should be in valid range");
    }
    
    void test_reset() {
        RSI rsi(5);
        
        for (int i = 1; i <= 10; ++i) {
            rsi.update(100.0 + i);
        }
        
        ASSERT_TRUE(rsi.ready(), "RSI should be ready");
        
        rsi.reset();
        ASSERT_FALSE(rsi.ready(), "RSI should not be ready after reset");
        
        // After reset, value should be 50.0 (neutral)
        ASSERT_DOUBLE_EQUAL(50.0, rsi.value(), 0.001, "RSI value should be 50.0 after reset");
    }
    
    void run_tests() override {
        test_basic_functionality();
        test_reset();
    }
TEST_CASE_END(TestRSI)

// Test case for MFI
TEST_CASE_BEGIN(TestMFI)
    void test_basic_functionality() {
        MFI mfi(14);  // Standard 14-period MFI
        
        ASSERT_EQUAL(14, mfi.period(), "Period should be 14");
        ASSERT_EQUAL("MFI", mfi.name(), "Name should be 'MFI'");
        
        // MFI should be in range [0, 100]
        // Generate sample data with typical price and volume patterns
        for (int i = 0; i < 30; ++i) {
            double high = 100.0 + std::sin(i * 0.3) * 5.0;
            double low = 95.0 + std::sin(i * 0.3) * 5.0;
            double close = 97.5 + std::sin(i * 0.3) * 5.0;
            double volume = 10000.0 + std::cos(i * 0.2) * 2000.0;
            
            mfi.update(high, low, close, volume);
            
            if (mfi.ready()) {
                double mfi_value = mfi.value();
                ASSERT_IN_RANGE(mfi_value, 0.0, 100.0, 
                               "MFI should be in range [0, 100]");
                
                // Check MFI interpretation
                if (mfi_value > 80.0) {
                    // std::cout << "  Overbought (MFI > 80) at step " << i << ": " << mfi_value << std::endl;
                } else if (mfi_value < 20.0) {
                    // std::cout << "  Oversold (MFI < 20) at step " << i << ": " << mfi_value << std::endl;
                }
            }
        }
        
        ASSERT_TRUE(mfi.ready(), "MFI should be ready after enough data");
        ASSERT_IN_RANGE(mfi.value(), 0.0, 100.0, "Final MFI should be in valid range");
    }
    
    void test_batch_calculation() {
        std::vector<double> highs, lows, closes, volumes;
        
        // Generate 20 data points
        for (int i = 0; i < 20; ++i) {
            highs.push_back(100.0 + i * 0.5);
            lows.push_back(95.0 + i * 0.5);
            closes.push_back(97.5 + i * 0.5);
            volumes.push_back(10000.0 + i * 500.0);
        }
        
        auto mfi_values = MFI::calculate(highs, lows, closes, volumes, 5);
        
        ASSERT_EQUAL(highs.size(), mfi_values.size(), 
                    "Batch calculation should return same number of values");
        
        for (size_t i = 0; i < mfi_values.size(); ++i) {
            ASSERT_IN_RANGE(mfi_values[i], 0.0, 100.0,
                           "Batch MFI values should be in range [0, 100]");
        }
    }
    
    void run_tests() override {
        test_basic_functionality();
        test_batch_calculation();
    }
TEST_CASE_END(TestMFI)

// Test case for IndicatorFactory
TEST_CASE_BEGIN(TestIndicatorFactory)
    void test_factory_creation() {
        // Test creating different indicator types
        auto ma = IndicatorFactory::create_indicator(IndicatorType::MA, 10);
        ASSERT_TRUE(ma != nullptr, "Should create MA indicator");
        ASSERT_EQUAL("MA", ma->name(), "Factory should create MA indicator");
        
        auto ema = IndicatorFactory::create_indicator(IndicatorType::EMA, 10);
        ASSERT_TRUE(ema != nullptr, "Should create EMA indicator");
        ASSERT_EQUAL("EMA", ema->name(), "Factory should create EMA indicator");
        
        auto rsi = IndicatorFactory::create_indicator(IndicatorType::RSI, 14);
        ASSERT_TRUE(rsi != nullptr, "Should create RSI indicator");
        ASSERT_EQUAL("RSI", rsi->name(), "Factory should create RSI indicator");
        
        auto mfi = IndicatorFactory::create_indicator(IndicatorType::MFI, 14);
        ASSERT_TRUE(mfi != nullptr, "Should create MFI indicator");
        ASSERT_EQUAL("MFI", mfi->name(), "Factory should create MFI indicator");
    }
    
    void test_indicator_functionality() {
        // Test that factory-created indicators work correctly
        auto ma = IndicatorFactory::create_indicator(IndicatorType::MA, 3);
        
        ma->update(10.0);
        ma->update(20.0);
        ma->update(30.0);
        
        ASSERT_TRUE(ma->ready(), "Factory-created MA should be ready");
        ASSERT_DOUBLE_EQUAL(20.0, ma->value(), 0.001,
                           "Factory-created MA should calculate correctly");
    }
    
    void run_tests() override {
        test_factory_creation();
        test_indicator_functionality();
    }
TEST_CASE_END(TestIndicatorFactory)

// Main test runner
int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "Technical Indicators Unit Tests" << std::endl;
    std::cout << "Date: 2026-03-15" << std::endl;
    std::cout << "========================================" << std::endl;
    
    TestSuite suite("Technical Indicators Test Suite");
    
    // Register test cases
    suite.add_test_case(&test_case_instance_TestMovingAverage);
    suite.add_test_case(&test_case_instance_TestExponentialMovingAverage);
    suite.add_test_case(&test_case_instance_TestRSI);
    suite.add_test_case(&test_case_instance_TestMFI);
    suite.add_test_case(&test_case_instance_TestIndicatorFactory);
    
    bool all_passed = suite.run_all();
    
    std::cout << "\n========================================" << std::endl;
    std::cout << "Test Run Completed" << std::endl;
    std::cout << "========================================" << std::endl;
    
    if (all_passed) {
        std::cout << "🎉 All indicator tests passed!" << std::endl;
        return 0;
    } else {
        std::cout << "❌ Some indicator tests failed." << std::endl;
        return 1;
    }
}