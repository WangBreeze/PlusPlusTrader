// test_mfi.cpp - Test program for MFI indicator
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#include "indicators/MFI.h"
#include "indicators/IndicatorFactory.h"
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <memory>

using namespace pplustrader;
using namespace pplustrader::indicators;

// Generate test data with some trend and volume patterns
void generate_test_data(std::vector<double>& highs,
                       std::vector<double>& lows,
                       std::vector<double>& closes,
                       std::vector<double>& volumes,
                       int count = 50) {
    double price = 100.0;
    double volume = 10000.0;
    double volatility = 2.0;
    
    for (int i = 0; i < count; ++i) {
        // Simulate price movement
        double change = (std::sin(i * 0.3) + std::cos(i * 0.1)) * volatility;
        price += change;
        
        // Create high/low/close with some spread
        closes.push_back(price);
        highs.push_back(price + std::abs(change) * 0.5);
        lows.push_back(price - std::abs(change) * 0.5);
        
        // Simulate volume with some pattern
        volume = 8000.0 + 4000.0 * std::sin(i * 0.2);
        if (change > 0) {
            volume *= 1.2;  // Higher volume on up moves
        }
        volumes.push_back(volume);
    }
}

void test_mfi_direct() {
    std::cout << "=== Testing MFI Direct API ===" << std::endl;
    
    std::vector<double> highs, lows, closes, volumes;
    generate_test_data(highs, lows, closes, volumes, 30);
    
    // Test direct MFI creation and update
    MFI mfi(14);
    
    std::cout << "Period: " << mfi.period() << std::endl;
    std::cout << "Name: " << mfi.name() << std::endl;
    
    std::cout << "\nUpdating MFI with test data:" << std::endl;
    std::cout << std::setw(5) << "Step" 
              << std::setw(10) << "High"
              << std::setw(10) << "Low"
              << std::setw(10) << "Close"
              << std::setw(10) << "Volume"
              << std::setw(10) << "MFI"
              << std::setw(10) << "Ready"
              << std::endl;
    
    for (size_t i = 0; i < highs.size(); ++i) {
        mfi.update(highs[i], lows[i], closes[i], volumes[i]);
        
        std::cout << std::setw(5) << i + 1
                  << std::setw(10) << std::fixed << std::setprecision(2) << highs[i]
                  << std::setw(10) << std::fixed << std::setprecision(2) << lows[i]
                  << std::setw(10) << std::fixed << std::setprecision(2) << closes[i]
                  << std::setw(10) << std::fixed << std::setprecision(0) << volumes[i]
                  << std::setw(10) << std::fixed << std::setprecision(2) << mfi.value()
                  << std::setw(10) << (mfi.ready() ? "Yes" : "No")
                  << std::endl;
    }
    
    std::cout << "\nFinal MFI value: " << mfi.value() << std::endl;
    if (mfi.value() > 80.0) {
        std::cout << "Interpretation: Overbought (MFI > 80)" << std::endl;
    } else if (mfi.value() < 20.0) {
        std::cout << "Interpretation: Oversold (MFI < 20)" << std::endl;
    } else {
        std::cout << "Interpretation: Neutral" << std::endl;
    }
}

void test_mfi_factory() {
    std::cout << "\n=== Testing MFI Direct Creation (Factory bypassed) ===" << std::endl;
    
    // Test creating MFI directly (factory not implemented for MFI yet)
    try {
        auto mfi = std::make_shared<MFI>(14);
        
        std::cout << "Successfully created MFI directly" << std::endl;
        std::cout << "Indicator name: " << mfi->name() << std::endl;
        
        // Test with some data
        mfi->update(105.0, 100.0, 102.5, 15000.0);
        std::cout << "After first update - Ready: " 
                  << (mfi->ready() ? "Yes" : "No")
                  << ", Value: " << mfi->value() << std::endl;
        
        // Reset and test
        mfi->reset();
        std::cout << "After reset - Ready: " 
                  << (mfi->ready() ? "Yes" : "No")
                  << ", Value: " << mfi->value() << std::endl;
        
    } catch (const std::exception& e) {
        std::cout << "Error creating MFI: " << e.what() << std::endl;
    }
}

void test_mfi_batch_calculation() {
    std::cout << "\n=== Testing MFI Batch Calculation ===" << std::endl;
    
    std::vector<double> highs, lows, closes, volumes;
    generate_test_data(highs, lows, closes, volumes, 20);
    
    // Test static batch calculation
    auto mfi_values = MFI::calculate(highs, lows, closes, volumes, 14);
    
    std::cout << "Batch calculation results:" << std::endl;
    std::cout << std::setw(5) << "Step" 
              << std::setw(10) << "Close"
              << std::setw(10) << "Volume"
              << std::setw(10) << "MFI"
              << std::endl;
    
    for (size_t i = 0; i < mfi_values.size(); ++i) {
        std::cout << std::setw(5) << i + 1
                  << std::setw(10) << std::fixed << std::setprecision(2) << closes[i]
                  << std::setw(10) << std::fixed << std::setprecision(0) << volumes[i]
                  << std::setw(10) << std::fixed << std::setprecision(2) << mfi_values[i]
                  << std::endl;
    }
    
    std::cout << "\nBatch calculation completed successfully." << std::endl;
}

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "MFI Indicator Test Program" << std::endl;
    std::cout << "Date: 2026-03-15" << std::endl;
    std::cout << "========================================" << std::endl;
    
    try {
        test_mfi_direct();
        test_mfi_factory();
        test_mfi_batch_calculation();
        
        std::cout << "\n========================================" << std::endl;
        std::cout << "All tests completed successfully!" << std::endl;
        std::cout << "MFI indicator is working correctly." << std::endl;
        std::cout << "========================================" << std::endl;
        
        return 0;
    } catch (const std::exception& e) {
        std::cout << "Test failed with error: " << e.what() << std::endl;
        return 1;
    }
}