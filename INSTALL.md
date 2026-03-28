# PlusPlusTrader 安装指南

## 目录

1. [系统要求](#系统要求)
2. [快速安装](#快速安装)
3. [详细安装步骤](#详细安装步骤)
4. [Docker安装](#docker安装)
5. [从源码编译](#从源码编译)
6. [验证安装](#验证安装)
7. [常见问题](#常见问题)
8. [卸载指南](#卸载指南)

## 系统要求

### 最低配置
- **操作系统**: Ubuntu 20.04+, CentOS 8+, macOS 10.15+, Windows 10/11 (WSL2)
- **CPU**: x86_64架构，支持SSE4.2指令集
- **内存**: 4GB RAM
- **存储**: 2GB可用空间
- **Python**: 3.8+
- **C++编译器**: GCC 9+, Clang 10+, MSVC 2019+

### 推荐配置
- **操作系统**: Ubuntu 22.04 LTS, macOS 12+, Windows 11 (WSL2)
- **CPU**: 4核以上，支持AVX2指令集
- **内存**: 8GB+ RAM
- **存储**: 10GB+ SSD
- **Python**: 3.10+
- **C++编译器**: GCC 11+, Clang 13+

### 开发环境要求
- **CMake**: 3.15+
- **Git**: 2.20+
- **pip**: 20.0+
- **虚拟环境**: venv或conda（推荐）

## 快速安装

### 一键安装脚本（Linux/macOS）

```bash
# 下载安装脚本
curl -O https://raw.githubusercontent.com/yourusername/PlusPlusTrader/main/install.sh
chmod +x install.sh

# 运行安装脚本
./install.sh
```

### Windows快速安装（WSL2）

```powershell
# 在WSL2中运行
wget https://raw.githubusercontent.com/yourusername/PlusPlusTrader/main/install.sh
chmod +x install.sh
./install.sh
```

### Python包安装（简易版）

```bash
# 安装Python包（仅Python功能，不含C++核心）
pip install pplustrader
```

## 详细安装步骤

### 步骤1：准备环境

#### Linux (Ubuntu/Debian)
```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装编译工具
sudo apt install -y build-essential cmake git python3 python3-pip python3-venv

# 安装Python开发库
sudo apt install -y python3-dev libpython3-dev

# 安装其他依赖
sudo apt install -y libboost-all-dev libeigen3-dev
```

#### Linux (CentOS/RHEL)
```bash
# 安装EPEL仓库
sudo yum install -y epel-release

# 安装编译工具
sudo yum install -y gcc-c++ cmake git python3 python3-pip python3-devel

# 安装其他依赖
sudo yum install -y boost-devel eigen3-devel
```

#### macOS
```bash
# 安装Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装编译工具
brew install cmake git python3

# 安装其他依赖
brew install boost eigen
```

#### Windows (WSL2)
```bash
# 在WSL2中安装Ubuntu
# 然后按照Ubuntu步骤安装
```

### 步骤2：获取源代码

```bash
# 克隆项目
git clone https://github.com/yourusername/PlusPlusTrader.git
cd PlusPlusTrader

# 或下载压缩包
wget https://github.com/yourusername/PlusPlusTrader/archive/refs/tags/v1.0.0.tar.gz
tar -xzf v1.0.0.tar.gz
cd PlusPlusTrader-1.0.0
```

### 步骤3：创建Python虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# 升级pip
pip install --upgrade pip
```

### 步骤4：安装Python依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 步骤5：编译C++核心

```bash
# 创建构建目录
mkdir build && cd build

# 配置CMake
cmake -DCMAKE_BUILD_TYPE=Release ..

# 编译（使用多核加速）
make -j$(nproc)

# 或指定编译线程数
make -j4

# 安装到系统（可选）
sudo make install
```

### 步骤6：安装Python绑定

```bash
# 返回项目根目录
cd ..

# 安装Python绑定
cd python
python setup.py build
python setup.py install --user

# 或使用pip安装
pip install .
```

### 步骤7：验证安装

```bash
# 运行验证脚本
python -c "import pplustrader as ppt; print(f'✅ PlusPlusTrader版本: {ppt.get_version()}')"

# 运行测试
python -m pytest tests/ -v
```

## Docker安装

### 使用预构建镜像

```bash
# 拉取最新镜像
docker pull yourusername/pplustrader:latest

# 运行容器
docker run -it --rm yourusername/pplustrader

# 运行带持久化存储的容器
docker run -it --rm -v $(pwd)/data:/app/data yourusername/pplustrader
```

### 从Dockerfile构建

```bash
# 克隆项目
git clone https://github.com/yourusername/PlusPlusTrader.git
cd PlusPlusTrader

# 构建Docker镜像
docker build -t pplustrader .

# 运行容器
docker run -it --rm pplustrader
```

### Docker Compose部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  pplustrader:
    image: yourusername/pplustrader:latest
    container_name: pplustrader
    ports:
      - "8050:8050"  # Web界面端口
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped
```

运行：
```bash
docker-compose up -d
```

## 从源码编译

### 高级编译选项

```bash
# 启用调试符号
cmake -DCMAKE_BUILD_TYPE=Debug ..

# 启用性能优化
cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_AVX2=ON ..

# 指定安装路径
cmake -DCMAKE_INSTALL_PREFIX=/opt/pplustrader ..

# 启用测试
cmake -DBUILD_TESTING=ON ..

# 禁用不需要的模块
cmake -DBUILD_WEBUI=OFF ..
```

### 交叉编译

```bash
# 设置交叉编译工具链
export CC=aarch64-linux-gnu-gcc
export CXX=aarch64-linux-gnu-g++

# 配置CMake
cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/toolchain-aarch64.cmake ..
```

## 验证安装

### 基本功能验证

```python
# test_installation.py
import pplustrader as ppt
import sys

def test_basic_functions():
    """测试基本功能"""
    print("🧪 开始验证安装...")
    
    # 测试版本信息
    version = ppt.get_version()
    print(f"✅ 版本信息: {version}")
    
    # 测试基本函数
    hello_result = ppt.hello()
    print(f"✅ Hello函数: {hello_result}")
    
    # 测试技术指标
    prices = [100.0, 102.0, 101.0, 105.0, 103.0, 108.0]
    sma_values = ppt.simple_moving_average(prices, 3)
    print(f"✅ 技术指标计算: {len(sma_values)}个SMA值")
    
    # 测试回测
    result = ppt.simulate_backtest(10000.0, prices)
    print(f"✅ 回测功能: {result}")
    
    print("🎉 所有基本功能验证通过！")
    return True

if __name__ == "__main__":
    try:
        success = test_basic_functions()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        sys.exit(1)
```

运行验证：
```bash
python test_installation.py
```

### 高级功能验证

```python
# test_advanced.py
from custom_indicator import CustomIndicatorFactory
from custom_indicator_examples import EnhancedMovingAverage
from optimized_indicator import PriceDataPool

def test_advanced_features():
    """测试高级功能"""
    print("🧪 测试高级功能...")
    
    # 测试自定义指标
    factory = CustomIndicatorFactory()
    factory.register(EnhancedMovingAverage)
    instance_id = factory.create('EnhancedMovingAverage', {'period': 20})
    print(f"✅ 自定义指标系统: 创建实例 {instance_id}")
    
    # 测试性能优化框架
    pool = PriceDataPool()
    data = pool.get_price_data()
    pool.return_price_data(data)
    print(f"✅ 性能优化框架: 内存池大小 {pool.pool_size}")
    
    # 测试用户反馈系统
    from user_feedback_system import FeedbackCollector
    collector = FeedbackCollector()
    stats = collector.get_stats()
    print(f"✅ 用户反馈系统: {stats}")
    
    print("🎉 所有高级功能验证通过！")
    return True
```

### 性能验证

```bash
# 运行性能测试
python performance_validation_simple.py

# 查看性能报告
cat performance_validation_report.md
```

## 常见问题

### 问题1：编译错误 "找不到Python.h"

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt install python3-dev

# CentOS/RHEL
sudo yum install python3-devel

# macOS
brew install python3
```

### 问题2：导入错误 "ModuleNotFoundError: No module named 'pplustrader'"

**解决方案**：
```bash
# 确保在正确的Python环境中
source venv/bin/activate

# 重新安装Python绑定
cd python
pip uninstall pplustrader -y
pip install .

# 或设置PYTHONPATH
export PYTHONPATH=/path/to/PlusPlusTrader/python:$PYTHONPATH
```

### 问题3：CMake错误 "找不到Boost"

**解决方案**：
```bash
# 安装Boost库
# Ubuntu/Debian
sudo apt install libboost-all-dev

# CentOS/RHEL
sudo yum install boost-devel

# macOS
brew install boost

# 指定Boost路径
cmake -DBOOST_ROOT=/path/to/boost ..
```

### 问题4：内存不足错误

**解决方案**：
```bash
# 增加交换空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 或减少编译线程
make -j2
```

### 问题5：Windows特定问题

**解决方案**：
1. 使用WSL2而不是原生Windows
2. 确保安装Visual Studio Build Tools
3. 使用管理员权限运行命令提示符

## 卸载指南

### 完全卸载

```bash
# 1. 卸载Python包
pip uninstall pplustrader -y

# 2. 删除构建目录
rm -rf build/

# 3. 删除Python缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.so" -delete

# 4. 删除虚拟环境（如果使用）
deactivate
rm -rf venv/

# 5. 删除系统安装（如果使用）
sudo rm -rf /usr/local/lib/libpplustrader*
sudo rm -rf /usr/local/include/pplustrader/
```

### 保留数据卸载

```bash
# 只卸载程序，保留数据
pip uninstall pplustrader -y

# 备份数据
cp -r data/ data_backup/
cp config/settings.yaml config_backup/

# 清理程序文件
rm -rf build/ venv/
```

## 获取帮助

如果遇到问题，请：

1. **查看文档**: 阅读[用户指南](docs/用户指南.md)
2. **搜索问题**: 查看[常见问题](#常见问题)部分
3. **提交Issue**: 访问[GitHub Issues](https://github.com/yourusername/PlusPlusTrader/issues)
4. **社区支持**: 加入[Discord社区](https://discord.gg/pplustrader)

## 下一步

安装完成后，建议：

1. **阅读教程**: 查看[快速开始](README.md#快速开始)
2. **运行示例**: 尝试`examples/`目录中的示例代码
3. **配置环境**: 根据需求修改`config/`目录中的配置文件
4. **加入社区**: 与其他用户交流使用经验

---

**安装完成！现在开始您的量化交易之旅吧！** 🚀

> 提示：建议定期更新到最新版本以获取性能改进和新功能。