"""
远程服务器基类
"""
import logging
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ServerStatus:
    """服务器状态"""
    def __init__(self):
        self.connected: bool = False
        self.cpu_usage: float = 0.0
        self.memory_usage: float = 0.0
        self.disk_usage: float = 0.0
        self.python_version: str = ""
        self.errors: list[str] = []

class BaseServer(ABC):
    """服务器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.status = ServerStatus()
        
    @abstractmethod
    def connect(self) -> bool:
        """连接到服务器"""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
        
    @abstractmethod
    def check_health(self) -> ServerStatus:
        """检查服务器健康状态"""
        pass
        
    @abstractmethod
    def execute_command(self, command: str) -> Tuple[str, str]:
        """执行命令
        
        Returns:
            Tuple[str, str]: (stdout, stderr)
        """
        pass
        
    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """上传文件"""
        pass
        
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """下载文件"""
        pass
        
    @abstractmethod
    def create_directory(self, path: str) -> bool:
        """创建目录"""
        pass
        
    @abstractmethod
    def remove_directory(self, path: str) -> bool:
        """删除目录"""
        pass
        
    def check_python(self) -> Optional[str]:
        """检查 Python 环境
        
        Returns:
            Optional[str]: Python 版本，如果检查失败则返回 None
        """
        try:
            stdout, stderr = self.execute_command("python --version")
            if stderr:
                logger.error(f"检查 Python 版本失败: {stderr}")
                return None
            return stdout.strip()
        except Exception as e:
            logger.error(f"检查 Python 版本失败: {str(e)}")
            return None 