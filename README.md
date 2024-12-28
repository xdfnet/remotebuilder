# RemoteBuilder

远程跨平台 Python 应用打包工具

## 项目简介

RemoteBuilder 是一个强大的远程跨平台 Python 应用打包工具，支持在远程服务器上为 Windows、macOS 和 Linux 平台构建应用程序。它提供了智能的服务器管理、高效的任务调度和可靠的打包流程。

## 为谁服务

- Python 应用开发团队：需要同时支持多个平台的打包需求
- 独立开发者：希望在不同环境下构建应用
- CI/CD 系统：需要自动化的跨平台打包能力
- 大规模应用分发：需要稳定可靠的打包服务

## 解决什么问题

1. 环境管理
   - 自动管理不同平台的构建环境
   - 智能调度最合适的构建服务器
   - 确保环境一致性和可靠性

2. 打包流程
   - 支持多种打包工具(PyInstaller等)
   - 提供统一的打包接口
   - 自动处理依赖关系

3. 资源优化
   - 智能负载均衡
   - 连接池复用
   - 并发任务处理
   - 文件传输优化

4. 可靠性保证
   - 自动故障转移
   - 状态实时监控
   - 错误自动恢复
   - 数据完整性校验

## 核心功能

1. 服务器管理
   - 多服务器支持
   - 智能负载均衡
   - 健康状态监控
   - 自动故障转移
   - 连接池管理

2. 任务调度
   - 并发任务处理
   - 队列优先级
   - 实时进度跟踪
   - 任务取消支持

3. 文件处理
   - 断点续传
   - 增量上传
   - 文件校验
   - 并发传输

4. 监控统计
   - 服务器状态
   - 任务进度
   - 资源使用
   - 性能指标

## 快速开始

1. 安装

```bash
pip install remotebuilder
```

2. 配置

创建配置文件 `config.yaml`:

```yaml
servers:
  windows:
    host: windows.example.com
    port: 22
    username: builder
    key_file: ~/.ssh/windows_key
  
  macos:
    host: macos.example.com
    port: 22
    username: builder
    key_file: ~/.ssh/macos_key
    
  linux:
    host: linux.example.com
    port: 22
    username: builder
    key_file: ~/.ssh/linux_key
```

3. 使用

```python
from remotebuilder import RemoteBuilder

# 创建构建器
builder = RemoteBuilder()

# 添加服务器
builder.add_server("win1", "windows", config["servers"]["windows"])
builder.add_server("mac1", "macos", config["servers"]["macos"])
builder.add_server("linux1", "linux", config["servers"]["linux"])

# 创建打包任务
task_id = builder.create_task(
    platform="windows",
    entry_script="app.py",
    workspace="./",
    config={
        "builder": "pyinstaller",
        "name": "MyApp",
        "icon": "icon.ico"
    }
)

# 获取任务状态
status = builder.get_task_status(task_id)
print(f"任务状态: {status['status']}")
print(f"进度: {status['progress']}%")
```

## 高级特性

1. 自动重连
```python
# 启用自动重连
builder.enable_auto_reconnect(
    max_attempts=3,
    delay=5
)
```

2. 负载均衡
```python
# 配置负载均衡策略
builder.set_load_balancer(
    cpu_weight=0.4,
    memory_weight=0.3,
    disk_weight=0.3
)
```

3. 并发控制
```python
# 设置最大并发任务数
builder.set_max_concurrent_tasks(5)
```

4. 监控回调
```python
# 添加状态变更回调
def on_status_change(task_id, status):
    print(f"任务 {task_id} 状态变更: {status}")
    
builder.add_status_callback(on_status_change)
```

## 项目结构

```
remotebuilder/
├── core/
│   ├── server/
│   │   ├── manager.py    # 服务器管理
│   │   ├── pool.py       # 连接池
│   │   └── base.py       # 基础接口
│   └── builder/
│       ├── manager.py    # 打包管理
│       ├── base.py       # 构建接口
│       └── pyinstaller.py # PyInstaller支持
├── docs/
│   └── project_plan.md   # 项目计划
└── tests/                # 测试用例
```

## 开发计划

1. 第一阶段 (已完成)
   - 核心功能实现
   - 基础框架搭建
   - 服务器管理
   - 打包流程

2. 第二阶段
   - Web管理界面
   - 更多打包工具
   - 监控系统
   - API完善

3. 第三阶段
   - 性能优化
   - 扩展功能
   - 文档完善
   - 社区建设

## 贡献指南

欢迎贡献代码，请参考 [CONTRIBUTING.md](CONTRIBUTING.md)

## 开源协议

MIT License
