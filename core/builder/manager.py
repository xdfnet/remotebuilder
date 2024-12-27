"""
打包管理器
负责管理跨平台打包任务
"""
import os
import logging
import tempfile
import shutil
from typing import Dict, Any, Optional, List
from ..server import ServerManager, BaseServer
from .base import BaseBuilder
from .pyinstaller import PyInstallerBuilder

logger = logging.getLogger(__name__)

class BuildTask:
    """打包任务"""
    
    def __init__(
        self,
        task_id: str,
        platform: str,
        entry_script: str,
        workspace: str,
        config: Dict[str, Any]
    ):
        self.task_id = task_id
        self.platform = platform
        self.entry_script = entry_script
        self.workspace = workspace
        self.config = config
        self.status = "pending"  # pending/running/success/failed
        self.error = None
        self.output_dir = None
        self.server: Optional[BaseServer] = None
        
class BuildManager:
    """打包管理器"""
    
    def __init__(self, server_manager: ServerManager):
        self.server_manager = server_manager
        self.tasks: Dict[str, BuildTask] = {}
        self.builders: Dict[str, BaseBuilder] = {
            'pyinstaller': PyInstallerBuilder()
        }
        
    def create_task(
        self,
        platform: str,
        entry_script: str,
        workspace: str,
        config: Dict[str, Any]
    ) -> Optional[str]:
        """
        创建打包任务
        
        Args:
            platform: 目标平台 (windows/macos/linux)
            entry_script: 入口脚本
            workspace: 工作目录
            config: 打包配置
            
        Returns:
            Optional[str]: 任务ID
        """
        try:
            # 生成任务ID
            task_id = f"build_{platform}_{os.path.basename(entry_script)}_{len(self.tasks)}"
            
            # 创建任务
            task = BuildTask(
                task_id=task_id,
                platform=platform,
                entry_script=entry_script,
                workspace=workspace,
                config=config
            )
            
            # 选择合适的服务器
            server_type = {
                'windows': 'windows',
                'macos': 'macos',
                'linux': 'unix'
            }.get(platform)
            
            if not server_type:
                logger.error(f"不支持的平台: {platform}")
                return None
                
            server = self.server_manager.select_server(server_type)
            if not server:
                logger.error(f"没有可用的 {platform} 打包服务器")
                return None
                
            task.server = server
            self.tasks[task_id] = task
            return task_id
            
        except Exception as e:
            logger.error(f"创建打包任务失败: {str(e)}")
            return None
            
    def start_task(self, task_id: str) -> bool:
        """
        启动打包任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否启动成功
        """
        try:
            if task_id not in self.tasks:
                logger.error(f"任务 {task_id} 不存在")
                return False
                
            task = self.tasks[task_id]
            if task.status != "pending":
                logger.error(f"任务 {task_id} 状态不正确: {task.status}")
                return False
                
            # 创建临时目录
            temp_dir = tempfile.mkdtemp(prefix=f"build_{task.platform}_")
            task.output_dir = temp_dir
            
            # 上传工作目录
            logger.info(f"正在上传工作目录到服务器: {task.workspace}")
            if not self._upload_workspace(task):
                return False
                
            # 选择打包工具
            builder = self.builders.get(task.config.get('builder', 'pyinstaller'))
            if not builder:
                logger.error(f"不支持的打包工具: {task.config.get('builder')}")
                return False
                
            # 开始打包
            task.status = "running"
            if not builder.build(task):
                task.status = "failed"
                return False
                
            # 下载打包结果
            logger.info("正在下载打包结果")
            if not self._download_output(task):
                task.status = "failed"
                return False
                
            task.status = "success"
            return True
            
        except Exception as e:
            logger.error(f"启动打包任务失败: {str(e)}")
            if task_id in self.tasks:
                self.tasks[task_id].status = "failed"
                self.tasks[task_id].error = str(e)
            return False
            
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Dict[str, Any]]: 任务状态
        """
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        return {
            'task_id': task.task_id,
            'platform': task.platform,
            'status': task.status,
            'error': task.error,
            'output_dir': task.output_dir
        }
        
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否取消成功
        """
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        if task.status == "running":
            # TODO: 实现任务取消逻辑
            pass
            
        task.status = "failed"
        task.error = "任务已取消"
        return True
        
    def cleanup_task(self, task_id: str) -> None:
        """
        清理任务
        
        Args:
            task_id: 任务ID
        """
        if task_id not in self.tasks:
            return
            
        task = self.tasks[task_id]
        
        # 清理临时目录
        if task.output_dir and os.path.exists(task.output_dir):
            try:
                shutil.rmtree(task.output_dir)
            except Exception as e:
                logger.error(f"清理临时目录失败: {str(e)}")
                
        # 释放服务器
        if task.server:
            server_type = {
                'windows': 'windows',
                'macos': 'macos',
                'linux': 'unix'
            }.get(task.platform)
            if server_type:
                self.server_manager.connection_pool.release_server(
                    server_type,
                    task.server
                )
                
        # 删除任务
        del self.tasks[task_id]
        
    def _upload_workspace(self, task: BuildTask) -> bool:
        """
        上传工作目录
        
        Args:
            task: 打包任务
            
        Returns:
            bool: 是否上传成功
        """
        try:
            # 创建远程工作目录
            remote_workspace = f"/tmp/workspace_{task.task_id}"
            if not task.server.create_directory(remote_workspace):
                logger.error("创建远程工作目录失败")
                return False
                
            # 上传文件
            for root, _, files in os.walk(task.workspace):
                for file in files:
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, task.workspace)
                    remote_path = os.path.join(remote_workspace, relative_path)
                    
                    # 创建父目录
                    parent_dir = os.path.dirname(remote_path)
                    if parent_dir != remote_workspace:
                        task.server.create_directory(parent_dir)
                        
                    # 上传文件
                    if not task.server.upload_file(local_path, remote_path):
                        logger.error(f"上传文件失败: {local_path}")
                        return False
                        
            return True
            
        except Exception as e:
            logger.error(f"上传工作目录失败: {str(e)}")
            return False
            
    def _download_output(self, task: BuildTask) -> bool:
        """
        下载打包结果
        
        Args:
            task: 打包任务
            
        Returns:
            bool: 是否下载成功
        """
        try:
            # 下载打包结果
            remote_output = f"/tmp/output_{task.task_id}"
            if not task.server.download_file(remote_output, task.output_dir):
                logger.error("下载打包结果失败")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"下载打包结果失败: {str(e)}")
            return False 