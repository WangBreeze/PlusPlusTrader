#!/usr/bin/env python3
"""
优化版Python自定义指标
实现性能优化功能：批量更新、NumPy支持、内存池
"""

import sys
import os
import time
import numpy as np
from typing import Dict, List, Any, Optional, Union
import threading
from collections import deque

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python.custom_indicator import PythonIndicator, SignalType, IndicatorConfig, factory

class PriceDataPool:
    """价格数据内存池"""
    
    def __init__(self, pool_size: int = 1000):
        self.pool_size = pool_size
        self.pool = deque(maxlen=pool_size)
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化内存池"""
        for _ in range(self.pool_size):
            self.pool.append(self._create_price_data())
    
    def _create_price_data(self) -> Dict[str, Any]:
        """创建价格数据模板"""
        return {
            "open": 0.0,
            "high": 0.0,
            "low": 0.0,
            "close": 0.0,
            "volume": 0,
            "timestamp": 0
        }
    
    def get_price_data(self) -> Dict[str, Any]:
        """从内存池获取价格数据对象"""
        if self.pool:
            return self.pool.pop()
        else:
            return self._create_price_data()
    
    def return_price_data(self, price_data: Dict[str, Any]):
        """归还价格数据对象到内存池"""
        # 重置数据
        for key in price_data:
            if isinstance(price_data[key], (int, float)):
                price_data[key] = 0
        self.pool.append(price_data)

class OptimizedIndicator(PythonIndicator):
    """优化版指标基类"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.memory_pool = PriceDataPool()
        self.batch_buffer = []
        self.batch_size = 100  # 默认批量大小
        self.last_batch_time = time.time()
        
    def batch_update(self, price_data_list: List[Dict[str, Any]]) -> List[float]:
        """
        批量更新指标
        参数:
            price_data_list: 价格数据列表
        返回:
            计算值列表
        """
        if not price_data_list:
            return []
        
        results = []
        for price_data in price_data_list:
            result = self.update(price_data)
            results.append(result)
        
        return results
    
    def optimized_update(self, price_data: Dict[str, Any]) -> float:
        """
        优化版单点更新
        使用内存池减少内存分配
        """
        # 使用内存池中的对象
        pooled_data = self.memory_pool.get_price_data()
        
        # 复制数据（避免修改原始数据）
        for key, value in price_data.items():
            pooled_data[key] = value
        
        # 执行更新
        result = self.update(pooled_data)
        
        # 归还对象到内存池
        self.memory_pool.return_price_data(pooled_data)
        
        return result
    
    def set_batch_size(self, batch_size: int):
        """设置批量大小"""
        self.batch_size = max(1, batch_size)
    
    def flush_batch(self) -> List[float]:
        """刷新批量缓冲区"""
        if not self.batch_buffer:
            return []
        
        results = self.batch_update(self.batch_buffer)
        self.batch_buffer.clear()
        self.last_batch_time = time.time()
        
        return results

class NumpyPriceData:
    """NumPy结构化价格数据"""
    
    # 定义结构化数据类型
    dtype = np.dtype([
        ('timestamp', 'i8'),
        ('open', 'f8'),
        ('high', 'f8'),
        ('low', 'f8'),
        ('close', 'f8'),
        ('volume', 'i8')
    ])
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.data = np.zeros(capacity, dtype=self.dtype)
        self.index = 0
    
    def add_price(self, timestamp: int, open_price: float, high: float, 
                  low: float, close: float, volume: int):
        """添加价格数据"""
        if self.index >= self.capacity:
            self._expand_capacity()
        
        self.data[self.index] = (timestamp, open_price, high, low, close, volume)
        self.index += 1
    
    def add_from_dict(self, price_dict: Dict[str, Any]):
        """从字典添加价格数据"""
        self.add_price(
            price_dict.get('timestamp', 0),
            price_dict.get('open', 0.0),
            price_dict.get('high', 0.0),
            price_dict.get('low', 0.0),
            price_dict.get('close', 0.0),
            price_dict.get('volume', 0)
        )
    
    def _expand_capacity(self):
        """扩展容量"""
        new_capacity = self.capacity * 2
        new_data = np.zeros(new_capacity, dtype=self.dtype)
        new_data[:self.capacity] = self.data
        self.data = new_data
        self.capacity = new_capacity
    
    def get_slice(self, start: int = 0, end: Optional[int] = None) -> np.ndarray:
        """获取数据切片"""
        if end is None:
            end = self.index
        return self.data[start:end]
    
    def clear(self):
        """清空数据"""
        self.index = 0

