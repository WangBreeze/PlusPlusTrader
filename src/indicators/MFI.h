// MFI.h - Money Flow Index indicator
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-15

#ifndef PPLUSTRADER_INDICATORS_MFI_H
#define PPLUSTRADER_INDICATORS_MFI_H

#include "Indicator.h"
#include <memory>
#include <vector>
#include <deque>

namespace pplustrader {
namespace indicators {

/**
 * @class MFI
 * @brief Money Flow Index indicator
 * 
 * MFI (Money Flow Index) is a momentum indicator that measures the 
 * strength of money flowing in and out of a security. It is similar to
 * RSI but uses volume in the calculation.
 * 
 * Formula:
 * 1. Typical Price = (High + Low + Close) / 3
 * 2. Raw Money Flow = Typical Price × Volume
 * 3. Money Flow Ratio = Positive Money Flow / Negative Money Flow
 * 4. MFI = 100 - (100 / (1 + Money Flow Ratio))
 * 
 * Typical period: 14
 * Overbought: >80
 * Oversold: <20
 */
class MFI : public Indicator {
public:
    /**
     * @brief Construct a new MFI indicator
     * @param period MFI calculation period (default: 14)
     */
    explicit MFI(int period = 14);
    
    ~MFI() override;
    
    /**
     * @brief Update indicator with new price and volume data
     * @param high High price
     * @param low Low price
     * @param close Close price
     * @param volume Trading volume
     */
    void update(double high, double low, double close, double volume) override;
    
    /**
     * @brief Get current MFI value
     * @return Current MFI value, or 50.0 if not ready
     */
    double value() const override;
    
    /**
     * @brief Check if indicator is ready (has enough data)
     * @return True if ready
     */
    bool ready() const override;
    
    /**
     * @brief Reset indicator to initial state
     */
    void reset() override;
    
    /**
     * @brief Get indicator name
     * @return "MFI"
     */
    std::string name() const override { return "MFI"; }
    
    /**
     * @brief Get current period setting
     * @return MFI period
     */
    int period() const { return period_; }
    
    /**
     * @brief Calculate MFI for a range of price and volume data
     * @param highs Vector of high prices
     * @param lows Vector of low prices
     * @param closes Vector of closing prices
     * @param volumes Vector of trading volumes
     * @return Vector of MFI values
     */
    static std::vector<double> calculate(const std::vector<double>& highs,
                                         const std::vector<double>& lows,
                                         const std::vector<double>& closes,
                                         const std::vector<double>& volumes,
                                         int period = 14);
    
private:
    int period_;                    // MFI calculation period
    std::deque<double> typical_prices_;  // Buffer of typical prices
    std::deque<double> raw_money_flows_; // Buffer of raw money flows
    std::deque<double> positive_flows_;  // Buffer of positive money flows
    std::deque<double> negative_flows_;  // Buffer of negative money flows
    bool ready_;                    // Indicator ready flag
    double current_mfi_;            // Current MFI value
    
    /**
     * @brief Calculate typical price
     */
    double calculate_typical_price(double high, double low, double close) const;
    
    /**
     * @brief Calculate raw money flow
     */
    double calculate_raw_money_flow(double typical_price, double volume) const;
    
    /**
     * @brief Update internal MFI calculation
     */
    void calculate_mfi();
    
    /**
     * @brief Initialize or clear buffers
     */
    void initialize_buffers();
};

} // namespace indicators
} // namespace pplustrader

#endif // PPLUSTRADER_INDICATORS_MFI_H