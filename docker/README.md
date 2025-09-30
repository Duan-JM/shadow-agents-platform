# Shadow Agents Platform - Docker 部署

使用 Docker Compose 快速部署完整的 Shadow Agents Platform。

## 服务架构

```
┌─────────────────────────────────────────────────┐
│                    Nginx (80)                   │
│            (反向代理 & 负载均衡)                  │
└──────────────┬──────────────┬──────────────────┘
               │              │
       ┌───────┴──────┐  ┌────┴─────┐
       │ Web (3000)   │  │ API (5000)│
       │  Next.js     │  │  Flask    │
       └──────────────┘  └─────┬─────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
         ┌────┴────┐     ┌────┴────┐    ┌──────┴──────┐
         │ Worker  │     │  Beat   │    │   Storage   │
         │ Celery  │     │ Celery  │    │   (local)   │
         └─────────┘     └─────────┘    └─────────────┘
              │                │
         ┌────┴────────────────┴─────┐
         │                            │
    ┌────┴─────┐  ┌────────┐  ┌──────┴──────┐
    │PostgreSQL│  │ Redis  │  │   Milvus    │
    │   (5432) │  │ (6379) │  │   (19530)   │
    └──────────┘  └────────┘  └─────────────┘
```

## 快速开始

### 1. 配置环境变量

```bash
cd docker
cp .env.example .env
vim .env  # 编辑配置
```

必须配置的环境变量：
- `SECRET_KEY`: 应用密钥（随机生成）
- `JWT_SECRET_KEY`: JWT 密钥（随机生成）
- `OPENAI_API_KEY`: OpenAI API Key

### 2. 启动所有服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务的日志
docker-compose logs -f api
docker-compose logs -f web
```

### 3. 初始化数据库

```bash
# 进入 API 容器
docker-compose exec api bash

# 运行数据库迁移
flask db upgrade

# 退出容器
exit
```

### 4. 访问应用

- **Web 界面**: http://localhost:3000
- **API 文档**: http://localhost:5000/api/docs
- **Nginx 入口**: http://localhost

## 服务说明

### 核心服务

- **nginx**: 反向代理，统一入口
- **web**: Next.js 前端应用
- **api**: Flask API 服务
- **worker**: Celery 异步任务处理
- **beat**: Celery 定时任务调度

### 数据服务

- **postgres**: PostgreSQL 15 + pgvector
- **redis**: Redis 7 缓存和消息队列
- **milvus**: Milvus 2.4 向量数据库
  - **milvus-etcd**: Milvus 元数据存储
  - **milvus-minio**: Milvus 对象存储

## 常用命令

### 启动和停止

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除数据卷（危险操作！）
docker-compose down -v

# 重启服务
docker-compose restart

# 重启特定服务
docker-compose restart api
```

### 查看状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看资源使用
docker stats

# 查看日志
docker-compose logs -f [service_name]
```

### 构建和更新

```bash
# 重新构建镜像
docker-compose build

# 重新构建特定服务
docker-compose build api

# 拉取最新镜像
docker-compose pull

# 更新并重启服务
docker-compose up -d --build
```

### 数据库操作

```bash
# 进入 PostgreSQL
docker-compose exec postgres psql -U postgres -d shadow_agents

# 备份数据库
docker-compose exec postgres pg_dump -U postgres shadow_agents > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U postgres shadow_agents < backup.sql

# 查看 Redis
docker-compose exec redis redis-cli
```

### 清理和维护

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的数据卷
docker volume prune

# 清理所有（危险！）
docker system prune -a --volumes
```

## 配置文件

### docker-compose.yml
主配置文件，定义所有服务。

### .env
环境变量配置文件。

### nginx/
Nginx 配置文件目录：
- `nginx.conf`: 主配置
- `conf.d/default.conf`: 站点配置

### postgres/
PostgreSQL 配置：
- `init.sql`: 初始化脚本

### redis/
Redis 配置：
- `redis.conf`: Redis 配置文件

## 数据持久化

数据卷：
- `postgres_data`: PostgreSQL 数据
- `redis_data`: Redis 数据
- `milvus_data`: Milvus 数据
- `milvus_etcd_data`: Milvus etcd 数据
- `milvus_minio_data`: Milvus MinIO 数据
- `api_storage`: API 文件存储
- `api_logs`: API 日志

备份数据：
```bash
# 备份所有数据卷
docker run --rm -v shadow-agents_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz /data
```

## 性能优化

### 1. 调整 Worker 数量

编辑 `docker-compose.yml`:
```yaml
worker:
  command: celery -A celery_app worker --loglevel=info -c 8  # 增加并发数
```

### 2. 配置资源限制

```yaml
api:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G
```

### 3. 使用外部数据库

如果你有独立的数据库服务，可以修改 `docker-compose.yml` 中的数据库连接配置。

## 监控和日志

### 查看实时日志

```bash
# 所有服务
docker-compose logs -f

# 只看错误
docker-compose logs -f | grep ERROR

# 特定时间范围
docker-compose logs --since 30m
docker-compose logs --since 2024-01-01T00:00:00
```

### 日志文件位置

- API 日志: `api_logs` 数据卷
- Nginx 日志: `/var/log/nginx/` (容器内)

## 故障排查

### 服务无法启动

```bash
# 查看详细错误
docker-compose logs [service_name]

# 检查端口占用
lsof -i :5000
lsof -i :3000

# 检查容器状态
docker-compose ps
```

### 数据库连接失败

```bash
# 检查数据库是否就绪
docker-compose exec postgres pg_isready -U postgres

# 测试连接
docker-compose exec api python -c "from extensions.ext_database import db; print(db)"
```

### 性能问题

```bash
# 查看资源使用
docker stats

# 检查日志
docker-compose logs -f | grep -i "slow\|error\|timeout"
```

## 生产环境建议

1. **使用 HTTPS**: 配置 SSL 证书
2. **数据备份**: 定期备份数据库和文件
3. **监控告警**: 集成 Prometheus + Grafana
4. **日志收集**: 使用 ELK 或 Loki
5. **密钥管理**: 使用 Docker Secrets 或外部密钥管理服务
6. **资源限制**: 为所有服务配置资源限制
7. **健康检查**: 配置合适的健康检查策略

## 许可证

MIT License
