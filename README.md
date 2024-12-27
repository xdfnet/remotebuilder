# RemoteBuilder

RemoteBuilder 是一个专业的远程跨平台打包工具，支持将 Python 应用程序打包为 Windows、macOS 和 Unix 可执行程序。它提供智能的远程打包功能，可以自动选择最优的打包服务器，实现高效的跨平台打包。

详细的项目规划和开发路线图请查看 [项目规划文档](docs/project_plan.md)。

## 特性

- 支持 Windows、macOS 和 Unix 三平台打包
- 智能远程打包服务器管理
- 自动负载均衡和故障转移
- 完整的环境检查和依赖管理
- 灵活的配置系统
- 详细的日志记录
- 自动重试机制
- 资源文件验证
- 交互式操作模式

## 项目结构

```text
remotebuilder/
├── main.py                 # 主程序
├── build_pack.py          # 打包脚本
├── requirements.txt       # 项目依赖
├── Info.plist            # macOS 应用配置
├── core/                 # 核心功能模块
│   ├── builder/         # 打包器实现
│   │   ├── base.py     # 基础打包类
│   │   └── pyinstaller.py  # PyInstaller 实现
│   └── server/         # 服务器管理
│       ├── base.py     # 基础服务器类
│       ├── windows.py  # Windows 服务器
│       ├── unix.py     # Unix 服务器
│       ├── macos.py    # macOS 服务器
│       └── factory.py  # 服务器工厂
└── src/                 # 源代码
    ├── core.py         # 核心工具
    ├── config.py       # 配置管理
    ├── packager.py     # 打包管理
    └── config.yaml     # 配置文件
```

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/xdfnet/remotebuilder.git
cd remotebuilder
```

2. 创建并激活虚拟环境：

```bash
# 使用 conda
conda create -n packager python=3.9
conda activate packager

# 或使用 venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python main.py --entry-script path/to/your/main.py --workspace path/to/workspace
```

### 参数说明

- `--entry-script`: 必需，入口脚本路径
- `--workspace`: 必需，工作空间路径
- `--platform`: 可选，目标平台 (windows/macos/unix/all)，默认为 all
- `--config`: 可选，配置文件路径
- `-i, --interactive`: 可选，启用交互式模式
- `--machine`: 可选，指定打包机器 (1/2/3)

### 交互式模式

在交互式模式下，您可以：
1. 选择目标平台
2. 选择打包机器
3. 配置打包选项
4. 监控打包进度

```bash
python main.py -i --entry-script path/to/your/main.py --workspace path/to/workspace
```

### 远程打包

RemoteBuilder 支持在远程服务器上进行打包操作。您需要在 `config.yaml` 中配置服务器信息：

```yaml
servers:
  windows:
    host: windows.example.com
    username: user
    password: pass  # 或使用 key_file
  macos:
    host: macos.example.com
    username: user
    key_file: ~/.ssh/id_rsa
```

## 开发指南

1. Fork 项目
2. 创建特性分支
3. 提交改动
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License
