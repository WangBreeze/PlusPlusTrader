#!/bin/bash
# PlusPlusTrader Web可视化界面启动脚本

echo "=================================================="
echo "  🦞 PlusPlusTrader Web可视化界面"
echo "=================================================="

# 检查Python依赖
echo "检查Python依赖..."
python3 -c "import dash" 2>/dev/null || {
    echo "安装Dash框架..."
    pip install dash plotly pandas -q
}

python3 -c "import plotly" 2>/dev/null || {
    echo "安装Plotly..."
    pip install plotly -q
}

# 检查pplustrader模块
echo "检查pplustrader模块..."
python3 -c "
import sys
sys.path.insert(0, '..')
sys.path.insert(0, '../python')
sys.path.insert(0, '../build/python/bindings')

try:
    from pplustrader.data import BinanceDataFeed
    print('✅ pplustrader模块可用')
except ImportError as e:
    print(f'⚠️ pplustrader模块不可用: {e}')
    print('将使用模拟数据模式')
"

# 启动Web服务器
echo "启动Web服务器..."
echo "👉 请访问: http://127.0.0.1:8050"
echo "🔄 按 Ctrl+C 停止服务器"
echo "=================================================="

cd "$(dirname "$0")"
python3 app.py