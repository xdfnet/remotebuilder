"""
连接池管理
"""
import logging
import threading
import time
from typing import Dict, Optional, List, Tuple
from queue import Queue, Empty
from .base import BaseServer

logger = logging.getLogger(__name__)

class PooledServer:
    """带连接池的服务器包装器"""
    
    def __init__(self, server: BaseServer):
        self.server = server
        self.last_used = 0.0
        self.in_use = False
        self.failed_count = 0
        self.last_check = 0.0
        self.health_status = None
        
    def acquire(self) -> None:
        """获取连接"""
        self.in_use = True
        self.last_used = time.time()
        
    def release(self) -> None:
        """释放连接"""
        self.in_use = False
        
    def mark_failed(self) -> None:
        """标记失败"""
        self.failed_count += 1
        
    def reset_failed(self) -> None:
        """重置失败计数"""
        self.failed_count = 0

class ConnectionPool:
    """服务器连接池"""
    
    def __init__(
        self,
        pool_size: int = 10,
        max_idle_time: int = 300,
        health_check_interval: int = 60,
        max_failed_attempts: int = 3
    ):
        self.pool_size = pool_size
        self.max_idle_time = max_idle_time
        self.health_check_interval = health_check_interval
        self.max_failed_attempts = max_failed_attempts
        self.pools: Dict[str, Queue[PooledServer]] = {}
        self.servers: Dict[str, List[PooledServer]] = {}
        self.lock = threading.Lock()
        
        # 启动监控线程
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_idle_connections,
            daemon=True
        )
        self.health_check_thread = threading.Thread(
            target=self._check_server_health,
            daemon=True
        )
        
        self.cleanup_thread.start()
        self.health_check_thread.start()
        
    def add_server(self, server_type: str, server: BaseServer) -> None:
        """添加服务器到连接池"""
        with self.lock:
            if server_type not in self.pools:
                self.pools[server_type] = Queue(self.pool_size)
                self.servers[server_type] = []
                
            pooled_server = PooledServer(server)
            self.servers[server_type].append(pooled_server)
            self.pools[server_type].put(pooled_server)
            logger.info(f"添加服务器到 {server_type} 连接池")
            
    def remove_server(self, server_type: str, server: BaseServer) -> None:
        """从连接池移除服务器"""
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
                    
            logger.info(f"从 {server_type} 连接池移除服务器")
            
    def acquire_server(self, server_type: str, timeout: int = 30) -> Optional[BaseServer]:
        """获取服务器连接"""
        if server_type not in self.pools:
            return None
            
        try:
            # 获取并验证服务器状态
            pooled_server = self._get_healthy_server(server_type, timeout)
            if not pooled_server:
                return None
                
            pooled_server.acquire()
            return pooled_server.server
            
        except Exception as e:
            logger.error(f"获取服务器连接失败: {str(e)}")
            return None
            
    def release_server(self, server_type: str, server: BaseServer) -> None:
        """释放服务器连接"""
        if server_type not in self.pools:
            return
            
        for pooled_server in self.servers[server_type]:
            if pooled_server.server == server and pooled_server.in_use:
                pooled_server.release()
                self.pools[server_type].put(pooled_server)
                break
                
    def _get_healthy_server(
        self,
        server_type: str,
        timeout: int
    ) -> Optional[PooledServer]:
        """获取健康的服务器"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                pooled_server = self.pools[server_type].get(timeout=1)
                
                # 检查失败次数
                if pooled_server.failed_count >= self.max_failed_attempts:
                    logger.warning(f"服务器失败次数过多,尝试重新连接")
                    if self._reconnect_server(pooled_server):
                        pooled_server.reset_failed()
                    else:
                        continue
                        
                # 检查健康状态
                current_time = time.time()
                if current_time - pooled_server.last_check > self.health_check_interval:
                    health_status = pooled_server.server.check_health()
                    pooled_server.health_status = health_status
                    pooled_server.last_check = current_time
                    
                    if health_status.errors:
                        logger.warning(f"服务器健康检查失败: {health_status.errors}")
                        pooled_server.mark_failed()
                        continue
                        
                return pooled_server
                
            except Empty:
                continue
                
        logger.error(f"无法获取健康的 {server_type} 服务器")
        return None
        
    def _reconnect_server(self, pooled_server: PooledServer) -> bool:
        """重新连接服务器"""
        try:
            pooled_server.server.disconnect()
            if pooled_server.server.connect():
                logger.info("服务器重新连接成功")
                return True
            else:
                logger.error("服务器重新连接失败")
                return False
        except Exception as e:
            logger.error(f"重新连接服务器失败: {str(e)}")
            return False
            
    def _check_server_health(self) -> None:
        """检查服务器健康状态"""
        while True:
            time.sleep(self.health_check_interval)
            
            with self.lock:
                for server_type, servers in self.servers.items():
                    for pooled_server in servers:
                        if not pooled_server.in_use:
                            try:
                                health_status = pooled_server.server.check_health()
                                pooled_server.health_status = health_status
                                pooled_server.last_check = time.time()
                                
                                if health_status.errors:
                                    logger.warning(
                                        f"{server_type} 服务器健康检查失败: "
                                        f"{health_status.errors}"
                                    )
                                    pooled_server.mark_failed()
                                    
                                    # 尝试重新连接
                                    if pooled_server.failed_count >= self.max_failed_attempts:
                                        self._reconnect_server(pooled_server)
                                        
                            except Exception as e:
                                logger.error(f"健康检查失败: {str(e)}")
                                pooled_server.mark_failed()
                                
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
                            logger.info(f"断开空闲连接: {server_type}")
                        except Exception as e:
                            logger.error(f"断开空闲连接失败: {str(e)}")
                            
                    # 更新服务器列表
                    self.servers[server_type] = active_servers
                    
                    # 重建连接池
                    self.pools[server_type] = Queue(self.pool_size)
                    for pooled_server in active_servers:
                        if not pooled_server.in_use:
                            self.pools[server_type].put(pooled_server)
                            
    def get_pool_status(self) -> Dict[str, Dict[str, Any]]:
        """获取连接池状态"""
        status = {}
        with self.lock:
            for server_type in self.pools.keys():
                pool_info = {
                    'total_servers': len(self.servers[server_type]),
                    'active_servers': len([
                        s for s in self.servers[server_type]
                        if s.in_use
                    ]),
                    'available_servers': self.pools[server_type].qsize(),
                    'failed_servers': len([
                        s for s in self.servers[server_type]
                        if s.failed_count > 0
                    ])
                }
                status[server_type] = pool_info
        return status
        
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
            logger.info("已清理所有连接") 