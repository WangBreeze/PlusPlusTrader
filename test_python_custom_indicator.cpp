/**
 * Python自定义指标测试
 */

#include <iostream>
#include <memory>
#include "custom/PythonIndicatorBridge.h"
#include "indicators/PriceData.h"

using namespace pplustrader;
using namespace pplustrader::custom;

int main() {
    std::cout << "=== Python自定义指标系统测试 ===\n" << std::endl;
    
    // 获取Python桥接单例
    PythonIndicatorBridge& bridge = PythonIndicatorBridge::getInstance();
    
    std::cout << "1. 初始化Python环境..." << std::endl;
    if (!bridge.initialize()) {
        std::cerr << "初始化失败: " << bridge.getLastError() << std::endl;
        return 1;
    }
    std::cout << "   Python环境初始化成功!\n" << std::endl;
    
    std::cout << "2. 检查Python环境可用性..." << std::endl;
    if (!bridge.isAvailable()) {
        std::cerr << "Python环境不可用" << std::endl;
        return 1;
    }
    std::cout << "   Python环境可用!\n" << std::endl;
    
    std::cout << "3. 列出可用的Python指标..." << std::endl;
    std::string indicators = bridge.listAvailableIndicators();
    std::cout << "   可用指标: " << indicators << "\n" << std::endl;
    
    std::cout << "4. 创建Python自定义指标实例..." << std::endl;
    std::string smaConfig = "{\"period\": 10}";
    std::string smaId = bridge.createIndicator("SimpleMovingAverage", smaConfig);
    
    if (smaId.empty()) {
        std::cerr << "创建SMA指标失败: " << bridge.getLastError() << std::endl;
        bridge.cleanup();
        return 1;
    }
    std::cout << "   创建SMA指标成功! 实例ID: " << smaId << "\n" << std::endl;
    
    std::cout << "5. 创建RSI指标实例..." << std::endl;
    std::string rsiConfig = "{\"period\": 14}";
    std::string rsiId = bridge.createIndicator("RelativeStrengthIndex", rsiConfig);
    
    if (rsiId.empty()) {
        std::cerr << "创建RSI指标失败: " << bridge.getLastError() << std::endl;
        bridge.removeIndicator(smaId);
        bridge.cleanup();
        return 1;
    }
    std::cout << "   创建RSI指标成功! 实例ID: " << rsiId << "\n" << std::endl;
    
    std::cout << "6. 模拟价格数据并更新指标..." << std::endl;
    std::vector<double> prices = {100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 
                                  110, 112, 111, 113, 115, 114, 116, 118, 117, 119};
    
    for (size_t i = 0; i < prices.size(); ++i) {
        double price = prices[i];
        
        // 构建价格数据JSON
        std::string priceData = "{"
            "\"open\":" + std::to_string(price - 1) + ","
            "\"high\":" + std::to_string(price + 1) + ","
            "\"low\":" + std::to_string(price - 2) + ","
            "\"close\":" + std::to_string(price) + ","
            "\"volume\":1000,"
            "\"timestamp\":" + std::to_string(i) +
            "}";
        
        // 更新SMA指标
        std::string smaResult = bridge.updateIndicator(smaId, priceData);
        
        // 更新RSI指标
        std::string rsiResult = bridge.updateIndicator(rsiId, priceData);
        
        // 获取指标值
        double smaValue = bridge.getIndicatorValue(smaId);
        double rsiValue = bridge.getIndicatorValue(rsiId);
        
        // 获取信号
        std::string smaSignal = bridge.getIndicatorSignal(smaId);
        std::string rsiSignal = bridge.getIndicatorSignal(rsiId);
        
        std::cout << "   时间 " << i << ": 价格=" << price 
                  << ", SMA=" << smaValue << " (" << smaSignal << ")"
                  << ", RSI=" << rsiValue << " (" << rsiSignal << ")" << std::endl;
    }
    std::cout << std::endl;
    
    std::cout << "7. 获取指标详细信息..." << std::endl;
    std::string smaInfo = bridge.getIndicatorInfo(smaId);
    std::string rsiInfo = bridge.getIndicatorInfo(rsiId);
    
    std::cout << "   SMA信息: " << smaInfo << std::endl;
    std::cout << "   RSI信息: " << rsiInfo << "\n" << std::endl;
    
    std::cout << "8. 列出活跃实例..." << std::endl;
    std::string activeInstances = bridge.listActiveInstances();
    std::cout << "   活跃实例: " << activeInstances << "\n" << std::endl;
    
    std::cout << "9. 测试PythonWrappedIndicator包装器..." << std::endl;
    {
        // 创建包装器
        PythonWrappedIndicator smaWrapper(bridge, smaId, "SMA_Wrapper");
        
        // 测试基本功能
        std::cout << "   指标名称: " << smaWrapper.getName() << std::endl;
        std::cout << "   指标描述: " << smaWrapper.getDescription() << std::endl;
        std::cout << "   指标类别: " << smaWrapper.getCategory() << std::endl;
        std::cout << "   Python可用: " << (smaWrapper.isPythonAvailable() ? "是" : "否") << std::endl;
        
        // 测试计算
        indicators::PriceData priceData;
        priceData.open = 120.0;
        priceData.high = 122.0;
        priceData.low = 118.0;
        priceData.close = 121.0;
        priceData.volume = 1500;
        priceData.timestamp = 20;
        
        double value = smaWrapper.calculate(priceData);
        indicators::Signal signal = smaWrapper.generateSignal(priceData, value);
        
        std::cout << "   计算值: " << value << std::endl;
        std::cout << "   信号: " << static_cast<int>(signal) << std::endl;
        
        // 测试获取值序列
        auto values = smaWrapper.getValues();
        auto signals = smaWrapper.getSignals();
        
        std::cout << "   值序列大小: " << values.size() << std::endl;
        std::cout << "   信号序列大小: " << signals.size() << std::endl;
        
        if (!values.empty()) {
            std::cout << "   最新值: " << values.back() << std::endl;
        }
        
        // 测试JSON序列化
        std::string jsonStr = smaWrapper.toJson();
        std::cout << "   JSON序列化: " << (jsonStr.length() > 50 ? jsonStr.substr(0, 50) + "..." : jsonStr) << std::endl;
    }
    std::cout << std::endl;
    
    std::cout << "10. 测试PythonIndicatorFactory..." << std::endl;
    {
        PythonIndicatorFactory factory(bridge);
        
        // 注册Python指标
        bool registered = factory.registerPythonIndicator("SimpleMovingAverage", smaConfig);
        std::cout << "   注册SMA指标: " << (registered ? "成功" : "失败") << std::endl;
        
        registered = factory.registerPythonIndicator("RelativeStrengthIndex", rsiConfig);
        std::cout << "   注册RSI指标: " << (registered ? "成功" : "失败") << std::endl;
        
        // 检查指标可用性
        bool smaAvailable = factory.isPythonIndicatorAvailable("SimpleMovingAverage");
        bool rsiAvailable = factory.isPythonIndicatorAvailable("RelativeStrengthIndex");
        bool unknownAvailable = factory.isPythonIndicatorAvailable("UnknownIndicator");
        
        std::cout << "   SMA可用: " << (smaAvailable ? "是" : "否") << std::endl;
        std::cout << "   RSI可用: " << (rsiAvailable ? "是" : "否") << std::endl;
        std::cout << "   未知指标可用: " << (unknownAvailable ? "是" : "否") << std::endl;
        
        // 获取可用指标列表
        auto availableIndicators = factory.getAvailablePythonIndicators();
        std::cout << "   可用指标列表: ";
        for (const auto& indicator : availableIndicators) {
            std::cout << indicator << " ";
        }
        std::cout << std::endl;
        
        // 创建包装指标
        auto smaIndicator = factory.createPythonIndicator("SimpleMovingAverage");
        if (smaIndicator) {
            std::cout << "   创建SMA包装指标成功: " << smaIndicator->getName() << std::endl;
            
            // 测试计算
            indicators::PriceData priceData;
            priceData.open = 122.0;
            priceData.high = 124.0;
            priceData.low = 120.0;
            priceData.close = 123.0;
            priceData.volume = 2000;
            priceData.timestamp = 21;
            
            double value = smaIndicator->calculate(priceData);
            std::cout << "   计算值: " << value << std::endl;
        } else {
            std::cout << "   创建SMA包装指标失败" << std::endl;
        }
    }
    std::cout << std::endl;
    
    std::cout << "11. 清理资源..." << std::endl;
    bridge.removeIndicator(smaId);
    bridge.removeIndicator(rsiId);
    
    std::cout << "   清理完成!\n" << std::endl;
    
    std::cout << "12. 清理Python环境..." << std::endl;
    bridge.cleanup();
    std::cout << "   Python环境清理完成!\n" << std::endl;
    
    std::cout << "=== 测试完成 ===" << std::endl;
    
    return 0;
}