"""
监控 API
提供监控数据的访问接口
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAPI, APIResponse
from ..monitor.base import MonitorService, SystemCollector
from ..monitor.task import TaskCollector
from ..monitor.server import ServerCollector
from ..builder import BuildManager
from ..server import ServerManager

class MonitorAPI(BaseAPI):
    """监控 API"""
    
    def __init__(
        self,
        build_manager: BuildManager,
        server_manager: ServerManager
    ):
        super().__init__()
        self.monitor_service = MonitorService()
        
        # 添加收集器
        self.monitor_service.add_collector(SystemCollector())
        self.monitor_service.add_collector(TaskCollector(build_manager))
        self.monitor_service.add_collector(ServerCollector(server_manager))
        
    def collect_metrics(self) -> APIResponse:
        """收集当前指标"""
        try:
            data = self.monitor_service.collect()
            return self.success_response(data)
            
        except Exception as e:
            return self.error_response(
                "Failed to collect metrics",
                str(e)
            )
            
    def get_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> APIResponse:
        """获取历史指标"""
        try:
            metrics = self.monitor_service.get_metrics_history(
                start_time,
                end_time
            )
            return self.success_response(metrics)
            
        except Exception as e:
            return self.error_response(
                "Failed to get metrics",
                str(e)
            )
            
    def get_alerts(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> APIResponse:
        """获取历史告警"""
        try:
            alerts = self.monitor_service.get_alerts_history(
                start_time,
                end_time
            )
            return self.success_response(alerts)
            
        except Exception as e:
            return self.error_response(
                "Failed to get alerts",
                str(e)
            )
            
    def get_system_metrics(self) -> APIResponse:
        """获取系统指标"""
        try:
            metrics = []
            for metric in self.monitor_service.metrics_history:
                if metric["name"].startswith("system_"):
                    metrics.append(metric)
            return self.success_response(metrics)
            
        except Exception as e:
            return self.error_response(
                "Failed to get system metrics",
                str(e)
            )
            
    def get_task_metrics(self) -> APIResponse:
        """获取任务指标"""
        try:
            metrics = []
            for metric in self.monitor_service.metrics_history:
                if any(metric["name"].startswith(prefix) for prefix in ["task_", "total_tasks"]):
                    metrics.append(metric)
            return self.success_response(metrics)
            
        except Exception as e:
            return self.error_response(
                "Failed to get task metrics",
                str(e)
            )
            
    def get_server_metrics(self) -> APIResponse:
        """获取服务器指标"""
        try:
            metrics = []
            for metric in self.monitor_service.metrics_history:
                if any(metric["name"].startswith(prefix) for prefix in ["server_", "total_servers"]):
                    metrics.append(metric)
            return self.success_response(metrics)
            
        except Exception as e:
            return self.error_response(
                "Failed to get server metrics",
                str(e)
            )
            
    def get_active_alerts(self) -> APIResponse:
        """获取活动告警"""
        try:
            alerts = []
            for alert in self.monitor_service.alerts_history:
                if alert["status"] == "active":
                    alerts.append(alert)
            return self.success_response(alerts)
            
        except Exception as e:
            return self.error_response(
                "Failed to get active alerts",
                str(e)
            )
            
    def get_metrics_by_name(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> APIResponse:
        """获取指定名称的指标"""
        try:
            metrics = []
            for metric in self.monitor_service.get_metrics_history(start_time, end_time):
                if metric["name"] == metric_name:
                    metrics.append(metric)
            return self.success_response(metrics)
            
        except Exception as e:
            return self.error_response(
                "Failed to get metrics by name",
                str(e)
            )
            
    def get_alerts_by_level(
        self,
        level: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> APIResponse:
        """获取指定级别的告警"""
        try:
            alerts = []
            for alert in self.monitor_service.get_alerts_history(start_time, end_time):
                if alert["level"] == level:
                    alerts.append(alert)
            return self.success_response(alerts)
            
        except Exception as e:
            return self.error_response(
                "Failed to get alerts by level",
                str(e)
            ) 