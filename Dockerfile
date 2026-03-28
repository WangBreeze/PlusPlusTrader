# PlusPlusTrader Docker镜像
# 版本: 1.0.0

# 使用官方Python镜像作为基础
FROM python:3.9-slim as builder

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libboost-all-dev \
    libeigen3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装Python依赖
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# 编译C++核心
RUN mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc)

# 安装Python包
RUN pip install -e .

# 第二阶段：运行阶段
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libboost-system1.74.0 \
    libboost-filesystem1.74.0 \
    libboost-thread1.74.0 \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 从构建阶段复制编译好的库
COPY --from=builder /app/build/libpplustrader.so /usr/local/lib/
COPY --from=builder /app/build/*.so /usr/local/lib/

# 设置库路径
ENV LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"

# 复制项目文件
COPY . /app
WORKDIR /app

# 创建数据目录
RUN mkdir -p /app/data /app/logs /app/configs

# 暴露Web界面端口
EXPOSE 8050

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import pplustrader; print('Health check passed')" || exit 1

# 默认命令
CMD ["python", "web/app.py"]

# 标签
LABEL maintainer="PlusPlusTrader Team <support@pplustrader.com>"
LABEL version="1.0.0"
LABEL description="PlusPlusTrader - 高性能量化交易框架"