# Dify 系统架构分析

## 整体架构概览

Dify 采用经典的前后端分离架构，基于微服务理念设计，主要包含以下核心组件：

```
┌─────────────────────────────────────────────────────────────┐
│                         用户层                               │
│                      (浏览器/客户端)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS/HTTP
                     │
┌────────────────────▼────────────────────────────────────────┐
│                      Nginx (反向代理)                         │
│              负责路由、负载均衡、SSL终结                      │
└────────┬──────────────────────────────────┬─────────────────┘
         │                                  │
         │                                  │
┌────────▼──────────┐              ┌───────▼──────────────────┐
│   Web Frontend    │              │      API Backend         │
│   (Next.js 15)    │              │   (Flask + Python 3.11)  │
│                   │              │                          │
│  - React 19       │              │  - API 服务 (Gunicorn)   │
│  - TypeScript     │              │  - Worker (Celery)       │
│  - Tailwind CSS   │              │  - Beat (定时任务)       │
└───────────────────┘              └──────────┬───────────────┘
                                              │
                     ┌────────────────────────┼────────────┐
                     │                        │            │
         ┌───────────▼─────────┐   ┌─────────▼─────┐  ┌──▼────────────┐
         │  PostgreSQL 15      │   │  Redis 6      │  │  Sandbox      │
         │  (主数据库)         │   │  (缓存/队列)  │  │  (代码执行)   │
         └─────────────────────┘   └───────────────┘  └───────────────┘
                     │
         ┌───────────▼─────────────────────┐
         │  Vector Database (可选)          │
         │  - Milvus (推荐)                │
         │  - Qdrant / Weaviate / Chroma  │
         │  - PGVector                     │
         └─────────────────────────────────┘
                     │
         ┌───────────▼─────────────────────┐
         │  Object Storage (可选)           │
         │  - Local FS (本地文件系统)       │
         │  - S3 / MinIO                   │
         │  - Azure Blob / Aliyun OSS      │
         └─────────────────────────────────┘
```

## 核心服务说明

### 1. **API 服务** (api)
- **镜像**: `langgenius/dify-api:1.9.1`
- **技术栈**: Flask 3.1.2 + Gunicorn + Gevent
- **职责**:
  - 提供 RESTful API 接口
  - 处理用户请求（认证、应用管理、工作流执行等）
  - 调用 AI 模型
  - 管理知识库和文档
- **端口**: 5001 (内部)
- **依赖**: PostgreSQL, Redis

### 2. **Worker 服务** (worker)
- **镜像**: `langgenius/dify-api:1.9.1` (同 API，不同启动模式)
- **技术栈**: Celery + Redis
- **职责**:
  - 异步任务处理
  - 文档索引和向量化
  - 批量操作
  - 邮件发送
- **依赖**: PostgreSQL, Redis

### 3. **Beat 服务** (worker_beat)
- **镜像**: `langgenius/dify-api:1.9.1`
- **技术栈**: Celery Beat
- **职责**:
  - 定时任务调度
  - 数据清理
  - 状态同步
- **依赖**: PostgreSQL, Redis

### 4. **Web 前端** (web)
- **镜像**: `langgenius/dify-web:1.9.1`
- **技术栈**: Next.js 15 + React 19 + TypeScript
- **职责**:
  - 用户界面展示
  - 交互逻辑处理
  - 服务端渲染 (SSR)
- **端口**: 3000 (内部)

### 5. **Plugin Daemon** (plugin_daemon)
- **镜像**: `langgenius/dify-plugin-daemon:0.3.0-local`
- **职责**:
  - 插件管理和执行
  - 插件隔离运行环境
- **端口**: 5002 (内部)

### 6. **Sandbox** (sandbox)
- **镜像**: `langgenius/dify-sandbox:0.2.12`
- **技术栈**: Go
- **职责**:
  - 安全的代码执行环境
  - Python/JavaScript 代码隔离执行
- **端口**: 8194 (内部)
- **网络**: ssrf_proxy_network (通过代理访问外部网络)

### 7. **PostgreSQL** (db)
- **镜像**: `postgres:15-alpine`
- **职责**:
  - 主数据存储
  - 存储用户、应用、工作流、消息等数据
- **端口**: 5432 (内部)
- **持久化**: `./volumes/db/data`

### 8. **Redis** (redis)
- **镜像**: `redis:6-alpine`
- **职责**:
  - 缓存层
  - Celery 消息队列
  - Session 存储
- **端口**: 6379 (内部)
- **持久化**: `./volumes/redis/data`

### 9. **Nginx** (nginx)
- **职责**:
  - 反向代理
  - 负载均衡
  - SSL 终结
  - 静态资源服务
- **端口**: 80 (HTTP), 443 (HTTPS)

### 10. **SSRF Proxy** (ssrf_proxy)
- **职责**:
  - 防止 SSRF 攻击
  - 控制外部网络访问
  - 代理 HTTP/HTTPS 请求
- **端口**: 3128 (内部)

## 数据流转

### 用户请求流程
```
用户浏览器 
  → Nginx (反向代理) 
  → Web Frontend (UI 渲染) 
  → API Backend (业务逻辑) 
  → PostgreSQL (数据持久化)
  → Redis (缓存)
```

### 异步任务流程
```
API Backend (创建任务)
  → Redis (任务队列)
  → Worker (执行任务)
  → PostgreSQL (结果存储)
  → Vector DB (向量存储)
```

