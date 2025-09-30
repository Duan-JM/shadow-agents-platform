# 开发指南

本文档提供 Shadow Agents Platform 的本地开发环境搭建和开发规范。

## 目录

- [环境要求](#环境要求)
- [本地开发设置](#本地开发设置)
- [开发规范](#开发规范)
- [测试](#测试)
- [调试](#调试)
- [常见问题](#常见问题)

## 环境要求

### 必需软件

- **Node.js**: >= 20.0.0
- **Python**: >= 3.11
- **PostgreSQL**: >= 15
- **Redis**: >= 6
- **Docker**: >= 20.10 (可选，用于 Milvus)

### 推荐工具

- **IDE**: VS Code / PyCharm / WebStorm
- **包管理**: pnpm (前端) / pip (后端)
- **Git**: >= 2.30

## 本地开发设置

### 1. 克隆项目

```bash
git clone https://github.com/your-org/shadow-agents-platform.git
cd shadow-agents-platform
```

### 2. 后端设置

#### 2.1 创建虚拟环境

```bash
cd api
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

#### 2.2 安装依赖

```bash
pip install -e .
```

#### 2.3 配置环境变量

```bash
cp .env.example .env
vim .env
```

必须配置的环境变量：
- `SECRET_KEY`: 应用密钥
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_DATABASE`: 数据库连接
- `REDIS_HOST`, `REDIS_PORT`: Redis 连接
- `OPENAI_API_KEY`: OpenAI API Key

#### 2.4 初始化数据库

```bash
# 创建数据库
createdb shadow_agents

# 运行迁移
flask db upgrade
```

#### 2.5 启动服务

```bash
# 启动 API
python app.py

# 启动 Celery Worker（新终端）
celery -A celery_app worker --loglevel=info

# 启动 Celery Beat（新终端）
celery -A celery_app beat --loglevel=info
```

API 将运行在 http://localhost:5000

### 3. 前端设置

#### 3.1 安装依赖

```bash
cd web
pnpm install
# 或 npm install
```

#### 3.2 配置环境变量

```bash
cp .env.example .env.local
vim .env.local
```

配置 API 地址：
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

#### 3.3 启动开发服务器

```bash
pnpm dev
# 或 npm run dev
```

前端将运行在 http://localhost:3000

### 4. 向量数据库（可选）

如果需要使用 RAG 功能，需要启动 Milvus：

```bash
# 使用 Docker Compose 启动 Milvus
cd docker
docker-compose up -d milvus-etcd milvus-minio milvus
```

Milvus 将运行在 http://localhost:19530

## 开发规范

### 代码风格

#### Python (后端)

- 遵循 PEP 8 规范
- 行长度：120 字符
- 使用 Black 格式化代码
- 使用 Ruff 进行 Linting
- 所有注释使用中文

格式化命令：
```bash
cd api
black .
ruff check .
```

示例：
```python
def get_user_by_id(user_id: str) -> Optional[User]:
    """
    根据 ID 获取用户
    
    参数:
        user_id: 用户 ID
        
    返回:
        用户对象，不存在则返回 None
    """
    return db.session.query(User).filter(User.id == user_id).first()
```

#### TypeScript (前端)

- 2 空格缩进
- 使用单引号
- 不使用分号
- 使用 Prettier 格式化
- 所有注释使用中文

格式化命令：
```bash
cd web
pnpm format
```

示例：
```typescript
/**
 * 获取用户信息
 * 
 * @param userId - 用户 ID
 * @returns 用户对象
 */
export async function getUser(userId: string): Promise<User> {
  const { data } = await http.get<User>(`/api/users/${userId}`)
  return data
}
```

### Git 规范

#### Commit Message

使用约定式提交（Conventional Commits）：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型（type）：
- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链相关

示例：
```
feat(api): 添加用户认证功能

- 实现 JWT 认证
- 添加登录和注册接口
- 增加权限验证中间件

Closes #123
```

#### 分支管理

- `main`: 主分支，始终保持可部署状态
- `develop`: 开发分支
- `feature/*`: 功能分支
- `fix/*`: 修复分支
- `release/*`: 发布分支

工作流程：
```bash
# 创建功能分支
git checkout -b feature/user-auth

# 开发完成后提交
git add .
git commit -m "feat(auth): 添加用户认证"

# 推送到远程
git push origin feature/user-auth

# 创建 Pull Request
```

### API 设计规范

#### RESTful API

- 使用名词复数形式
- 使用 HTTP 动词表示操作
- 使用合适的状态码

示例：
```
GET    /api/apps           # 获取应用列表
GET    /api/apps/:id       # 获取单个应用
POST   /api/apps           # 创建应用
PUT    /api/apps/:id       # 更新应用
DELETE /api/apps/:id       # 删除应用
```

#### 响应格式

成功响应：
```json
{
  "data": {
    "id": "123",
    "name": "My App"
  }
}
```

错误响应：
```json
{
  "error": "BadRequestError",
  "message": "Invalid parameters",
  "data": {
    "field": "email",
    "issue": "Email format is invalid"
  }
}
```

### 数据库规范

#### 模型定义

```python
from extensions.ext_database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
```

#### 迁移文件

```bash
# 创建迁移
flask db migrate -m "Add user table"

# 应用迁移
flask db upgrade

# 回滚
flask db downgrade
```

## 测试

### 后端测试

#### 单元测试

```python
import pytest
from app_factory import create_app

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

def test_login(client):
    """测试登录接口"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json['data']
```

运行测试：
```bash
cd api
pytest
pytest --cov=. --cov-report=html
```

### 前端测试

```typescript
import { render, screen } from '@testing-library/react'
import LoginPage from '@/app/(auth)/login/page'

describe('LoginPage', () => {
  it('renders login form', () => {
    render(<LoginPage />)
    expect(screen.getByText('登录')).toBeInTheDocument()
    expect(screen.getByLabelText('邮箱')).toBeInTheDocument()
  })
})
```

运行测试：
```bash
cd web
pnpm test
```

## 调试

### 后端调试

#### VS Code 配置

创建 `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "app.py",
        "FLASK_DEBUG": "1"
      },
      "args": ["run", "--no-debugger", "--no-reload"],
      "jinja": true
    }
  ]
}
```

#### 日志调试

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f'User {user_id} logged in')
logger.error(f'Failed to process: {error}')
```

### 前端调试

#### React DevTools

安装浏览器扩展：
- [React Developer Tools](https://react.dev/learn/react-developer-tools)

#### VS Code 调试

创建 `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run dev"
    }
  ]
}
```

## 常见问题

### 数据库连接失败

检查 PostgreSQL 是否运行：
```bash
pg_isready -h localhost -p 5432
```

检查配置：
```bash
psql -h localhost -U postgres -d shadow_agents
```

### Redis 连接失败

检查 Redis 是否运行：
```bash
redis-cli ping
```

### 端口被占用

查找占用进程：
```bash
lsof -i :5000  # API 端口
lsof -i :3000  # Web 端口
```

杀死进程：
```bash
kill -9 <PID>
```

### 依赖安装失败

清理缓存后重试：
```bash
# Python
pip cache purge
pip install -e .

# Node.js
rm -rf node_modules package-lock.json
npm install
```

## 性能优化

### 后端优化

1. **数据库查询优化**
   - 使用索引
   - 避免 N+1 查询
   - 使用分页

2. **缓存策略**
   - Redis 缓存热点数据
   - 缓存配置信息

3. **异步任务**
   - 使用 Celery 处理耗时任务

### 前端优化

1. **代码分割**
   - 使用动态导入
   - 路由级别分割

2. **图片优化**
   - 使用 Next.js Image 组件
   - WebP 格式

3. **缓存策略**
   - SWR 缓存策略
   - 静态资源 CDN

## 贡献指南

请参考 [CONTRIBUTING.md](../../CONTRIBUTING.md)

## 许可证

MIT License
