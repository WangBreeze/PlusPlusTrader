#!/bin/bash

# PlusPlusTrader 安装脚本
# 版本: 1.0.0
# 作者: PlusPlusTrader团队

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 打印标题
print_title() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}   PlusPlusTrader 安装程序   ${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python版本: $PYTHON_VERSION"
        
        # 检查Python版本
        if [[ "$PYTHON_VERSION" =~ ^3\.(8|9|10|11|12) ]]; then
            log_success "Python版本符合要求"
        else
            log_warning "Python版本可能过低，建议使用3.8+"
        fi
    else
        log_error "未找到Python3，请先安装Python3.8+"
        exit 1
    fi
    
    # 检查pip
    if command_exists pip3; then
        log_success "找到pip3"
    else
        log_warning "未找到pip3，尝试安装..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get install -y python3-pip
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install python3
        fi
    fi
    
    # 检查git
    if command_exists git; then
        log_success "找到git"
    else
        log_error "未找到git，请先安装git"
        exit 1
    fi
    
    # 检查CMake
    if command_exists cmake; then
        CMAKE_VERSION=$(cmake --version | head -n1 | cut -d' ' -f3)
        log_info "CMake版本: $CMAKE_VERSION"
        log_success "找到CMake"
    else
        log_warning "未找到CMake，尝试安装..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get install -y cmake
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install cmake
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            log_error "请在Windows上手动安装CMake"
            exit 1
        fi
    fi
    
    # 检查C++编译器
    if command_exists g++; then
        GCC_VERSION=$(g++ --version | head -n1 | cut -d' ' -f4)
        log_info "GCC版本: $GCC_VERSION"
        log_success "找到C++编译器"
    elif command_exists clang++; then
        CLANG_VERSION=$(clang++ --version | head -n1 | cut -d' ' -f3)
        log_info "Clang版本: $CLANG_VERSION"
        log_success "找到C++编译器"
    else
        log_warning "未找到C++编译器，尝试安装..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get install -y build-essential
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            xcode-select --install
        fi
    fi
    
    log_success "系统要求检查完成"
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y \
                build-essential \
                cmake \
                git \
                python3-dev \
                python3-venv \
                libboost-all-dev \
                libeigen3-dev
        # CentOS/RHEL
        elif command_exists yum; then
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y \
                cmake \
                git \
                python3-devel \
                boost-devel \
                eigen3-devel
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install cmake git boost eigen
        else
            log_warning "未找到Homebrew，建议安装Homebrew以简化依赖管理"
            log_info "访问 https://brew.sh 安装Homebrew"
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows (Git Bash)
        log_warning "Windows环境需要手动安装以下依赖:"
        log_info "1. Visual Studio 2019+ (包含C++桌面开发)"
        log_info "2. Python 3.8+ (从python.org下载)"
        log_info "3. CMake (从cmake.org下载)"
        log_info "4. Git (从git-scm.com下载)"
    fi
    
    log_success "系统依赖安装完成"
}

# 创建虚拟环境
create_venv() {
    log_info "创建Python虚拟环境..."
    
    if [ -d "venv" ]; then
        log_warning "虚拟环境已存在，是否重新创建？(y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            rm -rf venv
            python3 -m venv venv
        fi
    else
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        log_error "无法激活虚拟环境"
        exit 1
    fi
    
    log_success "虚拟环境创建并激活"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."
    
    # 升级pip
    pip install --upgrade pip setuptools wheel
    
    # 检查requirements.txt是否存在
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        log_error "未找到requirements.txt文件"
        exit 1
    fi
    
    # 安装开发依赖（如果存在）
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi
    
    log_success "Python依赖安装完成"
}

