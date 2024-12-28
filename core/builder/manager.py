"""
打包管理器
负责管理跨平台打包任务
"""
import os
import logging
import tempfile
import shutil
import hashlib
import threading
import time
from typing import Dict, Any, Optional, List, Set
from queue import Queue, Empty
from ..server import ServerManager, BaseServer
from .base import BaseBuilder
from .pyinstaller import PyInstallerBuilder

logger = logging.getLogger(__name__)

class TaskStatus:
    """任务状态"""
    PENDING = "pending"
    UPLOADING = "uploading"
    BUILDING = "building"
    DOWNLOADING = "downloading"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

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
        self.status = TaskStatus.PENDING
        self.error = None
        self.output_dir = None
        self.server: Optional[BaseServer] = None
        self.progress = 0.0
        self.start_time = None
        self.end_time = None
        self.uploaded_files: Set[str] = set()
        self.total_files = 0
        self.current_step = ""
        
class TaskQueue:
    """任务队列"""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.queue = Queue()
        self.running: Dict[str, BuildTask] = {}
        self.lock = threading.Lock()
        
    def add_task(self, task: BuildTask) -> None:
        """添加任务"""
        self.queue.put(task)
        
    def get_next_task(self) -> Optional[BuildTask]:
        """获取下一个任务"""
        if len(self.running) >= self.max_concurrent:
            return None
            
        try:
            return self.queue.get_nowait()
        except Empty:
            return None
            
    def start_task(self, task: BuildTask) -> None:
        """开始任务"""
        with self.lock:
            self.running[task.task_id] = task
            
    def finish_task(self, task_id: str) -> None:
        """完成任务"""
        with self.lock:
            if task_id in self.running:
                del self.running[task_id]
                
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            'queued': self.queue.qsize(),
            'running': len(self.running),
            'max_concurrent': self.max_concurrent
        }

