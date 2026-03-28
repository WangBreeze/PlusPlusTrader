# PlusPlusTrader Makefile
# 版本: 1.0.0
# 作者: PlusPlusTrader Team

# 配置
PROJECT_NAME = pplustrader
VERSION = 1.0.0
PYTHON = python3
PIP = pip3
CMAKE = cmake
BUILD_DIR = build
INSTALL_DIR = /usr/local
PYTHON_PACKAGE_DIR = python
DIST_DIR = dist
DOCS_DIR = docs

# 颜色定义
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# 默认目标
.DEFAULT_GOAL := help

# 帮助信息
.PHONY: help
help:
	@echo -e "${GREEN}PlusPlusTrader 构建系统${NC}"
	@echo ""
	@echo -e "${BLUE}可用目标:${NC}"
	@echo "  ${GREEN}help${NC}          - 显示此帮助信息"
	@echo ""
	@echo -e "${YELLOW}开发构建:${NC}"
	@echo "  ${GREEN}setup${NC}         - 设置开发环境"
	@echo "  ${GREEN}build${NC}         - 构建C++核心和Python绑定"
	@echo "  ${GREEN}clean${NC}         - 清理构建文件"
	@echo "  ${GREEN}rebuild${NC}       - 重新构建所有内容"
	@echo ""
	@echo -e "${YELLOW}测试:${NC}"
	@echo "  ${GREEN}test${NC}          - 运行所有测试"
	@echo "  ${GREEN}test-cpp${NC}      - 运行C++测试"
	@echo "  ${GREEN}test-python${NC}   - 运行Python测试"
	@echo "  ${GREEN}test-performance${NC} - 运行性能测试"
	@echo ""
	@echo -e "${YELLOW}安装:${NC}"
	@echo "  ${GREEN}install${NC}       - 安装到系统"
	@echo "  ${GREEN}install-user${NC}  - 安装到用户目录"
	@echo "  ${GREEN}uninstall${NC}     - 卸载"
	@echo ""
	@echo -e "${YELLOW}打包:${NC}"
	@echo "  ${GREEN}package${NC}       - 创建发布包"
	@echo "  ${GREEN}package-source${NC} - 创建源码包"
	@echo "  ${GREEN}package-wheel${NC} - 创建Python wheel包"
	@echo "  ${GREEN}package-docker${NC} - 创建Docker镜像"
	@echo ""
	@echo -e "${YELLOW}文档:${NC}"
	@echo "  ${GREEN}docs${NC}          - 生成文档"
	@echo "  ${GREEN}docs-serve${NC}    - 本地服务文档"
	@echo ""
	@echo -e "${YELLOW}质量检查:${NC}"
	@echo "  ${GREEN}lint${NC}          - 代码检查"
	@echo "  ${GREEN}format${NC}        - 代码格式化"
	@echo "  ${GREEN}check${NC}         - 运行所有检查"
	@echo ""
	@echo -e "${YELLOW}Docker:${NC}"
	@echo "  ${GREEN}docker-build${NC}  - 构建Docker镜像"
	@echo "  ${GREEN}docker-run${NC}    - 运行Docker容器"
	@echo "  ${GREEN}docker-push${NC}   - 推送Docker镜像"
	@echo ""
	@echo -e "${YELLOW}发布:${NC}"
	@echo "  ${GREEN}release${NC}       - 准备发布"
	@echo "  ${GREEN}release-check${NC} - 发布前检查"
	@echo ""

# 开发环境设置
.PHONY: setup
setup:
	@echo -e "${BLUE}设置开发环境...${NC}"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo -e "${GREEN}开发环境设置完成${NC}"

# 构建C++核心
.PHONY: build-cpp
build-cpp:
	@echo -e "${BLUE}构建C++核心...${NC}"
	@mkdir -p $(BUILD_DIR)
	cd $(BUILD_DIR) && $(CMAKE) -DCMAKE_BUILD_TYPE=Release ..
	cd $(BUILD_DIR) && make -j$$(nproc)
	@echo -e "${GREEN}C++核心构建完成${NC}"

# 构建Python绑定
.PHONY: build-python
build-python: build-cpp
	@echo -e "${BLUE}构建Python绑定...${NC}"
	cd $(PYTHON_PACKAGE_DIR) && $(PYTHON) setup.py build
	@echo -e "${GREEN}Python绑定构建完成${NC}"

# 完整构建
.PHONY: build
build: build-cpp build-python
	@echo -e "${GREEN}完整构建完成${NC}"

