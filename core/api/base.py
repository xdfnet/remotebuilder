"""
API 基础模块
提供核心接口和数据模型
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ServerConfig(BaseModel):
    """服务器配置"""
    host: str = Field(..., description="服务器地址")
    port: int = Field(22, description="SSH端口")
    username: str = Field(..., description="用户名")
    password: Optional[str] = Field(None, description="密码")
    key_file: Optional[str] = Field(None, description="密钥文件路径")
    
class ServerInfo(BaseModel):
    """服务器信息"""
    name: str = Field(..., description="服务器名称")
    type: str = Field(..., description="服务器类型")
    status: str = Field("offline", description="服务器状态")
    active: bool = Field(False, description="是否活动")
    cpu_usage: float = Field(0.0, description="CPU使用率")
    memory_usage: float = Field(0.0, description="内存使用率")
    disk_usage: float = Field(0.0, description="磁盘使用率")
    load: float = Field(0.0, description="负载分数")
    error: Optional[str] = Field(None, description="错误信息")
    last_check: datetime = Field(default_factory=datetime.now, description="最后检查时间")
    
class BuildConfig(BaseModel):
    """打包配置"""
    builder: str = Field("pyinstaller", description="打包工具")
    name: str = Field(..., description="应用名称")
    version: str = Field("1.0.0", description="应用版本")
    entry_script: str = Field(..., description="入口脚本")
    icon: Optional[str] = Field(None, description="图标文件")
    console: bool = Field(False, description="是否显示控制台")
    onefile: bool = Field(True, description="是否打包为单文件")
    clean: bool = Field(True, description="是否清理临时文件")
    requirements: Optional[str] = Field(None, description="依赖文件")
    extra_data: Optional[List[tuple]] = Field(None, description="额外数据文件")
    
class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str = Field(..., description="任务ID")
    platform: str = Field(..., description="目标平台")
    status: str = Field(..., description="任务状态")
    progress: float = Field(0.0, description="进度")
    current_step: str = Field("", description="当前步骤")
    error: Optional[str] = Field(None, description="错误信息")
    output_dir: Optional[str] = Field(None, description="输出目录")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    server: Optional[str] = Field(None, description="构建服务器")
    
class APIResponse(BaseModel):
    """API响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field("", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

class APIError(Exception):
    """API异常"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)

class BaseAPI:
    """API基类"""
    
    def __init__(self):
        self.version = "1.0.0"
        
    def health_check(self) -> APIResponse:
        """健康检查"""
        return APIResponse(
            success=True,
            message="Service is healthy",
            data={
                "version": self.version,
                "timestamp": datetime.now()
            }
        )
        
    def validate_server_config(self, config: Dict[str, Any]) -> ServerConfig:
        """验证服务器配置"""
        try:
            return ServerConfig(**config)
        except Exception as e:
            raise APIError(f"Invalid server config: {str(e)}")
            
    def validate_build_config(self, config: Dict[str, Any]) -> BuildConfig:
        """验证打包配置"""
        try:
            return BuildConfig(**config)
        except Exception as e:
            raise APIError(f"Invalid build config: {str(e)}")
            
    def format_server_info(self, info: Dict[str, Any]) -> ServerInfo:
        """格式化服务器信息"""
        try:
            return ServerInfo(**info)
        except Exception as e:
            raise APIError(f"Invalid server info: {str(e)}")
            
    def format_task_info(self, info: Dict[str, Any]) -> TaskInfo:
        """格式化任务信息"""
        try:
            return TaskInfo(**info)
        except Exception as e:
            raise APIError(f"Invalid task info: {str(e)}")
            
    def success_response(
        self,
        data: Any = None,
        message: str = "Success"
    ) -> APIResponse:
        """成功响应"""
        return APIResponse(
            success=True,
            message=message,
            data=data
        )
        
    def error_response(
        self,
        message: str,
        error: Optional[str] = None
    ) -> APIResponse:
        """错误响应"""
        return APIResponse(
            success=False,
            message=message,
            error=error
        ) 