class BuildManager:
    """打包管理器"""
    
    def __init__(
        self,
        server_manager: ServerManager,
        max_concurrent_tasks: int = 3,
        chunk_size: int = 1024 * 1024  # 1MB
    ):
        self.server_manager = server_manager
        self.tasks: Dict[str, BuildTask] = {}
        self.builders: Dict[str, BaseBuilder] = {
            'pyinstaller': PyInstallerBuilder()
        }
        self.task_queue = TaskQueue(max_concurrent_tasks)
        self.chunk_size = chunk_size
        
        # 启动任务处理线程
        self.worker_thread = threading.Thread(
            target=self._process_tasks,
            daemon=True
        )
        self.worker_thread.start()
        
    def create_task(
        self,
        platform: str,
        entry_script: str,
        workspace: str,
        config: Dict[str, Any]
    ) -> Optional[str]:
        """创建打包任务"""
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
            
            # 添加到任务队列
            self.task_queue.add_task(task)
            
            return task_id
            
        except Exception as e:
            logger.error(f"创建打包任务失败: {str(e)}")
            return None
            
    def _process_tasks(self) -> None:
        """处理任务队列"""
        while True:
            try:
                # 获取下一个任务
                if task := self.task_queue.get_next_task():
                    # 开始处理任务
                    self.task_queue.start_task(task)
                    self._run_task(task)
                    self.task_queue.finish_task(task.task_id)
                else:
                    # 没有任务或达到并发上限,等待一段时间
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"处理任务失败: {str(e)}")
                
    def _run_task(self, task: BuildTask) -> None:
        """运行任务"""
        try:
            task.start_time = time.time()
            
            # 创建临时目录
            temp_dir = tempfile.mkdtemp(prefix=f"build_{task.platform}_")
            task.output_dir = temp_dir
            
            # 上传工作目录
            task.status = TaskStatus.UPLOADING
            task.current_step = "正在上传工作目录"
            if not self._upload_workspace(task):
                task.status = TaskStatus.FAILED
                return
                
            # 选择打包工具
            builder = self.builders.get(task.config.get('builder', 'pyinstaller'))
            if not builder:
                logger.error(f"不支持的打包工具: {task.config.get('builder')}")
                task.status = TaskStatus.FAILED
                task.error = f"不支持的打包工具: {task.config.get('builder')}"
                return
                
            # 开始打包
            task.status = TaskStatus.BUILDING
            task.current_step = "正在执行打包"
            if not builder.build(task):
                task.status = TaskStatus.FAILED
                return
                
            # 下载打包结果
            task.status = TaskStatus.DOWNLOADING
            task.current_step = "正在下载打包结果"
            if not self._download_output(task):
                task.status = TaskStatus.FAILED
                return
                
            task.status = TaskStatus.SUCCESS
            task.progress = 100.0
            
        except Exception as e:
            logger.error(f"运行任务失败: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
        finally:
            task.end_time = time.time()
            
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(self.chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def _upload_workspace(self, task: BuildTask) -> bool:
        """上传工作目录"""
        try:
            # 创建远程工作目录
            remote_workspace = f"/tmp/workspace_{task.task_id}"
            if not task.server.create_directory(remote_workspace):
                logger.error("创建远程工作目录失败")
                task.error = "创建远程工作目录失败"
                return False
                
            # 统计需要上传的文件
            total_size = 0
            file_list = []
            for root, _, files in os.walk(task.workspace):
                for file in files:
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, task.workspace)
                    remote_path = os.path.join(remote_workspace, relative_path)
                    file_size = os.path.getsize(local_path)
                    total_size += file_size
                    file_list.append((local_path, remote_path, file_size))
                    
            task.total_files = len(file_list)
            uploaded_size = 0
            
            # 上传文件
            for local_path, remote_path, file_size in file_list:
                # 创建父目录
                parent_dir = os.path.dirname(remote_path)
                if parent_dir != remote_workspace:
                    task.server.create_directory(parent_dir)
                    
                # 检查文件是否已存在
                try:
                    remote_hash = task.server.execute_command(
                        f"sha256sum {remote_path} | cut -d' ' -f1"
                    )[0].strip()
                    local_hash = self._calculate_file_hash(local_path)
                    
                    if remote_hash == local_hash:
                        logger.debug(f"文件已存在且未修改: {remote_path}")
                        task.uploaded_files.add(relative_path)
                        uploaded_size += file_size
                        task.progress = (uploaded_size / total_size) * 100
                        continue
                except Exception:
                    pass
                    
                # 上传文件
                if not task.server.upload_file(local_path, remote_path):
                    logger.error(f"上传文件失败: {local_path}")
                    task.error = f"上传文件失败: {local_path}"
                    return False
                    
                task.uploaded_files.add(relative_path)
                uploaded_size += file_size
                task.progress = (uploaded_size / total_size) * 100
                
            return True
            
        except Exception as e:
            logger.error(f"上传工作目录失败: {str(e)}")
            task.error = f"上传工作目录失败: {str(e)}"
            return False
            
    def _download_output(self, task: BuildTask) -> bool:
        """下载打包结果"""
        try:
            # 下载打包结果
            remote_output = f"/tmp/output_{task.task_id}"
            if not task.server.download_file(remote_output, task.output_dir):
                logger.error("下载打包结果失败")
                task.error = "下载打包结果失败"
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"下载打包结果失败: {str(e)}")
            task.error = f"下载打包结果失败: {str(e)}"
            return False
            
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        return {
            'task_id': task.task_id,
            'platform': task.platform,
            'status': task.status,
            'progress': task.progress,
            'current_step': task.current_step,
            'error': task.error,
            'output_dir': task.output_dir,
            'start_time': task.start_time,
            'end_time': task.end_time,
            'uploaded_files': len(task.uploaded_files),
            'total_files': task.total_files
        }
        
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return self.task_queue.get_queue_status()
        
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        if task.status in [TaskStatus.SUCCESS, TaskStatus.FAILED]:
            return False
            
        task.status = TaskStatus.CANCELLED
        task.error = "任务已取消"
        return True
        
    def cleanup_task(self, task_id: str) -> None:
        """清理任务"""
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