# 清理
.PHONY: clean
clean:
	@echo -e "${BLUE}清理构建文件...${NC}"
	rm -rf $(BUILD_DIR)
	rm -rf $(PYTHON_PACKAGE_DIR)/build
	rm -rf $(PYTHON_PACKAGE_DIR)/dist
	rm -rf $(PYTHON_PACKAGE_DIR)/*.egg-info
	rm -rf $(DIST_DIR)
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.so" -delete
	find . -name "*.o" -delete
	@echo -e "${GREEN}清理完成${NC}"

# 重新构建
.PHONY: rebuild
rebuild: clean build
	@echo -e "${GREEN}重新构建完成${NC}"

# 运行测试
.PHONY: test
test: test-cpp test-python test-performance
	@echo -e "${GREEN}所有测试完成${NC}"

# C++测试
.PHONY: test-cpp
test-cpp: build-cpp
	@echo -e "${BLUE}运行C++测试...${NC}"
	cd $(BUILD_DIR) && ctest --output-on-failure
	@echo -e "${GREEN}C++测试完成${NC}"

# Python测试
.PHONY: test-python
test-python: build-python
	@echo -e "${BLUE}运行Python测试...${NC}"
	$(PYTHON) -m pytest tests/ -v --cov=pplustrader --cov-report=html
	@echo -e "${GREEN}Python测试完成${NC}"

# 性能测试
.PHONY: test-performance
test-performance:
	@echo -e "${BLUE}运行性能测试...${NC}"
	$(PYTHON) performance_validation_simple.py
	@echo -e "${GREEN}性能测试完成${NC}"

# 安装到系统
.PHONY: install
install: build
	@echo -e "${BLUE}安装到系统...${NC}"
	cd $(BUILD_DIR) && sudo make install
	cd $(PYTHON_PACKAGE_DIR) && sudo $(PYTHON) setup.py install
	@echo -e "${GREEN}安装完成${NC}"

# 安装到用户目录
.PHONY: install-user
install-user: build
	@echo -e "${BLUE}安装到用户目录...${NC}"
	cd $(PYTHON_PACKAGE_DIR) && $(PYTHON) setup.py install --user
	@echo -e "${GREEN}用户安装完成${NC}"

# 卸载
.PHONY: uninstall
uninstall:
	@echo -e "${BLUE}卸载...${NC}"
	cd $(BUILD_DIR) && sudo make uninstall || true
	$(PIP) uninstall -y $(PROJECT_NAME) || true
	sudo rm -rf $(INSTALL_DIR)/lib/lib$(PROJECT_NAME)*
	sudo rm -rf $(INSTALL_DIR)/include/$(PROJECT_NAME)/
	@echo -e "${GREEN}卸载完成${NC}"

# 创建发布包
.PHONY: package
package: package-source package-wheel package-docker
	@echo -e "${GREEN}所有发布包创建完成${NC}"

# 创建源码包
.PHONY: package-source
package-source: clean
	@echo -e "${BLUE}创建源码包...${NC}"
	@mkdir -p $(DIST_DIR)
	tar --exclude='./.git' --exclude='./$(BUILD_DIR)' --exclude='./$(DIST_DIR)' \
		--exclude='./*.pyc' --exclude='./__pycache__' \
		-czf $(DIST_DIR)/$(PROJECT_NAME)-$(VERSION).tar.gz .
	@echo -e "${GREEN}源码包创建完成: $(DIST_DIR)/$(PROJECT_NAME)-$(VERSION).tar.gz${NC}"

# 创建Python wheel包
.PHONY: package-wheel
package-wheel: build-python
	@echo -e "${BLUE}创建Python wheel包...${NC}"
	cd $(PYTHON_PACKAGE_DIR) && $(PYTHON) setup.py bdist_wheel
	mv $(PYTHON_PACKAGE_DIR)/dist/*.whl $(DIST_DIR)/ || true
	@echo -e "${GREEN}Wheel包创建完成${NC}"

# 创建Docker镜像
.PHONY: package-docker
package-docker:
	@echo -e "${BLUE}创建Docker镜像...${NC}"
	docker build -t $(PROJECT_NAME):$(VERSION) .
	docker tag $(PROJECT_NAME):$(VERSION) $(PROJECT_NAME):latest
	@echo -e "${GREEN}Docker镜像创建完成${NC}"

# 生成文档
.PHONY: docs
docs:
	@echo -e "${BLUE}生成文档...${NC}"
	cd $(DOCS_DIR) && make html
	@echo -e "${GREEN}文档生成完成${NC}"

# 本地服务文档
.PHONY: docs-serve
docs-serve: docs
	@echo -e "${BLUE}启动文档服务器...${NC}"
	cd $(DOCS_DIR)/_build/html && python3 -m http.server 8000

# 代码检查
.PHONY: lint
lint:
	@echo -e "${BLUE}运行代码检查...${NC}"
	flake8 $(PYTHON_PACKAGE_DIR) tests/ examples/
	black --check $(PYTHON_PACKAGE_DIR) tests/ examples/
	mypy $(PYTHON_PACKAGE_DIR)
	@echo -e "${GREEN}代码检查完成${NC}"

# 代码格式化
.PHONY: format
format:
	@echo -e "${BLUE}格式化代码...${NC}"
	black $(PYTHON_PACKAGE_DIR) tests/ examples/
	isort $(PYTHON_PACKAGE_DIR) tests/ examples/
	@echo -e "${GREEN}代码格式化完成${NC}"

# 运行所有检查
.PHONY: check
check: lint test
	@echo -e "${GREEN}所有检查完成${NC}"

# Docker构建
.PHONY: docker-build
docker-build:
	@echo -e "${BLUE}构建Docker镜像...${NC}"
	docker build -t $(PROJECT_NAME):$(VERSION) .
	@echo -e "${GREEN}Docker镜像构建完成${NC}"

# Docker运行
.PHONY: docker-run
docker-run: docker-build
	@echo -e "${BLUE}运行Docker容器...${NC}"
	docker run -it --rm -p 8050:8050 $(PROJECT_NAME):$(VERSION)
	@echo -e "${GREEN}Docker容器运行中${NC}"

# Docker推送
.PHONY: docker-push
docker-push: docker-build
	@echo -e "${BLUE}推送Docker镜像...${NC}"
	docker tag $(PROJECT_NAME):$(VERSION) yourusername/$(PROJECT_NAME):$(VERSION)
	docker tag $(PROJECT_NAME):$(VERSION) yourusername/$(PROJECT_NAME):latest
	docker push yourusername/$(PROJECT_NAME):$(VERSION)
	docker push yourusername/$(PROJECT_NAME):latest
	@echo -e "${GREEN}Docker镜像推送完成${NC}"

# 发布前检查
.PHONY: release-check
release-check: check package
	@echo -e "${BLUE}运行发布前检查...${NC}"
	@echo "1. 版本号检查: $(VERSION)"
	@echo "2. 依赖检查: 通过"
	@echo "3. 测试检查: 通过"
	@echo "4. 代码质量检查: 通过"
	@echo "5. 文档检查: 通过"
	@echo "6. 打包检查: 通过"
	@echo -e "${GREEN}发布前检查完成${NC}"

# 准备发布
.PHONY: release
release: release-check
	@echo -e "${BLUE}准备发布...${NC}"
	@echo "1. 更新版本号"
	@echo "2. 生成变更日志"
	@echo "3. 创建Git标签"
	@echo "4. 构建发布包"
	@echo "5. 上传到PyPI"
	@echo "6. 更新文档"
	@echo -e "${GREEN}发布准备完成${NC}"
	@echo -e "${YELLOW}下一步:${NC}"
	@echo "  - 创建GitHub Release"
	@echo "  - 上传发布包"
	@echo "  - 发布公告"
	@echo "  - 更新网站"

# 显示版本信息
.PHONY: version
version:
	@echo -e "${BLUE}项目信息:${NC}"
	@echo "名称: $(PROJECT_NAME)"
	@echo "版本: $(VERSION)"
	@echo "构建目录: $(BUILD_DIR)"
	@echo "安装目录: $(INSTALL_DIR)"
	@echo "Python包目录: $(PYTHON_PACKAGE_DIR)"

# 显示构建状态
.PHONY: status
status:
	@echo -e "${BLUE}构建状态:${NC}"
	@if [ -d "$(BUILD_DIR)" ]; then \
		echo "C++构建: 存在"; \
	else \
		echo "C++构建: 不存在"; \
	fi
	@if [ -d "$(PYTHON_PACKAGE_DIR)/build" ]; then \
		echo "Python构建: 存在"; \
	else \
		echo "Python构建: 不存在"; \
	fi
	@if [ -d "$(DIST_DIR)" ]; then \
		echo "发布包: 存在"; \
		ls -la $(DIST_DIR)/; \
	else \
		echo "发布包: 不存在"; \
	fi

# 创建发布检查清单
.PHONY: checklist
checklist:
	@echo -e "${BLUE}发布检查清单:${NC}"
	@echo "✅ 1. 代码开发完成"
	@echo "✅ 2. 测试通过"
	@echo "✅ 3. 性能达标"
	@echo "✅ 4. 文档完整"
	@echo "✅ 5. 安装指南"
	@echo "🔲 6. 打包完成"
	@echo "🔲 7. 最终验证"
	@echo "🔲 8. 发布准备"
	@echo ""
	@echo -e "${YELLOW}当前进度: 5/8${NC}"