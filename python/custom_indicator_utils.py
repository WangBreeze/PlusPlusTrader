"""
Python自定义指标工具模块
提供错误处理、日志记录、配置管理等功能
"""

import json
import logging
import traceback
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import os
import sys
from datetime import datetime
import inspect

# 导入基础模块
try:
    from custom_indicator import PythonIndicator, IndicatorConfig, SignalType
except ImportError:
    # 如果直接运行，使用相对导入
    from .custom_indicator import PythonIndicator, IndicatorConfig, SignalType


class ErrorSeverity(Enum):
    """错误严重程度"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorRecord:
    """错误记录"""
    timestamp: float
    severity: ErrorSeverity
    message: str
    indicator_name: str = ""
    instance_id: str = ""
    stack_trace: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['timestamp_str'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=2, default=str)


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        初始化错误处理器
        
        Args:
            log_file: 日志文件路径，如果为None则只输出到控制台
        """
        self.log_file = log_file
        self.errors: List[ErrorRecord] = []
        self.max_errors = 1000  # 最大错误记录数
        
        # 配置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """配置日志系统"""
        self.logger = logging.getLogger("CustomIndicatorErrors")
        self.logger.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果指定了日志文件）
        if self.log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(self.log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def record_error(self, 
                    severity: ErrorSeverity,
                    message: str,
                    indicator_name: str = "",
                    instance_id: str = "",
                    exception: Optional[Exception] = None,
                    **extra_data) -> ErrorRecord:
        """
        记录错误
        
        Args:
            severity: 错误严重程度
            message: 错误消息
            indicator_name: 指标名称
            instance_id: 实例ID
            exception: 异常对象
            **extra_data: 额外数据
            
        Returns:
            错误记录
        """
        # 获取堆栈跟踪
        stack_trace = ""
        if exception:
            stack_trace = "".join(traceback.format_exception(
                type(exception), exception, exception.__traceback__
            ))
        elif severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            stack_trace = "".join(traceback.format_stack())
        
        # 创建错误记录
        error = ErrorRecord(
            timestamp=time.time(),
            severity=severity,
            message=message,
            indicator_name=indicator_name,
            instance_id=instance_id,
            stack_trace=stack_trace,
            extra_data=extra_data
        )
        
        # 添加到错误列表
        self.errors.append(error)
        
        # 限制错误列表大小
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors:]
        
        # 记录到日志
        log_method = getattr(self.logger, severity.value)
        log_message = f"[{indicator_name}:{instance_id}] {message}"
        if extra_data:
            log_message += f" | Extra: {extra_data}"
        
        log_method(log_message)
        
        if stack_trace and severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            self.logger.debug(f"Stack trace:\n{stack_trace}")
        
        return error
    
    def get_errors(self, 
                  severity: Optional[ErrorSeverity] = None,
                  indicator_name: Optional[str] = None,
                  instance_id: Optional[str] = None,
                  limit: int = 100) -> List[ErrorRecord]:
        """
        获取错误记录
        
        Args:
            severity: 过滤严重程度
            indicator_name: 过滤指标名称
            instance_id: 过滤实例ID
            limit: 返回数量限制
            
        Returns:
            错误记录列表
        """
        filtered = self.errors
        
        if severity:
            filtered = [e for e in filtered if e.severity == severity]
        
        if indicator_name:
            filtered = [e for e in filtered if e.indicator_name == indicator_name]
        
        if instance_id:
            filtered = [e for e in filtered if e.instance_id == instance_id]
        
        return filtered[-limit:] if limit > 0 else filtered
    
    def clear_errors(self):
        """清除所有错误记录"""
        self.errors.clear()
        self.logger.info("Cleared all error records")
    
    def save_errors_to_file(self, filepath: str):
        """保存错误记录到文件"""
        errors_data = [error.to_dict() for error in self.errors]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(errors_data, f, indent=2, default=str)
        
        self.logger.info(f"Saved {len(errors_data)} errors to {filepath}")
    
    def load_errors_from_file(self, filepath: str):
        """从文件加载错误记录"""
        if not os.path.exists(filepath):
            self.logger.warning(f"Error file not found: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            errors_data = json.load(f)
        
        for data in errors_data:
            error = ErrorRecord(
                timestamp=data['timestamp'],
                severity=ErrorSeverity(data['severity']),
                message=data['message'],
                indicator_name=data.get('indicator_name', ''),
                instance_id=data.get('instance_id', ''),
                stack_trace=data.get('stack_trace', ''),
                extra_data=data.get('extra_data', {})
            )
            self.errors.append(error)
        
        self.logger.info(f"Loaded {len(errors_data)} errors from {filepath}")


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_timing(self, operation: str):
        """开始计时"""
        self.start_times[operation] = time.time()
    
    def stop_timing(self, operation: str) -> float:
        """结束计时并返回耗时"""
        if operation not in self.start_times:
            return 0.0
        
        duration = time.time() - self.start_times[operation]
        
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        self.metrics[operation].append(duration)
        
        # 保持最近100次记录
        if len(self.metrics[operation]) > 100:
            self.metrics[operation] = self.metrics[operation][-100:]
        
        del self.start_times[operation]
        return duration
    
    def get_statistics(self, operation: str) -> Dict[str, float]:
        """获取统计信息"""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}
        
        values = self.metrics[operation]
        
        return {
            'count': len(values),
            'total': sum(values),
            'mean': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'latest': values[-1],
            'p95': sorted(values)[int(len(values) * 0.95)] if len(values) > 1 else values[0]
        }
    
    def get_all_statistics(self) -> Dict[str, Dict[str, float]]:
        """获取所有操作的统计信息"""
        stats = {}
        for operation in self.metrics:
            stats[operation] = self.get_statistics(operation)
        return stats
    
    def reset(self):
        """重置所有指标"""
        self.metrics.clear()
        self.start_times.clear()


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "configs"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目录
        """
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
    
    def save_indicator_config(self, 
                             indicator_name: str,
                             config: Dict[str, Any],
                             config_name: Optional[str] = None) -> str:
        """
        保存指标配置
        
        Args:
            indicator_name: 指标名称
            config: 配置字典
            config_name: 配置名称，如果为None则使用时间戳
            
        Returns:
            配置文件路径
        """
        if config_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config_name = f"{indicator_name}_{timestamp}"
        
        # 确保扩展名
        if not config_name.endswith('.json'):
            config_name += '.json'
        
        filepath = os.path.join(self.config_dir, config_name)
        
        # 添加元数据
        config_with_meta = {
            'metadata': {
                'indicator_name': indicator_name,
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            },
            'config': config
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_with_meta, f, indent=2, default=str)
        
        return filepath
    
    def load_indicator_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载指标配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('config', {})
    
    def list_configs(self, indicator_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出配置文件
        
        Args:
            indicator_name: 过滤指标名称
            
        Returns:
            配置信息列表
        """
        configs = []
        
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.config_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    metadata = data.get('metadata', {})
                    
                    if indicator_name and metadata.get('indicator_name') != indicator_name:
                        continue
                    
                    configs.append({
                        'filename': filename,
                        'filepath': filepath,
                        'metadata': metadata,
                        'size': os.path.getsize(filepath),
                        'modified': os.path.getmtime(filepath)
                    })
                except Exception as e:
                    # 跳过损坏的配置文件
                    continue
        
        # 按修改时间排序（最新的在前）
        configs.sort(key=lambda x: x['modified'], reverse=True)
        return configs
    
    def delete_config(self, config_path: str) -> bool:
        """
        删除配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            是否删除成功
        """
        try:
            if os.path.exists(config_path):
                os.remove(config_path)
                return True
        except Exception:
            pass
        
        return False


