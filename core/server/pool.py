"""
连接池管理
"""
import logging
import threading
import time
from typing import Dict, Optional, List
from queue import Queue, Empty
from .base import BaseServer

logger = logging.getLogger(__name__)

class PooledServer:
    """带连接池的服务器包装器"""
    
    def __init__(self, server: BaseServer):
        self.server = server
        self.last_used = 0.0
        self.in_use = False
        
    def acquire(self) -> None:
        """获取连接"""
        self.in_use = True
        self.last_used = time.time()
        
    def release(self) -> None:
        """释放连接"""
        self.in_use = False
        
class ConnectionPool:
    """服务器连接池"""
    
    def __init__(self, pool_size: int = 10, max_idle_time: int = 300):
        self.pool_size = pool_size  # 连接池大小
        self.max_idle_time = max_idle_time  # 最大空闲时间(秒)
        self.pools: Dict[str, Queue[PooledServer]] = {}  # 服务器类型 -> 连接池
        self.servers: Dict[str, List[PooledServer]] = {}  # 服务器类型 -> 服务器列表
        self.lock = threading.Lock()
        
        # 启动空闲连接清理线程
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_idle_connections,
            daemon=True
        )
        self.cleanup_thread.start()
        
    def add_server(self, server_type: str, server: BaseServer) -> None:
        """
        添加服务器到连接池
        
        Args:
            server_type: 服务器类型
            server: 服务器实例
        """
        with self.lock:
            if server_type not in self.pools:
                self.pools[server_type] = Queue(self.pool_size)
                self.servers[server_type] = []
                
            pooled_server = PooledServer(server)
            self.servers[server_type].append(pooled_server)
            self.pools[server_type].put(pooled_server)
            
    def remove_server(self, server_type: str, server: BaseServer) -> None:
        """
        从连接池移除服务器
        
        Args:
            server_type: 服务器类型
            server: 服务器实例
        """
        with self.lock:
            if server_type not in self.pools:
                return
                
            # 从服务器列表中移除
            self.servers[server_type] = [
                s for s in self.servers[server_type]
                if s.server != server
            ]
            
            # 清空并重建连接池
            self.pools[server_type] = Queue(self.pool_size)
            for pooled_server in self.servers[server_type]:
                if not pooled_server.in_use:
                    self.pools[server_type].put(pooled_server)
                    
    def acquire_server(self, server_type: str, timeout: int = 30) -> Optional[BaseServer]:
        """
        获取服务器连接
        
        Args:
            server_type: 服务器类型
            timeout: 超时时间(秒)
            
        Returns:
            Optional[BaseServer]: 服务器实例
        """
        if server_type not in self.pools:
            return None
            
        try:
            pooled_server = self.pools[server_type].get(timeout=timeout)
            pooled_server.acquire()
            return pooled_server.server
        except Empty:
            logger.warning(f"获取 {server_type} 服务器连接超时")
            return None
            
    def release_server(self, server_type: str, server: BaseServer) -> None:
        """
        释放服务器连接
        
        Args:
            server_type: 服务器类型
            server: 服务器实例
        """
        if server_type not in self.pools:
            return
            
        for pooled_server in self.servers[server_type]:
            if pooled_server.server == server and pooled_server.in_use:
                pooled_server.release()
                self.pools[server_type].put(pooled_server)
                break
                
    def _cleanup_idle_connections(self) -> None:
        """清理空闲连接"""
        while True:
            time.sleep(60)  # 每分钟检查一次
            
            with self.lock:
                current_time = time.time()
                for server_type in list(self.pools.keys()):
                    idle_servers = []
                    active_servers = []
                    
                    # 检查所有服务器
                    for pooled_server in self.servers[server_type]:
                        if not pooled_server.in_use:
                            idle_time = current_time - pooled_server.last_used
                            if idle_time > self.max_idle_time:
                                idle_servers.append(pooled_server)
                            else:
                                active_servers.append(pooled_server)
                        else:
                            active_servers.append(pooled_server)
                            
                    # 断开空闲连接
                    for pooled_server in idle_servers:
                        try:
                            pooled_server.server.disconnect()
                        except Exception as e:
                            logger.error(f"断开空闲连接失败: {str(e)}")
                            
                    # 更新服务器列表
                    self.servers[server_type] = active_servers
                    
                    # 重建连接池
                    self.pools[server_type] = Queue(self.pool_size)
                    for pooled_server in active_servers:
                        if not pooled_server.in_use:
                            self.pools[server_type].put(pooled_server)
                            
    def cleanup(self) -> None:
        """清理所有连接"""
        with self.lock:
            for server_type in self.pools.keys():
                for pooled_server in self.servers[server_type]:
                    try:
                        pooled_server.server.disconnect()
                    except Exception as e:
                        logger.error(f"清理连接失败: {str(e)}")
                        
            self.pools.clear()
            self.servers.clear() 