"""
认证 API 集成测试

测试认证相关的 HTTP 端点
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import jwt
import pytest

from configs.app_config import Config
from models import Account, AccountStatus


class TestAuthAPI:
    """认证 API 测试类"""

    def test_register_success(self, client_integration, session):
        """测试成功注册"""
        response = client_integration.post(
            "/api/console/auth/register",
            json={"email": "test@example.com", "password": "password123", "name": "Test User"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["status"] == "active"
        assert "id" in data

        # 验证数据库中有该用户
        account = session.query(Account).filter_by(email="test@example.com").first()
        assert account is not None
        assert account.name == "Test User"

    def test_register_missing_fields(self, client_integration):
        """测试注册缺少必需字段"""
        # 缺少 password
        response = client_integration.post(
            "/api/console/auth/register", json={"email": "test@example.com", "name": "Test User"}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_register_invalid_email(self, client_integration):
        """测试注册无效邮箱"""
        response = client_integration.post(
            "/api/console/auth/register",
            json={"email": "invalid-email", "password": "password123", "name": "Test User"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_register_weak_password(self, client_integration):
        """测试注册弱密码"""
        response = client_integration.post(
            "/api/console/auth/register",
            json={"email": "test@example.com", "password": "123", "name": "Test User"},  # 少于 6 位
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_register_duplicate_email(self, client_integration, test_account):
        """测试注册重复邮箱"""
        response = client_integration.post(
            "/api/console/auth/register",
            json={"email": test_account.email, "password": "password123", "name": "Test User"},  # 使用已存在的邮箱
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["code"] == "RESOURCE_CONFLICT"

    def test_login_success(self, client_integration, test_account):
        """测试成功登录"""
        response = client_integration.post(
            "/api/console/auth/login",
            json={"email": test_account.email, "password": "test_password"},  # 使用 fixture 中的密码
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "account" in data
        assert "token" in data
        assert data["account"]["email"] == test_account.email

        # 验证 token 有效
        token = data["token"]
        from tests.conftest import TestConfig

        test_config = TestConfig()
        decoded = jwt.decode(token, test_config.SECRET_KEY, algorithms=["HS256"])
        assert decoded["email"] == test_account.email

    def test_login_missing_fields(self, client_integration):
        """测试登录缺少字段"""
        response = client_integration.post(
            "/api/console/auth/login",
            json={
                "email": "test@example.com"
                # 缺少 password
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_login_wrong_password(self, client_integration, test_account):
        """测试登录错误密码"""
        response = client_integration.post(
            "/api/console/auth/login", json={"email": test_account.email, "password": "wrong_password"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data["code"] == "AUTHENTICATION_ERROR"

    def test_login_nonexistent_account(self, client_integration):
        """测试登录不存在的账户"""
        response = client_integration.post(
            "/api/console/auth/login", json={"email": "nonexistent@example.com", "password": "password123"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data["code"] == "AUTHENTICATION_ERROR"

    def test_login_banned_account(self, client_integration, session, test_account):
        """测试登录被封禁的账户"""
        # 封禁账户
        test_account.status = AccountStatus.BANNED
        session.commit()

        response = client_integration.post(
            "/api/console/auth/login", json={"email": test_account.email, "password": "test_password"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data["code"] == "AUTHENTICATION_ERROR"

    def test_get_me_success(self, client_integration, auth_headers):
        """测试获取当前用户成功"""
        response = client_integration.get("/api/console/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "id" in data
        assert "email" in data
        assert "name" in data
        assert "status" in data

    def test_get_me_without_token(self, client_integration):
        """测试未提供 token 获取当前用户"""
        response = client_integration.get("/api/console/auth/me")

        assert response.status_code == 401
        data = response.get_json()
        assert data["code"] == "UNAUTHORIZED"

    def test_get_me_invalid_token(self, client_integration):
        """测试使用无效 token 获取当前用户"""
        response = client_integration.get("/api/console/auth/me", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == 401
        data = response.get_json()
        assert data["code"] == "UNAUTHORIZED"

    def test_get_me_expired_token(self, client_integration, test_account):
        """测试使用过期 token 获取当前用户"""
        # 创建一个已过期的 token
        from tests.conftest import TestConfig

        test_config = TestConfig()
        expired_token = jwt.encode(
            {
                "account_id": str(test_account.id),
                "email": test_account.email,
                "exp": datetime.utcnow() - timedelta(hours=1),  # 1 小时前过期
                "iat": datetime.utcnow() - timedelta(hours=2),
            },
            test_config.SECRET_KEY,
            algorithm="HS256",
        )

        response = client_integration.get("/api/console/auth/me", headers={"Authorization": f"Bearer {expired_token}"})

        assert response.status_code == 401
        data = response.get_json()
        assert data["code"] == "UNAUTHORIZED"

    def test_logout_success(self, client_integration, auth_headers):
        """测试登出成功"""
        response = client_integration.post("/api/console/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Logged out successfully"

    def test_logout_without_token(self, client_integration):
        """测试未登录时登出"""
        response = client_integration.post("/api/console/auth/logout")

        assert response.status_code == 401

    def test_change_password_success(self, client_integration, auth_headers, test_account):
        """测试修改密码成功"""
        response = client_integration.post(
            "/api/console/auth/password/change",
            headers=auth_headers,
            json={"old_password": "test_password", "new_password": "new_password123"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Password changed successfully"

        # 验证可以用新密码登录
        login_response = client_integration.post(
            "/api/console/auth/login", json={"email": test_account.email, "password": "new_password123"}
        )
        assert login_response.status_code == 200

    def test_change_password_wrong_old_password(self, client_integration, auth_headers):
        """测试修改密码时旧密码错误"""
        response = client_integration.post(
            "/api/console/auth/password/change",
            headers=auth_headers,
            json={"old_password": "wrong_password", "new_password": "new_password123"},
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data["code"] == "AUTHENTICATION_ERROR"

    def test_change_password_weak_new_password(self, client_integration, auth_headers):
        """测试修改密码时新密码太弱"""
        response = client_integration.post(
            "/api/console/auth/password/change",
            headers=auth_headers,
            json={"old_password": "test_password", "new_password": "123"},  # 少于 6 位
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_change_password_missing_fields(self, client_integration, auth_headers):
        """测试修改密码缺少字段"""
        response = client_integration.post(
            "/api/console/auth/password/change",
            headers=auth_headers,
            json={
                "old_password": "test_password"
                # 缺少 new_password
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_change_password_without_auth(self, client_integration):
        """测试未认证时修改密码"""
        response = client_integration.post(
            "/api/console/auth/password/change",
            json={"old_password": "test_password", "new_password": "new_password123"},
        )

        assert response.status_code == 401

    def test_reset_password_success(self, client_integration, test_account):
        """测试重置密码成功"""
        response = client_integration.post(
            "/api/console/auth/password/reset", json={"email": test_account.email, "new_password": "reset_password123"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Password reset successfully"

        # 验证可以用新密码登录
        login_response = client_integration.post(
            "/api/console/auth/login", json={"email": test_account.email, "password": "reset_password123"}
        )
        assert login_response.status_code == 200

    def test_reset_password_missing_fields(self, client_integration):
        """测试重置密码缺少字段"""
        response = client_integration.post(
            "/api/console/auth/password/reset",
            json={
                "email": "test@example.com"
                # 缺少 new_password
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