class IndicatorValidator:
    """指标验证器"""
    
    @staticmethod
    def validate_indicator_class(indicator_class) -> List[str]:
        """
        验证指标类
        
        Args:
            indicator_class: 指标类
            
        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        
        # 检查是否是PythonIndicator的子类
        if not issubclass(indicator_class, PythonIndicator):
            errors.append(f"Class must be a subclass of PythonIndicator")
            return errors
        
        # 检查必要方法
        required_methods = ['_calculate']
        for method in required_methods:
            if not hasattr(indicator_class, method):
                errors.append(f"Missing required method: {method}")
        
        # 检查方法签名
        try:
            # 检查_calculate方法
            calculate_method = getattr(indicator_class, '_calculate')
            sig = inspect.signature(calculate_method)
            params = list(sig.parameters.keys())
            
            if len(params) < 2 or params[1] != 'price_data':
                errors.append(f"_calculate method must accept 'price_data' parameter")
        except Exception as e:
            errors.append(f"Error checking method signatures: {e}")
        
        return errors
    
    @staticmethod
    def validate_config(config: Dict[str, Any], 
                       required_params: List[str] = None,
                       param_types: Dict[str, type] = None) -> List[str]:
        """
        验证配置
        
        Args:
            config: 配置字典
            required_params: 必要参数列表
            param_types: 参数类型映射
            
        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        
        if required_params:
            for param in required_params:
                if param not in config:
                    errors.append(f"Missing required parameter: {param}")
        
        if param_types:
            for param, expected_type in param_types.items():
                if param in config:
                    value = config[param]
                    if not isinstance(value, expected_type):
                        errors.append(f"Parameter '{param}' must be {expected_type.__name__}, got {type(value).__name__}")
        
        return errors


