# 配置说明

## 环境配置

### 系统要求
- Python 3.8+
- Node.js 14+
- npm 6+

### 环境变量
```bash
# 服务器配置
PORT=5000                 # API服务器端口
WEB_PORT=3000            # Web界面端口
DEBUG=True               # 调试模式
LOG_LEVEL=INFO          # 日志级别

# 数据库配置
DB_HOST=localhost       # 数据库主机
DB_PORT=5432           # 数据库端口
DB_NAME=remotebuilder  # 数据库名称
DB_USER=admin          # 数据库用户
DB_PASSWORD=******     # 数据库密码

# 缓存配置
REDIS_HOST=localhost   # Redis主机
REDIS_PORT=6379       # Redis端口
REDIS_DB=0           # Redis数据库编号

# 任务队列配置
QUEUE_MAX_SIZE=100    # 最大队列长度
TASK_TIMEOUT=3600    # 任务超时时间(秒)
```

## 服务器配置

### 基础配置
```yaml
server:
  name: "builder-1"           # 服务器名称
  host: "0.0.0.0"            # 监听地址
  port: 5000                 # 监听端口
  workers: 4                 # 工作进程数
  timeout: 3600             # 超时时间(秒)
```

### 安全配置
```yaml
security:
  secret_key: "your-secret-key"    # 密钥
  token_expire: 86400              # Token过期时间(秒)
  allowed_origins:                 # CORS配置
    - "http://localhost:3000"
    - "https://your-domain.com"
```

### 存储配置
```yaml
storage:
  type: "local"                    # 存储类型(local/s3)
  path: "./storage"               # 本地存储路径
  # S3配置(可选)
  s3:
    bucket: "your-bucket"
    region: "us-east-1"
    access_key: "your-access-key"
    secret_key: "your-secret-key"
```

## 监控配置

### 资源监控
```yaml
monitor:
  interval: 60                    # 监控间隔(秒)
  metrics:                        # 监控指标
    - cpu_usage
    - memory_usage
    - disk_usage
    - network_io
```

### 告警配置
```yaml
alert:
  enabled: true                   # 是否启用告警
  channels:                       # 告警通道
    - type: "email"
      recipients:
        - "admin@example.com"
    - type: "webhook"
      url: "https://your-webhook.com"
  thresholds:                     # 告警阈值
    cpu_usage: 80                # CPU使用率阈值(%)
    memory_usage: 85            # 内存使用率阈值(%)
    disk_usage: 90              # 磁盘使用率阈值(%)
```

## 日志配置
```yaml
logging:
  level: "INFO"                  # 日志级别
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "./logs/app.log"        # 日志文件路径
  max_size: 100                 # 单个日志文件大小限制(MB)
  backup_count: 10              # 日志文件备份数量
```

## 高级配置

### 性能调优
```yaml
performance:
  max_concurrent_tasks: 10       # 最大并发任务数
  task_queue_size: 100          # 任务队列大小
  thread_pool_size: 4           # 线程池大小
```

### 缓存配置
```yaml
cache:
  enabled: true                 # 是否启用缓存
  type: "redis"                # 缓存类型
  ttl: 3600                    # 缓存过期时间(秒)
  max_size: 1000              # 最大缓存条目数
``` 