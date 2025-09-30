"""
模型提供商配置仓储层
"""

import uuid
from typing import Optional

from models import ModelProvider, ProviderType
from repositories.base_repository import BaseRepository


class ModelProviderRepository(BaseRepository[ModelProvider]):
    """模型提供商配置仓储"""

    def __init__(self):
        super().__init__(ModelProvider)

    def get_by_tenant_id(self, tenant_id: uuid.UUID, include_inactive: bool = False) -> list[ModelProvider]:
        """
        根据租户 ID 获取提供商配置列表

        Args:
            tenant_id: 租户 ID
            include_inactive: 是否包含未激活的配置

        Returns:
            list[ModelProvider]: 提供商配置列表
        """
        query = self.session.query(ModelProvider).filter(ModelProvider.tenant_id == tenant_id)

        if not include_inactive:
            query = query.filter(ModelProvider.is_active == True)

        return query.order_by(ModelProvider.created_at.desc()).all()

    def get_by_tenant_and_type(
        self, tenant_id: uuid.UUID, provider_type: ProviderType, include_inactive: bool = False
    ) -> list[ModelProvider]:
        """
        根据租户 ID 和提供商类型获取配置列表

        Args:
            tenant_id: 租户 ID
            provider_type: 提供商类型
            include_inactive: 是否包含未激活的配置

        Returns:
            list[ModelProvider]: 提供商配置列表
        """
        query = (
            self.session.query(ModelProvider)
            .filter(ModelProvider.tenant_id == tenant_id)
            .filter(ModelProvider.provider_type == provider_type)
        )

        if not include_inactive:
            query = query.filter(ModelProvider.is_active == True)

        return query.order_by(ModelProvider.created_at.desc()).all()

    def get_active_by_tenant_and_name(self, tenant_id: uuid.UUID, name: str) -> Optional[ModelProvider]:
        """
        根据租户 ID 和名称获取激活的提供商配置

        Args:
            tenant_id: 租户 ID
            name: 提供商名称

        Returns:
            Optional[ModelProvider]: 提供商配置，不存在返回 None
        """
        return (
            self.session.query(ModelProvider)
            .filter(ModelProvider.tenant_id == tenant_id, ModelProvider.name == name, ModelProvider.is_active == True)
            .first()
        )

    def get_by_tenant_and_id(self, tenant_id: uuid.UUID, provider_id: uuid.UUID) -> Optional[ModelProvider]:
        """
        根据租户 ID 和提供商 ID 获取配置

        Args:
            tenant_id: 租户 ID
            provider_id: 提供商 ID

        Returns:
            Optional[ModelProvider]: 提供商配置，不存在返回 None
        """
        return (
            self.session.query(ModelProvider)
            .filter(ModelProvider.tenant_id == tenant_id, ModelProvider.id == provider_id)
            .first()
        )

    def activate(self, provider_id: uuid.UUID) -> bool:
        """
        激活提供商配置

        Args:
            provider_id: 提供商 ID

        Returns:
            bool: 是否成功
        """
        provider = self.get_by_id(provider_id)
        if not provider:
            return False

        provider.is_active = True
        self.session.commit()
        return True

    def deactivate(self, provider_id: uuid.UUID) -> bool:
        """
        停用提供商配置

        Args:
            provider_id: 提供商 ID

        Returns:
            bool: 是否成功
        """
        provider = self.get_by_id(provider_id)
        if not provider:
            return False

        provider.is_active = False
        self.session.commit()
        return True

    def count_by_tenant(self, tenant_id: uuid.UUID, include_inactive: bool = False) -> int:
        """
        统计租户的提供商配置数量

        Args:
            tenant_id: 租户 ID
            include_inactive: 是否包含未激活的配置

        Returns:
            int: 提供商配置数量
        """
        query = self.session.query(ModelProvider).filter(ModelProvider.tenant_id == tenant_id)

        if not include_inactive:
            query = query.filter(ModelProvider.is_active == True)

        return query.count()