# 编译C++核心
compile_cpp_core() {
    log_info "编译C++核心..."
    
    # 清理旧的构建目录
    if [ -d "build" ]; then
        log_warning "构建目录已存在，是否清理？(y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            rm -rf build
        fi
    fi
    
    # 创建构建目录
    mkdir -p build
    cd build || exit 1
    
    # 配置CMake
    log_info "配置CMake..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        cmake .. -G "Visual Studio 16 2019" -A x64
        log_warning "请在Visual Studio中打开build目录下的.sln文件进行编译"
        cd ..
        return
    else
        # Linux/macOS
        cmake .. -DCMAKE_BUILD_TYPE=Release
    fi
    
    # 编译
    log_info "编译代码..."
    if command_exists nproc; then
        CORES=$(nproc)
    else
        CORES=4
    fi
    
    make -j"$CORES"
    
    # 返回项目根目录
    cd ..
    
    log_success "C++核心编译完成"
}

# 安装Python包
install_python_package() {
    log_info "安装Python包..."
    
    # 开发模式安装
    pip install -e .
    
    log_success "Python包安装完成"
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    # 创建测试脚本
    cat > test_install.py << 'EOF'
import pplustrader as ppt
import sys

def test():
    print("=" * 50)
    print("PlusPlusTrader 安装验证")
    print("=" * 50)
    
    try:
        # 测试版本
        print(f"1. 版本: {ppt.__version__}")
        
        # 测试策略
        strategy = ppt.MACrossStrategy(short_period=10, long_period=30)
        print(f"2. 策略: {strategy.name}")
        
        # 测试指标
        sma = ppt.SMA(period=20)
        prices = [100, 102, 101, 105, 103]
        for price in prices:
            value = sma.update(price)
        print(f"3. 指标: SMA值 = {value:.2f}")
        
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
    success = test()
    sys.exit(0 if success else 1)
EOF
    
    # 运行测试
    if python test_install.py; then
        log_success "安装验证通过"
        rm -f test_install.py
    else
        log_error "安装验证失败"
        rm -f test_install.py
        exit 1
    fi
}

# 显示完成信息
show_completion() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}   安装完成！   ${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    
    echo -e "🎉 ${GREEN}PlusPlusTrader 已成功安装！${NC}\n"
    
    echo -e "${BLUE}下一步：${NC}"
    echo -e "1. ${YELLOW}激活虚拟环境：${NC}"
    echo -e "   Linux/macOS: ${GREEN}source venv/bin/activate${NC}"
    echo -e "   Windows: ${GREEN}venv\\Scripts\\activate${NC}"
    echo -e ""
    echo -e "2. ${YELLOW}运行示例：${NC}"
    echo -e "   ${GREEN}python examples/basic_backtest.py${NC}"
    echo -e ""
    echo -e "3. ${YELLOW}查看文档：${NC}"
    echo -e "   ${GREEN}打开 docs/TUTORIAL.md${NC}"
    echo -e ""
    echo -e "4. ${YELLOW}启动Web界面：${NC}"
    echo -e "   ${GREEN}python web/app.py${NC}"
    echo -e "   然后在浏览器打开 ${BLUE}http://localhost:8050${NC}"
    echo -e ""
    echo -e "${BLUE}获取帮助：${NC}"
    echo -e "📚 文档: ${GREEN}https://github.com/WangBreeze/PlusPlusTrader${NC}"
    echo -e "🐛 问题: ${GREEN}https://github.com/WangBreeze/PlusPlusTrader/issues${NC}"
    echo -e ""
    echo -e "${GREEN}感谢使用 PlusPlusTrader！🚀${NC}"
}

# 主函数
main() {
    print_title
    
    # 检查是否在项目目录中
    if [ ! -f "requirements.txt" ] && [ ! -f "pyproject.toml" ]; then
        log_error "请在PlusPlusTrader项目目录中运行此脚本"
        log_info "使用: git clone https://github.com/WangBreeze/PlusPlusTrader.git"
        log_info "然后: cd PlusPlusTrader"
        exit 1
    fi
    
    # 安装步骤
    check_requirements
    install_system_deps
    create_venv
    install_python_deps
    compile_cpp_core
    install_python_package
    verify_installation
    show_completion
}

# 运行主函数
main "$@"