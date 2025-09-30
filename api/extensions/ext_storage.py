"""
存储扩展

文件存储抽象层
"""
import os
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from flask import Flask


class Storage(ABC):
    """存储抽象基类"""
    
    @abstractmethod
    def save(self, filename: str, data: BinaryIO) -> str:
        """保存文件"""
        pass
    
    @abstractmethod
    def load(self, filename: str) -> bytes:
        """加载文件"""
        pass
    
    @abstractmethod
    def delete(self, filename: str) -> bool:
        """删除文件"""
        pass
    
    @abstractmethod
    def exists(self, filename: str) -> bool:
        """检查文件是否存在"""
        pass


class LocalStorage(Storage):
    """本地文件存储"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save(self, filename: str, data: BinaryIO) -> str:
        """保存文件到本地"""
        filepath = os.path.join(self.base_path, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(data.read())
        
        return filepath
    
    def load(self, filename: str) -> bytes:
        """从本地加载文件"""
        filepath = os.path.join(self.base_path, filename)
        with open(filepath, 'rb') as f:
            return f.read()
    
    def delete(self, filename: str) -> bool:
        """删除本地文件"""
        filepath = os.path.join(self.base_path, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def exists(self, filename: str) -> bool:
        """检查本地文件是否存在"""
        filepath = os.path.join(self.base_path, filename)
        return os.path.exists(filepath)


class StorageManager:
    """存储管理器"""
    
    def __init__(self):
        self._storage: Optional[Storage] = None
    
    def init_app(self, app: Flask) -> None:
        """
        初始化存储
        
        参数:
            app: Flask 应用实例
        """
        storage_type = app.config.get('STORAGE_TYPE', 'local')
        
        if storage_type == 'local':
            base_path = app.config.get('STORAGE_LOCAL_PATH', 'storage')
            self._storage = LocalStorage(base_path)
        else:
            raise ValueError(f'Unsupported storage type: {storage_type}')
    
    @property
    def storage(self) -> Storage:
        """获取存储实例"""
        if self._storage is None:
            raise RuntimeError('Storage not initialized')
        return self._storage


# 创建全局实例
storage = StorageManager()
