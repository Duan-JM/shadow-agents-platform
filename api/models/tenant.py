"""
租户模型

多租户系统的租户管理
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions.ext_database import db


class TenantPlan(enum.Enum):
    """租户套餐类型"""

    FREE = "free"  # 免费版
    PRO = "pro"  # 专业版
    ENTERPRISE = "enterprise"  # 企业版


class TenantStatus(enum.Enum):
    """租户状态"""

    ACTIVE = "active"  # 激活
    SUSPENDED = "suspended"  # 暂停
    DELETED = "deleted"  # 已删除


class Tenant(db.Model):
    """
    租户模型

    管理租户的基本信息、套餐和状态
    """

    __tablename__ = "tenants"

    # 主键
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="租户 ID")

    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="租户名称")

    # 套餐信息
    plan: Mapped[TenantPlan] = mapped_column(
        SQLEnum(TenantPlan), default=TenantPlan.FREE, nullable=False, comment="套餐类型"
    )

    # 状态
    status: Mapped[TenantStatus] = mapped_column(
        SQLEnum(TenantStatus), default=TenantStatus.ACTIVE, nullable=False, index=True, comment="租户状态"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间"
    )

    # 关系
    account_joins = relationship("TenantAccountJoin", back_populates="tenant", cascade="all, delete-orphan")
    apps = relationship("App", back_populates="tenant", cascade="all, delete-orphan")
    model_providers = relationship("ModelProvider", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<Tenant {self.name}>"

    def to_dict(self) -> dict:
        """
        转换为字典

        返回:
            租户信息字典
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "plan": self.plan.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @property
    def is_active(self) -> bool:
        """是否为激活状态"""
        return self.status == TenantStatus.ACTIVE


class TenantRole(enum.Enum):
    """租户成员角色"""

    OWNER = "owner"  # 所有者
    ADMIN = "admin"  # 管理员
    MEMBER = "member"  # 普通成员


class TenantAccountJoin(db.Model):
    """
    租户-用户关联模型

    管理用户在租户中的角色和权限
    """

    __tablename__ = "tenant_account_joins"

    # 主键
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="关联 ID")

    # 外键
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="租户 ID",
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户 ID",
    )

    # 角色
    role: Mapped[TenantRole] = mapped_column(
        SQLEnum(TenantRole), default=TenantRole.MEMBER, nullable=False, comment="角色"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, comment="加入时间")

    # 关系
    tenant = relationship("Tenant", back_populates="account_joins")
    account = relationship("Account", back_populates="tenant_joins")

    # 唯一约束
    __table_args__ = (db.UniqueConstraint("tenant_id", "account_id", name="unique_tenant_account"),)

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<TenantAccountJoin tenant={self.tenant_id} account={self.account_id} role={self.role.value}>"

    def to_dict(self) -> dict:
        """
        转换为字典

        返回:
            关联信息字典
        """
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "account_id": str(self.account_id),
            "role": self.role.value,
            "created_at": self.created_at.isoformat(),
        }

    @property
    def is_owner(self) -> bool:
        """是否为所有者"""
        return self.role == TenantRole.OWNER

    @property
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.role in (TenantRole.OWNER, TenantRole.ADMIN)
