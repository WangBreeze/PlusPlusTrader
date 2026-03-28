# PlusPlusTrader 安装指南

## 📋 目录

1. [系统要求](#系统要求)
2. [快速安装](#快速安装)
3. [详细安装步骤](#详细安装步骤)
4. [平台特定说明](#平台特定说明)
5. [Docker安装](#docker安装)
6. [开发环境配置](#开发环境配置)
7. [验证安装](#验证安装)
8. [故障排除](#故障排除)

## 🖥️ 系统要求

### 最低配置
- **操作系统**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows (10+ with WSL2)
- **Python**: 3.8 或更高版本
- **内存**: 4 GB RAM
- **存储**: 2 GB 可用空间
- **网络**: 互联网连接（用于下载数据和包）

### 推荐配置
- **操作系统**: Linux (Ubuntu 22.04 LTS)
- **Python**: 3.9 或 3.10
- **内存**: 8 GB RAM 或更多
- **存储**: 10 GB 可用空间（用于存储历史数据）
- **CPU**: 4核或更多
- **GPU**: 可选，用于机器学习加速

### 依赖软件
- **C++编译器**: GCC 9+, Clang 10+, MSVC 2019+
- **CMake**: 3.16 或更高版本
- **Git**: 版本控制
- **pip**: Python包管理器

## 🚀 快速安装

### 一键安装脚本 (Linux/macOS)

```bash
# 下载安装脚本
curl -O https://raw.githubusercontent.com/WangBreeze/PlusPlusTrader/main/install.sh

# 赋予执行权限
chmod +x install.sh

# 运行安装脚本
./install.sh

# 或者直接运行
bash <(curl -s https://raw.githubusercontent.com/WangBreeze/PlusPlusTrader/main/install.sh)
```

安装脚本会自动：
1. 检查系统要求
2. 安装必要的依赖
3. 克隆项目代码
4. 创建Python虚拟环境
5. 安装Python依赖
6. 编译C++核心
7. 安装Python包

### Windows快速安装 (WSL2)

```bash
# 在WSL2中运行
wget https://raw.githubusercontent.com/WangBreeze/PlusPlusTrader/main/install.sh
chmod +x install.sh
./install.sh
```

## 📝 详细安装步骤

### 步骤1: 克隆项目

```bash
# 使用HTTPS
git clone https://github.com/WangBreeze/PlusPlusTrader.git
cd PlusPlusTrader

# 或使用SSH
git clone git@github.com:WangBreeze/PlusPlusTrader.git
cd PlusPlusTrader
```

### 步骤2: 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate

# Windows:
# PowerShell:
venv\Scripts\Activate.ps1
# 或CMD:
venv\Scripts\activate.bat
```

### 步骤3: 安装Python依赖

```bash
# 升级pip
pip install --upgrade pip setuptools wheel

# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 步骤4: 编译C++核心

```bash
# 创建构建目录
mkdir build && cd build

# 配置CMake
cmake .. -DCMAKE_BUILD_TYPE=Release

# 编译
# Linux/macOS:
make -j$(nproc)

# Windows (使用Visual Studio):
# cmake .. -G "Visual Studio 16 2019" -A x64
# 然后用Visual Studio打开生成的.sln文件编译

# 返回项目根目录
cd ..
```

### 步骤5: 安装Python包

```bash
# 开发模式安装（可编辑）
pip install -e .

# 或普通安装
pip install .
```

## 🍎 平台特定说明

### Ubuntu/Debian

```bash
# 安装系统依赖
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-dev \
    python3-venv \
    libboost-all-dev \
    libeigen3-dev

# 如果需要GPU支持
sudo apt-get install -y \
    nvidia-cuda-toolkit \
    nvidia-cuda-dev
```

### CentOS/RHEL

```bash
# 安装系统依赖
sudo yum groupinstall -y "Development Tools"
sudo yum install -y \
    cmake \
    git \
    python3-devel \
    boost-devel \
    eigen3-devel

# 启用EPEL仓库（如果需要）
sudo yum install -y epel-release
```

### macOS

```bash
# 安装Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install cmake git boost eigen

# 安装Python（如果未安装）
brew install python@3.9

# 设置Python路径
echo 'export PATH="/usr/local/opt/python@3.9/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Windows (原生)

```bash
# 1. 安装Visual Studio 2019或更高版本
#    包含"C++桌面开发"工作负载

# 2. 安装Python 3.8+ from python.org
#    勾选"Add Python to PATH"

# 3. 安装CMake from cmake.org

# 4. 安装Git from git-scm.com

# 5. 打开"x64 Native Tools Command Prompt for VS 2019"
#    然后运行安装步骤
```

## 🐳 Docker安装

### 使用预构建镜像

```bash
# 拉取镜像
docker pull wangbreeze/pplustrader:latest

# 运行容器
docker run -it --rm \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/configs:/app/configs \
    -p 8050:8050 \
    wangbreeze/pplustrader:latest

# 进入容器
docker exec -it <container_id> bash
```

### 从Dockerfile构建

```bash
# 克隆项目
git clone https://github.com/WangBreeze/PlusPlusTrader.git
cd PlusPlusTrader

# 构建Docker镜像
docker build -t pplustrader .

# 运行
docker run -it --rm pplustrader
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  pplustrader:
    build: .
    container_name: pplustrader
    volumes:
      - ./data:/app/data
      - ./configs:/app/configs
      - ./logs:/app/logs
    ports:
      - "8050:8050"
    environment:
      - PYTHONPATH=/app
    command: python web/app.py
```

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 💻 开发环境配置

### VS Code配置

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "build/": true,
        "*.egg-info": true
    }
}
```

### PyCharm配置

1. **打开项目**: File → Open → 选择项目目录
2. **设置解释器**: 
   - File → Settings → Project → Python Interpreter
   - 点击齿轮图标 → Add
   - 选择"Existing environment"
   - 路径: `venv/bin/python` (Linux/macOS) 或 `venv\Scripts\python.exe` (Windows)
3. **配置运行配置**:
   - Run → Edit Configurations
   - 添加Python配置
   - Script path: 选择主脚本
   - Python interpreter: 选择虚拟环境

### Jupyter Notebook支持

```bash
# 安装Jupyter
pip install jupyter notebook

# 安装内核
python -m ipykernel install --user --name=pplustrader --display-name="Python (PlusPlusTrader)"

# 启动Jupyter
jupyter notebook

# 在notebook中使用
import sys
sys.path.append('/path/to/PlusPlusTrader')
import pplustrader as ppt
```

## ✅ 验证安装

### 基本验证

```python
# test_installation.py
import pplustrader as ppt
import sys

def test_installation():
    print("=" * 50)
    print("PlusPlusTrader 安装验证")
    print("=" * 50)
    
    # 1. 检查版本
    print(f"1. 版本检查: {ppt.__version__}")
    
    # 2. 检查Python版本
    print(f"2. Python版本: {sys.version}")
    
    # 3. 测试核心功能
    try:
        # 创建简单策略
        strategy = ppt.MACrossStrategy(short_period=10, long_period=30)
        print(f"3. 策略创建: ✓ {strategy.name}")
        
        # 测试技术指标
        sma = ppt.SMA(period=20)
        prices = [100, 102, 101, 105, 103]
        for price in prices:
            value = sma.update(price)
        print(f"4. 技术指标: ✓ SMA值 = {value:.2f}")
        
        # 测试数据源
        import pandas as pd
        import numpy as np
        
        # 创建测试数据
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        data = pd.DataFrame({
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(10000, 100000, 100)
        }, index=dates)
        
        data.to_csv('test_data.csv')
        data_source = ppt.CSVDataSource('test_data.csv')
        print(f"5. 数据源: ✓ 加载{len(data_source)}条数据")
        
        # 测试回测引擎
        backtest = ppt.BacktestEngine(
            data_source=data_source,
            strategy=strategy,
            initial_capital=100000
        )
        print("6. 回测引擎: ✓ 创建成功")
        
        # 运行简单回测
        results = backtest.run()
        print(f"7. 回测执行: ✓ 完成{results.trade_count}笔交易")
        
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！安装成功！")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)
```

运行验证脚本：
```bash
python test_installation.py
```

### 性能测试

```python
# performance_test.py
import pplustrader as ppt
import time
import numpy as np

def test_performance():
    print("性能测试")
    print("-" * 40)
    
    # 1. 指标计算性能
    n = 100000
    prices = np.random.randn(n).cumsum() + 100
    
    # Python实现
    start = time.time()
    sma_python = []
    window = 20
    for i in range(window, len(prices)):
        sma = np.mean(prices[i-window:i])
        sma_python.append(sma)
    python_time = time.time() - start
    
    # C++实现
    start = time.time()
    sma_cpp = ppt.fast_sma(prices, window)
    cpp_time = time.time() - start
    
    print(f"1. SMA计算性能:")
    print(f"   Python: {python_time:.4f}秒")
    print(f"   C++:    {cpp_time:.4f}秒")
    print(f"   加速比: {python_time/cpp_time:.1f}x")
    
    # 2. 回测性能
    print(f"\n2. 回测性能:")
    
    # 创建测试数据
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')
    data = pd.DataFrame({
        'open': np.random.randn(1000).cumsum() + 100,
        'high': np.random.randn(1000).cumsum() + 102,
        'low': np.random.randn(1000).cumsum() + 98,
        'close': np.random.randn(1000).cumsum() + 100,
        'volume': np.random.randint(10000, 100000, 1000)
    }, index=dates)
    
    data.to_csv('performance_data.csv')
    data_source = ppt.CSVDataSource('performance_data.csv')
    
    # 运行回测
    strategy = ppt.MACrossStrategy(short_period=10, long_period=30)
    backtest = ppt.BacktestEngine(
        data_source=data_source,
        strategy=strategy,
        initial_capital=100000
    )
    
    start = time.time()
    results = backtest.run()
    backtest_time = time.time() - start
    
    print(f"   数据量: {len(data_source)}条")
    print(f"   回测时间: {backtest_time:.2f}秒")
    print(f"   交易次数: {results.trade_count}")
    print(f"   每秒处理: {len(data_source)/backtest_time:.0f}条/秒")
    
    return True

if __name__ == "__main__":
    test_performance()
```

## 🔧 故障排除

### 常见问题

#### 1. 编译错误

**问题**: `error: 'some_function' was not declared in this scope`

**解决方案**:
```bash
# 清理构建目录
rm -rf build
mkdir build && cd build

# 重新配置和编译
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# 如果仍有问题，检查依赖
sudo apt-get install libboost-all-dev  # Ubuntu
brew install boost  # macOS
```

#### 2. Python导入错误

**问题**: `ModuleNotFoundError: No module named 'pplustrader'`

**解决方案**:
```bash
# 确保在虚拟环境中
source venv/bin/activate

# 重新安装
pip uninstall pplustrader -y
pip install -e .

# 检查Python路径
python -c "import sys; print(sys.path)"
```

#### 3. 内存不足

**问题**: `MemoryError` 或进程被杀死

**解决方案**:
```python
# 减少数据量
data_source = ppt.CSVDataSource("data.csv", limit=10000)

# 使用数据流式处理
class StreamingProcessor:
    def process_large_file(self, filepath):
        import pandas as pd
        chunk_size = 10000
        for chunk in pd.read_csv(filepath, chunksize=chunk_size):
            yield self.process_chunk(chunk)

# 增加系统交换空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. 网络问题

**问题**: 无法下载数据或包

**解决方案**:
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置代理
export http_proxy=http://your-proxy:port
export https_proxy=http://your-proxy:port

# 手动下载数据
python scripts/download_a_shares.py --source local --data-dir ./local_data
```

#### 5. 权限问题

**问题**: `Permission denied` 或 `Access is denied`

**解决方案**:
```bash
# Linux/macOS
sudo chmod -R 755 /path/to/PlusPlusTrader

# Windows (以管理员身份运行)
# 右键点击命令提示符 → 以管理员身份运行
```

### 获取帮助

#### 查看日志
```bash
# 启用详细日志
export PPT_LOG_LEVEL=DEBUG

# 查看安装日志
tail -f install.log

# 查看Python日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 诊断工具
```bash
# 系统信息
python -m pplustrader.diagnostics

# 依赖检查
python -c "import pplustrader; pplustrader.check_dependencies()"

# 性能分析
python -m cProfile -o profile.stats performance_test.py
```

#### 寻求帮助
1. **查看文档**: [https://pplustrader.readthedocs.io/](https://pplustrader.readthedocs.io/)
2. **搜索问题**: [GitHub Issues](https://github.com/WangBreeze/PlusPlusTrader/issues)
3. **社区讨论**: [Discord](https://discord.gg/your-discord-link)
4. **邮件支持**: support@pplustrader.com

## 🎉 安装完成！

恭喜！你已经成功安装了PlusPlusTrader。接下来可以：

### 开始学习
1. **阅读教程**: `docs/TUTORIAL.md`
2. **查看示例**: `examples/` 目录
3. **运行演示**: `python examples/basic_backtest.py`

### 开始使用
1. **下载数据**:
   ```bash
   python scripts/download_a_shares.py --symbol 000001.SZ --start 2024-01-01 --end 2024-12-31
   ```

2. **运行第一个回测**:
   ```python
   import pplustrader as ppt
   
   # 加载数据
   data_source = ppt.CSVDataSource("data/000001.SZ_SZSE_D.csv")
   
   # 创建策略
   strategy = ppt.MACrossStrategy(short_period=10, long_period=30)
   
   # 运行回测
   backtest = ppt.BacktestEngine(
       data_source=data_source,
       strategy=strategy,
       initial_capital=100000
   )
   
   results = backtest.run()
   print(f"总收益率: {results.total_return:.2%}")
   ```

3. **启动Web界面**:
   ```bash
   python web/app.py
   # 然后在浏览器打开 http://localhost:8050
   ```

### 下一步
- **学习策略开发**: 查看 `docs/STRATEGY_DEVELOPMENT.md`
- **了解风险管理**: 查看 `docs/RISK_MANAGEMENT.md`
- **参与社区**: 加入我们的Discord社区

---

**祝你在量化交易的道路上取得成功！** 🚀

如果在安装或使用过程中遇到任何问题，请随时联系我们。我们很乐意帮助你！

Happy Trading! 📈