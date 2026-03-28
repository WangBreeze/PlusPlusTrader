// KDJ.h - KDJ stochastic oscillator indicator
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-12

#ifndef PPLUSTRADER_INDICATORS_KDJ_H
#define PPLUSTRADER_INDICATORS_KDJ_H

#include "Indicator.h"
#include <memory>
#include <vector>

namespace pplustrader {
namespace indicators {

/**
 * @class KDJ
 * @brief KDJ stochastic oscillator indicator
 * 
 * KDJ is a momentum indicator that shows the location of the current
 * close relative to the high-low range over a set number of periods.
 * 
 * Components:
 * - K line: Fast stochastic (also called %K)
 * - D line: Slow stochastic (simple moving average of %K)
 * - J line: 3*%K - 2*%D
 * 
 * Typical parameters: N=9, M1=3, M2=3
 */
class KDJ : public Indicator {
public:
    /**
     * @brief Construct a new KDJ indicator
     * @param n Period for %K calculation (default: 9)
     * @param m1 Smoothing period for %D (default: 3)
     * @param m2 Smoothing period for %J (default: 3)
     */
    explicit KDJ(int n = 9, int m1 = 3, int m2 = 3);
    
    ~KDJ() override;
    
    /**
     * @brief Calculate KDJ values for given price data
     * @param highs Vector of high prices
     * @param lows Vector of low prices
     * @param closes Vector of closing prices
     * @return Tuple of (K_values, D_values, J_values)
     */
    std::tuple<std::vector<double>, std::vector<double>, std::vector<double>>
    calculate(const std::vector<double>& highs,
              const std::vector<double>& lows,
              const std::vector<double>& closes);
    
    /**
     * @brief Calculate KDJ values using TickData structure
     * @param ticks Vector of TickData
     * @return Tuple of (K_values, D_values, J_values)
     */
    std::tuple<std::vector<double>, std::vector<double>, std::vector<double>>
    calculate(const std::vector<core::TickData>& ticks) override;
    
    /**
     * @brief Get the indicator name
     * @return "KDJ"
     */
    std::string name() const override { return "KDJ"; }
    
    /**
     * @brief Get the %K period
     * @return Period for %K calculation
     */
    int get_n_period() const;
    
    /**
     * @brief Get the %D smoothing period
     * @return Smoothing period for %D
     */
    int get_m1_period() const;
    
    /**
     * @brief Get the %J smoothing period
     * @return Smoothing period for %J
     */
    int get_m2_period() const;
    
    /**
     * @brief Set the %K period
     * @param n New period value
     */
    void set_n_period(int n);
    
    /**
     * @brief Set the %D smoothing period
     * @param m1 New smoothing period
     */
    void set_m1_period(int m1);
    
    /**
     * @brief Set the %J smoothing period
     * @param m2 New smoothing period
     */
    void set_m2_period(int m2);
    
    /**
     * @brief Check for overbought condition (typically K > 80)
     * @param k_value Current K value
     * @param threshold Overbought threshold (default: 80)
     * @return True if overbought
     */
    static bool is_overbought(double k_value, double threshold = 80.0);
    
    /**
     * @brief Check for oversold condition (typically K < 20)
     * @param k_value Current K value
     * @param threshold Oversold threshold (default: 20)
     * @return True if oversold
     */
    static bool is_oversold(double k_value, double threshold = 20.0);
    
    /**
     * @brief Generate trading signals based on KDJ crossovers
     * @param k_values Vector of K values
     * @param d_values Vector of D values
     * @return Vector of signals: 1=buy, -1=sell, 0=hold
     */
    std::vector<int> generate_signals(const std::vector<double>& k_values,
                                     const std::vector<double>& d_values);
    
    /**
     * @brief Create a KDJ indicator with default parameters
     * @return Shared pointer to KDJ indicator
     */
    static std::shared_ptr<KDJ> create();
    
    /**
     * @brief Create a KDJ indicator with custom parameters
     * @param n Period for %K calculation
     * @param m1 Smoothing period for %D
     * @param m2 Smoothing period for %J
     * @return Shared pointer to KDJ indicator
     */
    static std::shared_ptr<KDJ> create(int n, int m1, int m2);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace indicators
} // namespace pplustrader

#endif // PPLUSTRADER_INDICATORS_KDJ_H