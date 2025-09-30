"""
用户账户模型

用户认证和账户管理的核心模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import enum

from extensions.ext_database import db


class AccountStatus(enum.Enum):
    """账户状态枚举"""
    ACTIVE = "active"          # 激活
    INACTIVE = "inactive"      # 未激活
    BANNED = "banned"          # 封禁


class Account(db.Model):
    """
    用户账户模型
    
    管理用户的基本信息、认证凭据和状态
    """
    __tablename__ = 'accounts'
    
    # 主键
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="用户 ID"
    )
    
    # 认证信息
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="邮箱地址"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希"
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="用户名"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="头像 URL"
    )
    
    # 状态
    status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus),
        default=AccountStatus.ACTIVE,
        nullable=False,
        index=True,
        comment="账户状态"
    )
    
    # 登录信息
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
    )
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="最后登录 IP"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )
    
    # 关系
    tenant_joins = relationship(
        "TenantAccountJoin",
        back_populates="account",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<Account {self.email}>"
    
    def to_dict(self) -> dict:
        """
        转换为字典
        
        返回:
            用户信息字典（不包含敏感信息）
        """
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "avatar": self.avatar,
            "status": self.status.value,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @property
    def is_active(self) -> bool:
        """是否为激活状态"""
        return self.status == AccountStatus.ACTIVE
    
    @property
    def is_banned(self) -> bool:
        """是否被封禁"""
        return self.status == AccountStatus.BANNED
