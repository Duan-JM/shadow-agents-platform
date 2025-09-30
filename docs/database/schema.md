# 数据库设计文档

基于 PostgreSQL 15 + pgvector 的数据库设计。

## 概述

Shadow Agents Platform 使用 PostgreSQL 作为主数据库，存储应用、用户、工作流等核心数据。

### 技术选型

- **数据库**: PostgreSQL 15
- **扩展**: pgvector (向量搜索)
- **ORM**: SQLAlchemy 2.0.29
- **迁移工具**: Flask-Migrate (Alembic)

## 表结构设计

### 1. 用户和租户管理

#### accounts (用户表)

```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, banned
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounts_email ON accounts(email);
CREATE INDEX idx_accounts_status ON accounts(status);
```

#### tenants (租户表)

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    plan VARCHAR(20) DEFAULT 'free',  -- free, pro, enterprise
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### tenant_account_joins (租户-用户关联表)

```sql
CREATE TABLE tenant_account_joins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member',  -- owner, admin, member
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, account_id)
);

CREATE INDEX idx_tenant_account_tenant ON tenant_account_joins(tenant_id);
CREATE INDEX idx_tenant_account_account ON tenant_account_joins(account_id);
```

### 2. 应用管理

#### apps (应用表)

```sql
CREATE TABLE apps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    mode VARCHAR(20) NOT NULL,  -- chat, completion, agent, workflow
    icon VARCHAR(20) DEFAULT '🤖',
    icon_background VARCHAR(20) DEFAULT '#E0F2FE',
    enable_site BOOLEAN DEFAULT true,
    enable_api BOOLEAN DEFAULT true,
    status VARCHAR(20) DEFAULT 'normal',  -- normal, archived
    created_by UUID REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_apps_tenant ON apps(tenant_id);
CREATE INDEX idx_apps_mode ON apps(mode);
CREATE INDEX idx_apps_status ON apps(status);
```

#### app_model_configs (应用模型配置表)

```sql
CREATE TABLE app_model_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    app_id UUID NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,  -- openai, anthropic, etc.
    model VARCHAR(100) NOT NULL,
    configs JSONB NOT NULL,  -- 模型参数配置
    opening_statement TEXT,
    suggested_questions JSONB,  -- 建议问题列表
    pre_prompt TEXT,  -- 系统提示词
    user_input_form JSONB,  -- 用户输入表单配置
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_app_model_app ON app_model_configs(app_id);
```

### 3. 工作流管理

#### workflows (工作流表)

```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    app_id UUID NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    version VARCHAR(20) DEFAULT 'draft',
    graph JSONB NOT NULL,  -- 工作流图数据 (nodes, edges)
    features JSONB,  -- 功能特性配置
    created_by UUID REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflows_app ON workflows(app_id);
CREATE INDEX idx_workflows_tenant ON workflows(tenant_id);
CREATE INDEX idx_workflows_version ON workflows(version);
```

### 4. 知识库管理

#### datasets (知识库表)

```sql
CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    provider VARCHAR(50) DEFAULT 'vendor',  -- vendor, external
    permission VARCHAR(20) DEFAULT 'only_me',  -- only_me, all_team
    indexing_technique VARCHAR(20) DEFAULT 'high_quality',  -- economy, high_quality
    embedding_model VARCHAR(100),
    embedding_model_provider VARCHAR(50),
    data_source_type VARCHAR(50),
    created_by UUID REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_datasets_tenant ON datasets(tenant_id);
CREATE INDEX idx_datasets_permission ON datasets(permission);
```

#### documents (文档表)

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    data_source_type VARCHAR(50) NOT NULL,  -- upload_file, notion, web
    data_source_info JSONB,
    indexing_status VARCHAR(20) DEFAULT 'waiting',  -- waiting, parsing, cleaning, splitting, embedding, completed, error
    processing_started_at TIMESTAMP,
    parsing_completed_at TIMESTAMP,
    cleaning_completed_at TIMESTAMP,
    splitting_completed_at TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT,
    enabled BOOLEAN DEFAULT true,
    disabled_at TIMESTAMP,
    disabled_by UUID REFERENCES accounts(id),
    archived BOOLEAN DEFAULT false,
    archived_reason TEXT,
    archived_at TIMESTAMP,
    archived_by UUID REFERENCES accounts(id),
    created_by UUID REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_dataset ON documents(dataset_id);
CREATE INDEX idx_documents_tenant ON documents(tenant_id);
CREATE INDEX idx_documents_status ON documents(indexing_status);
CREATE INDEX idx_documents_enabled ON documents(enabled);
```

#### document_segments (文档片段表)

```sql
CREATE TABLE document_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    position INT NOT NULL,
    content TEXT NOT NULL,
    word_count INT DEFAULT 0,
    tokens INT DEFAULT 0,
    keywords JSONB,
    index_node_id VARCHAR(255),  -- 向量数据库中的节点 ID
    index_node_hash VARCHAR(255),
    hit_count INT DEFAULT 0,
    enabled BOOLEAN DEFAULT true,
    disabled_at TIMESTAMP,
    disabled_by UUID REFERENCES accounts(id),
    status VARCHAR(20) DEFAULT 'waiting',  -- waiting, indexing, completed, error
    indexing_at TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT,
    created_by UUID REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_segments_document ON document_segments(document_id);
