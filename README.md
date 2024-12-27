# RemoteBuilder

RemoteBuilder 是一个强大的远程跨平台打包工具,支持在远程服务器上为 Windows、macOS 和 Linux 平台构建应用程序。

## 主要特性

- 跨平台打包支持
  - Windows 应用程序打包
  - macOS 应用程序打包
  - Linux 应用程序打包

- 智能服务器管理
  - 自动服务器选择
  - 负载均衡
  - 健康检查
  - 自动重连
  - 连接池管理

- 可靠性保证
  - 错误重试机制
  - 断线重连
  - 任务状态跟踪
  - 资源自动清理

- 打包工具支持
  - PyInstaller (默认)
  - 支持扩展其他打包工具

## 安装

```bash
# 克隆仓库
git clone https://github.com/xdfnet/remotebuilder.git

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

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

## 项目结构

```
remotebuilder/
├── core/
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
- [ ] 实现 Web 管理界面
- [ ] 添加打包任务队列
- [ ] 支持自定义打包脚本
- [ ] 添加监控和统计功能

## 贡献指南

欢迎提交 Pull Request 或 Issue!

## 开源协议

MIT License
