# RemoteBuilder

RemoteBuilder 是一个强大的远程跨平台打包工具,支持在远程服务器上为 Windows、macOS 和 Linux 平台构建应用程序。它提供了智能的服务器管理、可靠的错误处理和灵活的打包配置功能。

## 主要特性

- 跨平台打包支持
  - Windows 应用程序打包
  - macOS 应用程序打包
  - Linux 应用程序打包
  - 支持多种打包工具
  - 统一的打包配置

- 智能服务器管理
  - 自动服务器选择
  - 负载均衡调度
  - 实时健康检查
  - 自动断线重连
  - 连接池复用
  - 空闲资源回收

- 可靠性保证
  - 多级重试机制
  - 自动故障转移
  - 任务状态跟踪
  - 资源自动清理
  - 详细错误日志

- 打包工具支持
  - PyInstaller (默认)
  - 支持扩展其他打包工具
  - 统一的打包接口
  - 灵活的配置选项

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/xdfnet/remotebuilder.git

# 安装依赖
pip install -r requirements.txt
```

### 基本用法

1. 配置打包服务器:

```python
from core.server import ServerManager

# 创建服务器管理器
server_manager = ServerManager()

# 添加 Windows 打包服务器
server_manager.add_server(
    name="win_builder",
    server_type="windows",
    config={
        "host": "192.168.1.100",
        "username": "builder",
        "password": "password"
    }
)

# 添加 macOS 打包服务器
server_manager.add_server(
    name="mac_builder",
    server_type="macos",
    config={
        "host": "192.168.1.101",
        "username": "builder",
        "key_file": "~/.ssh/id_rsa"
    }
)
```

2. 创建打包任务:

```python
from core.builder import BuildManager

# 创建打包管理器
build_manager = BuildManager(server_manager)

# 创建打包任务
task_id = build_manager.create_task(
    platform="windows",  # windows/macos/linux
    entry_script="app.py",
    workspace="./src",
    config={
        "builder": "pyinstaller",
        "pyinstaller": {
            "name": "MyApp",
            "onefile": True,
            "console": False,
            "icon": "icon.ico",
            "hidden_imports": ["requests"],
            "datas": [
                ("assets", "assets"),
                ("config.yaml", ".")
            ]
        }
    }
)

# 启动任务
if build_manager.start_task(task_id):
    print("打包成功!")
    status = build_manager.get_task_status(task_id)
    print(f"输出目录: {status['output_dir']}")
else:
    print("打包失败!")
```

### 高级功能

1. 任务状态查询:

```python
# 获取任务状态
status = build_manager.get_task_status(task_id)
print(f"任务状态: {status['status']}")
print(f"错误信息: {status['error']}")
print(f"输出目录: {status['output_dir']}")
```

2. 取消任务:

```python
# 取消正在运行的任务
if build_manager.cancel_task(task_id):
    print("任务已取消")
```

3. 清理任务:

```python
# 清理任务资源
build_manager.cleanup_task(task_id)
```

4. 服务器管理:

```python
# 获取活动服务器列表
active_servers = server_manager.get_active_servers()

# 检查服务器健康状态
health_status = server_manager.check_servers_health()

# 断开服务器连接
server_manager.disconnect_server("win_builder")

# 清理所有连接
server_manager.cleanup()
```

## 项目结构

```
remotebuilder/
├── core/                # 核心代码
│   ├── server/         # 服务器管理
│   │   ├── base.py     # 服务器基类
│   │   ├── windows.py  # Windows 服务器
│   │   ├── macos.py    # macOS 服务器
│   │   ├── unix.py     # Unix 服务器
│   │   ├── pool.py     # 连接池
│   │   ├── retry.py    # 重试机制
│   │   ├── factory.py  # 服务器工厂
│   │   └── manager.py  # 服务器管理器
│   └── builder/        # 打包管理
│       ├── base.py     # 打包器基类
│       ├── pyinstaller.py  # PyInstaller 实现
│       └── manager.py  # 打包管理器
├── docs/              # 文档
├── examples/          # 示例代码
├── tests/            # 测试代码
├── README.md         # 项目说明
├── requirements.txt  # 依赖清单
└── LICENSE          # 开源协议
```

## 开发计划

- [ ] 添加更多打包工具支持
  - [ ] cx_Freeze
  - [ ] py2exe
  - [ ] py2app
  - [ ] auto-py-to-exe
  
- [ ] 实现 Web 管理界面
  - [ ] 任务管理
  - [ ] 服务器管理
  - [ ] 实时日志
  - [ ] 状态监控
  
- [ ] 添加打包任务队列
  - [ ] 任务优先级
  - [ ] 并发控制
  - [ ] 队列管理
  
- [ ] 支持自定义打包脚本
  - [ ] 脚本模板
  - [ ] 变量替换
  - [ ] 条件控制
  
- [ ] 添加监控和统计功能
  - [ ] 资源使用统计
  - [ ] 任务执行统计
  - [ ] 性能分析
  - [ ] 告警通知

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交改动 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 开源协议

本项目采用 MIT 开源协议 - 查看 [LICENSE](LICENSE) 了解详情
