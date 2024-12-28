# RemoteBuilder

跨平台Python应用打包工具

## 为谁服务

- Python应用开发团队
- 独立开发者
- CI/CD系统
- 大规模应用分发

## 解决什么问题

- 跨平台构建环境管理
- 自动化打包流程
- 资源优化
- 可靠性保证
- 统一接口

## 功能特性

### 核心功能
- 跨平台打包支持(Windows/Linux/macOS)
- 多种打包工具支持(PyInstaller/cx_Freeze/py2exe/py2app)
- 远程构建服务器管理
- 分布式任务调度
- 构建产物管理

### 管理功能
- Web管理界面
- 服务器管理
  - 服务器添加/移除
  - 状态监控
  - 健康检查
  - 自动重连
- 任务管理
  - 任务创建/取消
  - 进度跟踪
  - 日志查看
  - 产物下载
- 监控告警
  - 性能监控
  - 资源监控
  - 告警通知
  - 问题诊断

## 项目结构

```
.
├── core/               # 核心功能模块
│   ├── api/           # API接口
│   ├── builder/       # 构建实现
│   ├── config/        # 配置管理
│   ├── monitor/       # 监控系统
│   └── server/        # 服务器管理
├── web/               # Web管理界面
│   ├── src/
│   │   ├── assets/    # 静态资源
│   │   ├── components/# 组件
│   │   ├── layouts/   # 布局
│   │   ├── router/    # 路由配置
│   │   ├── styles/    # 样式文件
│   │   └── views/     # 页面
│   └── vite.config.js # 构建配置
├── docs/              # 文档
└── tests/             # 测试
```

## 安装使用

1. 克隆项目
```bash
git clone https://github.com/xdfnet/remotebuilder.git
cd remotebuilder
```

2. 安装依赖
```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd web
npm install
```

3. 启动服务
```bash
# 启动后端服务
python main.py

# 启动前端开发服务器
cd web
npm run dev
```

4. 访问管理界面
```
http://localhost:3000
```

## 开发计划

- [x] 第一阶段: 核心功能实现
  - [x] 远程服务器管理
  - [x] 构建系统
  - [x] 基础API

- [x] 第二阶段: Web管理系统
  - [x] 服务器管理界面
  - [x] 任务管理界面
  - [x] 监控告警系统
  - [x] 界面交互优化

- [ ] 第三阶段: 高级特性
  - [ ] 分布式任务调度
  - [ ] 智能负载均衡
  - [ ] 自动化测试
  - [ ] 性能优化

## 贡献指南

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 开源协议

[MIT License](./LICENSE)
