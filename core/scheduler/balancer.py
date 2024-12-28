from typing import Dict, List, Optional, Tuple
import time
from dataclasses import dataclass
import numpy as np

@dataclass
class ServerMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: float
    task_count: int
    last_updated: float

class LoadBalancer:
    def __init__(self):
        self.server_metrics: Dict[str, ServerMetrics] = {}
        # 负载计算权重
        self.weights = {
            'cpu': 0.35,
            'memory': 0.25,
            'disk': 0.15,
            'network': 0.15,
            'tasks': 0.10
        }
        # 服务器评分历史
        self.score_history: Dict[str, List[float]] = {}
        # 负载阈值
        self.thresholds = {
            'cpu': 0.8,
            'memory': 0.8,
            'disk': 0.9,
            'network': 0.8,
            'tasks': 10
        }

    def update_metrics(self, server_id: str, metrics: Dict[str, float]):
        """更新服务器指标"""
        self.server_metrics[server_id] = ServerMetrics(
            cpu_usage=metrics.get('cpu_usage', 0),
            memory_usage=metrics.get('memory_usage', 0),
            disk_usage=metrics.get('disk_usage', 0),
            network_usage=metrics.get('network_usage', 0),
            task_count=metrics.get('task_count', 0),
            last_updated=time.time()
        )
        
        # 计算并更新服务器评分历史
        score = self._calculate_server_score(server_id)
        if server_id not in self.score_history:
            self.score_history[server_id] = []
        self.score_history[server_id].append(score)
        
        # 保留最近100个评分记录
        if len(self.score_history[server_id]) > 100:
            self.score_history[server_id].pop(0)

    def select_server(self, requirements: Dict[str, float]) -> Optional[str]:
        """选择最适合的服务器"""
        if not self.server_metrics:
            return None

        # 计算每个服务器的综合评分
        server_scores: List[Tuple[str, float]] = []
        for server_id in self.server_metrics:
            if self._meets_requirements(server_id, requirements):
                score = self._calculate_server_score(server_id)
                trend = self._calculate_trend(server_id)
                # 考虑趋势调整最终评分
                final_score = score * (1 + trend)
                server_scores.append((server_id, final_score))

        if not server_scores:
            return None

        # 按评分排序
        server_scores.sort(key=lambda x: x[1], reverse=True)
        return server_scores[0][0]

    def _calculate_server_score(self, server_id: str) -> float:
        """计算服务器综合评分"""
        metrics = self.server_metrics[server_id]
        
        # 归一化各项指标
        normalized_metrics = {
            'cpu': 1 - metrics.cpu_usage,
            'memory': 1 - metrics.memory_usage,
            'disk': 1 - metrics.disk_usage,
            'network': 1 - metrics.network_usage,
            'tasks': max(0, 1 - metrics.task_count / self.thresholds['tasks'])
        }
        
        # 计算加权评分
        score = sum(self.weights[k] * normalized_metrics[k] for k in self.weights)
        return score

    def _calculate_trend(self, server_id: str) -> float:
        """计算服务器负载趋势"""
        if server_id not in self.score_history or len(self.score_history[server_id]) < 2:
            return 0
            
        # 使用最近的评分计算趋势
        recent_scores = self.score_history[server_id][-10:]
        if len(recent_scores) < 2:
            return 0
            
        # 使用线性回归计算趋势
        x = np.arange(len(recent_scores))
        y = np.array(recent_scores)
        slope = np.polyfit(x, y, 1)[0]
        
        # 归一化趋势值到 [-0.2, 0.2] 范围
        return max(min(slope * 10, 0.2), -0.2)

    def _meets_requirements(self, server_id: str, requirements: Dict[str, float]) -> bool:
        """检查服务器是否满足要求"""
        metrics = self.server_metrics[server_id]
        
        # 检查各项指标是否满足要求
        if metrics.cpu_usage > self.thresholds['cpu']:
            return False
        if metrics.memory_usage > self.thresholds['memory']:
            return False
        if metrics.disk_usage > self.thresholds['disk']:
            return False
        if metrics.network_usage > self.thresholds['network']:
            return False
        if metrics.task_count >= self.thresholds['tasks']:
            return False
            
        # 检查特定要求
        for key, value in requirements.items():
            if key in self.thresholds:
                current_value = getattr(metrics, f"{key}_usage", 0)
                if current_value + value > self.thresholds[key]:
                    return False
                    
        return True

    def get_server_status(self, server_id: str) -> Optional[Dict]:
        """获取服务器状态信息"""
        if server_id not in self.server_metrics:
            return None
            
        metrics = self.server_metrics[server_id]
        score = self._calculate_server_score(server_id)
        trend = self._calculate_trend(server_id)
        
        return {
            'metrics': {
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'disk_usage': metrics.disk_usage,
                'network_usage': metrics.network_usage,
                'task_count': metrics.task_count
            },
            'score': score,
            'trend': trend,
            'last_updated': metrics.last_updated
        }

    def get_cluster_status(self) -> Dict:
        """获取集群整体状态"""
        if not self.server_metrics:
            return {
                'server_count': 0,
                'total_tasks': 0,
                'average_load': 0,
                'healthy_servers': 0
            }
            
        server_count = len(self.server_metrics)
        total_tasks = sum(m.task_count for m in self.server_metrics.values())
        average_load = sum(self._calculate_server_score(sid) for sid in self.server_metrics) / server_count
        healthy_servers = sum(1 for sid in self.server_metrics if self._meets_requirements(sid, {}))
        
        return {
            'server_count': server_count,
            'total_tasks': total_tasks,
            'average_load': average_load,
            'healthy_servers': healthy_servers
        } 