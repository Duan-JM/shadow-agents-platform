"""
租户 API 集成测试

测试租户相关的 HTTP 端点
"""

import pytest

from models import Tenant, TenantPlan, TenantRole, TenantStatus


class TestTenantAPI:
    """租户 API 测试类"""

    def test_create_tenant_success(self, client_integration, auth_headers):
        """测试成功创建租户"""
        response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "My Test Tenant", "plan": "free"}
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "My Test Tenant"
        assert data["plan"] == "free"
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data

    def test_create_tenant_missing_name(self, client_integration, auth_headers):
        """测试创建租户缺少名称"""
        response = client_integration.post("/api/console/tenants", headers=auth_headers, json={"plan": "free"})

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_create_tenant_duplicate_name(self, client_integration, auth_headers, session):
        """测试创建重复名称的租户"""
        # 先创建一个租户
        client_integration.post("/api/console/tenants", headers=auth_headers, json={"name": "Duplicate Tenant"})

        # 尝试创建同名租户
        response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Duplicate Tenant"}
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["code"] == "RESOURCE_CONFLICT"

    def test_create_tenant_without_auth(self, client_integration):
        """测试未认证创建租户"""
        response = client_integration.post("/api/console/tenants", json={"name": "Test Tenant"})

        assert response.status_code == 401

    def test_get_tenants_success(self, client_integration, auth_headers, session, test_account):
        """测试获取租户列表"""
        # 先创建几个租户
        client_integration.post("/api/console/tenants", headers=auth_headers, json={"name": "Tenant 1"})
        client_integration.post("/api/console/tenants", headers=auth_headers, json={"name": "Tenant 2"})

        # 获取租户列表
        response = client_integration.get("/api/console/tenants", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2

        # 验证返回的租户信息
        tenant_names = [t["name"] for t in data]
        assert "Tenant 1" in tenant_names
        assert "Tenant 2" in tenant_names

        # 验证每个租户都有角色信息（创建者应该是 OWNER）
        for tenant in data:
            assert "role" in tenant
            assert tenant["role"] == "owner"

    def test_get_tenants_without_auth(self, client_integration):
        """测试未认证获取租户列表"""
        response = client_integration.get("/api/console/tenants")

        assert response.status_code == 401

    def test_get_tenant_success(self, client_integration, auth_headers, session):
        """测试获取租户详情"""
        # 先创建一个租户
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Detail Tenant"}
        )
        tenant_id = create_response.get_json()["id"]

        # 获取租户详情
        response = client_integration.get(f"/api/console/tenants/{tenant_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == tenant_id
        assert data["name"] == "Detail Tenant"
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_tenant_not_member(self, client_integration, auth_headers, session, test_account):
        """测试获取非成员租户详情"""
        # 创建另一个账户和租户
        import uuid

        from werkzeug.security import generate_password_hash

        from models import Account, AccountStatus

        other_account = Account(
            id=uuid.uuid4(),
            email="other@example.com",
            password_hash=generate_password_hash("password"),
            name="Other User",
            status=AccountStatus.ACTIVE,
        )
        session.add(other_account)

        from models import Tenant, TenantPlan, TenantStatus

        other_tenant = Tenant(id=uuid.uuid4(), name="Other Tenant", plan=TenantPlan.FREE, status=TenantStatus.ACTIVE)
        session.add(other_tenant)

        from models import TenantAccountJoin

        join = TenantAccountJoin(tenant_id=other_tenant.id, account_id=other_account.id, role=TenantRole.OWNER)
        session.add(join)
        session.commit()

        # 尝试获取其他人的租户
        response = client_integration.get(f"/api/console/tenants/{other_tenant.id}", headers=auth_headers)

        assert response.status_code == 403
        data = response.get_json()
        assert data["code"] == "AUTHORIZATION_ERROR"

    def test_get_tenant_not_found(self, client_integration, auth_headers):
        """测试获取不存在的租户"""
        import uuid

        fake_id = str(uuid.uuid4())

        response = client_integration.get(f"/api/console/tenants/{fake_id}", headers=auth_headers)

        assert response.status_code == 404
        data = response.get_json()
        assert data["code"] == "RESOURCE_NOT_FOUND"

    def test_update_tenant_success(self, client_integration, auth_headers, session):
        """测试更新租户信息（仅 OWNER）"""
        # 先创建一个租户
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Old Name"}
        )
        tenant_id = create_response.get_json()["id"]

        # 更新租户名称
        response = client_integration.put(
            f"/api/console/tenants/{tenant_id}", headers=auth_headers, json={"name": "New Name"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "New Name"

    def test_update_tenant_not_owner(self, client_integration, auth_headers, session, test_account):
        """测试非 OWNER 更新租户"""
        # 创建租户（test_account 是 OWNER）
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Test Tenant"}
        )
        tenant_id = create_response.get_json()["id"]

        # 创建另一个用户作为 ADMIN
        import uuid

        from werkzeug.security import generate_password_hash

        from models import Account, AccountStatus

        admin_account = Account(
            id=uuid.uuid4(),
            email="admin@example.com",
            password_hash=generate_password_hash("password"),
            name="Admin User",
            status=AccountStatus.ACTIVE,
        )
        session.add(admin_account)
        session.commit()

        # 添加为 ADMIN
        client_integration.post(
            f"/api/console/tenants/{tenant_id}/members",
            headers=auth_headers,
            json={"account_id": str(admin_account.id), "role": "admin"},
        )

        # 使用 ADMIN 账户的 token 尝试更新
        from datetime import datetime, timedelta

        import jwt

        from tests.conftest import TestConfig

        test_config = TestConfig()
        admin_token = jwt.encode(
            {
                "account_id": str(admin_account.id),
                "email": admin_account.email,
                "exp": datetime.utcnow() + timedelta(hours=24),
                "iat": datetime.utcnow(),
            },
            test_config.SECRET_KEY,
            algorithm="HS256",
        )

        admin_headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

        response = client_integration.put(
            f"/api/console/tenants/{tenant_id}", headers=admin_headers, json={"name": "Should Fail"}
        )

        assert response.status_code == 403

    def test_get_tenant_members_success(self, client_integration, auth_headers, session, test_account):
        """测试获取租户成员列表"""
        # 创建租户
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Members Tenant"}
        )
        tenant_id = create_response.get_json()["id"]

        # 获取成员列表
        response = client_integration.get(f"/api/console/tenants/{tenant_id}/members", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1  # 只有创建者
        assert data[0]["email"] == test_account.email
        assert data[0]["role"] == "owner"

    def test_add_member_success(self, client_integration, auth_headers, session, test_account):
        """测试添加租户成员"""
        # 创建租户
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Add Member Tenant"}
        )
        tenant_id = create_response.get_json()["id"]

        # 创建另一个账户
        import uuid

        from werkzeug.security import generate_password_hash

        from models import Account, AccountStatus

        new_member = Account(
            id=uuid.uuid4(),
            email="newmember@example.com",
            password_hash=generate_password_hash("password"),
            name="New Member",
            status=AccountStatus.ACTIVE,
        )
        session.add(new_member)
        session.commit()

        # 添加成员
        response = client_integration.post(
            f"/api/console/tenants/{tenant_id}/members",
            headers=auth_headers,
            json={"account_id": str(new_member.id), "role": "member"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Member added successfully"

        # 验证成员已添加
        members_response = client_integration.get(f"/api/console/tenants/{tenant_id}/members", headers=auth_headers)
        members = members_response.get_json()
        assert len(members) == 2

    def test_add_member_duplicate(self, client_integration, auth_headers, session, test_account):
        """测试添加重复成员"""
        # 创建租户
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Duplicate Member Tenant"}
        )
        tenant_id = create_response.get_json()["id"]

        # 创建新成员
        import uuid

        from werkzeug.security import generate_password_hash

        from models import Account, AccountStatus

        new_member = Account(
            id=uuid.uuid4(),
            email="member@example.com",
            password_hash=generate_password_hash("password"),
            name="Member",
            status=AccountStatus.ACTIVE,
        )
        session.add(new_member)
        session.commit()

        # 第一次添加
        client_integration.post(
            f"/api/console/tenants/{tenant_id}/members",
            headers=auth_headers,
            json={"account_id": str(new_member.id), "role": "member"},
        )

        # 第二次添加（应该失败）
        response = client_integration.post(
            f"/api/console/tenants/{tenant_id}/members",
            headers=auth_headers,
            json={"account_id": str(new_member.id), "role": "member"},
        )

        assert response.status_code == 409

    def test_remove_member_success(self, client_integration, auth_headers, session, test_account):
        """测试移除租户成员"""
        # 创建租户
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Remove Member Tenant"}
        )
        tenant_id = create_response.get_json()["id"]

        # 创建并添加成员
        import uuid

        from werkzeug.security import generate_password_hash

        from models import Account, AccountStatus

        member = Account(
            id=uuid.uuid4(),
            email="removeme@example.com",
            password_hash=generate_password_hash("password"),
            name="Remove Me",
            status=AccountStatus.ACTIVE,
        )
        session.add(member)
        session.commit()

        client_integration.post(
            f"/api/console/tenants/{tenant_id}/members",
            headers=auth_headers,
            json={"account_id": str(member.id), "role": "member"},
        )

        # 移除成员
        response = client_integration.delete(
            f"/api/console/tenants/{tenant_id}/members/{member.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Member removed successfully"

        # 验证成员已移除
        members_response = client_integration.get(f"/api/console/tenants/{tenant_id}/members", headers=auth_headers)
        members = members_response.get_json()
        assert len(members) == 1  # 只剩 OWNER

    def test_remove_owner_should_fail(self, client_integration, auth_headers, session, test_account):
        """测试不能移除 OWNER"""
        # 创建租户
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Cannot Remove Owner"}
        )
        tenant_id = create_response.get_json()["id"]

        # 尝试移除自己（OWNER）
        response = client_integration.delete(
            f"/api/console/tenants/{tenant_id}/members/{test_account.id}", headers=auth_headers
        )

        # 应该返回错误（服务层会抛出异常）
        assert response.status_code != 200

    def test_update_member_role_success(self, client_integration, auth_headers, session, test_account):
        """测试更新成员角色（仅 OWNER）"""
        # 创建租户
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "Role Update Tenant"}
        )
        tenant_id = create_response.get_json()["id"]

        # 创建并添加成员
        import uuid

        from werkzeug.security import generate_password_hash

        from models import Account, AccountStatus

        member = Account(
            id=uuid.uuid4(),
            email="member@example.com",
            password_hash=generate_password_hash("password"),
            name="Member",
            status=AccountStatus.ACTIVE,
        )
        session.add(member)
        session.commit()

        client_integration.post(
            f"/api/console/tenants/{tenant_id}/members",
            headers=auth_headers,
            json={"account_id": str(member.id), "role": "member"},
        )

        # 更新角色为 ADMIN
        response = client_integration.put(
            f"/api/console/tenants/{tenant_id}/members/{member.id}/role", headers=auth_headers, json={"role": "admin"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Role updated successfully"

        # 验证角色已更新
        members_response = client_integration.get(f"/api/console/tenants/{tenant_id}/members", headers=auth_headers)
        members = members_response.get_json()
        member_info = [m for m in members if m["email"] == "member@example.com"][0]
        assert member_info["role"] == "admin"

    def test_update_member_role_to_owner_should_fail(self, client_integration, auth_headers, session, test_account):
        """测试不能将成员角色设置为 OWNER"""
        # 创建租户
        create_response = client_integration.post(
            "/api/console/tenants", headers=auth_headers, json={"name": "No Owner Change"}
        )
        tenant_id = create_response.get_json()["id"]

        # 创建并添加成员
        import uuid

        from werkzeug.security import generate_password_hash

        from models import Account, AccountStatus

        member = Account(
            id=uuid.uuid4(),
            email="noowner@example.com",
            password_hash=generate_password_hash("password"),
            name="No Owner",
            status=AccountStatus.ACTIVE,
        )
        session.add(member)
        session.commit()

        client_integration.post(
            f"/api/console/tenants/{tenant_id}/members",
            headers=auth_headers,
            json={"account_id": str(member.id), "role": "member"},
        )

        # 尝试更新为 OWNER（应该失败）
        response = client_integration.put(
            f"/api/console/tenants/{tenant_id}/members/{member.id}/role", headers=auth_headers, json={"role": "owner"}
        )

        # 服务层会抛出业务逻辑错误
        assert response.status_code != 200
