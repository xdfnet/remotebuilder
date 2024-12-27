"""
基础打包类，定义打包接口和通用功能
"""
from typing import Dict, Any, List
from abc import ABC, abstractmethod

class BaseBuilder(ABC):
    """打包器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    @abstractmethod
    def prepare(self) -> bool:
        """准备打包环境"""
        pass
        
    @abstractmethod
    def build(self, entry_script: str, output_dir: str) -> bool:
        """执行打包"""
        pass
        
    @abstractmethod
    def verify(self, output_path: str) -> bool:
        """验证打包结果"""
        pass
        
    def cleanup(self) -> None:
        """清理临时文件"""
        pass

class BuildResult:
    """打包结果"""
    
    def __init__(self):
        self.success: bool = False
        self.platform: str = ""
        self.output_path: str = ""
        self.error_message: str = ""
        self.warnings: List[str] = []
        
    def __str__(self) -> str:
        status = "成功" if self.success else "失败"
        return f"打包{status}: {self.platform} -> {self.output_path}" 