"""
应用配置模块

从环境变量加载配置
"""
import os
from typing import Optional


class Config:
    """应用配置类"""
    
    # 基础配置
    ENV = os.getenv('ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_DATABASE = os.getenv('DB_DATABASE', 'shadow_agents')
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 30))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 10))
    
    # SQLAlchemy 配置
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """构建数据库连接 URI"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': DB_POOL_SIZE,
        'max_overflow': DB_MAX_OVERFLOW,
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
    
    # Redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    @property
    def REDIS_URL(self) -> str:
        """构建 Redis 连接 URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Celery 配置
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # 向量数据库配置
    VECTOR_STORE = os.getenv('VECTOR_STORE', 'milvus')
    MILVUS_URI = os.getenv('MILVUS_URI', 'http://localhost:19530')
    MILVUS_TOKEN = os.getenv('MILVUS_TOKEN', '')
    MILVUS_USER = os.getenv('MILVUS_USER', '')
    MILVUS_PASSWORD = os.getenv('MILVUS_PASSWORD', '')
    
    # 对象存储配置
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')
    STORAGE_LOCAL_PATH = os.getenv('STORAGE_LOCAL_PATH', 'storage')
    
    # OpenAI 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    
    # Anthropic 配置
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # CORS 配置
    CORS_ALLOW_ORIGINS = os.getenv('CORS_ALLOW_ORIGINS', 'http://localhost:3000').split(',')
    
    # JWT 配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'storage/uploads')
    
    # 应用信息
    APP_NAME = os.getenv('APP_NAME', 'Shadow Agents Platform')
    APP_VERSION = os.getenv('APP_VERSION', '0.1.0')
