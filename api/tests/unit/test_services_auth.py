"""
认证服务测试
"""

import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import jwt
import pytest

from models.account import Account, AccountStatus
from services.auth_service import AuthService
from services.exceptions import (
    AuthenticationError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)


class TestAuthService:
    """认证服务测试类"""

    @pytest.fixture
    def mock_account_repo(self):
        """Mock 账户仓储"""
        return Mock()

    @pytest.fixture
    def auth_service(self, mock_account_repo):
        """创建认证服务实例"""
        return AuthService(account_repo=mock_account_repo, secret_key="test_secret_key", token_expiry_hours=24)

    def test_register_success(self, auth_service, mock_account_repo):
        """测试注册成功"""
        # 准备数据
        email = "test@example.com"
        password = "password123"
        name = "Test User"

        # Mock 仓储方法
        mock_account_repo.email_exists.return_value = False

        # 创建 Mock 账户对象
        mock_account = Mock()
        mock_account.email = email
        mock_account.name = name
        mock_account.status = AccountStatus.ACTIVE
        mock_account_repo.create.return_value = mock_account

        # 执行注册
        account = auth_service.register(email, password, name)

        # 验证结果
        assert account.email == email
        assert account.name == name
        mock_account_repo.email_exists.assert_called_once_with(email)
        mock_account_repo.create.assert_called_once()

        # 验证密码已哈希
        create_args = mock_account_repo.create.call_args[1]
        assert create_args["password_hash"] != password  # 密码应该被哈希

    def test_register_duplicate_email(self, auth_service, mock_account_repo):
        """测试注册重复邮箱"""
        email = "existing@example.com"

        # Mock 仓储返回已存在的账户
        mock_account_repo.find_by_email.return_value = Account(email=email, name="Existing User")

        # 执行注册，应该抛出异常
        with pytest.raises(ResourceConflictError) as exc_info:
            auth_service.register(email, "password123", "New User")

        assert "already exists" in str(exc_info.value).lower()

    def test_register_invalid_email(self, auth_service, mock_account_repo):
        """测试注册无效邮箱"""
        invalid_emails = ["notanemail", "@example.com", "test@", "test @example.com", ""]

        for email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                auth_service.register(email, "password123", "Test User")

            assert "email" in str(exc_info.value).lower()

    def test_register_weak_password(self, auth_service, mock_account_repo):
        """测试注册弱密码"""
        weak_passwords = ["12345", "abc", ""]  # 太短  # 太短  # 空密码

        mock_account_repo.get_by_email.return_value = None

        for password in weak_passwords:
            with pytest.raises(ValidationError) as exc_info:
                auth_service.register("test@example.com", password, "Test User")

            assert "password" in str(exc_info.value).lower()

    def test_login_success(self, auth_service, mock_account_repo):
        """测试登录成功"""
        email = "test@example.com"
        password = "password123"

        # 创建一个带哈希密码的账户
        from werkzeug.security import generate_password_hash

        hashed_password = generate_password_hash(password)

        # 创建 Mock 账户
        mock_account = Mock()
        mock_account.id = uuid.uuid4()
        mock_account.email = email
        mock_account.name = "Test User"
        mock_account.password_hash = hashed_password
        mock_account.status = AccountStatus.ACTIVE

        mock_account_repo.get_by_email.return_value = mock_account
        mock_account_repo.update.return_value = mock_account
        mock_account_repo.get_by_id.return_value = mock_account

        # 执行登录
        logged_in_account, token = auth_service.login(email, password)

        # 验证结果
        assert logged_in_account.email == email
        assert token is not None
        mock_account_repo.update.assert_called_once()  # 应该更新 last_login_at

        # 验证 token 有效
        decoded = auth_service.verify_token(token)
        assert decoded.email == email

    def test_login_wrong_password(self, auth_service, mock_account_repo):
        """测试登录错误密码"""
        email = "test@example.com"

        from werkzeug.security import generate_password_hash

        hashed_password = generate_password_hash("correct_password")

        # 创建 Mock 账户
        mock_account = Mock()
        mock_account.email = email
        mock_account.password_hash = hashed_password
        mock_account.status = AccountStatus.ACTIVE

        mock_account_repo.get_by_email.return_value = mock_account

        # 执行登录，使用错误密码
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.login(email, "wrong_password")

        assert "invalid" in str(exc_info.value).lower()

    def test_login_nonexistent_account(self, auth_service, mock_account_repo):
        """测试登录不存在的账户"""
        mock_account_repo.get_by_email.return_value = None

        with pytest.raises(AuthenticationError):
            auth_service.login("nonexistent@example.com", "password123")

    def test_login_banned_account(self, auth_service, mock_account_repo):
        """测试登录被封禁的账户"""
        from werkzeug.security import generate_password_hash

        # 创建 Mock 账户
        mock_account = Mock()
        mock_account.email = "banned@example.com"
        mock_account.password_hash = generate_password_hash("password123")
        mock_account.status = AccountStatus.BANNED

        mock_account_repo.get_by_email.return_value = mock_account

        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.login("banned@example.com", "password123")

        assert "banned" in str(exc_info.value).lower()

    def test_login_inactive_account(self, auth_service, mock_account_repo):
        """测试登录未激活的账户"""
        from werkzeug.security import generate_password_hash

        # 创建 Mock 账户
        mock_account = Mock()
        mock_account.email = "inactive@example.com"
        mock_account.password_hash = generate_password_hash("password123")
        mock_account.status = AccountStatus.INACTIVE

        mock_account_repo.get_by_email.return_value = mock_account

        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.login("inactive@example.com", "password123")

        assert "inactive" in str(exc_info.value).lower()

    def test_verify_token_valid(self, auth_service, mock_account_repo):
        """测试验证有效 token"""
        email = "test@example.com"
        account_id = uuid.uuid4()

        # 生成 token
        token = auth_service._generate_token(str(account_id), email)

        # Mock 账户
        mock_account = Mock()
        mock_account.id = account_id
        mock_account.email = email
        mock_account.status = AccountStatus.ACTIVE
        mock_account_repo.get_by_id.return_value = mock_account

        # 验证 token
        verified_account = auth_service.verify_token(token)

        assert verified_account.id == account_id
        assert verified_account.email == email

    def test_verify_token_expired(self, auth_service, mock_account_repo):
        """测试验证过期 token"""
        email = "test@example.com"
        account_id = "123"

        # 生成一个已过期的 token
        payload = {
            "account_id": account_id,
            "email": email,
            "exp": datetime.utcnow() - timedelta(hours=1),  # 1小时前过期
            "iat": datetime.utcnow() - timedelta(hours=25),
        }
        token = jwt.encode(payload, auth_service.secret_key, algorithm="HS256")

        # 验证 token，应该抛出异常
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.verify_token(token)

        assert "expired" in str(exc_info.value).lower()

    def test_verify_token_invalid(self, auth_service, mock_account_repo):
        """测试验证无效 token"""
        invalid_tokens = ["invalid.token.here", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid", ""]

        for token in invalid_tokens:
            with pytest.raises(AuthenticationError):
                auth_service.verify_token(token)

    def test_verify_token_nonexistent_account(self, auth_service, mock_account_repo):
        """测试验证不存在账户的 token"""
        email = "test@example.com"
        account_id = uuid.uuid4()

        token = auth_service._generate_token(str(account_id), email)

        # Mock 账户不存在
        mock_account_repo.get_by_id.return_value = None

        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.verify_token(token)

        assert "not found" in str(exc_info.value).lower()

    def test_change_password_success(self, auth_service, mock_account_repo):
        """测试修改密码成功"""
        from werkzeug.security import generate_password_hash

        account_id = uuid.uuid4()
        old_password = "old_password"
        new_password = "new_password123"

        # 创建 Mock 账户
        mock_account = Mock()
        mock_account.id = account_id
        mock_account.email = "test@example.com"
        mock_account.password_hash = generate_password_hash(old_password)

        mock_account_repo.get_by_id.return_value = mock_account
        mock_account_repo.update.return_value = mock_account

        # 执行修改密码
        auth_service.change_password(account_id, old_password, new_password)

        # 验证调用了 update
        mock_account_repo.update.assert_called_once()

        # 验证新密码已哈希
        update_args = mock_account_repo.update.call_args[1]
        assert update_args["password_hash"] != new_password

    def test_change_password_wrong_old_password(self, auth_service, mock_account_repo):
        """测试修改密码时旧密码错误"""
        from werkzeug.security import generate_password_hash

        account_id = uuid.uuid4()

        # 创建 Mock 账户
        mock_account = Mock()
        mock_account.id = account_id
        mock_account.password_hash = generate_password_hash("correct_old_password")

        mock_account_repo.get_by_id.return_value = mock_account

        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.change_password(account_id, "wrong_old_password", "new_password")

        assert "incorrect" in str(exc_info.value).lower()

    def test_change_password_weak_new_password(self, auth_service, mock_account_repo):
        """测试修改密码为弱密码"""
        from werkzeug.security import generate_password_hash

        account_id = uuid.uuid4()
        old_password = "old_password"

        # 创建 Mock 账户
        mock_account = Mock()
        mock_account.id = account_id
        mock_account.password_hash = generate_password_hash(old_password)

        mock_account_repo.get_by_id.return_value = mock_account

        with pytest.raises(ValidationError) as exc_info:
            auth_service.change_password(account_id, old_password, "123")  # 太短

        assert "password" in str(exc_info.value).lower()

    def test_reset_password_success(self, auth_service, mock_account_repo):
        """测试重置密码成功"""
        email = "test@example.com"
        new_password = "new_password123"

        # 创建 Mock 账户
        mock_account = Mock()
        mock_account.email = email

        mock_account_repo.get_by_email.return_value = mock_account
        mock_account_repo.update.return_value = mock_account

        # 执行重置密码
        auth_service.reset_password(email, new_password)

        # 验证调用了 update
        mock_account_repo.update.assert_called_once()
