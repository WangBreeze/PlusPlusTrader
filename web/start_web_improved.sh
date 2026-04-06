#!/bin/bash
# PlusPlusTrader Web服务器改进启动脚本
# 版本: 1.1.0
# 日期: 2026-03-29

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装"
        exit 1
    fi
    
    # 检查Python版本
    python_version=$(python3 --version | awk '{print $2}')
    log_info "Python版本: $python_version"
    
    # 检查必要工具
    for cmd in ss curl; do
        if ! command -v $cmd &> /dev/null; then
            log_warning "$cmd 未安装，某些功能可能受限"
        fi
    done
    
    log_success "依赖检查完成"
}

# 停止现有进程
stop_existing_servers() {
    log_info "停止现有Web服务器进程..."
    
    # 查找相关进程
    pids=$(ps aux | grep "python.*simple_app" | grep -v grep | awk '{print $2}')
    
    if [ -z "$pids" ]; then
        log_info "未找到运行的Web服务器进程"
        return 0
    fi
    
    log_info "找到进程: $pids"
    
    # 优雅停止
    for pid in $pids; do
        log_info "停止进程 $pid..."
        kill $pid 2>/dev/null || true
    done
    
    # 等待进程停止
    sleep 2
    
    # 强制停止（如果需要）
    for pid in $pids; do
        if ps -p $pid > /dev/null 2>&1; then
            log_warning "进程 $pid 仍在运行，强制停止..."
            kill -9 $pid 2>/dev/null || true
        fi
    done
    
    # 再次检查
    sleep 1
    remaining_pids=$(ps aux | grep "python.*simple_app" | grep -v grep | awk '{print $2}')
    
    if [ -n "$remaining_pids" ]; then
        log_error "无法停止所有进程: $remaining_pids"
        return 1
    fi
    
    log_success "所有现有进程已停止"
}

# 检查端口占用
check_port() {
    local port=$1
    
    log_info "检查端口 $port 占用情况..."
    
    if ss -tlnp | grep -q ":$port "; then
        local process_info=$(ss -tlnp | grep ":$port " | head -1)
        log_warning "端口 $port 被占用: $process_info"
        
        # 尝试获取进程信息
        local pid=$(echo "$process_info" | grep -o 'pid=[0-9]*' | cut -d= -f2)
        if [ -n "$pid" ]; then
            local cmdline=$(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ' || echo "未知")
            log_warning "占用进程 $pid: $cmdline"
        fi
        
        return 1
    fi
    
    log_success "端口 $port 可用"
    return 0
}

# 启动Web服务器
start_web_server() {
    local port=8050
    
    log_info "启动Web服务器，端口: $port"
    
    # 切换到项目目录
    cd /home/wanglc/.openclaw/workspace/PlusPlusTrader/web || {
        log_error "无法切换到项目目录"
        exit 1
    }
    
    # 启动服务器
    log_info "启动Python Web服务器..."
    nohup python3 simple_app.py > web.log 2>&1 &
    local server_pid=$!
    
    log_info "服务器启动中，PID: $server_pid"
    
    # 等待服务器启动
    log_info "等待服务器启动..."
    local max_wait=10
    local wait_count=0
    
    while [ $wait_count -lt $max_wait ]; do
        if ss -tlnp | grep -q ":$port "; then
            log_success "服务器启动成功，端口 $port 已监听"
            return 0
        fi
        
        sleep 1
        ((wait_count++))
        log_info "等待中... ($wait_count/$max_wait 秒)"
    done
    
    log_error "服务器启动超时，端口 $port 未监听"
    
    # 检查进程状态
    if ps -p $server_pid > /dev/null 2>&1; then
        log_warning "进程 $server_pid 仍在运行，但端口未绑定"
    else
        log_error "进程 $server_pid 已退出"
    fi
    
    # 检查日志
    if [ -f web.log ]; then
        log_info "检查服务器日志..."
        tail -20 web.log
    fi
    
    return 1
}

# 验证服务
verify_service() {
    local port=8050
    local max_retries=3
    local retry_count=0
    
    log_info "验证Web服务..."
    
    while [ $retry_count -lt $max_retries ]; do
        log_info "尝试连接服务 (尝试 $((retry_count+1))/$max_retries)..."
        
        # 使用curl测试服务
        if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$port | grep -q "200"; then
            log_success "主页服务验证成功 (HTTP 200)"
            
            # 测试K线图页面
            if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$port/charts | grep -q "200"; then
                log_success "K线图服务验证成功 (HTTP 200)"
                return 0
            else
                log_warning "K线图服务验证失败"
            fi
        fi
        
        sleep 2
        ((retry_count++))
    done
    
    log_error "服务验证失败"
    return 1
}

# 显示状态信息
show_status() {
    local port=8050
    
    log_info "=== Web服务器状态 ==="
    
    # 显示进程信息
    local pids=$(ps aux | grep "python.*simple_app" | grep -v grep | awk '{print $2}')
    if [ -n "$pids" ]; then
        log_info "运行进程: $pids"
        for pid in $pids; do
            local uptime=$(ps -p $pid -o etime= 2>/dev/null || echo "未知")
            local cmd=$(ps -p $pid -o cmd= 2>/dev/null | cut -c1-50)
            log_info "  PID $pid: 运行时间 $uptime, 命令: $cmd..."
        done
    else
        log_warning "无Web服务器进程运行"
    fi
    
    # 显示端口信息
    if ss -tlnp | grep -q ":$port "; then
        local port_info=$(ss -tlnp | grep ":$port " | head -1)
        log_info "端口 $port: $port_info"
    else
        log_warning "端口 $port 未监听"
    fi
    
    # 显示服务状态
    log_info "测试服务连接..."
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$port | grep -q "200"; then
        log_success "服务状态: 正常 (HTTP 200)"
    else
        log_error "服务状态: 不可用"
    fi
    
    # 显示日志信息
    if [ -f web.log ]; then
        local log_size=$(du -h web.log | awk '{print $1}')
        local log_lines=$(wc -l < web.log)
        log_info "日志文件: web.log ($log_size, $log_lines 行)"
    fi
}

# 主函数
main() {
    echo "========================================"
    echo "  PlusPlusTrader Web服务器启动脚本"
    echo "  版本: 1.1.0 | 时间: $(date)"
    echo "========================================"
    
    # 检查参数
    local action=${1:-"start"}
    
    case $action in
        "start")
            log_info "执行启动操作..."
            check_dependencies
            stop_existing_servers
            check_port 8050 || {
                log_error "端口检查失败，无法启动"
                exit 1
            }
            start_web_server || {
                log_error "服务器启动失败"
                exit 1
            }
            verify_service || {
                log_error "服务验证失败"
                exit 1
            }
            show_status
            log_success "Web服务器启动完成"
            ;;
            
        "stop")
            log_info "执行停止操作..."
            stop_existing_servers
            log_success "Web服务器已停止"
            ;;
            
        "restart")
            log_info "执行重启操作..."
            $0 stop
            sleep 2
            $0 start
            ;;
            
        "status")
            log_info "执行状态检查..."
            show_status
            ;;
            
        *)
            echo "用法: $0 {start|stop|restart|status}"
            echo ""
            echo "命令说明:"
            echo "  start   启动Web服务器"
            echo "  stop    停止Web服务器"
            echo "  restart 重启Web服务器"
            echo "  status  查看服务器状态"
            exit 1
            ;;
    esac
    
    echo "========================================"
    echo "  操作完成: $action"
    echo "  完成时间: $(date)"
    echo "========================================"
}

# 执行主函数
main "$@"