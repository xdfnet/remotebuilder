# RemoteBuilder

远程跨平台Python应用打包服务

## 为谁服务

- Python应用开发团队 - 需要跨平台打包能力的开发团队
- 独立开发者 - 需要打包Python应用但缺乏完整环境的开发者
- CI/CD系统 - 需要自动化打包流程的持续集成系统
- 大规模应用分发 - 需要高效打包和分发Python应用的场景

## 解决什么问题

1. 环境管理
- 自动管理不同平台的打包环境
- 统一的环境配置和依赖管理
- 避免本地环境污染

2. 自动化流程
- 自动选择最优打包服务器
- 支持批量打包任务
- 提供任务队列和调度

3. 资源优化
- 分布式负载均衡
- 资源使用监控
- 自动伸缩和故障转移

4. 可靠性保证
- 服务器健康检查
- 自动重试和故障恢复
- 完整的日志记录

5. 统一接口
- RESTful API接口
- Web管理界面
- 命令行工具

## 功能特性

### 核心功能
- [x] 跨平台打包支持(Windows/macOS/Linux)
- [x] 分布式任务调度
- [x] 服务器管理和监控
- [x] 负载均衡
- [x] 故障转移
- [x] 资源监控
- [x] 告警系统

### Web界面
- [x] 服务器管理
- [x] 任务管理 
- [x] 监控面板
- [x] 告警中心

### API接口
- [x] RESTful API
- [x] WebSocket实时通知
- [x] 完整的API文档

## 快速开始

1. 安装依赖
```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd web && npm install
```

2. 启动服务
```bash
# 启动后端服务
python main.py

# 启动前端开发服务器
cd web && npm run dev
```

3. 访问服务
- Web界面: http://localhost:3000
- API文档: http://localhost:5000/docs

## 项目结构

```
.
├── core/               # 核心功能模块
│   ├── api/           # API接口
│   ├── builder/       # 打包功能
│   ├── monitor/       # 监控功能
│   ├── scheduler/     # 调度系统
│   └── server/        # 服务器管理
├── web/               # Web前端
│   ├── src/          # 源代码
│   └── public/       # 静态资源
├── docs/             # 文档
├── tests/            # 测试用例
└── example/          # 示例代码
```

## 配置说明

详细配置说明请参考 [配置文档](docs/configuration.md)

## 开发说明

请参考 [开发文档](docs/development.md)

## 贡献指南

请参考 [贡献指南](CONTRIBUTING.md)

## 开源协议

[MIT License](LICENSE)