CREATE INDEX idx_segments_dataset ON document_segments(dataset_id);
CREATE INDEX idx_segments_node ON document_segments(index_node_id);
CREATE INDEX idx_segments_status ON document_segments(status);
CREATE INDEX idx_segments_enabled ON document_segments(enabled);
```

### 5. 对话和消息

#### conversations (对话表)

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    app_id UUID NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'normal',  -- normal, archived
    from_source VARCHAR(50),  -- api, console
    from_end_user_id UUID,
    from_account_id UUID REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_app ON conversations(app_id);
CREATE INDEX idx_conversations_status ON conversations(status);
```

#### messages (消息表)

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    app_id UUID NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID,  -- 前端生成的消息 ID
    from_source VARCHAR(50),  -- api, console
    from_end_user_id UUID,
    from_account_id UUID REFERENCES accounts(id),
    query TEXT NOT NULL,
    answer TEXT,
    provider_response_latency FLOAT DEFAULT 0,
    message_tokens INT DEFAULT 0,
    message_unit_price DECIMAL(10, 7) DEFAULT 0,
    message_price_unit VARCHAR(10) DEFAULT 'USD',
    answer_tokens INT DEFAULT 0,
    answer_unit_price DECIMAL(10, 7) DEFAULT 0,
    answer_price_unit VARCHAR(10) DEFAULT 'USD',
    total_price DECIMAL(10, 7) DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'normal',  -- normal, stopped, error
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_app ON messages(app_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_from_source ON messages(from_source);
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_created ON messages(created_at DESC);
```

### 6. 模型提供商

#### providers (模型提供商表)

```sql
CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider_name VARCHAR(50) NOT NULL,  -- openai, anthropic, etc.
    provider_type VARCHAR(20) NOT NULL,  -- system, custom
    is_valid BOOLEAN DEFAULT false,
    quota_type VARCHAR(20),  -- trial, paid
    quota_limit INT,
    quota_used INT DEFAULT 0,
    encrypted_config TEXT,  -- 加密的配置信息（API Key 等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_providers_tenant ON providers(tenant_id);
CREATE INDEX idx_providers_name ON providers(provider_name);
```

## 数据关系图

```
tenants (租户)
  ├─→ apps (应用)
  │    ├─→ app_model_configs (模型配置)
  │    ├─→ workflows (工作流)
  │    ├─→ conversations (对话)
  │    └─→ messages (消息)
  ├─→ datasets (知识库)
  │    ├─→ documents (文档)
  │    └─→ document_segments (片段)
  ├─→ providers (模型提供商)
  └─→ tenant_account_joins (用户关联)
       └─→ accounts (用户)
```

## 索引策略

### 主要索引

1. **主键索引**: 所有表的 `id` 字段
2. **外键索引**: 所有外键字段
3. **状态索引**: `status` 字段
4. **时间索引**: `created_at` 字段（用于分页和排序）
5. **唯一索引**: `email`、租户-用户关联等

### 复合索引

对于频繁查询的组合条件，可以创建复合索引：

```sql
-- 应用查询：租户 + 状态
CREATE INDEX idx_apps_tenant_status ON apps(tenant_id, status);

-- 文档查询：知识库 + 启用状态
CREATE INDEX idx_documents_dataset_enabled ON documents(dataset_id, enabled);

-- 消息查询：对话 + 创建时间
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
```

## 分区策略

对于大表（如 messages），可以考虑分区：

```sql
-- 按月分区消息表
CREATE TABLE messages_2024_01 PARTITION OF messages
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE messages_2024_02 PARTITION OF messages
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

## 性能优化

### 1. 连接池配置

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 30,
    'max_overflow': 10,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
}
```

### 2. 查询优化

- 使用 `select_related` 和 `joinedload` 减少 N+1 查询
- 对大表使用分页和游标
- 定期清理归档数据

### 3. 缓存策略

- 使用 Redis 缓存热点数据
- 缓存模型配置和提供商信息
- 缓存用户会话和权限信息

## 数据迁移

使用 Flask-Migrate (Alembic) 管理数据库版本：

```bash
# 初始化迁移
flask db init

# 创建迁移
flask db migrate -m "Initial schema"

# 应用迁移
flask db upgrade

# 回滚
flask db downgrade
```

## 备份策略

### 1. 定期备份

```bash
# 每日备份
pg_dump -U postgres shadow_agents > backup_$(date +%Y%m%d).sql

# 压缩备份
pg_dump -U postgres shadow_agents | gzip > backup_$(date +%Y%m%d).sql.gz
```

### 2. 增量备份

使用 PostgreSQL 的 WAL 归档：

```sql
-- postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
```

### 3. 备份保留策略

- 每日备份保留 7 天
- 每周备份保留 4 周
- 每月备份保留 12 个月

## 安全考虑

1. **密码加密**: 使用 bcrypt 或 Argon2
2. **敏感数据加密**: API Key 等使用 AES-256 加密
3. **SQL 注入防护**: 使用 ORM 参数化查询
4. **权限控制**: 基于 RBAC 的多租户权限管理
5. **审计日志**: 记录关键操作日志

## 许可证

MIT License
