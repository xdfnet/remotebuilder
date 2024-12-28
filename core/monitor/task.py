"""
任务监控收集器
用于监控构建任务的状态和性能
"""
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base import BaseCollector, Metric, Alert, MetricType
from ..builder import BuildManager

class TaskCollector(BaseCollector):
    """任务监控收集器"""
    
    def __init__(self, build_manager: BuildManager):
        super().__init__()
        self.build_manager = build_manager
        
    def collect(self) -> List[Metric]:
        """收集任务指标"""
        self.clear()
        self.last_collect_time = datetime.now()
        
        # 任务总数
        total_tasks = len(self.build_manager.tasks)
        self.add_metric(Metric(
            name="total_tasks",
            type=MetricType.GAUGE,
            value=total_tasks
        ))
        
        # 按状态统计任务数
        status_counts = {}
        for task in self.build_manager.tasks.values():
            status = task.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
        for status, count in status_counts.items():
            self.add_metric(Metric(
                name="tasks_by_status",
                type=MetricType.GAUGE,
                value=count,
                labels={"status": status}
            ))
            
        # 任务队列长度
        queue_length = len(self.build_manager.task_queue)
        self.add_metric(Metric(
            name="task_queue_length",
            type=MetricType.GAUGE,
            value=queue_length
        ))
        
        # 正在运行的任务数
        running_tasks = len([t for t in self.build_manager.tasks.values() if t.is_running()])
        self.add_metric(Metric(
            name="running_tasks",
            type=MetricType.GAUGE,
            value=running_tasks
        ))
        
        # 任务完成率
        completed_tasks = len([t for t in self.build_manager.tasks.values() if t.status == "completed"])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        self.add_metric(Metric(
            name="task_completion_rate",
            type=MetricType.GAUGE,
            value=completion_rate,
            labels={"unit": "percent"}
        ))
        
        # 任务失败率
        failed_tasks = len([t for t in self.build_manager.tasks.values() if t.status == "failed"])
        failure_rate = (failed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        self.add_metric(Metric(
            name="task_failure_rate",
            type=MetricType.GAUGE,
            value=failure_rate,
            labels={"unit": "percent"}
        ))
        
        # 平均任务执行时间
        completed_task_times = []
        for task in self.build_manager.tasks.values():
            if task.status == "completed" and task.start_time and task.end_time:
                duration = (task.end_time - task.start_time).total_seconds()
                completed_task_times.append(duration)
                
        if completed_task_times:
            avg_duration = sum(completed_task_times) / len(completed_task_times)
            self.add_metric(Metric(
                name="avg_task_duration",
                type=MetricType.GAUGE,
                value=avg_duration,
                labels={"unit": "seconds"}
            ))
            
        # 检查告警阈值
        self._check_alerts()
        
        return self.metrics
        
    def _check_alerts(self):
        """检查告警"""
        # 检查队列积压
        for metric in self.metrics:
            if metric.name == "task_queue_length" and metric.value > 10:
                self.add_alert(Alert(
                    name="task_queue_backlog",
                    level="warning",
                    message=f"Task queue is backing up: {metric.value} tasks waiting",
                    metric=metric
                ))
                
            elif metric.name == "task_failure_rate" and metric.value > 20:
                self.add_alert(Alert(
                    name="high_failure_rate",
                    level="error",
                    message=f"Task failure rate is high: {metric.value}%",
                    metric=metric
                ))
                
        # 检查长时间运行的任务
        for task in self.build_manager.tasks.values():
            if task.is_running() and task.start_time:
                duration = (datetime.now() - task.start_time).total_seconds()
                if duration > 3600:  # 1小时
                    self.add_alert(Alert(
                        name="long_running_task",
                        level="warning",
                        message=f"Task {task.task_id} has been running for {duration/3600:.1f} hours",
                        metric=Metric(
                            name="task_duration",
                            type=MetricType.GAUGE,
                            value=duration,
                            labels={
                                "task_id": task.task_id,
                                "unit": "seconds"
                            }
                        )
                    ))
                    
        # 检查失败任务
        recent_failed_tasks = [
            t for t in self.build_manager.tasks.values()
            if t.status == "failed" and t.end_time
            and (datetime.now() - t.end_time) < timedelta(hours=1)
        ]
        
        if len(recent_failed_tasks) >= 3:
            self.add_alert(Alert(
                name="multiple_task_failures",
                level="error",
                message=f"Multiple tasks failed recently: {len(recent_failed_tasks)} failures in the last hour"
            )) 