class NumpyOptimizedIndicator(OptimizedIndicator):
    """支持NumPy的优化指标"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.numpy_buffer = NumpyPriceData()
        
    def numpy_update(self, price_array: np.ndarray) -> np.ndarray:
        """
        使用NumPy数组更新指标
        参数:
            price_array: 结构化NumPy数组
        返回:
            计算值数组
        """
        if price_array.dtype != NumpyPriceData.dtype:
            raise ValueError(f"Expected dtype {NumpyPriceData.dtype}, got {price_array.dtype}")
        
        results = np.zeros(len(price_array), dtype='f8')
        
        for i in range(len(price_array)):
            price_data = {
                'timestamp': price_array[i]['timestamp'],
                'open': price_array[i]['open'],
                'high': price_array[i]['high'],
                'low': price_array[i]['low'],
                'close': price_array[i]['close'],
                'volume': price_array[i]['volume']
            }
            results[i] = self.update(price_data)
        
        return results
    
    def batch_numpy_update(self, price_arrays: List[np.ndarray]) -> List[np.ndarray]:
        """批量NumPy更新"""
        results = []
        for price_array in price_arrays:
            result = self.numpy_update(price_array)
            results.append(result)
        return results

class AsyncIndicator:
    """异步指标包装器"""
    
    def __init__(self, indicator: PythonIndicator, max_queue_size: int = 10000):
        self.indicator = indicator
        self.update_queue = deque(maxlen=max_queue_size)
        self.results_queue = deque(maxlen=max_queue_size)
        self.running = False
        self.worker_thread = None
        
    def start(self):
        """启动异步处理"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
    
    def stop(self):
        """停止异步处理"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
    
    def async_update(self, price_data: Dict[str, Any]) -> int:
        """
        异步更新
        返回: 任务ID
        """
        task_id = len(self.update_queue)
        self.update_queue.append((task_id, price_data))
        return task_id
    
    def get_result(self, task_id: int, timeout: float = 1.0) -> Optional[float]:
        """获取结果"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            for result_id, result in self.results_queue:
                if result_id == task_id:
                    # 移除已处理的结果
                    self.results_queue.remove((result_id, result))
                    return result
        
        return None
    
    def _process_queue(self):
        """处理队列"""
        batch_size = 100
        batch = []
        
        while self.running:
            if not self.update_queue:
                time.sleep(0.001)  # 短暂休眠
                continue
            
            # 收集批量数据
            while self.update_queue and len(batch) < batch_size:
                task_id, price_data = self.update_queue.popleft()
                batch.append((task_id, price_data))
            
            if batch:
                # 批量处理
                for task_id, price_data in batch:
                    try:
                        result = self.indicator.update(price_data)
                        self.results_queue.append((task_id, result))
                    except Exception as e:
                        print(f"Error processing task {task_id}: {e}")
                
                batch.clear()

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            'update_count': 0,
            'total_update_time': 0.0,
            'batch_update_count': 0,
            'total_batch_time': 0.0,
            'memory_allocations': 0,
            'memory_deallocations': 0
        }
        self.start_time = time.time()
    
    def record_update(self, update_time: float):
        """记录单次更新"""
        self.metrics['update_count'] += 1
        self.metrics['total_update_time'] += update_time
    
    def record_batch_update(self, batch_size: int, batch_time: float):
        """记录批量更新"""
        self.metrics['batch_update_count'] += 1
        self.metrics['total_batch_time'] += batch_time
    
    def record_memory_allocation(self):
        """记录内存分配"""
        self.metrics['memory_allocations'] += 1
    
    def record_memory_deallocation(self):
        """记录内存释放"""
        self.metrics['memory_deallocations'] += 1
    
    def get_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        elapsed_time = time.time() - self.start_time
        
        avg_update_time = 0
        if self.metrics['update_count'] > 0:
            avg_update_time = self.metrics['total_update_time'] / self.metrics['update_count']
        
        avg_batch_time = 0
        if self.metrics['batch_update_count'] > 0:
            avg_batch_time = self.metrics['total_batch_time'] / self.metrics['batch_update_count']
        
        memory_leak = self.metrics['memory_allocations'] - self.metrics['memory_deallocations']
        
        return {
            'elapsed_time': elapsed_time,
            'update_count': self.metrics['update_count'],
            'updates_per_second': self.metrics['update_count'] / elapsed_time if elapsed_time > 0 else 0,
            'avg_update_time_ms': avg_update_time * 1000,
            'batch_update_count': self.metrics['batch_update_count'],
            'avg_batch_time_ms': avg_batch_time * 1000,
            'memory_allocations': self.metrics['memory_allocations'],
            'memory_deallocations': self.metrics['memory_deallocations'],
            'memory_leak': memory_leak,
            'memory_leak_percentage': (memory_leak / self.metrics['memory_allocations'] * 100) if self.metrics['memory_allocations'] > 0 else 0
        }

