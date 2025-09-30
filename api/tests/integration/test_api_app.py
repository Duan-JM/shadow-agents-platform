"""
应用 API 集成测试
"""

import uuid

import pytest
from werkzeug.security import generate_password_hash

from models import Account, AccountStatus, Tenant, TenantPlan, TenantStatus


class TestAppAPI:
    """应用 API 测试类"""

    def test_create_app_success(self, client_integration, auth_headers, session, test_account):
        """测试成功创建应用"""
        # 先创建一个租户
        from models import TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        # 添加成员关系
        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)
        session.commit()

        # 创建应用
        response = client_integration.post(
            "/api/console/apps",
            headers=auth_headers,
            json={
                "tenant_id": str(tenant.id),
                "name": "My Test App",
                "mode": "chat",
                "description": "Test description",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "My Test App"
        assert data["mode"] == "chat"
        assert data["description"] == "Test description"
        assert data["status"] == "normal"
        assert data["enable_site"] is True
        assert data["enable_api"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_app_missing_name(self, client_integration, auth_headers, session, test_account):
        """测试创建应用缺少名称"""
        # 创建租户
        from models import TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)
        session.commit()

        response = client_integration.post(
            "/api/console/apps", headers=auth_headers, json={"tenant_id": str(tenant.id), "mode": "chat"}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_create_app_invalid_mode(self, client_integration, auth_headers, session, test_account):
        """测试创建应用使用无效模式"""
        from models import TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)
        session.commit()

        response = client_integration.post(
            "/api/console/apps",
            headers=auth_headers,
            json={"tenant_id": str(tenant.id), "name": "Test App", "mode": "invalid"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_create_app_not_tenant_member(self, client_integration, auth_headers, session):
        """测试非租户成员创建应用"""
        # 创建一个租户，但不添加当前用户为成员
        tenant = Tenant(name="Other Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.commit()

        response = client_integration.post(
            "/api/console/apps",
            headers=auth_headers,
            json={"tenant_id": str(tenant.id), "name": "Test App", "mode": "chat"},
        )

        assert response.status_code == 403

    def test_create_app_without_auth(self, client_integration, session, test_account):
        """测试未认证创建应用"""
        from models import TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)
        session.commit()

        response = client_integration.post(
            "/api/console/apps", json={"tenant_id": str(tenant.id), "name": "Test App", "mode": "chat"}
        )

        assert response.status_code == 401

    def test_get_apps_success(self, client_integration, auth_headers, session, test_account):
        """测试获取应用列表"""
        from models import App, AppMode, TenantAccountJoin, TenantRole

        # 创建租户
        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        # 创建几个应用
        app1 = App(name="App 1", tenant_id=tenant.id, mode=AppMode.CHAT, created_by=test_account.id)
        app2 = App(name="App 2", tenant_id=tenant.id, mode=AppMode.COMPLETION, created_by=test_account.id)
        session.add(app1)
        session.add(app2)
        session.commit()

        # 获取应用列表
        response = client_integration.get(f"/api/console/apps?tenant_id={tenant.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
        app_names = [app["name"] for app in data]
        assert "App 1" in app_names
        assert "App 2" in app_names

    def test_get_apps_with_archived(self, client_integration, auth_headers, session, test_account):
        """测试获取包含已归档的应用列表"""
        from models import App, AppMode, AppStatus, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        # 创建正常和已归档应用
        app1 = App(name="Normal App", tenant_id=tenant.id, mode=AppMode.CHAT, created_by=test_account.id)
        app2 = App(
            name="Archived App",
            tenant_id=tenant.id,
            mode=AppMode.CHAT,
            status=AppStatus.ARCHIVED,
            created_by=test_account.id,
        )
        session.add(app1)
        session.add(app2)
        session.commit()

        # 不包含已归档
        response = client_integration.get(f"/api/console/apps?tenant_id={tenant.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1

        # 包含已归档
        response = client_integration.get(
            f"/api/console/apps?tenant_id={tenant.id}&include_archived=true", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2

    def test_get_app_success(self, client_integration, auth_headers, session, test_account):
        """测试获取应用详情"""
        from models import App, AppMode, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        app = App(name="Detail App", tenant_id=tenant.id, mode=AppMode.AGENT, created_by=test_account.id)
        session.add(app)
        session.commit()

        # 获取应用详情
        response = client_integration.get(f"/api/console/apps/{app.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Detail App"
        assert data["mode"] == "agent"
        assert "updated_at" in data

    def test_get_app_not_member(self, client_integration, auth_headers, session):
        """测试非租户成员获取应用详情"""
        from models import App, AppMode

        # 创建一个不属于当前用户的租户和应用
        tenant = Tenant(name="Other Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        app = App(name="Other App", tenant_id=tenant.id, mode=AppMode.CHAT)
        session.add(app)
        session.commit()

        response = client_integration.get(f"/api/console/apps/{app.id}", headers=auth_headers)

        assert response.status_code == 403

    def test_update_app_success(self, client_integration, auth_headers, session, test_account):
        """测试更新应用信息"""
        from models import App, AppMode, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        app = App(name="Old Name", tenant_id=tenant.id, mode=AppMode.CHAT, created_by=test_account.id)
        session.add(app)
        session.commit()

        # 更新应用
        response = client_integration.put(
            f"/api/console/apps/{app.id}",
            headers=auth_headers,
            json={"name": "New Name", "description": "New description"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "New Name"
        assert data["description"] == "New description"

    def test_delete_app_success(self, client_integration, auth_headers, session, test_account):
        """测试删除应用"""
        from models import App, AppMode, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        app = App(name="To Delete", tenant_id=tenant.id, mode=AppMode.CHAT, created_by=test_account.id)
        session.add(app)
        session.commit()

        app_id = app.id

        # 删除应用
        response = client_integration.delete(f"/api/console/apps/{app_id}", headers=auth_headers)

        assert response.status_code == 204

        # 验证已删除
        from repositories import AppRepository

        repo = AppRepository()
        deleted_app = repo.get_by_id(app_id)
        assert deleted_app is None

    def test_archive_app_success(self, client_integration, auth_headers, session, test_account):
        """测试归档应用"""
        from models import App, AppMode, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        app = App(name="To Archive", tenant_id=tenant.id, mode=AppMode.CHAT, created_by=test_account.id)
        session.add(app)
        session.commit()

        # 归档应用
        response = client_integration.post(f"/api/console/apps/{app.id}/archive", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "archived"

    def test_unarchive_app_success(self, client_integration, auth_headers, session, test_account):
        """测试取消归档应用"""
        from models import App, AppMode, AppStatus, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        app = App(
            name="Archived App",
            tenant_id=tenant.id,
            mode=AppMode.CHAT,
            status=AppStatus.ARCHIVED,
            created_by=test_account.id,
        )
        session.add(app)
        session.commit()

        # 取消归档
        response = client_integration.post(f"/api/console/apps/{app.id}/unarchive", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "normal"

    def test_enable_site_success(self, client_integration, auth_headers, session, test_account):
        """测试启用站点访问"""
        from models import App, AppMode, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        app = App(
            name="Test App", tenant_id=tenant.id, mode=AppMode.CHAT, enable_site=False, created_by=test_account.id
        )
        session.add(app)
        session.commit()

        # 启用站点
        response = client_integration.post(f"/api/console/apps/{app.id}/site/enable", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["enable_site"] is True

    def test_disable_site_success(self, client_integration, auth_headers, session, test_account):
        """测试禁用站点访问"""
        from models import App, AppMode, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        app = App(name="Test App", tenant_id=tenant.id, mode=AppMode.CHAT, enable_site=True, created_by=test_account.id)
        session.add(app)
        session.commit()

        # 禁用站点
        response = client_integration.post(f"/api/console/apps/{app.id}/site/disable", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["enable_site"] is False

    def test_enable_api_success(self, client_integration, auth_headers, session, test_account):
        """测试启用 API 访问"""
        from models import App, AppMode, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        app = App(name="Test App", tenant_id=tenant.id, mode=AppMode.CHAT, enable_api=False, created_by=test_account.id)
        session.add(app)
        session.commit()

        # 启用 API
        response = client_integration.post(f"/api/console/apps/{app.id}/api/enable", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["enable_api"] is True

    def test_disable_api_success(self, client_integration, auth_headers, session, test_account):
        """测试禁用 API 访问"""
        from models import App, AppMode, TenantAccountJoin, TenantRole

        tenant = Tenant(name="Test Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(tenant)
        session.flush()

        join = TenantAccountJoin(tenant_id=tenant.id, account_id=test_account.id, role=TenantRole.OWNER)
        session.add(join)

        app = App(name="Test App", tenant_id=tenant.id, mode=AppMode.CHAT, enable_api=True, created_by=test_account.id)
        session.add(app)
        session.commit()

        # 禁用 API
        response = client_integration.post(f"/api/console/apps/{app.id}/api/disable", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["enable_api"] is False
