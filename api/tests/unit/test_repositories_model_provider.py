"""
ModelProviderRepository 测试
"""

import pytest

from models import ModelProvider, ProviderType, Tenant, TenantPlan, TenantStatus
from repositories import ModelProviderRepository


class TestModelProviderRepository:
    """ModelProviderRepository 测试类"""

    @pytest.fixture
    def repository(self):
        """创建 repository 实例"""
        return ModelProviderRepository()

    @pytest.fixture
    def tenant(self, session):
        """创建测试租户"""
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.commit()
        return tenant

    def test_create_provider(self, repository, tenant):
        """测试创建提供商配置"""
        credentials = {"api_key": "sk-test-key"}
        created = repository.create(
            tenant_id=tenant.id,
            name="OpenAI GPT-4",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials(credentials),
        )

        assert created.id is not None
        assert created.name == "OpenAI GPT-4"
        assert created.tenant_id == tenant.id

    def test_get_by_tenant_id(self, repository, tenant, session):
        """测试根据租户 ID 获取提供商配置列表"""
        # 创建多个提供商配置
        provider1 = ModelProvider(
            tenant_id=tenant.id,
            name="OpenAI",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key1"}),
            is_active=True,
        )
        provider2 = ModelProvider(
            tenant_id=tenant.id,
            name="TEI",
            provider_type=ProviderType.TEI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"base_url": "http://localhost"}),
            is_active=True,
        )
        provider3 = ModelProvider(
            tenant_id=tenant.id,
            name="Inactive",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key3"}),
            is_active=False,
        )
        session.add(provider1)
        session.add(provider2)
        session.add(provider3)
        session.commit()

        # 只获取激活的
        providers = repository.get_by_tenant_id(tenant.id)
        assert len(providers) == 2

        # 包含未激活的
        providers_all = repository.get_by_tenant_id(tenant.id, include_inactive=True)
        assert len(providers_all) == 3

    def test_get_by_tenant_and_type(self, repository, tenant, session):
        """测试根据租户 ID 和类型获取提供商配置"""
        provider1 = ModelProvider(
            tenant_id=tenant.id,
            name="OpenAI 1",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key1"}),
        )
        provider2 = ModelProvider(
            tenant_id=tenant.id,
            name="OpenAI 2",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key2"}),
        )
        provider3 = ModelProvider(
            tenant_id=tenant.id,
            name="TEI",
            provider_type=ProviderType.TEI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"base_url": "http://localhost"}),
        )
        session.add(provider1)
        session.add(provider2)
        session.add(provider3)
        session.commit()

        # 获取 OpenAI 类型
        openai_providers = repository.get_by_tenant_and_type(tenant.id, ProviderType.OPENAI)
        assert len(openai_providers) == 2

        # 获取 TEI 类型
        tei_providers = repository.get_by_tenant_and_type(tenant.id, ProviderType.TEI)
        assert len(tei_providers) == 1

    def test_get_active_by_tenant_and_name(self, repository, tenant, session):
        """测试根据租户 ID 和名称获取激活的提供商配置"""
        provider1 = ModelProvider(
            tenant_id=tenant.id,
            name="OpenAI GPT-4",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key1"}),
            is_active=True,
        )
        provider2 = ModelProvider(
            tenant_id=tenant.id,
            name="Inactive Provider",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key2"}),
            is_active=False,
        )
        session.add(provider1)
        session.add(provider2)
        session.commit()

        # 获取激活的
        provider = repository.get_active_by_tenant_and_name(tenant.id, "OpenAI GPT-4")
        assert provider is not None
        assert provider.name == "OpenAI GPT-4"

        # 获取未激活的（应该返回 None）
        provider = repository.get_active_by_tenant_and_name(tenant.id, "Inactive Provider")
        assert provider is None

    def test_get_by_tenant_and_id(self, repository, tenant, session):
        """测试根据租户 ID 和提供商 ID 获取配置"""
        provider = ModelProvider(
            tenant_id=tenant.id,
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key"}),
        )
        session.add(provider)
        session.commit()

        # 正确的租户 ID
        found = repository.get_by_tenant_and_id(tenant.id, provider.id)
        assert found is not None
        assert found.id == provider.id

        # 错误的租户 ID（应该返回 None）
        import uuid

        wrong_tenant_id = uuid.uuid4()
        found = repository.get_by_tenant_and_id(wrong_tenant_id, provider.id)
        assert found is None

    def test_activate_provider(self, repository, tenant, session):
        """测试激活提供商配置"""
        provider = ModelProvider(
            tenant_id=tenant.id,
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key"}),
            is_active=False,
        )
        session.add(provider)
        session.commit()

        # 激活
        result = repository.activate(provider.id)
        assert result is True

        # 验证
        session.refresh(provider)
        assert provider.is_active is True

    def test_deactivate_provider(self, repository, tenant, session):
        """测试停用提供商配置"""
        provider = ModelProvider(
            tenant_id=tenant.id,
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key"}),
            is_active=True,
        )
        session.add(provider)
        session.commit()

        # 停用
        result = repository.deactivate(provider.id)
        assert result is True

        # 验证
        session.refresh(provider)
        assert provider.is_active is False

    def test_count_by_tenant(self, repository, tenant, session):
        """测试统计租户的提供商配置数量"""
        provider1 = ModelProvider(
            tenant_id=tenant.id,
            name="Provider 1",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key1"}),
            is_active=True,
        )
        provider2 = ModelProvider(
            tenant_id=tenant.id,
            name="Provider 2",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key2"}),
            is_active=True,
        )
        provider3 = ModelProvider(
            tenant_id=tenant.id,
            name="Provider 3",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key3"}),
            is_active=False,
        )
        session.add(provider1)
        session.add(provider2)
        session.add(provider3)
        session.commit()

        # 只统计激活的
        count = repository.count_by_tenant(tenant.id)
        assert count == 2

        # 包含未激活的
        count_all = repository.count_by_tenant(tenant.id, include_inactive=True)
        assert count_all == 3

    def test_update_provider(self, repository, tenant, session):
        """测试更新提供商配置"""
        provider = ModelProvider(
            tenant_id=tenant.id,
            name="Old Name",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key"}),
        )
        session.add(provider)
        session.commit()

        # 更新
        updated = repository.update(provider.id, name="New Name")

        assert updated.name == "New Name"

    def test_delete_provider(self, repository, tenant, session):
        """测试删除提供商配置"""
        provider = ModelProvider(
            tenant_id=tenant.id,
            name="To Delete",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key"}),
        )
        session.add(provider)
        session.commit()

        provider_id = provider.id

        # 删除
        result = repository.delete(provider_id)
        assert result is True

        # 验证已删除
        deleted = repository.get_by_id(provider_id)
        assert deleted is None
