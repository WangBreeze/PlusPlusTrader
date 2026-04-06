#!/bin/bash
# PlusPlusTrader Web界面启动脚本

set -e

echo "=================================================="
echo "🦞 PlusPlusTrader Web界面启动"
echo "=================================================="

# 检查Python版本
echo "🔍 检查Python版本..."
python3 --version

# 检查是否在正确的目录
if [ ! -f "simple_app.py" ]; then
    echo "❌ 错误：请在PlusPlusTrader/web目录下运行此脚本"
    exit 1
fi

# 检查端口是否被占用
PORT=8050
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 $PORT 已被占用，尝试使用其他端口..."
    PORT=8051
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        PORT=8052
    fi
    echo "✅ 使用端口: $PORT"
fi

# 修改simple_app.py中的端口
sed -i "s/port = 8050/port = $PORT/" simple_app.py

# 启动Web服务器
echo "🚀 启动Web服务器..."
echo "🌐 访问地址: http://127.0.0.1:$PORT"
echo "📱 功能:"
echo "  • 📊 仪表盘 - 实时数据监控"
echo "  • 📚 使用指南 - 完整文档"
echo "  • 💡 示例代码 - 实用代码片段"
echo "  • ⚙️ 系统配置 - 配置说明"
echo ""
echo "🛑 按 Ctrl+C 停止服务器"
echo "=================================================="

# 启动服务器
python3 simple_app.py