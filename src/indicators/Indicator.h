#ifndef PLUSPLUSTRADER_INDICATOR_H
#define PLUSPLUSTRADER_INDICATOR_H

#include <vector>
#include <string>
#include <memory>
#include "../core/Engine.h"

namespace pplustrader {
namespace indicators {

// 指标计算基类
class Indicator {
public:
    virtual ~Indicator() = default;
    
    // 初始化指标
    virtual void initialize() = 0;
    
    // 更新指标值（传入最新的Tick数据）
    virtual void update(const core::TickData& tick) = 0;
    
    // 获取指标名称
    virtual std::string name() const = 0;
    
    // 获取当前指标值
    virtual double value() const = 0;
    
    // 获取历史指标值（最近n个值）
    virtual std::vector<double> history(size_t n) const = 0;
    
    // 重置指标
    virtual void reset() = 0;
    
    // 是否准备就绪（有足够数据计算）
    virtual bool is_ready() const = 0;
};

} // namespace indicators
} // namespace pplustrader

#endif // PLUSPLUSTRADER_INDICATOR_H