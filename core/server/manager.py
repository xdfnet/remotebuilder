"""
服务器管理器
负责管理所有远程打包服务器,提供服务器选择、负载均衡等功能
"""
import logging
import time
from typing import Dict, List, Optional
from .base import BaseServer, ServerStatus
from .factory import ServerFactory
from .pool import ConnectionPool

logger = logging.getLogger(__name__)

class ServerManager:
    """服务器管理器"""
    
    def __init__(self):
        self.servers: Dict[str, BaseServer] = {}
        self.active_servers: Dict[str, BaseServer] = {}
        self.reconnect_attempts: Dict[str, int] = {}  # 记录重连次数
        self.max_reconnect_attempts = 3  # 最大重连次数
        self.reconnect_delay = 5  # 重连延迟(秒)
        self.connection_pool = ConnectionPool()  # 连接池
        
    def add_server(self, name: str, server_type: str, config: dict) -> bool:
        """
        添加服务器
        
        Args:
            name: 服务器名称
            server_type: 服务器类型 (windows/unix/macos)
            config: 服务器配置
            
        Returns:
            bool: 是否添加成功
        """
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
            return True
            
        except Exception as e:
            logger.error(f"添加服务器失败: {str(e)}")
            return False
            
    def remove_server(self, name: str) -> bool:
        """
        移除服务器
        
        Args:
            name: 服务器名称
            
        Returns:
            bool: 是否移除成功
        """
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
        """
        连接服务器
        
        Args:
            name: 服务器名称
            
        Returns:
            bool: 是否连接成功
        """
        try:
            if name not in self.servers:
                logger.error(f"服务器 {name} 不存在")
                return False
                
            server = self.servers[name]
            if server.connect():
                self.active_servers[name] = server
                self.reconnect_attempts[name] = 0
                return True
                
            # 连接失败,尝试重连
            return self.reconnect_server(name)
            
        except Exception as e:
            logger.error(f"连接服务器失败: {str(e)}")
            return False
            
    def reconnect_server(self, name: str) -> bool:
        """
        重连服务器
        
        Args:
            name: 服务器名称
            
        Returns:
            bool: 是否重连成功
        """
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
        """
        断开服务器连接
        
        Args:
            name: 服务器名称
            
        Returns:
            bool: 是否断开成功
        """
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
        """
        获取服务器实例
        
        Args:
            name: 服务器名称
            
        Returns:
            Optional[BaseServer]: 服务器实例
        """
        return self.servers.get(name)
        
    def get_active_servers(self) -> List[str]:
        """
        获取所有活动服务器
        
        Returns:
            List[str]: 活动服务器名称列表
        """
        return list(self.active_servers.keys())
        
    def check_servers_health(self) -> Dict[str, ServerStatus]:
        """
        检查所有活动服务器的健康状态
        
        Returns:
            Dict[str, ServerStatus]: 服务器状态字典
        """
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
                results[name] = status
            except Exception as e:
                logger.error(f"检查服务器 {name} 状态失败: {str(e)}")
                
        return results
        
    def select_server(self, server_type: str) -> Optional[BaseServer]:
        """
        根据负载情况选择合适的服务器
        
        Args:
            server_type: 服务器类型 (windows/unix/macos)
            
        Returns:
            Optional[BaseServer]: 选中的服务器实例
        """
        try:
            # 从连接池获取服务器
            server = self.connection_pool.acquire_server(server_type)
            if not server:
                return None
                
            # 检查服务器状态
            status = server.check_health()
            if status.errors:
                # 健康检查失败,释放连接并返回 None
                self.connection_pool.release_server(server_type, server)
                return None
                
            return server
            
        except Exception as e:
            logger.error(f"选择服务器失败: {str(e)}")
            if server:
                self.connection_pool.release_server(server_type, server)
            return None
            
    def cleanup(self) -> None:
        """清理所有连接"""
        for name in list(self.active_servers.keys()):
            self.disconnect_server(name)
        self.connection_pool.cleanup() 