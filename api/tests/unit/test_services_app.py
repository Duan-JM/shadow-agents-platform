"""
应用服务测试
"""

from unittest.mock import Mock

import pytest

from models.app import App, AppMode, AppStatus
from models.tenant import Tenant, TenantRole
from services.app_service import AppService
from services.exceptions import (
    AuthorizationError,
    ResourceNotFoundError,
    ValidationError,
)


class TestAppService:
    """应用服务测试类"""

    @pytest.fixture
    def mock_app_repo(self):
        """Mock 应用仓储"""
        return Mock()

    @pytest.fixture
    def mock_tenant_repo(self):
        """Mock 租户仓储"""
        return Mock()

    @pytest.fixture
    def app_service(self, mock_app_repo, mock_tenant_repo):
        """创建应用服务实例"""
        return AppService(app_repo=mock_app_repo, tenant_repo=mock_tenant_repo)

    def test_create_app_success(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试创建应用成功"""
        tenant_id = "tenant-123"
        account_id = "account-456"
        name = "Test App"
        mode = AppMode.CHAT

        # Mock 租户存在
        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 创建应用
        app = App(name=name, tenant_id=tenant_id, mode=mode, status=AppStatus.NORMAL)
        mock_app_repo.create.return_value = app

        # 执行创建
        created_app = app_service.create_app(tenant_id, account_id, name, mode)

        # 验证结果
        assert created_app.name == name
        assert created_app.mode == mode
        mock_app_repo.create.assert_called_once()

    def test_create_app_invalid_name(self, app_service, mock_tenant_repo):
        """测试创建应用名称无效"""
        tenant_id = "tenant-123"
        account_id = "account-456"

        invalid_names = ["", "   ", "a" * 101]  # 空名称  # 只有空格  # 超长

        for name in invalid_names:
            with pytest.raises(ValidationError) as exc_info:
                app_service.create_app(tenant_id, account_id, name, AppMode.CHAT)

            assert "name" in str(exc_info.value).lower()

    def test_create_app_nonexistent_tenant(self, app_service, mock_tenant_repo):
        """测试创建应用时租户不存在"""
        # Mock 租户不存在
        mock_tenant_repo.get_by_id.return_value = None

        with pytest.raises(ResourceNotFoundError) as exc_info:
            app_service.create_app("nonexistent-tenant", "account-123", "Test App", AppMode.CHAT)

        assert "tenant" in str(exc_info.value).lower()

    def test_create_app_not_tenant_member(self, app_service, mock_tenant_repo):
        """测试创建应用时不是租户成员"""
        tenant_id = "tenant-123"
        account_id = "account-456"

        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 不是租户成员
        mock_tenant_repo.is_member.return_value = False

        with pytest.raises(AuthorizationError) as exc_info:
            app_service.create_app(tenant_id, account_id, "Test App", AppMode.CHAT)

        assert "not a member" in str(exc_info.value).lower()

    def test_create_app_with_config_success(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试创建应用及配置成功"""
        tenant_id = "tenant-123"
        account_id = "account-456"

        app_data = {"name": "Test App", "mode": AppMode.CHAT, "description": "Test description"}
        config_data = {"provider": "openai", "model_name": "gpt-4"}

        # Mock 租户存在
        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 创建应用
        app = App(name="Test App", tenant_id=tenant_id)
        mock_app_repo.create_with_config.return_value = app

        # 执行创建
        created_app = app_service.create_app_with_config(tenant_id, account_id, app_data, config_data)

        # 验证结果
        assert created_app.name == "Test App"
        mock_app_repo.create_with_config.assert_called_once()

        # 验证传递的参数包含必要字段
        call_args = mock_app_repo.create_with_config.call_args[0]
        assert call_args[0]["tenant_id"] == tenant_id
        assert call_args[0]["created_by"] == account_id

    def test_update_app_success(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试更新应用成功"""
        app_id = "app-123"
        account_id = "account-456"
        updates = {"name": "Updated App", "description": "New description"}

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123", name="Old App")
        mock_app_repo.get_by_id.return_value = app

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 更新后的应用
        updated_app = App(id=app_id, name="Updated App")
        mock_app_repo.update.return_value = updated_app

        # 执行更新
        result = app_service.update_app(app_id, account_id, **updates)

        # 验证结果
        assert result.name == "Updated App"
        mock_app_repo.update.assert_called_once()

    def test_update_app_not_tenant_member(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试更新应用时不是租户成员"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123")
        mock_app_repo.get_by_id.return_value = app

        # Mock 不是租户成员
        mock_tenant_repo.is_member.return_value = False

        # 执行更新，应该抛出异常
        with pytest.raises(AuthorizationError):
            app_service.update_app(app_id, account_id, name="New Name")

    def test_update_app_config_success(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试更新应用配置成功"""
        app_id = "app-123"
        account_id = "account-456"
        config_data = {"provider": "anthropic", "model_name": "claude-3"}

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123")
        mock_app_repo.get_by_id.return_value = app
        mock_app_repo.get_with_config.return_value = app

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # 执行更新配置
        result = app_service.update_app_config(app_id, account_id, config_data)

        # 验证调用
        mock_app_repo.update_config.assert_called_once_with(app_id, config_data)
        mock_app_repo.get_with_config.assert_called_once_with(app_id)

    def test_delete_app_success(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试删除应用成功"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123")
        mock_app_repo.get_by_id.return_value = app

        # Mock 是 ADMIN
        mock_tenant_repo.get_member_role.return_value = TenantRole.ADMIN

        # 执行删除
        app_service.delete_app(app_id, account_id)

        # 验证调用
        mock_app_repo.delete.assert_called_once_with(app_id)

    def test_delete_app_insufficient_permission(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试删除应用权限不足"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123")
        mock_app_repo.get_by_id.return_value = app

        # Mock 是 MEMBER（权限不足）
        mock_tenant_repo.get_member_role.return_value = TenantRole.MEMBER

        # 执行删除，应该抛出异常
        with pytest.raises(AuthorizationError) as exc_info:
            app_service.delete_app(app_id, account_id)

        assert "only admin or owner" in str(exc_info.value).lower()

    def test_archive_app_success(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试归档应用成功"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123")
        mock_app_repo.get_by_id.return_value = app

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 归档后的应用
        archived_app = App(id=app_id, status=AppStatus.ARCHIVED)
        mock_app_repo.archive.return_value = archived_app

        # 执行归档
        result = app_service.archive_app(app_id, account_id)

        # 验证结果
        assert result.status == AppStatus.ARCHIVED
        mock_app_repo.archive.assert_called_once_with(app_id)

    def test_unarchive_app_success(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试取消归档应用成功"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123", status=AppStatus.ARCHIVED)
        mock_app_repo.get_by_id.return_value = app

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 取消归档后的应用
        unarchived_app = App(id=app_id, status=AppStatus.NORMAL)
        mock_app_repo.unarchive.return_value = unarchived_app

        # 执行取消归档
        result = app_service.unarchive_app(app_id, account_id)

        # 验证结果
        assert result.status == AppStatus.NORMAL
        mock_app_repo.unarchive.assert_called_once_with(app_id)

    def test_get_tenant_apps_success(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试获取租户应用列表成功"""
        tenant_id = "tenant-123"
        account_id = "account-456"

        # Mock 租户存在
        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 应用列表
        apps = [App(id="app-1", name="App 1", tenant_id=tenant_id), App(id="app-2", name="App 2", tenant_id=tenant_id)]
        mock_app_repo.get_active_apps_by_tenant.return_value = apps

        # 执行获取
        result = app_service.get_tenant_apps(tenant_id, account_id)

        # 验证结果
        assert len(result) == 2
        assert result[0].name == "App 1"
        assert result[1].name == "App 2"
        mock_app_repo.get_active_apps_by_tenant.assert_called_once_with(tenant_id)

    def test_get_tenant_apps_include_archived(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试获取租户应用列表包含已归档"""
        tenant_id = "tenant-123"
        account_id = "account-456"

        # Mock 租户存在和成员资格
        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)
        mock_tenant_repo.is_member.return_value = True

        # Mock 应用列表（包含已归档）
        apps = [
            App(id="app-1", name="App 1", status=AppStatus.NORMAL),
            App(id="app-2", name="App 2", status=AppStatus.ARCHIVED),
        ]
        mock_app_repo.get_by_tenant.return_value = apps

        # 执行获取（包含已归档）
        result = app_service.get_tenant_apps(tenant_id, account_id, include_archived=True)

        # 验证结果
        assert len(result) == 2
        mock_app_repo.get_by_tenant.assert_called_once_with(tenant_id)

    def test_get_tenant_apps_not_tenant_member(self, app_service, mock_tenant_repo):
        """测试获取租户应用时不是租户成员"""
        tenant_id = "tenant-123"
        account_id = "account-456"

        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 不是租户成员
        mock_tenant_repo.is_member.return_value = False

        # 执行获取，应该抛出异常
        with pytest.raises(AuthorizationError):
            app_service.get_tenant_apps(tenant_id, account_id)

    def test_get_app_detail_success(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试获取应用详情成功"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在（包含配置）
        app = App(id=app_id, tenant_id="tenant-123", name="Test App", mode=AppMode.CHAT)
        mock_app_repo.get_with_config.return_value = app

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # 执行获取
        result = app_service.get_app_detail(app_id, account_id)

        # 验证结果
        assert result.id == app_id
        assert result.name == "Test App"
        mock_app_repo.get_with_config.assert_called_once_with(app_id)

    def test_toggle_site_enable(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试启用网站访问"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123", enable_site=False)
        mock_app_repo.get_by_id.return_value = app

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 更新后的应用
        updated_app = App(id=app_id, enable_site=True)
        mock_app_repo.enable_site.return_value = updated_app

        # 执行启用
        result = app_service.toggle_site(app_id, account_id, True)

        # 验证结果
        assert result.enable_site is True
        mock_app_repo.enable_site.assert_called_once_with(app_id, True)

    def test_toggle_site_disable(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试禁用网站访问"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123", enable_site=True)
        mock_app_repo.get_by_id.return_value = app

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 更新后的应用
        updated_app = App(id=app_id, enable_site=False)
        mock_app_repo.enable_site.return_value = updated_app

        # 执行禁用
        result = app_service.toggle_site(app_id, account_id, False)

        # 验证结果
        assert result.enable_site is False

    def test_toggle_api_enable(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试启用 API 访问"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123", enable_api=False)
        mock_app_repo.get_by_id.return_value = app

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 更新后的应用
        updated_app = App(id=app_id, enable_api=True)
        mock_app_repo.enable_api.return_value = updated_app

        # 执行启用
        result = app_service.toggle_api(app_id, account_id, True)

        # 验证结果
        assert result.enable_api is True
        mock_app_repo.enable_api.assert_called_once_with(app_id, True)

    def test_toggle_api_disable(self, app_service, mock_app_repo, mock_tenant_repo):
        """测试禁用 API 访问"""
        app_id = "app-123"
        account_id = "account-456"

        # Mock 应用存在
        app = App(id=app_id, tenant_id="tenant-123", enable_api=True)
        mock_app_repo.get_by_id.return_value = app

        # Mock 是租户成员
        mock_tenant_repo.is_member.return_value = True

        # Mock 更新后的应用
        updated_app = App(id=app_id, enable_api=False)
        mock_app_repo.enable_api.return_value = updated_app

        # 执行禁用
        result = app_service.toggle_api(app_id, account_id, False)

        # 验证结果
        assert result.enable_api is False
