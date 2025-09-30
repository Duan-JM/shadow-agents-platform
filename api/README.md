# Shadow Agents Platform - 后端 API

基于 Flask 3.1.2 的后端服务，提供 RESTful API 接口。

## 技术栈

- **Python**: 3.11+
- **Web 框架**: Flask 3.1.2
- **WSGI 服务器**: Gunicorn + Gevent
- **异步任务**: Celery 5.5.2
- **数据库**: PostgreSQL 15 + SQLAlchemy 2.0.29
- **缓存**: Redis 6
- **向量数据库**: Milvus 2.5

## 目录结构

```
api/
├── configs/          # 配置模块
├── controllers/      # 控制器（路由处理）
│   ├── console/     # 管理后台 API
│   └── service/     # 对外服务 API
├── core/            # 核心业务逻辑
│   ├── app/         # 应用核心
│   ├── workflow/    # 工作流引擎
│   ├── rag/         # RAG 检索增强
│   └── model_runtime/ # 模型运行时
├── models/          # 数据模型
├── services/        # 业务服务层
├── repositories/    # 数据访问层
├── extensions/      # Flask 扩展
├── libs/            # 工具库
├── tasks/           # Celery 任务
├── migrations/      # 数据库迁移
└── tests/           # 测试代码
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -e .
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库、Redis 等
vim .env
```

### 3. 初始化数据库

```bash
# 创建数据库（需要先启动 PostgreSQL）
createdb shadow_agents

# 运行数据库迁移
flask db upgrade
```

### 4. 启动服务

**开发模式：**

```bash
# 启动 API 服务
python app.py

# 启动 Celery Worker
celery -A celery_app worker --loglevel=info

# 启动 Celery Beat（定时任务）
celery -A celery_app beat --loglevel=info
```

**生产模式：**

```bash
# 使用 Gunicorn 启动 API
gunicorn app:app -c gunicorn.conf.py

# 启动 Celery Worker
celery -A celery_app worker --loglevel=info -c 4

# 启动 Celery Beat
celery -A celery_app beat --loglevel=info
```

## Docker 部署

```bash
# 构建镜像
docker build -t shadow-agents-api:latest .

# 运行容器
docker run -d \
  --name shadow-agents-api \
  -p 5000:5000 \
  -e DB_HOST=postgres \
  -e REDIS_HOST=redis \
  shadow-agents-api:latest
```

## 开发指南

### 代码风格

- 遵循 PEP 8 规范（行长度 120 字符）
- 使用 Black 进行代码格式化
- 使用 Ruff 进行代码检查
- 所有注释必须使用中文

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html

# 运行特定测试文件
pytest tests/unit/test_xxx.py
```

### 代码检查

```bash
# 格式化代码
black .

# 代码检查
ruff check .

# 类型检查
mypy .
```

## API 文档

启动服务后访问：

- **Swagger UI**: `http://localhost:5000/api/docs`
- **ReDoc**: `http://localhost:5000/api/redoc`

## 许可证

MIT License
