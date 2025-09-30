# 部署指南

本文档提供 Shadow Agents Platform 的生产环境部署指南。

## 目录

- [部署架构](#部署架构)
- [Docker Compose 部署](#docker-compose-部署)
- [环境变量配置](#环境变量配置)
- [数据备份与恢复](#数据备份与恢复)
- [监控与日志](#监控与日志)
- [安全加固](#安全加固)
- [性能调优](#性能调优)
- [故障排查](#故障排查)

## 部署架构

### 推荐架构

```
Internet
   ↓
[Nginx/Load Balancer]
   ↓
[Web (Next.js)] ←→ [API (Flask)]
                       ↓
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
    [PostgreSQL]   [Redis]      [Milvus]
         ↓             ↓
    [Worker]       [Beat]
```

### 最小配置要求

- **CPU**: 4 核
- **内存**: 8GB
- **存储**: 50GB SSD
- **网络**: 10Mbps

### 推荐配置

- **CPU**: 8 核+
- **内存**: 16GB+
- **存储**: 100GB+ SSD
- **网络**: 100Mbps+

## Docker Compose 部署

### 1. 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 2. 克隆项目

```bash
cd /opt
sudo git clone https://github.com/your-org/shadow-agents-platform.git
cd shadow-agents-platform
```

### 3. 配置环境变量

```bash
cd docker
cp .env.example .env
sudo vim .env
```

必须配置的变量：
```bash
# 安全密钥（使用随机生成）
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 数据库密码
DB_PASSWORD=$(openssl rand -hex 16)

# Redis 密码
REDIS_PASSWORD=$(openssl rand -hex 16)

# OpenAI API Key
OPENAI_API_KEY=your-openai-api-key

# 域名配置（如果有）
DOMAIN=yourdomain.com
```

### 4. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 初始化数据库

```bash
# 等待服务启动
sleep 30

# 运行数据库迁移
docker-compose exec api flask db upgrade

# 创建超级管理员（可选）
docker-compose exec api python scripts/create_admin.py
```

### 6. 验证部署

访问以下地址：
- **Web 界面**: http://your-server-ip:3000
- **API 文档**: http://your-server-ip:5000/api/docs
- **健康检查**: http://your-server-ip/health

## 环境变量配置

### 核心配置

```bash
# 环境
ENV=production              # production / development
DEBUG=false                 # true / false

# 安全
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### 数据库配置

```bash
DB_HOST=postgres           # 数据库主机
DB_PORT=5432               # 数据库端口
DB_USER=postgres           # 数据库用户
DB_PASSWORD=strong-password # 数据库密码
DB_DATABASE=shadow_agents  # 数据库名称
```

### Redis 配置

```bash
REDIS_HOST=redis           # Redis 主机
REDIS_PORT=6379            # Redis 端口
REDIS_PASSWORD=password    # Redis 密码
REDIS_DB=0                 # Redis 数据库编号
```

### 向量数据库配置

```bash
VECTOR_STORE=milvus        # milvus
MILVUS_URI=http://milvus:19530
MILVUS_USER=               # Milvus 用户（可选）
MILVUS_PASSWORD=           # Milvus 密码（可选）
```

### AI 模型配置

```bash
# OpenAI
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic（可选）
ANTHROPIC_API_KEY=sk-ant-xxx
```

### 日志配置

```bash
LOG_LEVEL=INFO             # DEBUG / INFO / WARNING / ERROR
LOG_FILE=logs/app.log      # 日志文件路径
```

## 数据备份与恢复

### 自动备份脚本

创建 `/opt/shadow-agents-platform/scripts/backup.sh`:

```bash
#!/bin/bash

# 备份目录
BACKUP_DIR="/opt/backups/shadow-agents"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份 PostgreSQL
docker-compose exec -T postgres pg_dump -U postgres shadow_agents | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 备份文件存储
docker run --rm -v shadow-agents_api_storage:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/storage_$DATE.tar.gz /data

# 保留最近 7 天的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

设置定时任务：

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点备份
0 2 * * * /opt/shadow-agents-platform/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### 数据恢复

```bash
# 恢复数据库
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U postgres shadow_agents

# 恢复文件
docker run --rm -v shadow-agents_api_storage:/data -v $(pwd):/backup alpine tar xzf /backup/storage_backup.tar.gz -C /
```

## 监控与日志

### 日志管理

#### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f api
docker-compose logs -f web

# 查看最近 100 行
docker-compose logs --tail=100 api

# 查看特定时间范围
docker-compose logs --since 2024-01-01T00:00:00 api
```

#### 日志轮转

创建 `/etc/logrotate.d/shadow-agents`:

```
/opt/shadow-agents-platform/docker/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}
```

### 监控指标

#### 系统监控

```bash
# CPU 和内存使用
docker stats

# 磁盘使用
df -h
docker system df

# 网络连接
netstat -tunlp | grep -E '(3000|5000|5432|6379|19530)'
```

#### 应用监控

推荐集成以下工具：

1. **Prometheus + Grafana** - 指标监控
2. **Sentry** - 错误追踪
3. **ELK Stack** - 日志分析

## 安全加固

### 1. 使用 HTTPS

#### 安装 Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### Nginx HTTPS 配置

修改 `docker/nginx/conf.d/default.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... 其他配置
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 2. 防火墙配置

```bash
# 使用 ufw
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable

# 或使用 iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### 3. 限流配置

在 Nginx 中添加限流：

```nginx
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            # ... 其他配置
        }
    }
}
```

### 4. 密钥管理

使用 Docker Secrets 或外部密钥管理服务（如 AWS Secrets Manager、HashiCorp Vault）。

```yaml
# docker-compose.yml
services:
  api:
    secrets:
      - db_password
      - openai_api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  openai_api_key:
    file: ./secrets/openai_api_key.txt
```

## 性能调优

### 1. 数据库优化

#### PostgreSQL 配置

编辑 PostgreSQL 配置：

```sql
-- 连接数
max_connections = 100

-- 内存配置
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 16MB
maintenance_work_mem = 512MB

-- 查询优化
random_page_cost = 1.1  # SSD
effective_io_concurrency = 200
```

#### 索引优化

```sql
-- 查找缺少索引的表
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- 查找未使用的索引
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public';
```

### 2. Redis 优化

```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### 3. API 优化

#### Gunicorn Worker 配置

```python
# gunicorn.conf.py
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
max_requests = 10000
```

#### 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_model_config(model_id: str):
    """缓存模型配置"""
    return db.session.query(ModelConfig).filter_by(id=model_id).first()
```

### 4. 前端优化

#### Next.js 配置

```javascript
// next.config.js
module.exports = {
  // 启用压缩
  compress: true,
  
  // 图片优化
  images: {
    formats: ['image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
  },
  
  // 开启 SWC 压缩
  swcMinify: true,
}
```

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 查看详细日志
docker-compose logs [service_name]

# 检查端口占用
sudo lsof -i :5000
sudo lsof -i :3000

# 检查资源使用
docker stats
```

#### 2. 数据库连接失败

```bash
# 检查数据库是否就绪
docker-compose exec postgres pg_isready -U postgres

# 测试连接
docker-compose exec postgres psql -U postgres -d shadow_agents

# 检查连接数
docker-compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

#### 3. 内存不足

```bash
# 查看内存使用
free -h
docker stats

# 增加 swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. 磁盘空间不足

```bash
# 查看磁盘使用
df -h
docker system df

# 清理 Docker
docker system prune -a --volumes
docker image prune -a
```

### 健康检查

创建健康检查脚本 `scripts/health_check.sh`:

```bash
#!/bin/bash

# 检查 API
if ! curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "API health check failed"
    docker-compose restart api
fi

# 检查 Web
if ! curl -f http://localhost:3000/ > /dev/null 2>&1; then
    echo "Web health check failed"
    docker-compose restart web
fi

# 检查数据库
if ! docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "Database health check failed"
    docker-compose restart postgres
fi
```

定时运行：

```bash
*/5 * * * * /opt/shadow-agents-platform/scripts/health_check.sh >> /var/log/health_check.log 2>&1
```

## 更新和维护

### 滚动更新

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 滚动更新（零停机）
docker-compose up -d --no-deps --build api
docker-compose up -d --no-deps --build web

# 运行数据库迁移
docker-compose exec api flask db upgrade
```

### 版本回滚

```bash
# 回滚到上一个版本
git checkout tags/v1.0.0
docker-compose down
docker-compose up -d --build

# 数据库回滚
docker-compose exec api flask db downgrade
```

## 许可证

MIT License
