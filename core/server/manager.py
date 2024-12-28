"""
服务器管理器
负责管理所有远程打包服务器,提供服务器选择、负载均衡等功能
"""
import logging
import time
import random
from typing import Dict, List, Optional, Tuple
from .base import BaseServer, ServerStatus
from .factory import ServerFactory
from .pool import ConnectionPool

logger = logging.getLogger(__name__)

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self):
        self.server_loads: Dict[str, float] = {}
        self.last_selected: Dict[str, float] = {}
        
    def update_load(self, server_name: str, status: ServerStatus) -> None:
        """更新服务器负载信息"""
        # 计算综合负载分数 (0-100)
        load_score = (
            status.cpu_usage * 0.4 +  # CPU 使用率权重 40%
            status.memory_usage * 0.3 +  # 内存使用率权重 30%
            status.disk_usage * 0.3  # 磁盘使用率权重 30%
        )
        self.server_loads[server_name] = load_score
        
    def select_server(self, available_servers: List[str]) -> Optional[str]:
        """选择负载最低的服务器"""
        if not available_servers:
            return None
            
        # 过滤掉最近使用过的服务器
        current_time = time.time()
        candidates = [
            server for server in available_servers
            if current_time - self.last_selected.get(server, 0) > 5  # 5秒内不重复选择
        ]
        
        if not candidates:
            candidates = available_servers
            
        # 按负载排序
        candidates.sort(key=lambda x: self.server_loads.get(x, 0))
        
        # 从负载最低的三个服务器中随机选择一个
        selected = random.choice(candidates[:min(3, len(candidates))])
        self.last_selected[selected] = current_time
        return selected

