#!/usr/bin/env python3
"""
测试PlusPlusTrader Python模块功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, '.')
sys.path.insert(0, 'python')
sys.path.insert(0, 'build/python/bindings')

print("=" * 60)
print("测试 PlusPlusTrader Python 模块")
print("=" * 60)

try:
    import pplustrader
    print(f"✅ pplustrader 模块导入成功")
    print(f"版本: {pplustrader.__version__}")
    if hasattr(pplustrader, '__description__'):
        print(f"描述: {pplustrader.__description__}")
    if hasattr(pplustrader, '__author__'):
        print(f"作者: {pplustrader.__author__}")
    
    # 检查C++核心可用性
    if hasattr(pplustrader, '_CPP_AVAILABLE'):
        print(f"C++核心可用: {pplustrader._CPP_AVAILABLE}")
    else:
        print("C++核心可用: 未知")
    
    # 测试C++绑定功能
    print("\n测试C++绑定功能:")
    try:
        # 尝试创建C++对象
        tick_data = pplustrader.TickData()
        print(f"✅ TickData 创建成功")
        
        order_type = pplustrader.OrderType.MARKET
        print(f"✅ OrderType 枚举访问成功: {order_type}")
        
        # 测试简单函数
        if hasattr(pplustrader, 'hello'):
            result = pplustrader.hello()
            print(f"✅ hello() 函数调用成功: {result}")
        
        if hasattr(pplustrader, 'get_version'):
            version = pplustrader.get_version()
            print(f"✅ get_version() 函数调用成功: {version}")
            
    except Exception as e:
        print(f"❌ C++绑定功能测试失败: {e}")
    
    # 测试Python扩展模块
    print("\n测试Python扩展模块:")
    try:
        # 测试数据适配器
        from pplustrader.data import DataFeed, CSVDataFeed
        print(f"✅ DataFeed 类导入成功")
        
        # 测试策略模块
        from pplustrader.strategies import Strategy, MovingAverageCrossover
        print(f"✅ Strategy 类导入成功")
        
    except Exception as e:
        print(f"❌ Python扩展模块测试失败: {e}")
    
    print("\n✅ Python模块测试完成!")
    
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)