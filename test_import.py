#!/usr/bin/env python3
"""
测试Python模块导入
"""

import sys
import os

# 添加build目录到Python路径
build_dir = os.path.join(os.path.dirname(__file__), "build")
python_bindings_dir = os.path.join(build_dir, "python", "bindings")
sys.path.insert(0, python_bindings_dir)

print(f"Python路径: {sys.path}")
print(f"构建目录: {build_dir}")
print(f"Python绑定目录: {python_bindings_dir}")

# 尝试导入模块
try:
    import pplustrader
    print("✅ 成功导入 pplustrader 模块")
    print(f"模块位置: {pplustrader.__file__}")
    
    # 测试基本功能
    print("\n测试基本功能:")
    print(f"版本: {pplustrader.get_version()}")
    
    # 测试自定义指标
    print("\n测试自定义指标导入:")
    try:
        from pplustrader.custom_indicator_examples import SimpleMovingAverage
        print("✅ 成功导入 SimpleMovingAverage")
        
        # 创建并测试SMA
        sma = SimpleMovingAverage(period=20)
        print(f"✅ 成功创建 SMA 指标: {sma}")
        
        # 测试更新
        value, signal = sma.update(100)
        print(f"✅ 成功更新 SMA: 值={value}, 信号={signal}")
        
    except ImportError as e:
        print(f"❌ 导入自定义指标失败: {e}")
        print("尝试从python目录导入...")
        
        # 尝试从python目录导入
        python_dir = os.path.join(os.path.dirname(__file__), "python")
        sys.path.insert(0, python_dir)
        
        try:
            from custom_indicator_examples import SimpleMovingAverage
            print("✅ 从python目录成功导入 SimpleMovingAverage")
            
            sma = SimpleMovingAverage(period=20)
            print(f"✅ 成功创建 SMA 指标: {sma}")
            
            value, signal = sma.update(100)
            print(f"✅ 成功更新 SMA: 值={value}, 信号={signal}")
            
        except ImportError as e2:
            print(f"❌ 从python目录导入也失败: {e2}")
            
except ImportError as e:
    print(f"❌ 导入 pplustrader 失败: {e}")
    
    # 列出目录内容
    print("\n目录内容:")
    if os.path.exists(python_bindings_dir):
        print(f"{python_bindings_dir}:")
        for item in os.listdir(python_bindings_dir):
            print(f"  - {item}")
    else:
        print(f"目录不存在: {python_bindings_dir}")