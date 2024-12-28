"""
打包任务 API
提供任务管理相关的接口
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAPI, APIError, APIResponse, BuildConfig, TaskInfo
from ..builder import BuildManager

class BuilderAPI(BaseAPI):
    """打包任务API"""
    
    def __init__(self, build_manager: BuildManager):
        super().__init__()
        self.build_manager = build_manager
        
    def create_task(
        self,
        platform: str,
        entry_script: str,
        workspace: str,
        config: Dict[str, Any]
    ) -> APIResponse:
        """创建打包任务"""
        try:
            # 验证配置
            build_config = self.validate_build_config(config)
            
            # 创建任务
            task_id = self.build_manager.create_task(
                platform=platform,
                entry_script=entry_script,
                workspace=workspace,
                config=build_config.dict()
            )
            
            if not task_id:
                return self.error_response("Failed to create task")
                
            return self.success_response(
                {
                    "task_id": task_id,
                    "message": "Task created successfully"
                }
            )
            
        except APIError as e:
            return self.error_response(e.message)
        except Exception as e:
            return self.error_response(
                "Failed to create task",
                str(e)
            )
            
    def get_task(self, task_id: str) -> APIResponse:
        """获取任务信息"""
        try:
            task_info = self.build_manager.get_task_status(task_id)
            if not task_info:
                return self.error_response(f"Task {task_id} not found")
                
            return self.success_response(
                self.format_task_info(task_info).dict()
            )
            
        except Exception as e:
            return self.error_response(
                "Failed to get task info",
                str(e)
            )
            
    def list_tasks(
        self,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 100
    ) -> APIResponse:
        """获取任务列表"""
        try:
            task_list = []
            count = 0
            
            for task_id, task in self.build_manager.tasks.items():
                # 根据条件过滤
                if status and task.status != status:
                    continue
                if platform and task.platform != platform:
                    continue
                    
                task_info = self.build_manager.get_task_status(task_id)
                if task_info:
                    task_list.append(
                        self.format_task_info(task_info).dict()
                    )
                    
                count += 1
                if count >= limit:
                    break
                    
            return self.success_response(task_list)
            
        except Exception as e:
            return self.error_response(
                "Failed to list tasks",
                str(e)
            )
            
    def cancel_task(self, task_id: str) -> APIResponse:
        """取消任务"""
        try:
            if not self.build_manager.cancel_task(task_id):
                return self.error_response(
                    f"Failed to cancel task {task_id}"
                )
                
            return self.success_response(
                message=f"Task {task_id} cancelled successfully"
            )
            
        except Exception as e:
            return self.error_response(
                "Failed to cancel task",
                str(e)
            )
            
    def cleanup_task(self, task_id: str) -> APIResponse:
        """清理任务"""
        try:
            self.build_manager.cleanup_task(task_id)
            return self.success_response(
                message=f"Task {task_id} cleaned up successfully"
            )
            
        except Exception as e:
            return self.error_response(
                "Failed to cleanup task",
                str(e)
            )
            
    def get_queue_status(self) -> APIResponse:
        """获取队列状态"""
        try:
            status = self.build_manager.get_queue_status()
            return self.success_response(status)
            
        except Exception as e:
            return self.error_response(
                "Failed to get queue status",
                str(e)
            )
            
    def get_supported_builders(self) -> APIResponse:
        """获取支持的打包工具"""
        try:
            builders = list(self.build_manager.builders.keys())
            return self.success_response(builders)
            
        except Exception as e:
            return self.error_response(
                "Failed to get supported builders",
                str(e)
            ) 