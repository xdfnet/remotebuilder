"""
打包器基类
"""
import logging
from abc import ABC, abstractmethod
from ..server.manager import BuildTask

logger = logging.getLogger(__name__)

class BaseBuilder(ABC):
    """打包器基类"""
    
    @abstractmethod
    def build(self, task: BuildTask) -> bool:
        """
        执行打包
        
        Args:
            task: 打包任务
            
        Returns:
            bool: 是否打包成功
        """
        pass 