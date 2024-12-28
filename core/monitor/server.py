"""
服务器监控收集器
用于监控远程构建服务器的状态和性能
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base import BaseCollector, Metric, Alert, MetricType
from ..server import ServerManager

class ServerCollector(BaseCollector):
    """服务器监控收集器"""
    
    def __init__(self, server_manager: ServerManager):
        super().__init__()
        self.server_manager = server_manager
        
    def collect(self) -> List[Metric]:
        """收集服务器指标"""
        self.clear()
        self.last_collect_time = datetime.now()
        
        # 服务器总数
        total_servers = len(self.server_manager.servers)
        self.add_metric(Metric(
            name="total_servers",
            type=MetricType.GAUGE,
            value=total_servers
        ))
        
        # 活动服务器数
        active_servers = len(self.server_manager.active_servers)
        self.add_metric(Metric(
            name="active_servers",
            type=MetricType.GAUGE,
            value=active_servers
        ))
        
        # 服务器可用率
        availability = (active_servers / total_servers * 100) if total_servers > 0 else 0
        self.add_metric(Metric(
            name="server_availability",
            type=MetricType.GAUGE,
            value=availability,
            labels={"unit": "percent"}
        ))
        
        # 收集每个服务器的指标
        for name, server in self.server_manager.servers.items():
            # 服务器状态
            is_active = name in self.server_manager.active_servers
            self.add_metric(Metric(
                name="server_status",
                type=MetricType.GAUGE,
                value=1 if is_active else 0,
                labels={"server": name}
            ))
            
            if is_active:
                # 获取服务器健康状态
                health = server.check_health()
                if health:
                    # CPU 使用率
                    self.add_metric(Metric(
                        name="server_cpu_usage",
                        type=MetricType.GAUGE,
                        value=health.cpu_usage,
                        labels={
                            "server": name,
                            "unit": "percent"
                        }
                    ))
                    
                    # 内存使用率
                    self.add_metric(Metric(
                        name="server_memory_usage",
                        type=MetricType.GAUGE,
                        value=health.memory_usage,
                        labels={
                            "server": name,
                            "unit": "percent"
                        }
                    ))
                    
                    # 磁盘使用率
                    self.add_metric(Metric(
                        name="server_disk_usage",
                        type=MetricType.GAUGE,
                        value=health.disk_usage,
                        labels={
                            "server": name,
                            "unit": "percent"
                        }
                    ))
                    
                    # 负载分数
                    load = self.server_manager.load_balancer.server_loads.get(name, 0.0)
                    self.add_metric(Metric(
                        name="server_load",
                        type=MetricType.GAUGE,
                        value=load,
                        labels={"server": name}
                    ))
                    
                    # 错误计数
                    error_count = len(health.errors)
                    self.add_metric(Metric(
                        name="server_errors",
                        type=MetricType.GAUGE,
                        value=error_count,
                        labels={"server": name}
                    ))
                    
        # 检查告警阈值
        self._check_alerts()
        
        return self.metrics
        
    def _check_alerts(self):
        """检查告警"""
        # 检查服务器可用性
        for metric in self.metrics:
            if metric.name == "server_availability" and metric.value < 50:
                self.add_alert(Alert(
                    name="low_availability",
                    level="error",
                    message=f"Server availability is low: {metric.value}%",
                    metric=metric
                ))
                
            elif metric.name == "server_cpu_usage" and metric.value > 80:
                self.add_alert(Alert(
                    name="high_server_cpu_usage",
                    level="warning",
                    message=f"High CPU usage on server {metric.labels['server']}: {metric.value}%",
                    metric=metric
                ))
                
            elif metric.name == "server_memory_usage" and metric.value > 80:
                self.add_alert(Alert(
                    name="high_server_memory_usage",
                    level="warning",
                    message=f"High memory usage on server {metric.labels['server']}: {metric.value}%",
                    metric=metric
                ))
                
            elif metric.name == "server_disk_usage" and metric.value > 80:
                self.add_alert(Alert(
                    name="high_server_disk_usage",
                    level="warning",
                    message=f"High disk usage on server {metric.labels['server']}: {metric.value}%",
                    metric=metric
                ))
                
            elif metric.name == "server_load" and metric.value > 0.8:
                self.add_alert(Alert(
                    name="high_server_load",
                    level="warning",
                    message=f"High load on server {metric.labels['server']}: {metric.value}",
                    metric=metric
                ))
                
            elif metric.name == "server_errors" and metric.value > 0:
                self.add_alert(Alert(
                    name="server_errors",
                    level="error",
                    message=f"Errors detected on server {metric.labels['server']}: {metric.value} errors",
                    metric=metric
                ))
                
        # 检查离线服务器
        offline_servers = set(self.server_manager.servers.keys()) - set(self.server_manager.active_servers)
        if offline_servers:
            self.add_alert(Alert(
                name="offline_servers",
                level="warning",
                message=f"Servers are offline: {', '.join(offline_servers)}"
            )) 