class ServerManager:
    """服务器管理器"""
    
    def __init__(self):
        self.servers: Dict[str, BaseServer] = {}
        self.active_servers: Dict[str, BaseServer] = {}
        self.reconnect_attempts: Dict[str, int] = {}
        self.max_reconnect_attempts = 3
        self.reconnect_delay = 5
        self.connection_pool = ConnectionPool()
        self.load_balancer = LoadBalancer()
        
    def add_server(self, name: str, server_type: str, config: dict) -> bool:
        """添加服务器"""
        try:
            if name in self.servers:
                logger.warning(f"服务器 {name} 已存在")
                return False
                
            server = ServerFactory.create_server(server_type, config)
            if not server:
                logger.error(f"创建服务器 {name} 失败")
                return False
                
            self.servers[name] = server
            self.reconnect_attempts[name] = 0
            self.connection_pool.add_server(server_type, server)
            
            # 初始化负载信息
            if status := server.check_health():
                self.load_balancer.update_load(name, status)
                
            return True
            
        except Exception as e:
            logger.error(f"添加服务器失败: {str(e)}")
            return False
            
    def remove_server(self, name: str) -> bool:
        """移除服务器"""
        try:
            if name not in self.servers:
                logger.warning(f"服务器 {name} 不存在")
                return False
                
            server = self.servers[name]
            if name in self.active_servers:
                server.disconnect()
                del self.active_servers[name]
                
            # 从连接池移除
            server_type = None
            for t, cls in ServerFactory._server_types.items():
                if isinstance(server, cls):
                    server_type = t
                    break
                    
            if server_type:
                self.connection_pool.remove_server(server_type, server)
                
            del self.servers[name]
            del self.reconnect_attempts[name]
            return True
            
        except Exception as e:
            logger.error(f"移除服务器失败: {str(e)}")
            return False
            
    def connect_server(self, name: str) -> bool:
        """连接服务器"""
        try:
            if name not in self.servers:
                logger.error(f"服务器 {name} 不存在")
                return False
                
            server = self.servers[name]
            if server.connect():
                self.active_servers[name] = server
                self.reconnect_attempts[name] = 0
                
                # 更新负载信息
                if status := server.check_health():
                    self.load_balancer.update_load(name, status)
                    
                return True
                
            # 连接失败,尝试重连
            return self.reconnect_server(name)
            
        except Exception as e:
            logger.error(f"连接服务器失败: {str(e)}")
            return False
            
    def reconnect_server(self, name: str) -> bool:
        """重连服务器"""
        try:
            if name not in self.servers:
                logger.error(f"服务器 {name} 不存在")
                return False
                
            server = self.servers[name]
            attempts = self.reconnect_attempts[name]
            
            while attempts < self.max_reconnect_attempts:
                logger.info(f"正在重连服务器 {name}, 第 {attempts + 1} 次尝试")
                time.sleep(self.reconnect_delay)
                
                if server.connect():
                    self.active_servers[name] = server
                    self.reconnect_attempts[name] = 0
                    
                    # 更新负载信息
                    if status := server.check_health():
                        self.load_balancer.update_load(name, status)
                        
                    logger.info(f"服务器 {name} 重连成功")
                    return True
                    
                attempts += 1
                self.reconnect_attempts[name] = attempts
                
            logger.error(f"服务器 {name} 重连失败,已达到最大重试次数")
            return False
            
        except Exception as e:
            logger.error(f"重连服务器失败: {str(e)}")
            return False
            
    def disconnect_server(self, name: str) -> bool:
        """断开服务器连接"""
        try:
            if name not in self.active_servers:
                logger.warning(f"服务器 {name} 未连接")
                return False
                
            server = self.active_servers[name]
            server.disconnect()
            del self.active_servers[name]
            return True
            
        except Exception as e:
            logger.error(f"断开服务器连接失败: {str(e)}")
            return False
            
    def get_server(self, name: str) -> Optional[BaseServer]:
        """获取服务器实例"""
        return self.servers.get(name)
        
    def get_active_servers(self) -> List[str]:
        """获取所有活动服务器"""
        return list(self.active_servers.keys())
        
    def check_servers_health(self) -> Dict[str, ServerStatus]:
        """检查所有活动服务器的健康状态"""
        results = {}
        for name, server in list(self.active_servers.items()):
            try:
                status = server.check_health()
                if status.errors:
                    # 健康检查失败,尝试重连
                    logger.warning(f"服务器 {name} 健康检查失败,尝试重连")
                    if not self.reconnect_server(name):
                        # 重连失败,从活动服务器列表中移除
                        del self.active_servers[name]
                        continue
                    # 重连成功,重新检查健康状态
                    status = server.check_health()
                    
                # 更新负载信息
                self.load_balancer.update_load(name, status)
                results[name] = status
                
            except Exception as e:
                logger.error(f"检查服务器 {name} 状态失败: {str(e)}")
                
        return results
        
    def select_server(self, server_type: str) -> Optional[BaseServer]:
        """根据负载情况选择合适的服务器"""
        try:
            # 获取指定类型的活动服务器
            available_servers = [
                name for name, server in self.active_servers.items()
                if isinstance(server, ServerFactory._server_types[server_type])
            ]
            
            # 使用负载均衡器选择服务器
            if selected_name := self.load_balancer.select_server(available_servers):
                return self.active_servers[selected_name]
                
            # 如果没有可用服务器,尝试从连接池获取
            return self.connection_pool.acquire_server(server_type)
            
        except Exception as e:
            logger.error(f"选择服务器失败: {str(e)}")
            return None
            
    def get_server_stats(self) -> Dict[str, Dict]:
        """获取服务器统计信息"""
        stats = {
            'servers': {},
            'pool_status': self.connection_pool.get_pool_status()
        }
        
        for name, server in self.servers.items():
            server_info = {
                'active': name in self.active_servers,
                'reconnect_attempts': self.reconnect_attempts[name],
                'load': self.load_balancer.server_loads.get(name, 0)
            }
            
            if name in self.active_servers:
                if status := server.check_health():
                    server_info.update({
                        'cpu_usage': status.cpu_usage,
                        'memory_usage': status.memory_usage,
                        'disk_usage': status.disk_usage,
                        'errors': status.errors
                    })
                    
            stats['servers'][name] = server_info
            
        return stats
        
    def cleanup(self) -> None:
        """清理所有连接"""
        for name in list(self.active_servers.keys()):
            self.disconnect_server(name)
        self.connection_pool.cleanup() 