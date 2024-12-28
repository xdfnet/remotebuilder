import unittest
import time
from core.scheduler.distributed import DistributedScheduler, TaskPriority, TaskStatus
from core.scheduler.balancer import LoadBalancer

class TestDistributedScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = DistributedScheduler()
        self.balancer = LoadBalancer()

    def tearDown(self):
        self.scheduler.shutdown()

    def test_task_submission(self):
        """测试任务提交"""
        task = self.scheduler.submit_task(
            task_id="test_task_1",
            priority=TaskPriority.HIGH,
            server_requirements={'cpu': 0.5, 'memory': 0.5}
        )
        
        self.assertEqual(task.id, "test_task_1")
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.status, TaskStatus.PENDING)

    def test_task_cancellation(self):
        """测试任务取消"""
        task = self.scheduler.submit_task(
            task_id="test_task_2",
            priority=TaskPriority.MEDIUM,
            server_requirements={}
        )
        
        success = self.scheduler.cancel_task(task.id)
        self.assertTrue(success)
        
        task_status = self.scheduler.get_task_status(task.id)
        self.assertEqual(task_status.status, TaskStatus.CANCELLED)

    def test_task_priority(self):
        """测试任务优先级"""
        # 提交多个不同优先级的任务
        tasks = []
        priorities = [
            TaskPriority.LOW,
            TaskPriority.HIGH,
            TaskPriority.MEDIUM,
            TaskPriority.URGENT
        ]
        
        for i, priority in enumerate(priorities):
            task = self.scheduler.submit_task(
                task_id=f"priority_task_{i}",
                priority=priority,
                server_requirements={}
            )
            tasks.append(task)
            
        # 等待调度器处理
        time.sleep(2)
        
        # 验证任务处理顺序
        processed_tasks = list(self.scheduler.active_tasks.values())
        self.assertTrue(len(processed_tasks) > 0)
        
        # 检查最高优先级的任务是否最先处理
        if processed_tasks:
            self.assertEqual(processed_tasks[0].priority, TaskPriority.URGENT)

    def test_server_selection(self):
        """测试服务器选择"""
        # 更新服务器指标
        self.balancer.update_metrics("server1", {
            'cpu_usage': 0.3,
            'memory_usage': 0.4,
            'disk_usage': 0.5,
            'network_usage': 0.2,
            'task_count': 2
        })
        
        self.balancer.update_metrics("server2", {
            'cpu_usage': 0.7,
            'memory_usage': 0.8,
            'disk_usage': 0.6,
            'network_usage': 0.5,
            'task_count': 5
        })
        
        # 测试服务器选择
        selected_server = self.balancer.select_server({
            'cpu': 0.2,
            'memory': 0.3
        })
        
        # 应该选择负载较低的server1
        self.assertEqual(selected_server, "server1")

    def test_load_balancing(self):
        """测试负载均衡"""
        # 模拟服务器负载变化
        for i in range(5):
            self.balancer.update_metrics("server1", {
                'cpu_usage': 0.2 + i * 0.1,
                'memory_usage': 0.3 + i * 0.1,
                'disk_usage': 0.4,
                'network_usage': 0.3,
                'task_count': i
            })
            
        # 检查负载趋势
        status = self.balancer.get_server_status("server1")
        self.assertIsNotNone(status)
        self.assertIn('trend', status)
        self.assertTrue(status['trend'] < 0)  # 负载上升,趋势应为负

    def test_cluster_status(self):
        """测试集群状态"""
        # 添加多个服务器
        servers = {
            "server1": {
                'cpu_usage': 0.3,
                'memory_usage': 0.4,
                'disk_usage': 0.5,
                'network_usage': 0.2,
                'task_count': 2
            },
            "server2": {
                'cpu_usage': 0.6,
                'memory_usage': 0.5,
                'disk_usage': 0.4,
                'network_usage': 0.3,
                'task_count': 3
            }
        }
        
        for server_id, metrics in servers.items():
            self.balancer.update_metrics(server_id, metrics)
            
        # 获取集群状态
        status = self.balancer.get_cluster_status()
        
        # 验证状态信息
        self.assertEqual(status['server_count'], 2)
        self.assertEqual(status['total_tasks'], 5)
        self.assertTrue(0 <= status['average_load'] <= 1)
        self.assertEqual(status['healthy_servers'], 2)

if __name__ == '__main__':
    unittest.main() 