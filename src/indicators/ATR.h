// ATR.h - Average True Range indicator
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-12

#ifndef PPLUSTRADER_INDICATORS_ATR_H
#define PPLUSTRADER_INDICATORS_ATR_H

#include "Indicator.h"
#include <memory>
#include <vector>

namespace pplustrader {
namespace indicators {

/**
 * @class ATR
 * @brief Average True Range indicator
 * 
 * ATR measures market volatility by decomposing the entire range
 * of an asset price for that period.
 * 
 * True Range (TR) is the greatest of:
 * 1. Current high - current low
 * 2. |Current high - previous close|
 * 3. |Current low - previous close|
 * 
 * ATR is typically a 14-period moving average of TR.
 */
class ATR : public Indicator {
public:
    /**
     * @brief Construct a new ATR indicator
     * @param period Smoothing period (default: 14)
     */
    explicit ATR(int period = 14);
    
    ~ATR() override;
    
    /**
     * @brief Calculate ATR values for given price data
     * @param highs Vector of high prices
     * @param lows Vector of low prices
     * @param closes Vector of closing prices
     * @return Vector of ATR values
     */
    std::vector<double> calculate(const std::vector<double>& highs,
                                 const std::vector<double>& lows,
                                 const std::vector<double>& closes);
    
    /**
     * @brief Calculate ATR values using TickData structure
     * @param ticks Vector of TickData
     * @return Vector of ATR values
     */
    std::vector<double> calculate(const std::vector<core::TickData>& ticks) override;
    
    /**
     * @brief Get the indicator name
     * @return "ATR"
     */
    std::string name() const override { return "ATR"; }
    
    /**
     * @brief Get the ATR period
     * @return Smoothing period
     */
    int get_period() const;
    
    /**
     * @brief Set the ATR period
     * @param period New period value
     */
    void set_period(int period);
    
    /**
     * @brief Calculate True Range (TR) values
     * @param highs Vector of high prices
     * @param lows Vector of low prices
     * @param closes Vector of closing prices
     * @return Vector of TR values
     */
    static std::vector<double> calculate_true_range(
        const std::vector<double>& highs,
        const std::vector<double>& lows,
        const std::vector<double>& closes);
    
    /**
     * @brief Calculate normalized ATR (ATR / Close * 100)
     * @param highs Vector of high prices
     * @param lows Vector of low prices
     * @param closes Vector of closing prices
     * @return Vector of normalized ATR values (%)
     */
    std::vector<double> calculate_normalized_atr(
        const std::vector<double>& highs,
        const std::vector<double>& lows,
        const std::vector<double>& closes);
    
    /**
     * @brief Calculate volatility levels based on ATR
     * @param atr_values Vector of ATR values
     * @param closes Vector of closing prices
     * @return Vector of volatility levels: 0=low, 1=medium, 2=high
     */
    static std::vector<int> calculate_volatility_levels(
        const std::vector<double>& atr_values,
        const std::vector<double>& closes);
    
    /**
     * @brief Calculate stop loss levels based on ATR
     * @param closes Vector of closing prices
     * @param atr_values Vector of ATR values
     * @param multiplier ATR multiplier for stop loss (default: 2.0)
     * @param is_long True for long positions, false for short
     * @return Vector of stop loss prices
     */
    std::vector<double> calculate_stop_loss(
        const std::vector<double>& closes,
        const std::vector<double>& atr_values,
        double multiplier = 2.0,
        bool is_long = true);
    
    /**
     * @brief Calculate position size based on ATR and risk
     * @param account_balance Account balance
     * @param risk_per_trade Risk per trade as percentage (e.g., 1.0 for 1%)
     * @param atr_value Current ATR value
     * @param current_price Current price
     * @return Position size in units
     */
    static double calculate_position_size(
        double account_balance,
        double risk_per_trade,
        double atr_value,
        double current_price);
    
    /**
     * @brief Create an ATR indicator with default parameters
     * @return Shared pointer to ATR indicator
     */
    static std::shared_ptr<ATR> create();
    
    /**
     * @brief Create an ATR indicator with custom period
     * @param period Smoothing period
     * @return Shared pointer to ATR indicator
     */
    static std::shared_ptr<ATR> create(int period);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace indicators
} // namespace pplustrader

#endif // PPLUSTRADER_INDICATORS_ATR_H