### 工作流执行流程
```
用户触发 
  → API (工作流调度) 
  → Workflow Engine (节点执行)
  → LLM Provider (模型调用)
  → Vector DB (知识检索)
  → Sandbox (代码执行)
  → PostgreSQL (执行记录)
```

## 网络架构

### 网络划分
1. **default network**: 默认网络，所有服务互联
2. **ssrf_proxy_network**: SSRF 防护网络，限制外部访问

### 端口映射
- **80**: Nginx HTTP (外部访问)
- **443**: Nginx HTTPS (外部访问)
- **5002**: Plugin Daemon (可选外部访问)
- **5003**: Plugin Debug (开发模式)

## 存储架构

### 1. 关系型数据库 (PostgreSQL)
- **用途**: 主数据存储
- **存储内容**:
  - 用户账户和权限
  - 应用配置
  - 工作流定义
  - 对话历史
  - 知识库元数据
  - 执行日志

### 2. 缓存数据库 (Redis)
- **用途**: 缓存和消息队列
- **存储内容**:
  - Session 数据
  - API 限流数据
  - Celery 任务队列
  - 临时缓存

### 3. 向量数据库 (可选多种)
- **推荐**: Milvus
- **替代方案**: Qdrant, Weaviate, Chroma, PGVector
- **用途**: 向量检索
- **存储内容**:
  - 文档向量
  - Embedding 数据
  - 知识库索引

### 4. 对象存储 (可选)
- **默认**: 本地文件系统
- **云存储**: S3, Azure Blob, Aliyun OSS, Google Cloud Storage
- **用途**: 文件存储
- **存储内容**:
  - 用户上传文件
  - 生成的图片/文件
  - 导出数据

## 扩展性设计

### 水平扩展
1. **API 服务**: 可多实例部署，通过 Nginx 负载均衡
2. **Worker 服务**: 可多实例部署，共享 Redis 队列
3. **数据库**: 支持主从复制、读写分离
4. **向量数据库**: 支持分片和副本

### 高可用设计
1. **服务重启策略**: `restart: always`
2. **健康检查**: PostgreSQL, Redis 均配置健康检查
3. **数据持久化**: 所有数据目录挂载到宿主机
4. **故障恢复**: Celery 任务支持重试机制

## 安全机制

### 1. 认证授权
- JWT Token 认证
- API Key 管理
- OAuth 集成支持

### 2. 网络隔离
- SSRF Proxy 防护
- 内部网络隔离
- Sandbox 环境隔离

### 3. 数据安全
- 敏感信息加密
- 密钥管理 (SECRET_KEY)
- 数据库密码保护

### 4. 代码安全
- Sandbox 代码执行隔离
- 网络访问控制
- 资源限制

## 监控和日志

### 日志管理
- **位置**: `/app/logs/` (容器内)
- **格式**: 可配置
- **级别**: INFO (可配置为 DEBUG)
- **轮转**: 最大 20MB, 保留 5 个文件

### 监控集成
- **Sentry**: 错误追踪和性能监控
- **OpenTelemetry**: 可选的链路追踪
- **健康检查**: PostgreSQL, Redis 配置探活

## 配置管理

### 环境变量
- 所有配置通过环境变量管理
- 支持 `.env` 文件
- 共享配置 (`x-shared-env`)

### 关键配置项
- `SECRET_KEY`: 应用密钥 (必须修改)
- `DB_*`: 数据库配置
- `REDIS_*`: Redis 配置
- `VECTOR_STORE`: 向量数据库选择
- `STORAGE_TYPE`: 对象存储类型

## 部署模式

### 1. 单机部署 (Docker Compose)
- **适用场景**: 开发、测试、小规模生产
- **优点**: 部署简单，资源占用少
- **缺点**: 扩展性有限

### 2. 集群部署 (推荐生产环境)
- **适用场景**: 大规模生产环境
- **方案**: Kubernetes + Helm
- **优点**: 高可用、易扩展、自动恢复

## 性能优化

### 1. API 层
- Gunicorn + Gevent 异步处理
- 连接池优化 (SQLAlchemy)
- Redis 缓存策略

### 2. 数据库层
- PostgreSQL 连接池配置
- 索引优化
- 查询优化

### 3. 向量检索
- 索引优化
- 批量查询
- 缓存热门查询

## 技术选型总结

| 组件 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| 后端框架 | Flask | 3.1.2 | 轻量级 Web 框架 |
| 异步任务 | Celery | 5.5.2 | 分布式任务队列 |
| Web 服务器 | Gunicorn | 23.0.0 | WSGI HTTP 服务器 |
| 异步模型 | Gevent | 25.9.1 | 协程库 |
| 数据库 | PostgreSQL | 15 | 关系型数据库 |
| ORM | SQLAlchemy | 2.0.29 | Python ORM |
| 缓存 | Redis | 6 | 内存数据库 |
| 前端框架 | Next.js | 15.5.0 | React SSR 框架 |
| UI 库 | React | 19.1.1 | 前端框架 |
| 类型系统 | TypeScript | - | 静态类型 |
| 样式 | Tailwind CSS | - | 实用优先的 CSS |
| 反向代理 | Nginx | - | 高性能 Web 服务器 |
| 向量数据库 | Milvus (推荐) | - | 向量检索引擎 |
| 代码沙箱 | Go | - | 安全执行环境 |

---

**文档版本**: v1.0  
**最后更新**: 2025-09-30  
**基于 Dify 版本**: 1.9.1
