"""
Redis 扩展

初始化 Redis 客户端
"""
from typing import Any, Optional
from flask import Flask
import redis


class RedisClient:
    """Redis 客户端包装类"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    def init_app(self, app: Flask) -> None:
        """
        初始化 Redis 连接
        
        参数:
            app: Flask 应用实例
        """
        redis_config = {
            'host': app.config['REDIS_HOST'],
            'port': app.config['REDIS_PORT'],
            'db': app.config['REDIS_DB'],
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_keepalive': True,
        }
        
        if app.config['REDIS_PASSWORD']:
            redis_config['password'] = app.config['REDIS_PASSWORD']
        
        self._client = redis.Redis(**redis_config)
    
    @property
    def client(self) -> redis.Redis:
        """获取 Redis 客户端实例"""
        if self._client is None:
            raise RuntimeError('Redis client not initialized')
        return self._client
    
    def get(self, key: str) -> Optional[str]:
        """获取键值"""
        return self.client.get(key)
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """设置键值"""
        return self.client.set(key, value, ex=ex)
    
    def delete(self, *keys: str) -> int:
        """删除键"""
        return self.client.delete(*keys)
    
    def exists(self, *keys: str) -> int:
        """检查键是否存在"""
        return self.client.exists(*keys)


# 创建全局实例
redis_client = RedisClient()
