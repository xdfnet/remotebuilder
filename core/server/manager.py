"""
服务器管理器
负责管理所有远程打包服务器,提供服务器选择、负载均衡等功能
"""
import logging
from typing import Dict, List, Optional
from .base import BaseServer, ServerStatus
from .factory import ServerFactory

logger = logging.getLogger(__name__)

class ServerManager:
    """服务器管理器"""
    
    def __init__(self):
        self.servers: Dict[str, BaseServer] = {}
        self.active_servers: Dict[str, BaseServer] = {}
        
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
                logger.error(f"创建���务器 {name} 失败")
                return False
                
            self.servers[name] = server
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
                
            del self.servers[name]
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
                return True
            return False
            
        except Exception as e:
            logger.error(f"连接服务器失败: {str(e)}")
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
        for name, server in self.active_servers.items():
            try:
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
            # 获取指定类型的活动服务器
            available_servers = [
                (name, server) 
                for name, server in self.active_servers.items()
                if isinstance(server, ServerFactory.get_server_class(server_type))
            ]
            
            if not available_servers:
                logger.warning(f"没有可用的 {server_type} 服务器")
                return None
                
            # 检查服务器状态
            server_stats = []
            for name, server in available_servers:
                status = server.check_health()
                if status.errors:
                    continue
                    
                # 计算综合负载分数 (CPU、内存、磁盘的平均值)
                load_score = (
                    status.cpu_usage +
                    status.memory_usage +
                    status.disk_usage
                ) / 3
                server_stats.append((load_score, server))
                
            if not server_stats:
                logger.warning(f"没有健康的 {server_type} 服务器")
                return None
                
            # 选择负载最低的服务器
            server_stats.sort(key=lambda x: x[0])
            return server_stats[0][1]
            
        except Exception as e:
            logger.error(f"选择服务器失���: {str(e)}")
            return None
            
    def cleanup(self) -> None:
        """清理所有连接"""
        for name in list(self.active_servers.keys()):
            self.disconnect_server(name) 