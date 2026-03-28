#!/bin/bash

# PlusPlusTrader 发布打包脚本
# 版本: 1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="pplustrader"
VERSION="1.0.0"
AUTHOR="PlusPlusTrader Team"
LICENSE="MIT"

# 目录配置
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
RELEASES_DIR="$PROJECT_ROOT/releases"
BUILD_DIR="$PROJECT_ROOT/build"

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

# 显示标题
show_title() {
    echo -e "${GREEN}"
    echo "================================================"
    echo "    PlusPlusTrader 发布打包工具"
    echo "================================================"
    echo -e "${NC}"
    echo "项目: $PROJECT_NAME"
    echo "版本: $VERSION"
    echo "作者: $AUTHOR"
    echo "许可证: $LICENSE"
    echo ""
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 '$1' 未找到"
        return 1
    fi
    return 0
}

# 清理目录
clean_dist() {
    log_info "清理发布目录..."
    if [ -d "$DIST_DIR" ]; then
        rm -rf "$DIST_DIR"
    fi
    mkdir -p "$DIST_DIR"
    log_success "发布目录清理完成"
}

# 创建源码包
create_source_package() {
    log_info "创建源码包..."
    
    PACKAGE_NAME="${PROJECT_NAME}-${VERSION}"
    TAR_FILE="${DIST_DIR}/${PACKAGE_NAME}.tar.gz"
    ZIP_FILE="${DIST_DIR}/${PACKAGE_NAME}.zip"
    
    # 排除的文件和目录
    EXCLUDE_PATTERNS=(
        ".git"
        ".github"
        ".vscode"
        ".idea"
        "__pycache__"
        "*.pyc"
        "*.pyo"
        "*.so"
        "*.o"
        "build"
        "dist"
        "releases"
        "venv"
        ".env"
        "*.log"
        "*.tmp"
        "*.bak"
    )
    
    # 创建tar.gz包
    log_info "创建 $TAR_FILE..."
    tar --exclude-vcs \
        --exclude="build" \
        --exclude="dist" \
        --exclude="releases" \
        --exclude="venv" \
        --exclude="__pycache__" \
        --exclude="*.pyc" \
        --exclude="*.pyo" \
        --exclude="*.so" \
        --exclude="*.o" \
        -czf "$TAR_FILE" \
        -C "$PROJECT_ROOT" \
        .
    
    # 创建zip包
    log_info "创建 $ZIP_FILE..."
    cd "$PROJECT_ROOT" && zip -r "$ZIP_FILE" . \
        -x "*.git*" \
        -x "build/*" \
        -x "dist/*" \
        -x "releases/*" \
        -x "venv/*" \
        -x "*__pycache__*" \
        -x "*.pyc" \
        -x "*.pyo" \
        -x "*.so" \
        -x "*.o"
    
    log_success "源码包创建完成:"
    log_success "  - $(basename $TAR_FILE)"
    log_success "  - $(basename $ZIP_FILE)"
}

