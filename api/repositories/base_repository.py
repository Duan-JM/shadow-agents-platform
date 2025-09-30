"""
基础 Repository

提供通用的 CRUD 操作
"""
from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from extensions.ext_database import db

# 泛型类型变量
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    基础 Repository 类
    
    提供通用的数据库操作方法
    """
    
    def __init__(self, model: Type[T]):
        """
        初始化
        
        参数:
            model: 模型类
        """
        self.model = model
        self.session: Session = db.session
    
    def create(self, **kwargs) -> T:
        """
        创建记录
        
        参数:
            **kwargs: 模型字段和值
            
        返回:
            创建的模型实例
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance
    
    def get_by_id(self, id: UUID) -> Optional[T]:
        """
        根据 ID 获取记录
        
        参数:
            id: 记录 ID
            
        返回:
            模型实例或 None
        """
        return self.session.query(self.model).filter(
            self.model.id == id
        ).first()
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        获取所有记录
        
        参数:
            limit: 限制数量
            offset: 偏移量
            
        返回:
            模型实例列表
        """
        query = self.session.query(self.model)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def update(self, id: UUID, **kwargs) -> Optional[T]:
        """
        更新记录
        
        参数:
            id: 记录 ID
            **kwargs: 要更新的字段和值
            
        返回:
            更新后的模型实例或 None
        """
        instance = self.get_by_id(id)
        if not instance:
            return None
        
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        self.session.commit()
        self.session.refresh(instance)
        return instance
    
    def delete(self, id: UUID) -> bool:
        """
        删除记录
        
        参数:
            id: 记录 ID
            
        返回:
            是否删除成功
        """
        instance = self.get_by_id(id)
        if not instance:
            return False
        
        self.session.delete(instance)
        self.session.commit()
        return True
    
    def count(self) -> int:
        """
        统计记录数量
        
        返回:
            记录总数
        """
        return self.session.query(self.model).count()
    
    def exists(self, id: UUID) -> bool:
        """
        检查记录是否存在
        
        参数:
            id: 记录 ID
            
        返回:
            是否存在
        """
        return self.session.query(
            self.session.query(self.model).filter(
                self.model.id == id
            ).exists()
        ).scalar()
