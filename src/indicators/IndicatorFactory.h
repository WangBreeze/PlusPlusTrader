// IndicatorFactory.h - Factory for creating indicators
// Part of PlusPlusTrader quantitative trading system
// Created: 2026-03-12

#ifndef PPLUSTRADER_INDICATORS_INDICATORFACTORY_H
#define PPLUSTRADER_INDICATORS_INDICATORFACTORY_H

#include "Indicator.h"
#include "MA.h"
#include "MACD.h"
#include "RSI.h"
#include "BB.h"
#include "KDJ.h"
#include "ATR.h"
#include <memory>
#include <string>
#include <unordered_map>
#include <any>

namespace pplustrader {
namespace indicators {

/**
 * @class IndicatorFactory
 * @brief Factory for creating technical indicators
 * 
 * Provides unified interface for creating indicators by name
 * with configurable parameters.
 */
class IndicatorFactory {
public:
    /**
     * @brief Create an indicator by name
     * @param name Indicator name (e.g., "MA", "RSI", "BB")
     * @param params Optional parameters as key-value pairs
     * @return Shared pointer to indicator, nullptr if not found
     */
    static std::shared_ptr<Indicator> create(const std::string& name,
                                            const std::unordered_map<std::string, std::any>& params = {});
    
    /**
     * @brief Create a Moving Average indicator
     * @param period MA period (default: 20)
     * @return Shared pointer to MA indicator
     */
    static std::shared_ptr<MA> create_ma(int period = 20);
    
    /**
     * @brief Create an Exponential Moving Average indicator
     * @param period EMA period (default: 12)
     * @return Shared pointer to MA indicator with EMA type
     */
    static std::shared_ptr<MA> create_ema(int period = 12);
    
    /**
     * @brief Create a MACD indicator
     * @param fast_period Fast EMA period (default: 12)
     * @param slow_period Slow EMA period (default: 26)
     * @param signal_period Signal line period (default: 9)
     * @return Shared pointer to MACD indicator
     */
    static std::shared_ptr<MACD> create_macd(int fast_period = 12,
                                           int slow_period = 26,
                                           int signal_period = 9);
    
    /**
     * @brief Create an RSI indicator
     * @param period RSI period (default: 14)
     * @return Shared pointer to RSI indicator
     */
    static std::shared_ptr<RSI> create_rsi(int period = 14);
    
    /**
     * @brief Create a Bollinger Bands indicator
     * @param period MA period (default: 20)
     * @param std_dev Standard deviation multiplier (default: 2.0)
     * @return Shared pointer to BB indicator
     */
    static std::shared_ptr<BB> create_bb(int period = 20, double std_dev = 2.0);
    
    /**
     * @brief Create a KDJ indicator
     * @param n_period %K period (default: 9)
     * @param d_period %D smoothing period (default: 3)
     * @param j_period %J smoothing period (default: 3)
     * @return Shared pointer to KDJ indicator
     */
    static std::shared_ptr<KDJ> create_kdj(int n_period = 9,
                                         int d_period = 3,
                                         int j_period = 3);
    
    /**
     * @brief Create an ATR indicator
     * @param period ATR period (default: 14)
     * @return Shared pointer to ATR indicator
     */
    static std::shared_ptr<ATR> create_atr(int period = 14);
    
    /**
     * @brief Get list of available indicator names
     * @return Vector of indicator names
     */
    static std::vector<std::string> available_indicators();
    
    /**
     * @brief Check if an indicator is available
     * @param name Indicator name
     * @return True if available
     */
    static bool is_available(const std::string& name);
    
    /**
     * @brief Get default parameters for an indicator
     * @param name Indicator name
     * @return Map of parameter names to default values
     */
    static std::unordered_map<std::string, std::any> get_default_params(const std::string& name);
    
    /**
     * @brief Get parameter description for an indicator
     * @param name Indicator name
     * @return Map of parameter names to descriptions
     */
    static std::unordered_map<std::string, std::string> get_param_descriptions(const std::string& name);
    
    /**
     * @brief Create indicator from configuration string
     * @param config String in format "NAME:param1=value1,param2=value2"
     * @return Shared pointer to indicator
     */
    static std::shared_ptr<Indicator> create_from_string(const std::string& config);
    
    /**
     * @brief Create multiple indicators from configuration
     * @param configs Vector of configuration strings
     * @return Vector of indicator pointers
     */
    static std::vector<std::shared_ptr<Indicator>> create_multiple(const std::vector<std::string>& configs);
    
    /**
     * @brief Register a custom indicator creator
     * @param name Indicator name
     * @param creator Function that creates the indicator
     */
    static void register_creator(const std::string& name,
                                std::function<std::shared_ptr<Indicator>(const std::unordered_map<std::string, std::any>&)> creator);
    
    /**
     * @brief Unregister an indicator creator
     * @param name Indicator name
     */
    static void unregister_creator(const std::string& name);
    
    /**
     * @brief Clear all registered creators
     */
    static void clear_registry();
    
private:
    // Private constructor, static-only class
    IndicatorFactory() = delete;
    
    // Registry of indicator creators
    static std::unordered_map<std::string,
        std::function<std::shared_ptr<Indicator>(const std::unordered_map<std::string, std::any>&)>>&
        get_registry();
    
    // Initialize the registry with built-in indicators
    static void initialize_registry();
    
    // Parse parameter map for specific indicator types
    template<typename T>
    static std::shared_ptr<T> create_with_params(
        const std::unordered_map<std::string, std::any>& params,
        std::function<std::shared_ptr<T>()> default_creator);
};

} // namespace indicators
} // namespace pplustrader

#endif // PPLUSTRADER_INDICATORS_INDICATORFACTORY_H