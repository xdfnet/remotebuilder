from typing import Dict, List, Optional
import time
import threading
from queue import PriorityQueue
from dataclasses import dataclass
from enum import Enum

class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    URGENT = 3

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: str
    priority: TaskPriority
    server_requirements: Dict
    created_at: float
    status: TaskStatus = TaskStatus.PENDING
    assigned_server: Optional[str] = None
    progress: float = 0.0
    error: Optional[str] = None

class DistributedScheduler:
    def __init__(self):
        self.task_queue = PriorityQueue()
        self.tasks: Dict[str, Task] = {}
        self.active_tasks: Dict[str, Task] = {}
        self.server_loads: Dict[str, float] = {}
        self.lock = threading.Lock()
        self._running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def submit_task(self, task_id: str, priority: TaskPriority, server_requirements: Dict) -> Task:
        """提交新任务到调度队列"""
        task = Task(
            id=task_id,
            priority=priority,
            server_requirements=server_requirements,
            created_at=time.time()
        )
        with self.lock:
            self.tasks[task_id] = task
            # 优先级队列项格式: (优先级, 创建时间, 任务ID)
            self.task_queue.put((-priority.value, task.created_at, task_id))
        return task

    def cancel_task(self, task_id: str) -> bool:
        """取消指定任务"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    task.status = TaskStatus.CANCELLED
                    if task_id in self.active_tasks:
                        del self.active_tasks[task_id]
                    return True
            return False

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return self.tasks.get(task_id)

    def update_server_load(self, server_id: str, load: float):
        """更新服务器负载信息"""
        with self.lock:
            self.server_loads[server_id] = load

    def _find_suitable_server(self, task: Task) -> Optional[str]:
        """根据任务要求和服务器负载选择合适的服务器"""
        suitable_servers = []
        for server_id, load in self.server_loads.items():
            # 检查服务器是否满足任务要求
            if self._check_server_requirements(server_id, task.server_requirements):
                suitable_servers.append((server_id, load))
        
        if not suitable_servers:
            return None
            
        # 按负载排序,选择负载最低的服务器
        suitable_servers.sort(key=lambda x: x[1])
        return suitable_servers[0][0]

    def _check_server_requirements(self, server_id: str, requirements: Dict) -> bool:
        """检查服务器是否满足任务要求"""
        # TODO: 实现具体的要求检查逻辑
        return True

    def _scheduler_loop(self):
        """调度器主循环"""
        while self._running:
            try:
                if self.task_queue.empty():
                    time.sleep(1)
                    continue

                # 获取优先级最高的任务
                _, _, task_id = self.task_queue.get()
                task = self.tasks[task_id]

                # 跳过已取消的任务
                if task.status == TaskStatus.CANCELLED:
                    continue

                # 寻找合适的服务器
                server_id = self._find_suitable_server(task)
                if not server_id:
                    # 没有合适的服务器,放回队列
                    self.task_queue.put((-task.priority.value, task.created_at, task_id))
                    time.sleep(1)
                    continue

                # 分配任务到服务器
                with self.lock:
                    task.status = TaskStatus.RUNNING
                    task.assigned_server = server_id
                    self.active_tasks[task_id] = task

            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(1)

    def shutdown(self):
        """关闭调度器"""
        self._running = False
        self.scheduler_thread.join()

    def get_queue_status(self) -> Dict:
        """获取队列状态统计"""
        stats = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        for task in self.tasks.values():
            stats[task.status.value] += 1
        return stats 