import time
import psutil
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PerformanceMetrics:
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    process_count: int
    thread_count: int
    open_files: int

class PerformanceMonitor:
    def __init__(self, interval: int = 5):
        self.interval = interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
        self.callbacks: List[Callable[[PerformanceMetrics], None]] = []
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # 性能阈值设置
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'disk_usage_percent': 90.0,
            'process_count': 500,
            'thread_count': 2000,
            'open_files': 1000
        }

    def start(self):
        """启动监控"""
        if self._running:
            return
            
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def stop(self):
        """停止监控"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
            self._monitor_thread = None

    def add_callback(self, callback: Callable[[PerformanceMetrics], None]):
        """添加指标回调函数"""
        self.callbacks.append(callback)

    def get_current_metrics(self) -> PerformanceMetrics:
        """获取当前性能指标"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = self._get_disk_io()
        network_io = self._get_network_io()
        process_count = len(psutil.pids())
        thread_count = threading.active_count()
        open_files = self._count_open_files()
        
        metrics = PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_io=disk_io,
            network_io=network_io,
            process_count=process_count,
            thread_count=thread_count,
            open_files=open_files
        )
        
        return metrics

    def get_metrics_history(self, 
                          start_time: Optional[float] = None,
                          end_time: Optional[float] = None) -> List[PerformanceMetrics]:
        """获取历史性能指标"""
        if not start_time and not end_time:
            return self.metrics_history
            
        filtered_metrics = []
        for metric in self.metrics_history:
            if start_time and metric.timestamp < start_time:
                continue
            if end_time and metric.timestamp > end_time:
                continue
            filtered_metrics.append(metric)
            
        return filtered_metrics

    def check_thresholds(self, metrics: PerformanceMetrics) -> Dict[str, bool]:
        """检查性能指标是否超过阈值"""
        violations = {}
        
        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            violations['cpu_percent'] = True
            
        if metrics.memory_percent > self.thresholds['memory_percent']:
            violations['memory_percent'] = True
            
        if metrics.process_count > self.thresholds['process_count']:
            violations['process_count'] = True
            
        if metrics.thread_count > self.thresholds['thread_count']:
            violations['thread_count'] = True
            
        if metrics.open_files > self.thresholds['open_files']:
            violations['open_files'] = True
            
        return violations

    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                metrics = self.get_current_metrics()
                
                # 添加到历史记录
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                    
                # 检查阈值并触发回调
                violations = self.check_thresholds(metrics)
                if violations:
                    for callback in self.callbacks:
                        try:
                            callback(metrics)
                        except Exception as e:
                            print(f"Callback error: {e}")
                            
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(self.interval)

    def _get_disk_io(self) -> Dict[str, float]:
        """获取磁盘IO统计"""
        disk_io = psutil.disk_io_counters()
        if not disk_io:
            return {'read_bytes': 0, 'write_bytes': 0}
            
        return {
            'read_bytes': disk_io.read_bytes,
            'write_bytes': disk_io.write_bytes
        }

    def _get_network_io(self) -> Dict[str, float]:
        """获取网络IO统计"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv
        }

    def _count_open_files(self) -> int:
        """统计打开的文件数"""
        try:
            return len(psutil.Process().open_files())
        except:
            return 0

    def get_performance_report(self) -> Dict:
        """生成性能报告"""
        if not self.metrics_history:
            return {
                'status': 'No data available'
            }
            
        current = self.metrics_history[-1]
        
        # 计算平均值
        avg_cpu = sum(m.cpu_percent for m in self.metrics_history) / len(self.metrics_history)
        avg_memory = sum(m.memory_percent for m in self.metrics_history) / len(self.metrics_history)
        
        # 找出峰值
        peak_cpu = max(m.cpu_percent for m in self.metrics_history)
        peak_memory = max(m.memory_percent for m in self.metrics_history)
        
        return {
            'timestamp': datetime.fromtimestamp(current.timestamp).isoformat(),
            'current_status': {
                'cpu_percent': current.cpu_percent,
                'memory_percent': current.memory_percent,
                'process_count': current.process_count,
                'thread_count': current.thread_count
            },
            'averages': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory
            },
            'peaks': {
                'cpu_percent': peak_cpu,
                'memory_percent': peak_memory
            },
            'threshold_violations': self.check_thresholds(current)
        } 