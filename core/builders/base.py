"""
构建器基类
定义通用的构建接口和方法
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BuildError(Exception):
    """构建错误"""
    pass

class BuildStatus:
    """构建状态"""
    PENDING = "pending"
    PREPARING = "preparing"
    BUILDING = "building"
    PACKAGING = "packaging"
    CLEANING = "cleaning"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BaseBuilder(ABC):
    """构建器基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace("builder", "")
        self.supported_platforms = []
        self.current_task = None
        self.status = BuildStatus.PENDING
        self.progress = 0.0
        self.errors = []
        self.output = []
        self.start_time = None
        self.end_time = None
        
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证构建配置"""
        pass
        
    @abstractmethod
    def prepare_environment(self, workspace: str) -> bool:
        """准备构建环境"""
        pass
        
    @abstractmethod
    def build(self, entry_script: str, config: Dict[str, Any]) -> bool:
        """执行构建"""
        pass
        
    @abstractmethod
    def package(self, output_dir: str) -> bool:
        """打包"""
        pass
        
    @abstractmethod
    def cleanup(self) -> bool:
        """清理"""
        pass
        
    def supports_platform(self, platform: str) -> bool:
        """检查是否支持指定平台"""
        return platform.lower() in self.supported_platforms
        
    def get_status(self) -> Dict[str, Any]:
        """获取构建状态"""
        return {
            "builder": self.name,
            "status": self.status,
            "progress": self.progress,
            "errors": self.errors,
            "output": self.output,
            "start_time": self.start_time,
            "end_time": self.end_time
        }
        
    def log_error(self, error: str):
        """记录错误"""
        logger.error(f"Build error: {error}")
        self.errors.append(error)
        
    def log_output(self, output: str):
        """记录输出"""
        logger.info(output)
        self.output.append(output)
        
    def update_progress(self, progress: float):
        """更新进度"""
        self.progress = min(max(progress, 0.0), 100.0)
        
    def start(self):
        """开始构建"""
        self.status = BuildStatus.PREPARING
        self.progress = 0.0
        self.errors = []
        self.output = []
        self.start_time = datetime.now()
        self.end_time = None
        
    def complete(self):
        """完成构建"""
        self.status = BuildStatus.COMPLETED
        self.progress = 100.0
        self.end_time = datetime.now()
        
    def fail(self, error: str):
        """构建失败"""
        self.log_error(error)
        self.status = BuildStatus.FAILED
        self.end_time = datetime.now()
        
    def cancel(self):
        """取消构建"""
        self.status = BuildStatus.CANCELLED
        self.end_time = datetime.now()
        
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.status in [
            BuildStatus.PREPARING,
            BuildStatus.BUILDING,
            BuildStatus.PACKAGING
        ] 