# 全局工具实例
error_handler = ErrorHandler(log_file="logs/custom_indicators.log")
performance_monitor = PerformanceMonitor()
config_manager = ConfigManager()
indicator_validator = IndicatorValidator()


def error_handler_decorator(func: Callable) -> Callable:
    """错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            # 获取指标信息（如果可用）
            indicator_name = ""
            instance_id = ""
            
            # 尝试从参数中提取指标信息
            for arg in args:
                if isinstance(arg, PythonIndicator):
                    indicator_name = arg.name
                    break
            
            # 开始性能监控
            operation = f"{func.__module__}.{func.__name__}"
            performance_monitor.start_timing(operation)
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 结束性能监控
            duration = performance_monitor.stop_timing(operation)
            
            # 记录成功（可选）
            if duration > 0.1:  # 如果耗时超过100ms，记录警告
                error_handler.record_error(
                    severity=ErrorSeverity.WARNING,
                    message=f"Function {func.__name__} took {duration:.3f}s",
                    indicator_name=indicator_name,
                    instance_id=instance_id,
                    duration=duration
                )
            
            return result
            
        except Exception as e:
            # 记录错误
            error_handler.record_error(
                severity=ErrorSeverity.ERROR,
                message=f"Error in {func.__name__}: {str(e)}",
                indicator_name=indicator_name,
                instance_id=instance_id,
                exception=e
            )
            
            # 重新抛出异常
            raise
    
    return wrapper


def validate_and_create_indicator(indicator_class, 
                                 config: Dict[str, Any],
                                 indicator_name: str = "") -> Optional[PythonIndicator]:
    """
    验证并创建指标实例
    
    Args:
        indicator_class: 指标类
        config: 配置字典
        indicator_name: 指标名称
        
    Returns:
        指标实例，如果验证失败则返回None
    """
    try:
        # 验证指标类
        class_errors = indicator_validator.validate_indicator_class(indicator_class)
        if class_errors:
            for error in class_errors:
                error_handler.record_error(
                    severity=ErrorSeverity.ERROR,
                    message=f"Indicator class validation failed: {error}",
                    indicator_name=indicator_name or indicator_class.__name__
                )
            return None
        
        # 创建配置对象
        indicator_config = IndicatorConfig(
            name=indicator_name or indicator_class.__name__,
            parameters=config
        )
        
        # 验证配置
        if hasattr(indicator_class, '__init__'):
            # 尝试获取类的必要参数
            init_method = getattr(indicator_class, '__init__')
            sig = inspect.signature(init_method)
            
            # 检查是否有config参数
            params = list(sig.parameters.keys())
            if 'config' in params:
                # 创建实例
                instance = indicator_class(indicator_config)
                
                # 记录成功
                error_handler.record_error(
                    severity=ErrorSeverity.INFO,
                    message=f"Successfully created indicator instance",
                    indicator_name=instance.name
                )
                
                return instance
        
        error_handler.record_error(
            severity=ErrorSeverity.ERROR,
            message="Indicator class does not accept config parameter",
            indicator_name=indicator_name or indicator_class.__name__
        )
        return None
        
    except Exception as e:
        error_handler.record_error(
            severity=ErrorSeverity.ERROR,
            message=f"Failed to create indicator: {str(e)}",
            indicator_name=indicator_name or indicator_class.__name__,
            exception=e
        )
        return None


def load_indicator_from_config(config_file: str) -> Optional[PythonIndicator]:
    """
    从配置文件加载指标
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        指标实例，如果加载失败则返回None
    """
    try:
        # 加载配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        metadata = config_data.get('metadata', {})
        config = config_data.get('config', {})
        
        indicator_name = metadata.get('indicator_name', '')
        
        if not indicator_name:
            error_handler.record_error(
                severity=ErrorSeverity.ERROR,
                message="Config file missing indicator_name in metadata",
                extra_data={'config_file': config_file}
            )
            return None
        
        # 动态导入指标类
        # 这里需要根据实际情况实现
        # 暂时返回None，实际实现应该根据indicator_name找到对应的类
        
        error_handler.record_error(
            severity=ErrorSeverity.WARNING,
            message="Dynamic indicator loading not implemented",
            indicator_name=indicator_name,
            extra_data={'config_file': config_file}
        )
        
        return None
        
    except Exception as e:
        error_handler.record_error(
            severity=ErrorSeverity.ERROR,
            message=f"Failed to load indicator from config: {str(e)}",
            extra_data={'config_file': config_file},
            exception=e
        )
        return None


def export_indicator_template(indicator_class,
                             template_name: str = None) -> str:
    """
    导出指标模板
    
    Args:
        indicator_class: 指标类
        template_name: 模板名称
        
    Returns:
        模板文件路径
    """
    if template_name is None:
        template_name = f"template_{indicator_class.__name__}.py"
    
    template_content = f'''"""
{indicator_class.__name__} - 自定义指标模板
基于 {indicator_class.__name__} 类创建的自定义指标模板
"""

from custom_indicator import PythonIndicator, IndicatorConfig, SignalType
from custom_indicator_utils import error_handler_decorator


class {indicator_class.__name__}Template(PythonIndicator):
    """{indicator_class.__name__} 模板类"""
    
    def __init__(self, config: IndicatorConfig):
        super().__init__(config)
        
        # 设置默认参数
        default_params = {{
            'param1': 10,
            'param2': 20.0,
            'param3': 'default_value'
        }}
        
        for key, value in default_params.items():
            if key not in self.config.parameters:
                self.config.parameters[key] = value
        
        self.config.required_parameters = ['param1', 'param2']
        self.config.default_values = default_params
        
        # 初始化内部状态
        self._internal_state = []
    
    @error_handler_decorator
    def _calculate(self, price_data: dict) -> float:
        """
        计算指标值
        
        Args:
            price_data: 价格数据字典，包含:
                - open: 开盘价
                - high: 最高价  
                - low: 最低价
                - close: 收盘价
                - volume: 成交量
                - timestamp: 时间戳
                
        Returns:
            指标值
        """
        # 获取价格数据
        close_price = price_data.get('close', 0)
        
        # 获取参数
        param1 = self.config.parameters.get('param1', 10)
        param2 = self.config.parameters.get('param2', 20.0)
        
        # TODO: 实现指标计算逻辑
        # 这里是一个示例：简单的移动平均
        self._internal_state.append(close_price)
        
        if len(self._internal_state) > param1:
            self._internal_state.pop(0)
        
        if not self._internal_state:
            return close_price
        
        # 计算平均值
        value = sum(self._internal_state) / len(self._internal_state)
        
        return value
    
    @error_handler_decorator
    def _generate_signal(self, price_data: dict, value: float) -> SignalType:
        """
        生成交易信号
        
        Args:
            price_data: 价格数据
            value: 当前指标值
            
        Returns:
            交易信号
        """
        close_price = price_data.get('close', 0)
        
        if len(self.values) < 2:
            return SignalType.HOLD
        
        # TODO: 实现信号生成逻辑
        # 这里是一个示例：价格与指标值比较
        prev_value = self.values[-2]
        
        if close_price > value and close_price <= prev_value:
            return SignalType.BUY
        elif close_price < value and close_price >= prev_value:
            return SignalType.SELL
        
        return SignalType.HOLD
    
    def get_internal_state(self):
        """获取内部状态（可选）"""
        return self._internal_state.copy()


# 使用示例
if __name__ == "__main__":
    # 创建配置
    config = IndicatorConfig(
        name="{indicator_class.__name__}Template",
        description="基于{indicator_class.__name__}的自定义指标模板",
        parameters={{
            'param1': 20,
            'param2': 30.0,
            'param3': 'custom_value'
        }}
    )
    
    # 创建指标实例
    indicator = {indicator_class.__name__}Template(config)
    
    # 测试更新
    test_data = {{
        'open': 100.0,
        'high': 102.0,
        'low': 98.0,
        'close': 101.0,
        'volume': 1000,
        'timestamp': 1
    }}
    
    value = indicator.update(test_data)
    signal = indicator.get_last_signal()
    
    print(f"指标值: {{value}}")
    print(f"信号: {{signal}}")
'''
    
    # 保存模板文件
    template_dir = "templates"
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, template_name)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    error_handler.record_error(
        severity=ErrorSeverity.INFO,
        message=f"Exported indicator template: {template_name}",
        indicator_name=indicator_class.__name__,
        extra_data={'template_path': template_path}
    )
    
    return template_path


def run_diagnostics() -> Dict[str, Any]:
    """运行系统诊断"""
    diagnostics = {
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd()
        },
        'error_stats': {
            'total_errors': len(error_handler.errors),
            'by_severity': {},
            'recent_errors': []
        },
        'performance_stats': performance_monitor.get_all_statistics(),
        'config_stats': {
            'config_dir': config_manager.config_dir,
            'config_count': len(config_manager.list_configs())
        }
    }
    
    # 错误统计
    for severity in ErrorSeverity:
        count = len(error_handler.get_errors(severity=severity))
        diagnostics['error_stats']['by_severity'][severity.value] = count
    
    # 最近错误
    recent_errors = error_handler.get_errors(limit=5)
    diagnostics['error_stats']['recent_errors'] = [
        error.to_dict() for error in recent_errors
    ]
    
    return diagnostics


def print_diagnostics():
    """打印诊断信息"""
    diag = run_diagnostics()
    
    print("=== 自定义指标系统诊断 ===\n")
    
    print("系统信息:")
    print(f"  时间: {diag['timestamp']}")
    print(f"  Python版本: {diag['system_info']['python_version'].split()[0]}")
    print(f"  平台: {diag['system_info']['platform']}")
    print(f"  工作目录: {diag['system_info']['working_directory']}\n")
    
    print("错误统计:")
    print(f"  总错误数: {diag['error_stats']['total_errors']}")
    for severity, count in diag['error_stats']['by_severity'].items():
        print(f"  {severity}: {count}")
    
    print("\n性能统计:")
    for operation, stats in diag['performance_stats'].items():
        if stats:
            print(f"  {operation}:")
            print(f"    调用次数: {stats.get('count', 0)}")
            print(f"    平均耗时: {stats.get('mean', 0):.4f}s")
            print(f"    最新耗时: {stats.get('latest', 0):.4f}s")
    
    print(f"\n配置统计:")
    print(f"  配置目录: {diag['config_stats']['config_dir']}")
    print(f"  配置文件数: {diag['config_stats']['config_count']}")
    
    print("\n最近错误:")
    for error in diag['error_stats']['recent_errors'][:3]:
        print(f"  [{error['severity']}] {error['message']}")
        if error['indicator_name']:
            print(f"    指标: {error['indicator_name']}")
    
    print("\n=== 诊断完成 ===")


if __name__ == "__main__":
    print_diagnostics()