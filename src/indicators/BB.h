// BB.h - Bollinger Bands indicator
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-12

#ifndef PPLUSTRADER_INDICATORS_BB_H
#define PPLUSTRADER_INDICATORS_BB_H

#include "Indicator.h"
#include <memory>
#include <vector>

namespace pplustrader {
namespace indicators {

/**
 * @class BB
 * @brief Bollinger Bands indicator
 * 
 * Bollinger Bands consist of:
 * - Middle Band: N-period simple moving average (SMA)
 * - Upper Band: K standard deviations above the middle band
 * - Lower Band: K standard deviations below the middle band
 * 
 * Typical parameters: N=20, K=2.0
 */
class BB : public Indicator {
public:
    /**
     * @brief Construct a new BB indicator
     * @param period Moving average period (default: 20)
     * @param std_dev Number of standard deviations (default: 2.0)
     */
    explicit BB(int period = 20, double std_dev = 2.0);
    
    ~BB() override;
    
    /**
     * @brief Calculate Bollinger Bands for given price data
     * @param prices Vector of closing prices
     * @return Tuple of (upper_band, middle_band, lower_band)
     */
    std::tuple<std::vector<double>, std::vector<double>, std::vector<double>> 
    calculate(const std::vector<double>& prices) override;
    
    /**
     * @brief Get the indicator name
     * @return "BB"
     */
    std::string name() const override { return "BB"; }
    
    /**
     * @brief Get the period parameter
     * @return Moving average period
     */
    int get_period() const;
    
    /**
     * @brief Get the standard deviation multiplier
     * @return Number of standard deviations
     */
    double get_std_dev() const;
    
    /**
     * @brief Set the period parameter
     * @param period New period value
     */
    void set_period(int period);
    
    /**
     * @brief Set the standard deviation multiplier
     * @param std_dev New standard deviation value
     */
    void set_std_dev(double std_dev);
    
    /**
     * @brief Calculate Bollinger Bands width (upper - lower) / middle
     * @param prices Vector of closing prices
     * @return Vector of bandwidth values
     */
    std::vector<double> calculate_bandwidth(const std::vector<double>& prices);
    
    /**
     * @brief Calculate %B indicator (price position within bands)
     * @param prices Vector of closing prices
     * @return Vector of %B values (0-1 range, can exceed)
     */
    std::vector<double> calculate_percent_b(const std::vector<double>& prices);
    
    /**
     * @brief Create a BB indicator with default parameters
     * @return Shared pointer to BB indicator
     */
    static std::shared_ptr<BB> create();
    
    /**
     * @brief Create a BB indicator with custom parameters
     * @param period Moving average period
     * @param std_dev Standard deviation multiplier
     * @return Shared pointer to BB indicator
     */
    static std::shared_ptr<BB> create(int period, double std_dev);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace indicators
} // namespace pplustrader

#endif // PPLUSTRADER_INDICATORS_BB_H