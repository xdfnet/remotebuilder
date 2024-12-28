"""
FastAPI 应用程序
提供 RESTful API 接口
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .base import ServerConfig, BuildConfig, ServerInfo, TaskInfo, APIResponse
from .server import ServerAPI
from .builder import BuilderAPI
from .monitor import MonitorAPI
from ..server import ServerManager
from ..builder import BuildManager

logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="RemoteBuilder API",
    description="远程跨平台 Python 应用打包服务 API",
    version="1.0.0"
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 创建管理器实例
server_manager = ServerManager()
build_manager = BuildManager(server_manager)

# 创建 API 实例
server_api = ServerAPI(server_manager)
builder_api = BuilderAPI(build_manager)
monitor_api = MonitorAPI(build_manager, server_manager)

# 请求模型
class AddServerRequest(BaseModel):
    """添加服务器请求"""
    name: str
    type: str
    config: Dict[str, Any]
    
class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    platform: str
    entry_script: str
    workspace: str
    config: Dict[str, Any]

# 健康检查
@app.get("/health")
async def health_check() -> APIResponse:
    """健康检查"""
    return server_api.health_check()

# 服务器管理 API
@app.post("/servers")
async def add_server(request: AddServerRequest) -> APIResponse:
    """添加服务器"""
    return server_api.add_server(
        request.name,
        request.type,
        request.config
    )
    
@app.delete("/servers/{name}")
async def remove_server(name: str) -> APIResponse:
    """移除服务器"""
    return server_api.remove_server(name)
    
@app.get("/servers/{name}")
async def get_server(name: str) -> APIResponse:
    """获取服务器信息"""
    return server_api.get_server(name)
    
@app.get("/servers")
async def list_servers() -> APIResponse:
    """获取服务器列表"""
    return server_api.list_servers()
    
@app.post("/servers/{name}/connect")
async def connect_server(name: str) -> APIResponse:
    """连接服务器"""
    return server_api.connect_server(name)
    
@app.post("/servers/{name}/disconnect")
async def disconnect_server(name: str) -> APIResponse:
    """断开服务器连接"""
    return server_api.disconnect_server(name)
    
@app.get("/servers/{name}/health")
async def check_server_health(name: str) -> APIResponse:
    """检查服务器健康状态"""
    return server_api.check_server_health(name)
    
@app.get("/servers/stats")
async def get_server_stats() -> APIResponse:
    """获取服务器统计信息"""
    return server_api.get_server_stats()

# 任务管理 API
@app.post("/tasks")
async def create_task(request: CreateTaskRequest) -> APIResponse:
    """创建打包任务"""
    return builder_api.create_task(
        request.platform,
        request.entry_script,
        request.workspace,
        request.config
    )
    
@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> APIResponse:
    """获取任务信息"""
    return builder_api.get_task(task_id)
    
@app.get("/tasks")
async def list_tasks(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = 100
) -> APIResponse:
    """获取任务列表"""
    return builder_api.list_tasks(status, platform, limit)
    
@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str) -> APIResponse:
    """取消任务"""
    return builder_api.cancel_task(task_id)
    
@app.delete("/tasks/{task_id}")
async def cleanup_task(task_id: str) -> APIResponse:
    """清理任务"""
    return builder_api.cleanup_task(task_id)
    
@app.get("/tasks/queue")
async def get_queue_status() -> APIResponse:
    """获取队列状态"""
    return builder_api.get_queue_status()
    
@app.get("/builders")
async def get_supported_builders() -> APIResponse:
    """获取支持的打包工具"""
    return builder_api.get_supported_builders()

# 监控 API
@app.get("/monitor/metrics")
async def collect_metrics() -> APIResponse:
    """收集当前指标"""
    return monitor_api.collect_metrics()
    
@app.get("/monitor/metrics/history")
async def get_metrics(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> APIResponse:
    """获取历史指标"""
    return monitor_api.get_metrics(start_time, end_time)
    
@app.get("/monitor/alerts")
async def get_alerts(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> APIResponse:
    """获取历史告警"""
    return monitor_api.get_alerts(start_time, end_time)
    
@app.get("/monitor/metrics/system")
async def get_system_metrics() -> APIResponse:
    """获取系统指标"""
    return monitor_api.get_system_metrics()
    
@app.get("/monitor/metrics/tasks")
async def get_task_metrics() -> APIResponse:
    """获取任务指标"""
    return monitor_api.get_task_metrics()
    
@app.get("/monitor/metrics/servers")
async def get_server_metrics() -> APIResponse:
    """获取服务器指标"""
    return monitor_api.get_server_metrics()
    
@app.get("/monitor/alerts/active")
async def get_active_alerts() -> APIResponse:
    """获取活动告警"""
    return monitor_api.get_active_alerts()
    
@app.get("/monitor/metrics/{metric_name}")
async def get_metrics_by_name(
    metric_name: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> APIResponse:
    """获取指定名称的指标"""
    return monitor_api.get_metrics_by_name(
        metric_name,
        start_time,
        end_time
    )
    
@app.get("/monitor/alerts/{level}")
async def get_alerts_by_level(
    level: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> APIResponse:
    """获取指定级别的告警"""
    return monitor_api.get_alerts_by_level(
        level,
        start_time,
        end_time
    )

# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return APIResponse(
        success=False,
        message=str(exc.detail),
        error=str(exc)
    )
    
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.exception("Unhandled exception")
    return APIResponse(
        success=False,
        message="Internal server error",
        error=str(exc)
    ) 