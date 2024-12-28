# 开发指南

## 开发环境搭建

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/remotebuilder.git
cd remotebuilder
```

### 2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd web
npm install
```

## 项目结构说明

```
.
├── core/                # 核心功能模块
│   ├── api/            # API接口定义
│   │   ├── routes/     # 路由定义
│   │   └── models/     # 数据模型
│   ├── builder/        # 打包功能实现
│   │   ├── windows/    # Windows打包
│   │   ├── macos/      # macOS打包
│   │   └── linux/      # Linux打包
│   ├── monitor/        # 监控功能
│   ├── scheduler/      # 调度系统
│   └── server/         # 服务器管理
├── web/                # Web前端
│   ├── src/           # 源代码
│   │   ├── components/# 组件
│   │   ├── pages/     # 页面
│   │   └── utils/     # 工具函数
│   └── public/        # 静态资源
├── tests/             # 测试用例
└── example/           # 示例代码
```

## 开发规范

### Python代码规范
- 遵循PEP 8规范
- 使用类型注解
- 编写文档字符串
- 单元测试覆盖率要求 > 80%

### JavaScript代码规范
- 使用ESLint
- 遵循Airbnb JavaScript规范
- 使用TypeScript
- 组件测试覆盖率要求 > 80%

## API开发

### 添加新API
1. 在 `core/api/routes` 下创建路由文件
2. 在 `core/api/models` 下定义数据模型
3. 编写API文档
4. 添加单元测试

示例：
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class TaskCreate(BaseModel):
    name: str
    platform: str
    source_path: str

@router.post("/tasks")
async def create_task(task: TaskCreate):
    try:
        # 实现任务创建逻辑
        return {"task_id": "new_task_id"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 前端开发

### 添加新页面
1. 在 `web/src/pages` 下创建页面组件
2. 在路由配置中添加新页面
3. 添加必要的组件测试

示例：
```typescript
// TaskList.tsx
import React from 'react';
import { Table } from 'antd';

interface Task {
  id: string;
  name: string;
  status: string;
}

const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    // 获取任务列表
    fetchTasks();
  }, []);

  return (
    <Table
      dataSource={tasks}
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: '名称', dataIndex: 'name' },
        { title: '状态', dataIndex: 'status' }
      ]}
    />
  );
};

export default TaskList;
```

## 测试指南

### 运行测试
```bash
# 后端测试
pytest tests/

# 前端测试
cd web
npm test
```

### 编写测试
- 使用pytest进行后端测试
- 使用Jest和React Testing Library进行前端测试
- 遵循AAA模式（Arrange-Act-Assert）
- 使用mock处理外部依赖

示例：
```python
# test_tasks.py
import pytest
from core.api.models import Task

def test_create_task():
    # Arrange
    task_data = {
        "name": "test_task",
        "platform": "windows",
        "source_path": "/path/to/source"
    }
    
    # Act
    task = Task.create(**task_data)
    
    # Assert
    assert task.name == task_data["name"]
    assert task.platform == task_data["platform"]
```

## 调试技巧

### 后端调试
1. 使用Python调试器
```python
import pdb; pdb.set_trace()
```

2. 使用日志
```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### 前端调试
1. 使用React Developer Tools
2. 使用Chrome DevTools
3. 使用console.log()进行调试输出

## 部署指南

### 开发环境
```bash
# 启动后端服务
python main.py

# 启动前端开发服务器
cd web
npm run dev
```

### 生产环境
```bash
# 构建前端
cd web
npm run build

# 启动生产服务器
gunicorn main:app --workers 4 --bind 0.0.0.0:5000
``` 