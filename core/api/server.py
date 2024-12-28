"""
服务器管理 API
提供服务器管理相关的接口
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAPI, APIError, APIResponse, ServerConfig, ServerInfo
from ..server import ServerManager

class ServerAPI(BaseAPI):
    """服务器管理API"""
    
    def __init__(self, server_manager: ServerManager):
        super().__init__()
        self.server_manager = server_manager
        
    def add_server(
        self,
        name: str,
        server_type: str,
        config: Dict[str, Any]
    ) -> APIResponse:
        """添加服务器"""
        try:
            # 验证配置
            server_config = self.validate_server_config(config)
            
            # 添加服务器
            if not self.server_manager.add_server(
                name,
                server_type,
                server_config.dict()
            ):
                return self.error_response("Failed to add server")
                
            return self.success_response(
                message=f"Server {name} added successfully"
            )
            
        except APIError as e:
            return self.error_response(e.message)
        except Exception as e:
            return self.error_response(
                "Failed to add server",
                str(e)
            )
            
    def remove_server(self, name: str) -> APIResponse:
        """移除服务器"""
        try:
            if not self.server_manager.remove_server(name):
                return self.error_response(
                    f"Failed to remove server {name}"
                )
                
            return self.success_response(
                message=f"Server {name} removed successfully"
            )
            
        except Exception as e:
            return self.error_response(
                "Failed to remove server",
                str(e)
            )
            
    def get_server(self, name: str) -> APIResponse:
        """获取服务器信息"""
        try:
            server = self.server_manager.get_server(name)
            if not server:
                return self.error_response(f"Server {name} not found")
                
            # 获取服务器状态
            status = None
            if name in self.server_manager.active_servers:
                status = server.check_health()
                
            # 获取服���器信息
            server_info = {
                "name": name,
                "type": server.__class__.__name__.lower().replace("server", ""),
                "status": "online" if status else "offline",
                "active": name in self.server_manager.active_servers,
                "cpu_usage": status.cpu_usage if status else 0.0,
                "memory_usage": status.memory_usage if status else 0.0,
                "disk_usage": status.disk_usage if status else 0.0,
                "load": self.server_manager.load_balancer.server_loads.get(name, 0.0),
                "error": status.errors[0] if status and status.errors else None,
                "last_check": datetime.now()
            }
            
            return self.success_response(
                self.format_server_info(server_info).dict()
            )
            
        except Exception as e:
            return self.error_response(
                "Failed to get server info",
                str(e)
            )
            
    def list_servers(self) -> APIResponse:
        """获取服务器列表"""
        try:
            server_list = []
            
            for name, server in self.server_manager.servers.items():
                # 获取服务器状态
                status = None
                if name in self.server_manager.active_servers:
                    status = server.check_health()
                    
                # 获取服务器信息
                server_info = {
                    "name": name,
                    "type": server.__class__.__name__.lower().replace("server", ""),
                    "status": "online" if status else "offline",
                    "active": name in self.server_manager.active_servers,
                    "cpu_usage": status.cpu_usage if status else 0.0,
                    "memory_usage": status.memory_usage if status else 0.0,
                    "disk_usage": status.disk_usage if status else 0.0,
                    "load": self.server_manager.load_balancer.server_loads.get(name, 0.0),
                    "error": status.errors[0] if status and status.errors else None,
                    "last_check": datetime.now()
                }
                
                server_list.append(
                    self.format_server_info(server_info).dict()
                )
                
            return self.success_response(server_list)
            
        except Exception as e:
            return self.error_response(
                "Failed to list servers",
                str(e)
            )
            
    def connect_server(self, name: str) -> APIResponse:
        """连接服务器"""
        try:
            if not self.server_manager.connect_server(name):
                return self.error_response(
                    f"Failed to connect server {name}"
                )
                
            return self.success_response(
                message=f"Server {name} connected successfully"
            )
            
        except Exception as e:
            return self.error_response(
                "Failed to connect server",
                str(e)
            )
            
    def disconnect_server(self, name: str) -> APIResponse:
        """断开服务器连接"""
        try:
            if not self.server_manager.disconnect_server(name):
                return self.error_response(
                    f"Failed to disconnect server {name}"
                )
                
            return self.success_response(
                message=f"Server {name} disconnected successfully"
            )
            
        except Exception as e:
            return self.error_response(
                "Failed to disconnect server",
                str(e)
            )
            
    def check_server_health(self, name: str) -> APIResponse:
        """检查服务器健康状态"""
        try:
            server = self.server_manager.get_server(name)
            if not server:
                return self.error_response(f"Server {name} not found")
                
            if name not in self.server_manager.active_servers:
                return self.error_response(f"Server {name} is not connected")
                
            status = server.check_health()
            
            server_info = {
                "name": name,
                "type": server.__class__.__name__.lower().replace("server", ""),
                "status": "online",
                "active": True,
                "cpu_usage": status.cpu_usage,
                "memory_usage": status.memory_usage,
                "disk_usage": status.disk_usage,
                "load": self.server_manager.load_balancer.server_loads.get(name, 0.0),
                "error": status.errors[0] if status.errors else None,
                "last_check": datetime.now()
            }
            
            return self.success_response(
                self.format_server_info(server_info).dict()
            )
            
        except Exception as e:
            return self.error_response(
                "Failed to check server health",
                str(e)
            )
            
    def get_server_stats(self) -> APIResponse:
        """获取服务器统计信息"""
        try:
            stats = self.server_manager.get_server_stats()
            return self.success_response(stats)
            
        except Exception as e:
            return self.error_response(
                "Failed to get server stats",
                str(e)
            ) 