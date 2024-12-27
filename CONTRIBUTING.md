# 贡献指南

感谢您对 RemoteBuilder 项目的关注！我们欢迎任何形式的贡献，包括但不限于：

- 报告问题
- 提交功能建议
- 改进文档
- 提交代码

## 开发环境设置

1. Fork 项目并克隆到本地：
```bash
git clone https://github.com/yourusername/remotebuilder.git
cd remotebuilder
```

2. 创建虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写详细的文档字符串
- 保持代码简洁清晰
- 添加必要的注释

## 提交规范

1. 创建功能分支：
```bash
git checkout -b feature/your-feature
```

2. 提交信息格式：
```
<type>(<scope>): <subject>

<body>

<footer>
```

类型（type）：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

3. 示例：
```
feat(server): 添加服务器自动重连功能

- 实现断线重��机制
- 添加重连次数限制
- 添加重连间隔配置

Closes #123
```

## 测试

- 为新功能添加测试用例
- 确保所有测试通过
- 保持测试覆盖率

## Pull Request

1. 更新您的分支：
```bash
git fetch upstream
git rebase upstream/main
```

2. 推送到您的仓库：
```bash
git push origin feature/your-feature
```

3. 创建 Pull Request，包括：
- 清晰的标题和描述
- 相关的 issue 链接
- 破坏性改动说明
- 测试结果

## 行为准则

- 尊重所有贡献者
- 保持专业和友善
- 接受建设性的批评
- 关注问题本身

## 获取帮助

- 查看项目文档
- 搜索已有的 issues
- 创建新的 issue
- 通过邮件联系维护者

再次感谢您的贡献！ 