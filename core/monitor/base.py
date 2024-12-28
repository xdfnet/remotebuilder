"""
监控系统基础模块
定义监控接口和通用方法
"""
import os
import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class MetricType:
    """指标类型"""
    GAUGE = "gauge"  # 瞬时值
    COUNTER = "counter"  # 计数器
    HISTOGRAM = "histogram"  # 直方图

class Metric:
    """监控指标"""
    
    def __init__(
        self,
        name: str,
        type: str,
        value: float = 0.0,
        labels: Dict[str, str] = None
    ):
        self.name = name
        self.type = type
        self.value = value
        self.labels = labels or {}
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "type": self.type,
            "value": self.value,
            "labels": self.labels,
            "timestamp": self.timestamp
        }

class Alert:
    """告警信息"""
    
    def __init__(
        self,
        name: str,
        level: str,
        message: str,
        metric: Optional[Metric] = None
    ):
        self.name = name
        self.level = level
        self.message = message
        self.metric = metric
        self.timestamp = datetime.now()
        self.status = "active"
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "level": self.level,
            "message": self.message,
            "metric": self.metric.to_dict() if self.metric else None,
            "timestamp": self.timestamp,
            "status": self.status
        }

class BaseCollector(ABC):
    """指标收集器基类"""
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.alerts: List[Alert] = []
        self.last_collect_time = None
        
    @abstractmethod
    def collect(self) -> List[Metric]:
        """收集指标"""
        pass
        
    def add_metric(self, metric: Metric):
        """添加指标"""
        self.metrics.append(metric)
        
    def add_alert(self, alert: Alert):
        """添加告警"""
        self.alerts.append(alert)
        logger.warning(f"Alert: {alert.message}")
        
    def clear(self):
        """清理数据"""
        self.metrics = []
        self.alerts = []
        
class SystemCollector(BaseCollector):
    """系统指标收集器"""
    
    def __init__(self):
        super().__init__()
        self.process = psutil.Process()
        
    def collect(self) -> List[Metric]:
        """收集系统指标"""
        self.clear()
        self.last_collect_time = datetime.now()
        
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self.add_metric(Metric(
            name="system_cpu_usage",
            type=MetricType.GAUGE,
            value=cpu_percent,
            labels={"unit": "percent"}
        ))
        
        # 内存使用率
        memory = psutil.virtual_memory()
        self.add_metric(Metric(
            name="system_memory_usage",
            type=MetricType.GAUGE,
            value=memory.percent,
            labels={"unit": "percent"}
        ))
        
        # 磁盘使用率
        disk = psutil.disk_usage("/")
        self.add_metric(Metric(
            name="system_disk_usage",
            type=MetricType.GAUGE,
            value=disk.percent,
            labels={"unit": "percent"}
        ))
        
        # 进程指标
        process_cpu_percent = self.process.cpu_percent()
        process_memory_percent = self.process.memory_percent()
        
        self.add_metric(Metric(
            name="process_cpu_usage",
            type=MetricType.GAUGE,
            value=process_cpu_percent,
            labels={"unit": "percent"}
        ))
        
        self.add_metric(Metric(
            name="process_memory_usage",
            type=MetricType.GAUGE,
            value=process_memory_percent,
            labels={"unit": "percent"}
        ))
        
        # 检查告警阈值
        self._check_alerts()
        
        return self.metrics
        
    def _check_alerts(self):
        """检查告警"""
        # CPU 使用率告警
        for metric in self.metrics:
            if metric.name == "system_cpu_usage" and metric.value > 80:
                self.add_alert(Alert(
                    name="high_cpu_usage",
                    level="warning",
                    message=f"System CPU usage is high: {metric.value}%",
                    metric=metric
                ))
                
            elif metric.name == "system_memory_usage" and metric.value > 80:
                self.add_alert(Alert(
                    name="high_memory_usage",
                    level="warning",
                    message=f"System memory usage is high: {metric.value}%",
                    metric=metric
                ))
                
            elif metric.name == "system_disk_usage" and metric.value > 80:
                self.add_alert(Alert(
                    name="high_disk_usage",
                    level="warning",
                    message=f"System disk usage is high: {metric.value}%",
                    metric=metric
                ))

class MonitorService:
    """监控服务"""
    
    def __init__(self):
        self.collectors: List[BaseCollector] = []
        self.metrics_history: List[Dict[str, Any]] = []
        self.alerts_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
    def add_collector(self, collector: BaseCollector):
        """添加收集器"""
        self.collectors.append(collector)
        
    def collect(self) -> Dict[str, Any]:
        """收集所有指标"""
        all_metrics = []
        all_alerts = []
        
        for collector in self.collectors:
            metrics = collector.collect()
            all_metrics.extend(metrics)
            all_alerts.extend(collector.alerts)
            
        # 保存历史数据
        for metric in all_metrics:
            self.metrics_history.append(metric.to_dict())
        for alert in all_alerts:
            self.alerts_history.append(alert.to_dict())
            
        # 限制历史数据大小
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
        if len(self.alerts_history) > self.max_history_size:
            self.alerts_history = self.alerts_history[-self.max_history_size:]
            
        return {
            "metrics": [m.to_dict() for m in all_metrics],
            "alerts": [a.to_dict() for a in all_alerts]
        }
        
    def get_metrics_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """获取历史指标"""
        if not start_time and not end_time:
            return self.metrics_history
            
        filtered = []
        for metric in self.metrics_history:
            timestamp = metric["timestamp"]
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            filtered.append(metric)
            
        return filtered
        
    def get_alerts_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """获取历史告警"""
        if not start_time and not end_time:
            return self.alerts_history
            
        filtered = []
        for alert in self.alerts_history:
            timestamp = alert["timestamp"]
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            filtered.append(alert)
            
        return filtered 