"""
模型提供商配置 API 集成测试

测试模型提供商配置相关的 HTTP 端点
"""

import json
import uuid

import pytest
from pytest_mock import MockerFixture

from models import (
    Account,
    AccountStatus,
    ModelProvider,
    ProviderType,
    Tenant,
    TenantPlan,
    TenantStatus,
)


class TestModelProviderAPI:
    """模型提供商配置 API 测试类"""

    @pytest.fixture
    def test_account(self, session):
        """创建测试账号"""
        account = Account(
            email="provider_test@example.com",
            password_hash="hashed_password",
            name="Provider Test User",
            status=AccountStatus.ACTIVE,
        )
        session.add(account)
        session.commit()
        return account

    @pytest.fixture
    def test_tenant(self, session, test_account):
        """创建测试租户"""
        tenant = Tenant(name="Provider Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.commit()
        return tenant

    def test_add_provider_success(self, client_integration, auth_headers, test_tenant, mocker: MockerFixture):
        """测试成功添加提供商配置"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={
                "name": "OpenAI GPT-4",
                "provider_type": "OPENAI",
                "credentials": {"api_key": "sk-test-key", "base_url": "https://api.openai.com/v1"},
                "config": {"default_model": "gpt-4"},
            },
        )

        # 如果失败，打印错误信息
        if response.status_code != 201:
            print(f"Error response: {response.get_json()}")

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "OpenAI GPT-4"
        assert data["provider_type"] == "OPENAI"
        assert data["is_active"] is True
        assert data["config"]["default_model"] == "gpt-4"
        assert "id" in data
        assert "tenant_id" in data

    def test_add_provider_missing_name(self, client_integration, auth_headers, test_tenant):
        """测试添加提供商配置缺少名称"""
        response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"provider_type": "OPENAI", "credentials": {"api_key": "sk-test-key"}},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_add_provider_invalid_type(self, client_integration, auth_headers, test_tenant):
        """测试添加提供商配置，类型无效"""
        response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Invalid Provider", "provider_type": "INVALID_TYPE", "credentials": {"api_key": "key"}},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_add_provider_missing_credentials(self, client_integration, auth_headers, test_tenant):
        """测试添加提供商配置缺少凭证"""
        response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Test Provider", "provider_type": "OPENAI"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_add_provider_invalid_credentials(
        self, client_integration, auth_headers, test_tenant, mocker: MockerFixture
    ):
        """测试添加提供商配置，凭证无效"""
        # Mock 凭证验证失败
        mocker.patch(
            "services.model_provider_service.ModelProviderService._validate_credentials",
            side_effect=Exception("Invalid API key"),
        )

        response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Test Provider", "provider_type": "OPENAI", "credentials": {"api_key": "invalid"}},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_list_providers(self, client_integration, auth_headers, test_tenant, session, mocker: MockerFixture):
        """测试获取提供商配置列表"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        # 先添加两个配置
        client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Provider 1", "provider_type": "OPENAI", "credentials": {"api_key": "key1"}},
        )
        client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Provider 2", "provider_type": "TEI", "credentials": {"base_url": "http://localhost"}},
        )

        # 获取列表
        response = client_integration.get(
            f"/api/console/tenants/{test_tenant.id}/model-providers", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["data"]) == 2

    def test_list_providers_by_type(
        self, client_integration, auth_headers, test_tenant, session, mocker: MockerFixture
    ):
        """测试按类型过滤提供商配置列表"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        # 添加不同类型的配置
        client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "OpenAI", "provider_type": "OPENAI", "credentials": {"api_key": "key"}},
        )
        client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "TEI", "provider_type": "TEI", "credentials": {"base_url": "http://localhost"}},
        )

        # 只获取 OPENAI 类型
        response = client_integration.get(
            f"/api/console/tenants/{test_tenant.id}/model-providers?provider_type=OPENAI", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] == 1
        assert data["data"][0]["provider_type"] == "OPENAI"

    def test_get_provider(self, client_integration, auth_headers, test_tenant, session, mocker: MockerFixture):
        """测试获取提供商配置详情"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        # 先添加一个配置
        add_response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Test Provider", "provider_type": "OPENAI", "credentials": {"api_key": "key"}},
        )
        provider_id = add_response.get_json()["id"]

        # 获取详情
        response = client_integration.get(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{provider_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == provider_id
        assert data["name"] == "Test Provider"
        assert data["provider_type"] == "OPENAI"

    def test_get_provider_not_found(self, client_integration, auth_headers, test_tenant):
        """测试获取不存在的提供商配置"""
        fake_id = str(uuid.uuid4())
        response = client_integration.get(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_update_provider_name(self, client_integration, auth_headers, test_tenant, session, mocker: MockerFixture):
        """测试更新提供商配置名称"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        # 先添加一个配置
        add_response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Old Name", "provider_type": "OPENAI", "credentials": {"api_key": "key"}},
        )
        provider_id = add_response.get_json()["id"]

        # 更新名称
        response = client_integration.put(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{provider_id}",
            headers=auth_headers,
            json={"name": "New Name"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "New Name"

    def test_update_provider_config(
        self, client_integration, auth_headers, test_tenant, session, mocker: MockerFixture
    ):
        """测试更新提供商配置"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        # 先添加一个配置
        add_response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={
                "name": "Test Provider",
                "provider_type": "OPENAI",
                "credentials": {"api_key": "key"},
                "config": {"timeout": 30},
            },
        )
        provider_id = add_response.get_json()["id"]

        # 更新配置
        response = client_integration.put(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{provider_id}",
            headers=auth_headers,
            json={"config": {"timeout": 60, "max_retries": 3}},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["config"]["timeout"] == 60
        assert data["config"]["max_retries"] == 3

    def test_delete_provider(self, client_integration, auth_headers, test_tenant, session, mocker: MockerFixture):
        """测试删除提供商配置"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        # 先添加一个配置
        add_response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "To Delete", "provider_type": "OPENAI", "credentials": {"api_key": "key"}},
        )
        provider_id = add_response.get_json()["id"]

        # 删除
        response = client_integration.delete(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{provider_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data

        # 验证已删除
        get_response = client_integration.get(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{provider_id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_test_connection_success(
        self, client_integration, auth_headers, test_tenant, session, mocker: MockerFixture
    ):
        """测试连接成功"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        # 先添加一个配置
        add_response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Test Provider", "provider_type": "OPENAI", "credentials": {"api_key": "key"}},
        )
        provider_id = add_response.get_json()["id"]

        # 测试连接
        response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{provider_id}/test", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "success" in data
        assert data["success"] is True

    def test_activate_provider(self, client_integration, auth_headers, test_tenant, session, mocker: MockerFixture):
        """测试激活提供商配置"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        # 先添加一个配置
        add_response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Test Provider", "provider_type": "OPENAI", "credentials": {"api_key": "key"}},
        )
        provider_id = add_response.get_json()["id"]

        # 先停用
        client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{provider_id}/deactivate", headers=auth_headers
        )

        # 再激活
        response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{provider_id}/activate", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["is_active"] is True

    def test_deactivate_provider(self, client_integration, auth_headers, test_tenant, session, mocker: MockerFixture):
        """测试停用提供商配置"""
        # Mock 凭证验证
        mocker.patch("services.model_provider_service.ModelProviderService._validate_credentials", return_value=True)

        # 先添加一个配置
        add_response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers",
            headers=auth_headers,
            json={"name": "Test Provider", "provider_type": "OPENAI", "credentials": {"api_key": "key"}},
        )
        provider_id = add_response.get_json()["id"]

        # 停用
        response = client_integration.post(
            f"/api/console/tenants/{test_tenant.id}/model-providers/{provider_id}/deactivate", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["is_active"] is False

    def test_unauthorized_access(self, client_integration, test_tenant):
        """测试未授权访问"""
        response = client_integration.get(f"/api/console/tenants/{test_tenant.id}/model-providers")

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data
