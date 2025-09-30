"""
认证服务

处理用户注册、登录、JWT 令牌等认证相关业务逻辑
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from models.account import Account, AccountStatus
from repositories.account_repository import AccountRepository
from services.exceptions import (
    AuthenticationError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)


class AuthService:
    """认证服务类"""

    def __init__(
        self,
        account_repo: Optional[AccountRepository] = None,
        secret_key: str = "change-me-in-production",
        token_expiry_hours: int = 24,
    ):
        """
        初始化

        参数:
            account_repo: 账户仓储
            secret_key: JWT 密钥
            token_expiry_hours: 令牌过期时间（小时）
        """
        self.account_repo = account_repo or AccountRepository()
        self.secret_key = secret_key
        self.token_expiry_hours = token_expiry_hours

    def register(self, email: str, password: str, name: str) -> Account:
        """
        注册新账户

        参数:
            email: 邮箱
            password: 密码
            name: 姓名

        返回:
            创建的账户

        异常:
            ValidationError: 数据验证失败
            ResourceConflictError: 邮箱已存在
        """
        # 验证邮箱格式
        if not self._validate_email(email):
            raise ValidationError("Invalid email format")

        # 验证密码强度
        if not self._validate_password(password):
            raise ValidationError("Password must be at least 6 characters")

        # 验证姓名
        if not name or len(name.strip()) == 0:
            raise ValidationError("Name is required")

        # 检查邮箱是否已存在
        if self.account_repo.email_exists(email):
            raise ResourceConflictError(f"Email already exists: {email}")

        # 创建账户
        password_hash = generate_password_hash(password)
        account = self.account_repo.create(
            email=email, password_hash=password_hash, name=name.strip(), status=AccountStatus.ACTIVE
        )

        return account

    def login(self, email: str, password: str) -> Tuple[Account, str]:
        """
        登录

        参数:
            email: 邮箱
            password: 密码

        返回:
            (账户, JWT令牌)

        异常:
            AuthenticationError: 认证失败
        """
        # 获取账户
        account = self.account_repo.get_by_email(email)
        if not account:
            raise AuthenticationError("Invalid email or password")

        # 检查账户状态
        if account.status == AccountStatus.BANNED:
            raise AuthenticationError("Account has been banned")

        if account.status == AccountStatus.INACTIVE:
            raise AuthenticationError("Account is inactive")

        # 验证密码
        if not check_password_hash(account.password_hash, password):
            raise AuthenticationError("Invalid email or password")

        # 更新最后登录时间
        self.account_repo.update(account.id, last_login_at=datetime.utcnow())

        # 生成 JWT 令牌
        token = self._generate_token(account.id, account.email)

        return account, token

    def verify_token(self, token: str) -> Account:
        """
        验证 JWT 令牌

        参数:
            token: JWT 令牌

        返回:
            账户实例

        异常:
            AuthenticationError: 令牌无效或过期
        """
        try:
            # 解码令牌
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            account_id = payload.get("account_id")

            if not account_id:
                raise AuthenticationError("Invalid token")

            # 获取账户
            account = self.account_repo.get_by_id(UUID(account_id))
            if not account:
                raise AuthenticationError("Account not found")

            # 检查账户状态
            if not account.is_active:
                raise AuthenticationError("Account is not active")

            return account

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

    def change_password(self, account_id: UUID, old_password: str, new_password: str) -> Account:
        """
        修改密码

        参数:
            account_id: 账户 ID
            old_password: 旧密码
            new_password: 新密码

        返回:
            更新后的账户

        异常:
            ResourceNotFoundError: 账户不存在
            AuthenticationError: 旧密码错误
            ValidationError: 新密码不符合要求
        """
        # 获取账户
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundError("Account", str(account_id))

        # 验证旧密码
        if not check_password_hash(account.password_hash, old_password):
            raise AuthenticationError("Old password is incorrect")

        # 验证新密码
        if not self._validate_password(new_password):
            raise ValidationError("New password must be at least 6 characters")

        # 更新密码
        new_password_hash = generate_password_hash(new_password)
        updated_account = self.account_repo.update(account_id, password_hash=new_password_hash)

        return updated_account

    def reset_password(self, email: str, new_password: str) -> Account:
        """
        重置密码

        参数:
            email: 邮箱
            new_password: 新密码

        返回:
            更新后的账户

        异常:
            ResourceNotFoundError: 账户不存在
            ValidationError: 新密码不符合要求
        """
        # 获取账户
        account = self.account_repo.get_by_email(email)
        if not account:
            raise ResourceNotFoundError("Account", email)

        # 验证新密码
        if not self._validate_password(new_password):
            raise ValidationError("Password must be at least 6 characters")

        # 更新密码
        new_password_hash = generate_password_hash(new_password)
        updated_account = self.account_repo.update(account.id, password_hash=new_password_hash)

        return updated_account

    def _generate_token(self, account_id: UUID, email: str) -> str:
        """
        生成 JWT 令牌

        参数:
            account_id: 账户 ID
            email: 邮箱

        返回:
            JWT 令牌
        """
        payload = {
            "account_id": str(account_id),
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token

    def _validate_email(self, email: str) -> bool:
        """
        验证邮箱格式

        参数:
            email: 邮箱

        返回:
            是否有效
        """
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _validate_password(self, password: str) -> bool:
        """
        验证密码强度

        参数:
            password: 密码

        返回:
            是否有效
        """
        return len(password) >= 6
