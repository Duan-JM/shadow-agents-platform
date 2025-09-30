"""
ModelProviderService 测试
"""

import uuid

import pytest
from pytest_mock import MockerFixture

from models import ModelProvider, ProviderType, Tenant, TenantPlan, TenantStatus
from services import ModelProviderService
from services.exceptions import (
    AuthorizationError,
    BusinessLogicError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)


class TestModelProviderService:
    """ModelProviderService 测试类"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return ModelProviderService()

    @pytest.fixture
    def tenant(self, session):
        """创建测试租户"""
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.commit()
        return tenant

    def test_add_provider_success(self, service, tenant, mocker: MockerFixture):
        """测试成功添加提供商配置"""
        # Mock 凭证验证
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        credentials = {"api_key": "sk-test-key", "base_url": "https://api.openai.com/v1"}
        provider = service.add_provider(
            tenant_id=tenant.id,
            name="OpenAI GPT-4",
            provider_type=ProviderType.OPENAI,
            credentials=credentials,
            config={"default_model": "gpt-4"},
        )

        assert provider.id is not None
        assert provider.name == "OpenAI GPT-4"
        assert provider.provider_type == ProviderType.OPENAI
        assert provider.is_active is True
        assert provider.config["default_model"] == "gpt-4"

    def test_add_provider_tenant_not_found(self, service, session):
        """测试添加提供商配置，租户不存在"""
        with pytest.raises(ResourceNotFoundError, match="Tenant"):
            service.add_provider(
                tenant_id=uuid.uuid4(),
                name="Test Provider",
                provider_type=ProviderType.OPENAI,
                credentials={"api_key": "key"},
            )

    def test_add_provider_empty_name(self, service, tenant):
        """测试添加提供商配置，名称为空"""
        with pytest.raises(ValidationError, match="Provider name is required"):
            service.add_provider(
                tenant_id=tenant.id, name="", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
            )

    def test_add_provider_name_too_long(self, service, tenant):
        """测试添加提供商配置，名称过长"""
        long_name = "a" * 101
        with pytest.raises(ValidationError, match="Provider name is too long"):
            service.add_provider(
                tenant_id=tenant.id, name=long_name, provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
            )

    def test_add_provider_duplicate_name(self, service, tenant, session, mocker: MockerFixture):
        """测试添加提供商配置，名称重复"""
        # Mock 凭证验证
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        # 先添加一个
        service.add_provider(
            tenant_id=tenant.id, name="OpenAI", provider_type=ProviderType.OPENAI, credentials={"api_key": "key1"}
        )

        # 再添加同名的
        with pytest.raises(ResourceConflictError, match="already exists"):
            service.add_provider(
                tenant_id=tenant.id, name="OpenAI", provider_type=ProviderType.OPENAI, credentials={"api_key": "key2"}
            )

    def test_add_provider_no_credentials(self, service, tenant):
        """测试添加提供商配置，缺少凭证"""
        with pytest.raises(ValidationError, match="Credentials are required"):
            service.add_provider(
                tenant_id=tenant.id, name="Test Provider", provider_type=ProviderType.OPENAI, credentials=None
            )

    def test_add_provider_invalid_credentials(self, service, tenant, mocker: MockerFixture):
        """测试添加提供商配置，凭证无效"""
        # Mock 凭证验证失败
        mocker.patch.object(service, "_validate_credentials", side_effect=Exception("Invalid API key"))

        with pytest.raises(BusinessLogicError, match="Invalid credentials"):
            service.add_provider(
                tenant_id=tenant.id,
                name="Test Provider",
                provider_type=ProviderType.OPENAI,
                credentials={"api_key": "invalid"},
            )

    def test_get_provider_success(self, service, tenant, session, mocker: MockerFixture):
        """测试获取提供商配置"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        # 添加提供商
        provider = service.add_provider(
            tenant_id=tenant.id, name="Test Provider", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )

        # 获取
        fetched = service.get_provider(tenant.id, provider.id)
        assert fetched.id == provider.id
        assert fetched.name == "Test Provider"

    def test_get_provider_not_found(self, service, tenant):
        """测试获取不存在的提供商配置"""
        with pytest.raises(ResourceNotFoundError, match="Provider"):
            service.get_provider(tenant.id, uuid.uuid4())

    def test_list_providers(self, service, tenant, session, mocker: MockerFixture):
        """测试获取提供商配置列表"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        # 添加多个提供商
        service.add_provider(
            tenant_id=tenant.id, name="Provider 1", provider_type=ProviderType.OPENAI, credentials={"api_key": "key1"}
        )
        service.add_provider(
            tenant_id=tenant.id,
            name="Provider 2",
            provider_type=ProviderType.TEI,
            credentials={"base_url": "http://localhost"},
        )

        # 获取列表
        providers = service.list_providers(tenant.id)
        assert len(providers) == 2

    def test_list_providers_by_type(self, service, tenant, session, mocker: MockerFixture):
        """测试按类型过滤提供商配置列表"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        service.add_provider(
            tenant_id=tenant.id, name="OpenAI", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )
        service.add_provider(
            tenant_id=tenant.id,
            name="TEI",
            provider_type=ProviderType.TEI,
            credentials={"base_url": "http://localhost"},
        )

        # 只获取 OpenAI 类型
        openai_providers = service.list_providers(tenant.id, provider_type=ProviderType.OPENAI)
        assert len(openai_providers) == 1
        assert openai_providers[0].provider_type == ProviderType.OPENAI

    def test_update_provider_name(self, service, tenant, session, mocker: MockerFixture):
        """测试更新提供商配置名称"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider = service.add_provider(
            tenant_id=tenant.id, name="Old Name", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )

        # 更新名称
        updated = service.update_provider(tenant.id, provider.id, name="New Name")
        assert updated.name == "New Name"

    def test_update_provider_credentials(self, service, tenant, session, mocker: MockerFixture):
        """测试更新提供商配置凭证"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider = service.add_provider(
            tenant_id=tenant.id,
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            credentials={"api_key": "old_key"},
        )

        # 更新凭证
        new_credentials = {"api_key": "new_key"}
        updated = service.update_provider(tenant.id, provider.id, credentials=new_credentials)

        # 验证凭证已更新（通过解密验证）
        decrypted = ModelProvider.decrypt_credentials(updated.encrypted_credentials)
        assert decrypted["api_key"] == "new_key"

    def test_update_provider_config(self, service, tenant, session, mocker: MockerFixture):
        """测试更新提供商配置"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider = service.add_provider(
            tenant_id=tenant.id,
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            credentials={"api_key": "key"},
            config={"timeout": 30},
        )

        # 更新配置
        new_config = {"timeout": 60, "max_retries": 3}
        updated = service.update_provider(tenant.id, provider.id, config=new_config)
        assert updated.config["timeout"] == 60
        assert updated.config["max_retries"] == 3

    def test_update_provider_duplicate_name(self, service, tenant, session, mocker: MockerFixture):
        """测试更新提供商配置，名称冲突"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider1 = service.add_provider(
            tenant_id=tenant.id, name="Provider 1", provider_type=ProviderType.OPENAI, credentials={"api_key": "key1"}
        )
        provider2 = service.add_provider(
            tenant_id=tenant.id, name="Provider 2", provider_type=ProviderType.OPENAI, credentials={"api_key": "key2"}
        )

        # 尝试将 provider2 改名为 provider1 的名称
        with pytest.raises(ResourceConflictError, match="already exists"):
            service.update_provider(tenant.id, provider2.id, name="Provider 1")

    def test_delete_provider(self, service, tenant, session, mocker: MockerFixture):
        """测试删除提供商配置"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider = service.add_provider(
            tenant_id=tenant.id, name="To Delete", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )

        # 删除
        result = service.delete_provider(tenant.id, provider.id)
        assert result is True

        # 验证已删除
        with pytest.raises(ResourceNotFoundError):
            service.get_provider(tenant.id, provider.id)

    def test_activate_provider(self, service, tenant, session, mocker: MockerFixture):
        """测试激活提供商配置"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider = service.add_provider(
            tenant_id=tenant.id, name="Test Provider", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )

        # 先停用
        service.deactivate_provider(tenant.id, provider.id)

        # 再激活
        activated = service.activate_provider(tenant.id, provider.id)
        assert activated.is_active is True

    def test_activate_already_active(self, service, tenant, session, mocker: MockerFixture):
        """测试激活已激活的提供商配置"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider = service.add_provider(
            tenant_id=tenant.id, name="Test Provider", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )

        # 已经是激活状态，再次激活应该报错
        with pytest.raises(BusinessLogicError, match="already active"):
            service.activate_provider(tenant.id, provider.id)

    def test_deactivate_provider(self, service, tenant, session, mocker: MockerFixture):
        """测试停用提供商配置"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider = service.add_provider(
            tenant_id=tenant.id, name="Test Provider", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )

        # 停用
        deactivated = service.deactivate_provider(tenant.id, provider.id)
        assert deactivated.is_active is False

    def test_deactivate_already_inactive(self, service, tenant, session, mocker: MockerFixture):
        """测试停用已停用的提供商配置"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider = service.add_provider(
            tenant_id=tenant.id, name="Test Provider", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )

        # 先停用
        service.deactivate_provider(tenant.id, provider.id)

        # 再次停用应该报错
        with pytest.raises(BusinessLogicError, match="already inactive"):
            service.deactivate_provider(tenant.id, provider.id)

    def test_test_connection_success(self, service, tenant, session, mocker: MockerFixture):
        """测试连接成功"""
        mocker.patch.object(service, "_validate_credentials", return_value=True)

        provider = service.add_provider(
            tenant_id=tenant.id, name="Test Provider", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )

        # 测试连接
        result = service.test_connection(tenant.id, provider.id)
        assert result["success"] is True
        assert "successful" in result["message"].lower()

    def test_test_connection_failure(self, service, tenant, session, mocker: MockerFixture):
        """测试连接失败"""
        # 第一次调用成功（添加时），第二次调用失败（测试连接时）
        call_count = [0]

        def mock_validate(provider_type, credentials):
            call_count[0] += 1
            if call_count[0] == 1:
                return True
            raise Exception("Connection failed")

        mocker.patch.object(service, "_validate_credentials", side_effect=mock_validate)

        provider = service.add_provider(
            tenant_id=tenant.id, name="Test Provider", provider_type=ProviderType.OPENAI, credentials={"api_key": "key"}
        )

        # 测试连接
        result = service.test_connection(tenant.id, provider.id)
        assert result["success"] is False
        assert "Connection failed" in result["message"]