# 创建Python包
create_python_package() {
    log_info "创建Python包..."
    
    PYTHON_DIR="$PROJECT_ROOT/python"
    
    if [ ! -d "$PYTHON_DIR" ]; then
        log_error "Python目录不存在: $PYTHON_DIR"
        return 1
    fi
    
    # 进入Python目录
    cd "$PYTHON_DIR"
    
    # 构建wheel包
    log_info "构建wheel包..."
    python3 setup.py bdist_wheel
    
    # 构建源码包
    log_info "构建源码包..."
    python3 setup.py sdist
    
    # 移动文件到dist目录
    for file in dist/*; do
        if [ -f "$file" ]; then
            mv "$file" "$DIST_DIR/"
            log_success "移动: $(basename $file)"
        fi
    done
    
    # 返回项目根目录
    cd "$PROJECT_ROOT"
    
    log_success "Python包创建完成"
}

# 创建安装包
create_installer_package() {
    log_info "创建安装包..."
    
    PACKAGE_NAME="${PROJECT_NAME}-installer-${VERSION}"
    INSTALLER_DIR="${DIST_DIR}/${PACKAGE_NAME}"
    TAR_FILE="${DIST_DIR}/${PACKAGE_NAME}.tar.gz"
    
    # 创建安装包目录
    mkdir -p "$INSTALLER_DIR"
    
    # 复制必要文件
    FILES_TO_COPY=(
        "README.md"
        "INSTALL.md"
        "CHANGELOG.md"
        "LICENSE"
        "requirements.txt"
        "install.sh"
        "Dockerfile"
        "docker-compose.yml"
        "Makefile"
        "RELEASE_CHECKLIST.md"
        "RELEASE_ANNOUNCEMENT.md"
    )
    
    for file in "${FILES_TO_COPY[@]}"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            cp "$PROJECT_ROOT/$file" "$INSTALLER_DIR/"
            log_success "复制: $file"
        else
            log_warning "文件不存在: $file"
        fi
    done
    
    # 复制脚本目录
    if [ -d "$PROJECT_ROOT/scripts" ]; then
        cp -r "$PROJECT_ROOT/scripts" "$INSTALLER_DIR/"
        log_success "复制: scripts/"
    fi
    
    # 复制示例目录
    if [ -d "$PROJECT_ROOT/examples" ]; then
        cp -r "$PROJECT_ROOT/examples" "$INSTALLER_DIR/"
        log_success "复制: examples/"
    fi
    
    # 复制配置目录
    if [ -d "$PROJECT_ROOT/config" ]; then
        cp -r "$PROJECT_ROOT/config" "$INSTALLER_DIR/"
        log_success "复制: config/"
    fi
    
    # 创建安装脚本
    create_installer_script "$INSTALLER_DIR"
    
    # 创建tar包
    log_info "创建安装包: $(basename $TAR_FILE)"
    tar -czf "$TAR_FILE" -C "$DIST_DIR" "$PACKAGE_NAME"
    
    # 清理临时目录
    rm -rf "$INSTALLER_DIR"
    
    log_success "安装包创建完成: $(basename $TAR_FILE)"
}

# 创建安装脚本
create_installer_script() {
    local installer_dir="$1"
    
    cat > "$installer_dir/install.sh" << 'EOF'
#!/bin/bash
# PlusPlusTrader 安装脚本
# 版本: 1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 项目配置
PROJECT_NAME="pplustrader"
VERSION="1.0.0"
AUTHOR="PlusPlusTrader Team"
LICENSE="MIT"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示欢迎信息
show_welcome() {
    echo -e "${GREEN}"
    echo "================================================"
    echo "        PlusPlusTrader 安装程序"
    echo "================================================"
    echo -e "${NC}"
    echo "版本: $VERSION"
    echo "项目: $PROJECT_NAME"
    echo "作者: $AUTHOR"
    echo "许可证: $LICENSE"
    echo ""
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "需要Python 3.8+，请先安装Python"
        return 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(python3 -c "import sys; print(sys.version_info >= (3, 8))") == "False" ]]; then
        log_error "需要Python 3.8+，当前版本: $PYTHON_VERSION"
        return 1
    fi
    
    log_success "Python版本: $PYTHON_VERSION"
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "需要pip，请先安装pip"
        return 1
    fi
    
    log_success "系统要求检查通过"
    return 0
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install --upgrade pip
        pip3 install -r requirements.txt
        log_success "Python依赖安装完成"
    else
        log_error "requirements.txt 文件不存在"
        return 1
    fi
    
    return 0
}

# 运行安装脚本
run_install_script() {
    log_info "运行安装脚本..."
    
    if [ -f "install.sh" ]; then
        chmod +x install.sh
        ./install.sh
    elif [ -f "Makefile" ]; then
        make build
        make install-user
    else
        log_error "未找到安装脚本"
        return 1
    fi
    
    return 0
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    if python3 -c "import pplustrader as ppt; print(f'✅ PlusPlusTrader版本: {ppt.get_version()}')"; then
        log_success "安装验证成功"
        return 0
    else
        log_error "安装验证失败"
        return 1
    fi
}

# 显示完成信息
show_completion() {
    echo ""
    echo -e "${GREEN}================================================"
    echo "        PlusPlusTrader 安装完成！"
    echo "================================================"
    echo -e "${NC}"
    
    echo "🎉 恭喜！PlusPlusTrader 已成功安装。"
    echo ""
    echo "🚀 快速开始:"
    echo "  运行示例: python3 examples/basic_usage.py"
    echo "  启动Web界面: python3 web/dashboard.py"
    echo ""
    echo "📚 文档:"
    echo "  查看 README.md 获取更多信息"
    echo ""
    echo "💬 获取帮助:"
    echo "  GitHub Issues: https://github.com/yourusername/PlusPlusTrader/issues"
    echo "  文档网站: https://docs.pplustrader.com"
    echo ""
}

# 主函数
main() {
    show_welcome
    
    # 检查系统要求
    if ! check_requirements; then
        exit 1
    fi
    
    # 安装依赖
    if ! install_dependencies; then
        exit 1
    fi
    
    # 运行安装脚本
    if ! run_install_script; then
        exit 1
    fi
    
    # 验证安装
    if ! verify_installation; then
        exit 1
    fi
    
    # 显示完成信息
    show_completion
}

# 运行主函数
main "$@"
EOF
    
    # 设置执行权限
    chmod +x "$installer_dir/install.sh"
    log_success "创建安装脚本: install.sh"
}

# 计算文件校验和
calculate_checksums() {
    log_info "计算文件校验和..."
    
    CHECKSUMS_JSON="$DIST_DIR/checksums.json"
    CHECKSUMS_TXT="$DIST_DIR/checksums.txt"
    
    # 创建JSON格式的校验和
    echo "{" > "$CHECKSUMS_JSON"
    FIRST=true
    
    for file in "$DIST_DIR"/*; do
        if [ -f "$file" ]; then
            FILENAME=$(basename "$file")
            FILESIZE=$(stat -c%s "$file")
            MD5=$(md5sum "$file" | awk '{print $1}')
            SHA256=$(sha256sum "$file" | awk '{print $1}')
            
            if [ "$FIRST" = false ]; then
                echo "," >> "$CHECKSUMS_JSON"
            fi
            FIRST=false
            
            cat >> "$CHECKSUMS_JSON" << EOF
  "$FILENAME": {
    "size": $FILESIZE,
    "md5": "$MD5",
    "sha256": "$SHA256"
  }
EOF
        fi
    done
    
    echo "}" >> "$CHECKSUMS_JSON"
    
    # 创建文本格式的校验和
    cat > "$CHECKSUMS_TXT" << EOF
PlusPlusTrader $VERSION 文件校验和
========================================

EOF
    
    for file in "$DIST_DIR"/*; do
        if [ -f "$file" ]; then
            FILENAME=$(basename "$file")
            FILESIZE=$(stat -c%s "$file")
            MD5=$(md5sum "$file" | awk '{print $1}')
            SHA256=$(sha256sum "$file" | awk '{print $1}')
            
            cat >> "$CHECKSUMS_TXT" << EOF
文件: $FILENAME
大小: $FILESIZE 字节
MD5: $MD5
SHA256: $SHA256
----------------------------------------

EOF
        fi
    done
    
    log_success "校验和文件创建完成:"
    log_success "  - $(basename $CHECKSUMS_JSON)"
    log_success "  - $(basename $CHECKSUMS_TXT)"
}

# 创建发布说明
create_release_notes() {
    log_info "创建发布说明..."
    
    RELEASE_NOTES="$RELEASES_DIR/release-$VERSION.md"
    
    cat > "$RELEASE_NOTES" << EOF
# PlusPlusTrader $VERSION 发布说明

## 发布信息
- **版本**: $VERSION
- **发布日期**: $(date +%Y-%m-%d)
- **发布类型**: 正式发布
- **项目**: $PROJECT_NAME
- **作者**: $AUTHOR
- **许可证**: $LICENSE

## 发布内容

### 源码包
- \`${PROJECT_NAME}-${VERSION}.tar.gz\` - 完整源码包
- \`${PROJECT_NAME}-${VERSION}.zip\` - ZIP格式源码包

### Python包
- \`${PROJECT_NAME}-${VERSION}-py3-none-any.whl\` - Python wheel包
- \`${PROJECT_NAME}-${VERSION}.tar.gz\` - Python源码包

### 安装包
- \`${PROJECT_NAME}-installer-${VERSION}.tar.gz\` - 完整安装包

### 校验和文件
- \`checksums.json\` - JSON格式校验和
- \`checksums.txt\` - 文本格式校验和

## 安装方式

### 1. 使用安装包
\`\`\`bash
tar -xzf ${PROJECT_NAME}-installer-${VERSION}.tar.gz
cd ${PROJECT_NAME}-installer-${VERSION}
./install.sh
\`\`\`

### 2. 使用源码包
\`\`\`bash
tar -xzf ${PROJECT_NAME}-${VERSION}.tar.gz
cd ${PROJECT_NAME}-${VERSION}
./install.sh
\`\`\`

### 3. 使用Python包
\`\`\`bash
pip install ${PROJECT_NAME}-${VERSION}-py3-none-any.whl
\`\`\`

## 系统要求
- **操作系统**: Linux/macOS/Windows (WSL2)
- **Python**: 3.8+
- **内存**: 4GB+ (推荐8GB)
- **存储**: 2GB+ 可用空间

## 功能特性
- 高性能C++核心引擎
- 完整的技术指标系统
- 专业的回测引擎
- Python生态完美集成
- 现代化Web界面
- 用户反馈和社区功能

## 性能指标
- 高频延迟: 67.7微秒/数据点
- 吞吐量: 14,771数据点/秒
- 最佳吞吐量: 1,000,000+点/秒
- 内存效率: 内存池机制，无显著泄漏

## 文档资源
- 用户指南: docs/用户指南.md
- API文档: docs/API文档.md
- 安装指南: INSTALL.md
- 示例代码: examples/

## 获取帮助
- GitHub Issues: https://github.com/yourusername/PlusPlusTrader/issues
- 文档网站: https://docs.pplustrader.com
- Discord社区: https://discord.gg/pplustrader

## 校验和验证
安装前请验证文件完整性，使用校验和文件确保文件未被篡改。

## 发布团队
- 项目负责人: 王立超
- 开发团队: PlusPlusTrader Team
- 质量保证: OpenClaw AI助手
- 文档团队: OpenClaw AI助手

## 更新日志
详细更新内容请查看 CHANGELOG.md 文件。

---
*PlusPlusTrader 团队*
*$(date +%Y年%m月%d日)*
EOF
    
    log_success "发布说明创建完成: $(basename $RELEASE_NOTES)"
}

# 显示发布包信息
show_package_info() {
    log_info "发布包信息汇总..."
    
    echo ""
    echo -e "${GREEN}================================================"
    echo "        发布包创建完成！"
    echo "================================================"
    echo -e "${NC}"
    
    echo "📦 创建的发布包:"
    echo ""
    
    TOTAL_SIZE=0
    FILE_COUNT=0
    
    for file in "$DIST_DIR"/*; do
        if [ -f "$file" ]; then
            FILENAME=$(basename "$file")
            FILESIZE=$(stat -c%s "$file")
            SIZE_MB=$(echo "scale=2; $FILESIZE / 1048576" | bc)
            TOTAL_SIZE=$((TOTAL_SIZE + FILESIZE))
            FILE_COUNT=$((FILE_COUNT + 1))
            
            printf "  %-40s %8.2f MB\n" "$FILENAME" "$SIZE_MB"
        fi
    done
    
    TOTAL_SIZE_MB=$(echo "scale=2; $TOTAL_SIZE / 1048576" | bc)
    
    echo ""
    echo "📊 统计信息:"
    echo "  文件数量: $FILE_COUNT 个"
    echo "  总大小: $TOTAL_SIZE_MB MB"
    echo ""
    echo "📁 文件位置: $DIST_DIR"
    echo "📝 发布说明: $RELEASES_DIR/release-$VERSION.md"
    echo ""
    echo "🚀 下一步:"
    echo "  1. 测试发布包安装"
    echo "  2. 创建GitHub Release"
    echo "  3. 上传发布文件"
    echo "  4. 发布公告"
    echo ""
}

# 主函数
main() {
    show_title
    
    # 检查必要命令
    check_command tar || exit 1
    check_command zip || exit 1
    check_command python3 || exit 1
    check_command pip3 || exit 1
    
    # 清理发布目录
    clean_dist
    
    # 创建各种包
    create_source_package
    create_python_package
    create_installer_package
    
    # 计算校验和
    calculate_checksums
    
    # 创建发布说明
    create_release_notes
    
    # 显示结果
    show_package_info
    
    echo -e "${GREEN}🎉 发布打包完成！${NC}"
}

# 运行主函数
main "$@"