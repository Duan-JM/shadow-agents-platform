"""
模型提供商配置服务层
"""

import uuid
from typing import Optional

from core.model_runtime import ModelProviderFactory, ProviderCredentials
from core.model_runtime import ProviderType as RuntimeProviderType
from models import ModelProvider, ProviderType, Tenant
from repositories import ModelProviderRepository, TenantRepository
from services.exceptions import (
    AuthorizationError,
    BusinessLogicError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)


class ModelProviderService:
    """模型提供商配置服务"""

    def __init__(self):
        self.provider_repo = ModelProviderRepository()
        self.tenant_repo = TenantRepository()

    def add_provider(
        self,
        tenant_id: uuid.UUID,
        name: str,
        provider_type: ProviderType,
        credentials: dict,
        config: Optional[dict] = None,
        quota_config: Optional[dict] = None,
        created_by: Optional[uuid.UUID] = None,
    ) -> ModelProvider:
        """
        添加模型提供商配置

        Args:
            tenant_id: 租户 ID
            name: 提供商名称
            provider_type: 提供商类型
            credentials: 凭证字典
            config: 额外配置
            quota_config: 配额配置
            created_by: 创建者 ID

        Returns:
            ModelProvider: 创建的提供商配置

        Raises:
            ResourceNotFoundError: 租户不存在
            ValidationError: 参数验证失败
            ResourceConflictError: 名称已存在
            BusinessLogicError: 凭证验证失败
        """
        # 验证租户存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        # 验证名称
        if not name or len(name.strip()) == 0:
            raise ValidationError("Provider name is required")

        if len(name) > 100:
            raise ValidationError("Provider name is too long (max 100 characters)")

        # 检查名称是否已存在
        existing = self.provider_repo.get_active_by_tenant_and_name(tenant_id, name)
        if existing:
            raise ResourceConflictError(f"Provider with name '{name}' already exists")

        # 验证凭证
        if not credentials:
            raise ValidationError("Credentials are required")

        # 验证凭证是否有效
        try:
            self._validate_credentials(provider_type, credentials)
        except Exception as e:
            raise BusinessLogicError(f"Invalid credentials: {str(e)}")

        # 加密凭证
        encrypted_credentials = ModelProvider.encrypt_credentials(credentials)

        # 创建提供商配置
        provider = self.provider_repo.create(
            tenant_id=tenant_id,
            name=name,
            provider_type=provider_type,
            encrypted_credentials=encrypted_credentials,
            is_active=True,
            config=config or {},
            quota_config=quota_config or {},
            created_by=created_by,
        )

        return provider

    def get_provider(self, tenant_id: uuid.UUID, provider_id: uuid.UUID) -> ModelProvider:
        """
        获取提供商配置

        Args:
            tenant_id: 租户 ID
            provider_id: 提供商 ID

        Returns:
            ModelProvider: 提供商配置

        Raises:
            ResourceNotFoundError: 提供商配置不存在
            AuthorizationError: 无权访问
        """
        provider = self.provider_repo.get_by_tenant_and_id(tenant_id, provider_id)
        if not provider:
            raise ResourceNotFoundError("Provider", str(provider_id))

        return provider

    def list_providers(
        self, tenant_id: uuid.UUID, include_inactive: bool = False, provider_type: Optional[ProviderType] = None
    ) -> list[ModelProvider]:
        """
        获取提供商配置列表

        Args:
            tenant_id: 租户 ID
            include_inactive: 是否包含未激活的配置
            provider_type: 提供商类型过滤

        Returns:
            list[ModelProvider]: 提供商配置列表

        Raises:
            ResourceNotFoundError: 租户不存在
        """
        # 验证租户存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        if provider_type:
            return self.provider_repo.get_by_tenant_and_type(tenant_id, provider_type, include_inactive)
        else:
            return self.provider_repo.get_by_tenant_id(tenant_id, include_inactive)

    def update_provider(
        self,
        tenant_id: uuid.UUID,
        provider_id: uuid.UUID,
        name: Optional[str] = None,
        credentials: Optional[dict] = None,
        config: Optional[dict] = None,
        quota_config: Optional[dict] = None,
        updated_by: Optional[uuid.UUID] = None,
    ) -> ModelProvider:
        """
        更新提供商配置

        Args:
            tenant_id: 租户 ID
            provider_id: 提供商 ID
            name: 新名称
            credentials: 新凭证
            config: 新配置
            quota_config: 新配额配置
            updated_by: 更新者 ID

        Returns:
            ModelProvider: 更新后的提供商配置

        Raises:
            ResourceNotFoundError: 提供商配置不存在
            ValidationError: 参数验证失败
            ResourceConflictError: 名称冲突
            BusinessLogicError: 凭证验证失败
        """
        # 获取提供商配置
        provider = self.get_provider(tenant_id, provider_id)

        updates = {}

        # 更新名称
        if name is not None:
            if len(name.strip()) == 0:
                raise ValidationError("Provider name cannot be empty")

            if len(name) > 100:
                raise ValidationError("Provider name is too long (max 100 characters)")

            # 检查名称冲突
            if name != provider.name:
                existing = self.provider_repo.get_active_by_tenant_and_name(tenant_id, name)
                if existing:
                    raise ResourceConflictError(f"Provider with name '{name}' already exists")

            updates["name"] = name

        # 更新凭证
        if credentials is not None:
            # 验证凭证
            try:
                self._validate_credentials(provider.provider_type, credentials)
            except Exception as e:
                raise BusinessLogicError(f"Invalid credentials: {str(e)}")

            updates["encrypted_credentials"] = ModelProvider.encrypt_credentials(credentials)

        # 更新配置
        if config is not None:
            updates["config"] = config

        if quota_config is not None:
            updates["quota_config"] = quota_config

        if updated_by is not None:
            updates["updated_by"] = updated_by

        # 执行更新
        if updates:
            updated_provider = self.provider_repo.update(provider_id, **updates)
            return updated_provider

        return provider

    def delete_provider(self, tenant_id: uuid.UUID, provider_id: uuid.UUID) -> bool:
        """
        删除提供商配置

        Args:
            tenant_id: 租户 ID
            provider_id: 提供商 ID

        Returns:
            bool: 是否删除成功

        Raises:
            ResourceNotFoundError: 提供商配置不存在
        """
        # 验证提供商配置存在且属于该租户
        provider = self.get_provider(tenant_id, provider_id)

        # 删除
        return self.provider_repo.delete(provider_id)

    def activate_provider(self, tenant_id: uuid.UUID, provider_id: uuid.UUID) -> ModelProvider:
        """
        激活提供商配置

        Args:
            tenant_id: 租户 ID
            provider_id: 提供商 ID

        Returns:
            ModelProvider: 更新后的提供商配置

        Raises:
            ResourceNotFoundError: 提供商配置不存在
            BusinessLogicError: 已经是激活状态
        """
        provider = self.get_provider(tenant_id, provider_id)

        if provider.is_active:
            raise BusinessLogicError("Provider is already active")

        self.provider_repo.activate(provider_id)

        # 刷新获取最新状态
        return self.provider_repo.get_by_id(provider_id)

    def deactivate_provider(self, tenant_id: uuid.UUID, provider_id: uuid.UUID) -> ModelProvider:
        """
        停用提供商配置

        Args:
            tenant_id: 租户 ID
            provider_id: 提供商 ID

        Returns:
            ModelProvider: 更新后的提供商配置

        Raises:
            ResourceNotFoundError: 提供商配置不存在
            BusinessLogicError: 已经是停用状态
        """
        provider = self.get_provider(tenant_id, provider_id)

        if not provider.is_active:
            raise BusinessLogicError("Provider is already inactive")

        self.provider_repo.deactivate(provider_id)

        # 刷新获取最新状态
        return self.provider_repo.get_by_id(provider_id)

    def test_connection(self, tenant_id: uuid.UUID, provider_id: uuid.UUID) -> dict:
        """
        测试提供商连接

        Args:
            tenant_id: 租户 ID
            provider_id: 提供商 ID

        Returns:
            dict: 测试结果 {"success": bool, "message": str}

        Raises:
            ResourceNotFoundError: 提供商配置不存在
        """
        provider = self.get_provider(tenant_id, provider_id)

        # 解密凭证
        credentials = ModelProvider.decrypt_credentials(provider.encrypted_credentials)

        try:
            # 调用提供商验证接口
            self._validate_credentials(provider.provider_type, credentials)
            return {"success": True, "message": "Connection successful"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def _validate_credentials(self, provider_type: ProviderType, credentials: dict) -> bool:
        """
        验证凭证是否有效

        Args:
            provider_type: 提供商类型
            credentials: 凭证字典

        Returns:
            bool: 是否有效

        Raises:
            Exception: 验证失败时抛出异常
        """
        # 转换为运行时提供商类型
        runtime_type = RuntimeProviderType(provider_type.value)

        # 创建运行时凭证对象
        runtime_credentials = ProviderCredentials(provider_type=runtime_type, credentials=credentials)

        # 获取提供商实例并验证
        provider = ModelProviderFactory.get_provider(runtime_type)
        return provider.validate_credentials(runtime_credentials)
