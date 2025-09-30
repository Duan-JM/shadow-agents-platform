"""
模型提供商配置模型
"""

import json
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions.ext_database import db


class ProviderType(str, Enum):
    """提供商类型枚举"""

    OPENAI = "openai"
    TEI = "tei"


class ModelProvider(db.Model):
    """模型提供商配置模型"""

    __tablename__ = "model_providers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_type: Mapped[ProviderType] = mapped_column(SQLEnum(ProviderType), nullable=False, index=True)
    encrypted_credentials: Mapped[str] = mapped_column(Text, nullable=False)  # 加密后的凭证 JSON
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=True)  # 额外配置（如默认模型、超时等）
    quota_config: Mapped[dict] = mapped_column(JSON, nullable=True)  # 配额配置
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="model_providers")

    def __repr__(self) -> str:
        return f"<ModelProvider {self.name} ({self.provider_type})>"

    def to_dict(self, include_credentials: bool = False) -> dict:
        """
        转换为字典

        Args:
            include_credentials: 是否包含凭证（默认不包含，用于安全）

        Returns:
            dict: 字典表示
        """
        data = {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "provider_type": self.provider_type.value,
            "is_active": self.is_active,
            "config": self.config or {},
            "quota_config": self.quota_config or {},
            "created_by": str(self.created_by) if self.created_by else None,
            "updated_by": str(self.updated_by) if self.updated_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

        if include_credentials:
            # 注意：这里返回的是加密后的凭证，需要在使用前解密
            data["encrypted_credentials"] = self.encrypted_credentials

        return data

    @staticmethod
    def encrypt_credentials(credentials: dict) -> str:
        """
        加密凭证

        Args:
            credentials: 凭证字典

        Returns:
            str: 加密后的凭证字符串

        Note:
            这里暂时使用简单的 JSON 序列化，实际应该使用加密算法（如 Fernet）
        """
        # TODO: 实现真正的加密逻辑
        return json.dumps(credentials)

    @staticmethod
    def decrypt_credentials(encrypted_credentials: str) -> dict:
        """
        解密凭证

        Args:
            encrypted_credentials: 加密后的凭证字符串

        Returns:
            dict: 凭证字典

        Note:
            这里暂时使用简单的 JSON 反序列化，实际应该使用解密算法（如 Fernet）
        """
        # TODO: 实现真正的解密逻辑
        return json.loads(encrypted_credentials)
