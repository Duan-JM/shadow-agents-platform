"""
ModelProvider 模型单元测试
"""

import uuid

import pytest

from models import ModelProvider, ProviderType, Tenant, TenantPlan, TenantStatus


class TestModelProviderModel:
    """ModelProvider 模型测试类"""

    def test_create_model_provider(self, session):
        """测试创建模型提供商配置"""
        # 创建租户
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        # 创建模型提供商配置
        credentials = {"api_key": "sk-test-key", "base_url": "https://api.openai.com/v1"}
        provider = ModelProvider(
            tenant_id=tenant.id,
            name="OpenAI GPT-4",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials(credentials),
            is_active=True,
            config={"default_model": "gpt-4", "timeout": 60},
        )
        session.add(provider)
        session.commit()

        # 验证
        assert provider.id is not None
        assert provider.tenant_id == tenant.id
        assert provider.name == "OpenAI GPT-4"
        assert provider.provider_type == ProviderType.OPENAI
        assert provider.is_active is True
        assert provider.config["default_model"] == "gpt-4"

    def test_provider_type_enum(self):
        """测试提供商类型枚举"""
        assert ProviderType.OPENAI == "openai"
        assert ProviderType.TEI == "tei"

    def test_to_dict(self, session):
        """测试转换为字典"""
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        credentials = {"api_key": "sk-test-key"}
        provider = ModelProvider(
            tenant_id=tenant.id,
            name="OpenAI GPT-3.5",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials(credentials),
            config={"timeout": 30},
            quota_config={"max_tokens": 100000},
        )
        session.add(provider)
        session.commit()

        # 不包含凭证
        data = provider.to_dict()
        assert data["name"] == "OpenAI GPT-3.5"
        assert data["provider_type"] == "openai"
        assert data["is_active"] is True
        assert "encrypted_credentials" not in data
        assert data["config"]["timeout"] == 30
        assert data["quota_config"]["max_tokens"] == 100000

        # 包含凭证
        data_with_creds = provider.to_dict(include_credentials=True)
        assert "encrypted_credentials" in data_with_creds

    def test_encrypt_decrypt_credentials(self):
        """测试凭证加密解密"""
        credentials = {"api_key": "sk-test-key", "base_url": "https://api.openai.com/v1"}

        # 加密
        encrypted = ModelProvider.encrypt_credentials(credentials)
        assert isinstance(encrypted, str)
        assert encrypted != str(credentials)

        # 解密
        decrypted = ModelProvider.decrypt_credentials(encrypted)
        assert decrypted == credentials

    def test_relationship_with_tenant(self, session):
        """测试与租户的关系"""
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        # 创建多个提供商配置
        provider1 = ModelProvider(
            tenant_id=tenant.id,
            name="OpenAI",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key1"}),
        )
        provider2 = ModelProvider(
            tenant_id=tenant.id,
            name="TEI",
            provider_type=ProviderType.TEI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"base_url": "http://localhost:8080"}),
        )
        session.add(provider1)
        session.add(provider2)
        session.commit()

        # 通过租户访问提供商配置
        session.refresh(tenant)
        assert len(tenant.model_providers) == 2

    def test_is_active_default(self, session):
        """测试 is_active 默认值"""
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        provider = ModelProvider(
            tenant_id=tenant.id,
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key"}),
        )
        session.add(provider)
        session.commit()

        assert provider.is_active is True

    def test_deactivate_provider(self, session):
        """测试停用提供商"""
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

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
        provider.is_active = False
        session.commit()

        assert provider.is_active is False

    def test_config_json_field(self, session):
        """测试配置 JSON 字段"""
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        config = {
            "default_model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "models": ["gpt-3.5-turbo", "gpt-4"],
        }

        provider = ModelProvider(
            tenant_id=tenant.id,
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key"}),
            config=config,
        )
        session.add(provider)
        session.commit()

        # 读取验证
        session.refresh(provider)
        assert provider.config["default_model"] == "gpt-4"
        assert provider.config["temperature"] == 0.7
        assert "gpt-4" in provider.config["models"]

    def test_created_by_updated_by(self, session):
        """测试创建者和更新者字段"""
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        creator_id = uuid.uuid4()
        updater_id = uuid.uuid4()

        provider = ModelProvider(
            tenant_id=tenant.id,
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            encrypted_credentials=ModelProvider.encrypt_credentials({"api_key": "key"}),
            created_by=creator_id,
            updated_by=updater_id,
        )
        session.add(provider)
        session.commit()

        assert provider.created_by == creator_id
        assert provider.updated_by == updater_id
