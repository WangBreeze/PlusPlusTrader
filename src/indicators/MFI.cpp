// MFI.cpp - Money Flow Index indicator implementation
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#include "MFI.h"
#include <algorithm>
#include <cmath>
#include <numeric>

namespace pplustrader {
namespace indicators {

MFI::MFI(int period) 
    : period_(period), ready_(false), current_mfi_(50.0) {
    if (period_ <= 0) {
        period_ = 14;  // Default period
    }
    initialize_buffers();
}

MFI::~MFI() {
    // Clean up if needed
}

void MFI::update(double high, double low, double close, double volume) {
    // Calculate typical price and raw money flow
    double typical_price = calculate_typical_price(high, low, close);
    double raw_money_flow = calculate_raw_money_flow(typical_price, volume);
    
    // Store data
    typical_prices_.push_back(typical_price);
    raw_money_flows_.push_back(raw_money_flow);
    
    // Determine if this is positive or negative money flow
    if (typical_prices_.size() > 1) {
        size_t current_idx = typical_prices_.size() - 1;
        size_t prev_idx = typical_prices_.size() - 2;
        
        if (typical_prices_[current_idx] > typical_prices_[prev_idx]) {
            positive_flows_.push_back(raw_money_flow);
            negative_flows_.push_back(0.0);
        } else if (typical_prices_[current_idx] < typical_prices_[prev_idx]) {
            positive_flows_.push_back(0.0);
            negative_flows_.push_back(raw_money_flow);
        } else {
            positive_flows_.push_back(0.0);
            negative_flows_.push_back(0.0);
        }
    } else {
        // First data point, can't determine direction yet
        positive_flows_.push_back(0.0);
        negative_flows_.push_back(0.0);
    }
    
    // Keep buffers to period size
    if (typical_prices_.size() > static_cast<size_t>(period_)) {
        typical_prices_.pop_front();
        raw_money_flows_.pop_front();
        positive_flows_.pop_front();
        negative_flows_.pop_front();
    }
    
    // Calculate MFI if we have enough data
    if (typical_prices_.size() == static_cast<size_t>(period_)) {
        calculate_mfi();
        ready_ = true;
    } else {
        ready_ = false;
        current_mfi_ = 50.0;  // Neutral value when not ready
    }
}

double MFI::value() const {
    return current_mfi_;
}

bool MFI::ready() const {
    return ready_;
}

void MFI::reset() {
    initialize_buffers();
    ready_ = false;
    current_mfi_ = 50.0;
}

double MFI::calculate_typical_price(double high, double low, double close) const {
    return (high + low + close) / 3.0;
}

double MFI::calculate_raw_money_flow(double typical_price, double volume) const {
    return typical_price * volume;
}

void MFI::calculate_mfi() {
    // Sum positive and negative money flows
    double positive_sum = std::accumulate(positive_flows_.begin(), 
                                          positive_flows_.end(), 0.0);
    double negative_sum = std::accumulate(negative_flows_.begin(), 
                                          negative_flows_.end(), 0.0);
    
    // Calculate money flow ratio and MFI
    if (negative_sum == 0.0) {
        // Avoid division by zero
        if (positive_sum > 0.0) {
            current_mfi_ = 100.0;
        } else {
            current_mfi_ = 50.0;
        }
    } else {
        double money_flow_ratio = positive_sum / negative_sum;
        current_mfi_ = 100.0 - (100.0 / (1.0 + money_flow_ratio));
        
        // Clamp to valid range [0, 100]
        current_mfi_ = std::max(0.0, std::min(100.0, current_mfi_));
    }
}

void MFI::initialize_buffers() {
    typical_prices_.clear();
    raw_money_flows_.clear();
    positive_flows_.clear();
    negative_flows_.clear();
}

std::vector<double> MFI::calculate(const std::vector<double>& highs,
                                   const std::vector<double>& lows,
                                   const std::vector<double>& closes,
                                   const std::vector<double>& volumes,
                                   int period) {
    if (highs.size() != lows.size() || 
        highs.size() != closes.size() ||
        highs.size() != volumes.size() ||
        highs.empty()) {
        return {};
    }
    
    std::vector<double> mfi_values;
    MFI indicator(period);
    
    for (size_t i = 0; i < highs.size(); ++i) {
        indicator.update(highs[i], lows[i], closes[i], volumes[i]);
        if (indicator.ready()) {
            mfi_values.push_back(indicator.value());
        } else {
            mfi_values.push_back(50.0);  // Neutral value when not ready
        }
    }
    
    return mfi_values;
}

} // namespace indicators
} // namespace pplustrader