"""
服务器工厂类
"""
import logging
from typing import Dict, Any, Optional, Type
from .base import BaseServer
from .windows import WindowsServer
from .unix import UnixServer
from .macos import MacOSServer

logger = logging.getLogger(__name__)

class ServerFactory:
    """服务器工厂类"""
    
    _server_types = {
        'windows': WindowsServer,
        'unix': UnixServer,
        'macos': MacOSServer
    }
    
    @classmethod
    def get_server_class(cls, server_type: str) -> Optional[Type[BaseServer]]:
        """
        获取服务器类
        
        Args:
            server_type: 服务器类型 (windows/unix/macos)
            
        Returns:
            Type[BaseServer]: 服务器类
        """
        return cls._server_types.get(server_type.lower())
    
    @classmethod
    def create_server(cls, server_type: str, config: Dict[str, Any]) -> Optional[BaseServer]:
        """
        创建服务器实例
        
        Args:
            server_type: 服务器类型 (windows/unix/macos)
            config: 服务器配置
            
        Returns:
            BaseServer: 服务器实例
        """
        try:
            if server_class := cls.get_server_class(server_type):
                return server_class(config)
            else:
                logger.error(f"不支持的服务器类型: {server_type}")
                return None
                
        except Exception as e:
            logger.error(f"创建服务器实例失败: {str(e)}")
            return None 