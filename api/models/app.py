"""
应用模型

AI 应用的核心模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import enum

from extensions.ext_database import db


class AppMode(enum.Enum):
    """应用模式"""
    CHAT = "chat"              # 聊天型
    COMPLETION = "completion"  # 补全型
    AGENT = "agent"            # Agent 型
    WORKFLOW = "workflow"      # 工作流型


class AppStatus(enum.Enum):
    """应用状态"""
    NORMAL = "normal"          # 正常
    ARCHIVED = "archived"      # 已归档


class App(db.Model):
    """
    应用模型
    
    管理 AI 应用的基本信息和配置
    """
    __tablename__ = 'apps'
    
    # 主键
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="应用 ID"
    )
    
    # 外键
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="租户 ID"
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="应用名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="应用描述"
    )
    
    # 应用配置
    mode: Mapped[AppMode] = mapped_column(
        SQLEnum(AppMode),
        nullable=False,
        index=True,
        comment="应用模式"
    )
    icon: Mapped[str] = mapped_column(
        String(20),
        default="🤖",
        nullable=False,
        comment="应用图标 emoji"
    )
    icon_background: Mapped[str] = mapped_column(
        String(20),
        default="#E0F2FE",
        nullable=False,
        comment="图标背景色"
    )
    
    # 功能开关
    enable_site: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用站点访问"
    )
    enable_api: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用 API 访问"
    )
    
    # 状态
    status: Mapped[AppStatus] = mapped_column(
        SQLEnum(AppStatus),
        default=AppStatus.NORMAL,
        nullable=False,
        index=True,
        comment="应用状态"
    )
    
    # 创建者
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey('accounts.id', ondelete='SET NULL'),
        nullable=True,
        comment="创建者 ID"
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
    tenant = relationship("Tenant", back_populates="apps")
    model_config = relationship(
        "AppModelConfig",
        back_populates="app",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<App {self.name} mode={self.mode.value}>"
    
    def to_dict(self) -> dict:
        """
        转换为字典
        
        返回:
            应用信息字典
        """
        result = {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "mode": self.mode.value,
            "icon": self.icon,
            "icon_background": self.icon_background,
            "enable_site": self.enable_site,
            "enable_api": self.enable_api,
            "status": self.status.value,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        # 如果有模型配置，添加到结果中
        if self.model_config:
            result["model_config"] = self.model_config.to_dict()
        
        return result
    
    @property
    def is_active(self) -> bool:
        """是否为正常状态"""
        return self.status == AppStatus.NORMAL


class AppModelConfig(db.Model):
    """
    应用模型配置
    
    存储应用的 AI 模型配置
    """
    __tablename__ = 'app_model_configs'
    
    # 主键
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="配置 ID"
    )
    
    # 外键
    app_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey('apps.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
        comment="应用 ID"
    )
    
    # 模型配置
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="模型提供商"
    )
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="模型名称"
    )
    configs: Mapped[dict] = mapped_column(
        db.JSON,
        nullable=False,
        default=dict,
        comment="模型参数配置"
    )
    
    # 提示词配置
    opening_statement: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="开场白"
    )
    suggested_questions: Mapped[Optional[list]] = mapped_column(
        db.JSON,
        nullable=True,
        comment="建议问题列表"
    )
    pre_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="系统提示词"
    )
    user_input_form: Mapped[Optional[dict]] = mapped_column(
        db.JSON,
        nullable=True,
        comment="用户输入表单配置"
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
    app = relationship("App", back_populates="model_config")
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<AppModelConfig app={self.app_id} provider={self.provider} model={self.model}>"
    
    def to_dict(self) -> dict:
        """
        转换为字典
        
        返回:
            配置信息字典
        """
        return {
            "id": str(self.id),
            "app_id": str(self.app_id),
            "provider": self.provider,
            "model": self.model,
            "configs": self.configs,
            "opening_statement": self.opening_statement,
            "suggested_questions": self.suggested_questions,
            "pre_prompt": self.pre_prompt,
            "user_input_form": self.user_input_form,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