def test_optimization():
    """测试优化效果"""
    print("="*60)
    print("优化功能测试")
    print("="*60)
    
    # 创建原始指标
    instance_id = factory.create("SimpleMovingAverage", {"window": 20})
    original_indicator = factory.get_instance(instance_id)
    
    if not original_indicator:
        print("无法创建原始指标")
        return
    
    # 创建优化指标
    optimized_indicator = OptimizedIndicator("OptimizedSMA", {"window": 20})
    
    # 生成测试数据
    test_data = []
    price = 100.0
    for i in range(1000):
        change = (random.random() - 0.5) * 2
        price += change
        test_data.append({
            "open": price,
            "high": price + abs(change),
            "low": price - abs(change),
            "close": price,
            "volume": 10000 + i * 10,
            "timestamp": i
        })
    
    # 测试原始性能
    print("\n1. 原始性能测试:")
    start_time = time.time()
    for price_data in test_data:
        original_indicator.update(price_data)
    original_time = time.time() - start_time
    print(f"   耗时: {original_time:.4f} 秒")
    print(f"   平均: {original_time/len(test_data)*1000000:.1f} 微秒/更新")
    
    # 测试优化性能
    print("\n2. 优化性能测试:")
    start_time = time.time()
    for price_data in test_data:
        optimized_indicator.optimized_update(price_data)
    optimized_time = time.time() - start_time
    print(f"   耗时: {optimized_time:.4f} 秒")
    print(f"   平均: {optimized_time/len(test_data)*1000000:.1f} 微秒/更新")
    
    # 测试批量更新
    print("\n3. 批量更新测试:")
    start_time = time.time()
    results = optimized_indicator.batch_update(test_data)
    batch_time = time.time() - start_time
    print(f"   耗时: {batch_time:.4f} 秒")
    print(f"   平均: {batch_time/len(test_data)*1000000:.1f} 微秒/更新")
    
    # 性能对比
    print("\n4. 性能对比:")
    print(f"   优化 vs 原始: {original_time/optimized_time:.2f}x 提升")
    print(f"   批量 vs 原始: {original_time/batch_time:.2f}x 提升")
    print(f"   批量 vs 优化: {optimized_time/batch_time:.2f}x 提升")
    
    # 测试NumPy支持
    print("\n5. NumPy支持测试:")
    numpy_indicator = NumpyOptimizedIndicator("NumpySMA", {"window": 20})
    
    # 创建NumPy数组
    numpy_data = NumpyPriceData(len(test_data))
    for price_data in test_data:
        numpy_data.add_from_dict(price_data)
    
    price_array = numpy_data.get_slice()
    
    start_time = time.time()
    numpy_results = numpy_indicator.numpy_update(price_array)
    numpy_time = time.time() - start_time
    
    print(f"   NumPy耗时: {numpy_time:.4f} 秒")
    print(f"   平均: {numpy_time/len(test_data)*1000000:.1f} 微秒/更新")
    print(f"   NumPy vs 原始: {original_time/numpy_time:.2f}x 提升")
    
    return {
        'original_time': original_time,
        'optimized_time': optimized_time,
        'batch_time': batch_time,
        'numpy_time': numpy_time,
        'test_data_size': len(test_data)
    }

if __name__ == "__main__":
    import random
    
    print("Python自定义指标优化模块")
    print("="*60)
    
    # 运行测试
    results = test_optimization()
    
    print("\n" + "="*60)
    print("优化测试完成！")
    print("="*60)