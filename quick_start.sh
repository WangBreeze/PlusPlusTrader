#!/bin/bash
# PlusPlusTrader 快速启动脚本

set -e  # 遇到错误时退出

echo "================================================"
echo "  🦞 PlusPlusTrader 快速启动"
echo "================================================"

# 检查操作系统
echo "🔍 检查系统环境..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ Linux 系统检测"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ macOS 系统检测"
else
    echo "⚠️  不支持的操作系统: $OSTYPE"
    exit 1
fi

# 检查Python版本
echo "🐍 检查Python版本..."
python3 --version || {
    echo "❌ Python3 未安装"
    exit 1
}

# 检查pip
echo "📦 检查pip..."
python3 -m pip --version || {
    echo "❌ pip 未安装"
    echo "正在安装pip..."
    python3 -m ensurepip --upgrade
}

# 安装系统依赖
echo "🔧 安装系统依赖..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # 检测包管理器
    if command -v apt-get &> /dev/null; then
        echo "使用 apt-get 安装依赖..."
        sudo apt-get update
        sudo apt-get install -y cmake build-essential python3-dev python3-pip
    elif command -v yum &> /dev/null; then
        echo "使用 yum 安装依赖..."
        sudo yum install -y cmake gcc-c++ python3-devel python3-pip
    else
        echo "⚠️  无法识别包管理器，请手动安装依赖"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "使用 Homebrew 安装依赖..."
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew 未安装"
        echo "请访问 https://brew.sh 安装Homebrew"
        exit 1
    fi
    brew install cmake python3
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt --user

# 检查pybind11安装
echo "🔗 检查pybind11..."
python3 -c "import pybind11" 2>/dev/null || {
    echo "安装 pybind11..."
    python3 -m pip install pybind11 --user
}

# 编译C++核心
echo "⚙️  编译C++核心..."
if [ ! -d "build" ]; then
    mkdir -p build
fi

cd build
echo "配置CMake..."
cmake .. -DCMAKE_BUILD_TYPE=Release 2>&1 | tail -20

echo "编译项目..."
make -j$(nproc) 2>&1 | tail -20

# 检查编译结果
if [ -f "src/example/example" ]; then
    echo "✅ C++核心编译成功"
else
    echo "⚠️  C++核心编译可能有问题"
fi

cd ..

# 安装Python包
echo "🐍 安装Python包..."
cd python
python3 -m pip install -e . --user
cd ..

# 验证安装
echo "🔍 验证安装..."
python3 -c "
import sys
sys.path.insert(0, '.')
sys.path.insert(0, './python')
sys.path.insert(0, './build/python/bindings')

try:
    import pplustrader
    print('✅ pplustrader 导入成功')
except ImportError as e:
    print(f'❌ pplustrader 导入失败: {e}')
    import traceback
    traceback.print_exc()
"

# 检查Web依赖
echo "🌐 检查Web依赖..."
python3 -c "import dash" 2>/dev/null || {
    echo "安装Web依赖..."
    python3 -m pip install dash plotly pandas --user
}

echo ""
echo "================================================"
echo "  🎉 安装完成！"
echo "================================================"
echo ""
echo "接下来可以："
echo ""
echo "1. 🚀 启动Web界面："
echo "   cd web && ./start.sh"
echo "   访问 http://127.0.0.1:8050"
echo ""
echo "2. 📚 运行示例："
echo "   cd python/examples"
echo "   python3 simple_strategy.py"
echo ""
echo "3. 🔧 开发测试："
echo "   cd build && ./src/example/example"
echo ""
echo "4. 📖 查看文档："
echo "   阅读 README.md 获取更多信息"
echo ""
echo "================================================"
echo "  有问题？查看故障排除章节或提交Issue"
echo "================================================"