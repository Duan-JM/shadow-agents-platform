-- Shadow Agents Platform 数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建数据库（如果不存在）
-- 注意：这个脚本在数据库已存在时会跳过

-- 创建基础表结构会在后续通过 Flask-Migrate 创建
