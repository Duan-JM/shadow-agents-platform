"""
Account 模型测试
"""
import pytest
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from models.account import Account, AccountStatus
from extensions.ext_database import db


class TestAccountModel:
    """Account 模型测试类"""
    
    def test_create_account(self, app, factory):
        """测试创建账户"""
        with app.app_context():
            # 创建账户
            account = factory.create_account(
                email="test@example.com",
                password="password123",
                name="Test User"
            )
            
            # 验证
            assert account.id is not None
            assert account.email == "test@example.com"
            assert account.name == "Test User"
            assert account.status == AccountStatus.ACTIVE
            assert account.created_at is not None
            assert account.updated_at is not None
    
    def test_account_password_hash(self, app):
        """测试密码哈希"""
        with app.app_context():
            # 创建账户
            password = "securepassword123"
            account = Account(
                email="test@example.com",
                password_hash=generate_password_hash(password),
                name="Test User"
            )
            db.session.add(account)
            db.session.commit()
            
            # 验证密码哈希
            assert account.password_hash != password
            assert check_password_hash(account.password_hash, password)
            assert not check_password_hash(account.password_hash, "wrongpassword")
    
    def test_account_unique_email(self, app, factory):
        """测试邮箱唯一性"""
        with app.app_context():
            # 创建第一个账户
            factory.create_account(email="test@example.com")
            
            # 尝试创建相同邮箱的账户
            with pytest.raises(Exception):  # IntegrityError
                factory.create_account(email="test@example.com")
                db.session.commit()
    
    def test_account_status(self, app, factory):
        """测试账户状态"""
        with app.app_context():
            # 激活状态
            active_account = factory.create_account(
                email="active@example.com",
                status=AccountStatus.ACTIVE
            )
            assert active_account.is_active
            assert not active_account.is_banned
            
            # 封禁状态
            banned_account = factory.create_account(
                email="banned@example.com",
                status=AccountStatus.BANNED
            )
            assert not banned_account.is_active
            assert banned_account.is_banned
    
    def test_account_to_dict(self, app, factory):
        """测试转换为字典"""
        with app.app_context():
            account = factory.create_account()
            
            data = account.to_dict()
            
            # 验证字段
            assert "id" in data
            assert "email" in data
            assert "name" in data
            assert "status" in data
            assert "created_at" in data
            assert "updated_at" in data
            
            # 验证不包含敏感信息
            assert "password_hash" not in data
            
            # 验证数据类型
            assert isinstance(data["id"], str)
            assert isinstance(data["email"], str)
            assert isinstance(data["status"], str)
    
    def test_account_last_login(self, app, factory):
        """测试最后登录信息"""
        with app.app_context():
            account = factory.create_account()
            
            # 初始状态
            assert account.last_login_at is None
            assert account.last_login_ip is None
            
            # 更新登录信息
            account.last_login_at = datetime.utcnow()
            account.last_login_ip = "192.168.1.1"
            db.session.commit()
            
            # 验证更新
            assert account.last_login_at is not None
            assert account.last_login_ip == "192.168.1.1"
    
    def test_account_avatar(self, app, factory):
        """测试头像"""
        with app.app_context():
            # 无头像
            account1 = factory.create_account(email="test1@example.com")
            assert account1.avatar is None
            
            # 有头像
            account2 = factory.create_account(
                email="test2@example.com",
                avatar="https://example.com/avatar.png"
            )
            assert account2.avatar == "https://example.com/avatar.png"
    
    def test_account_repr(self, app, factory):
        """测试字符串表示"""
        with app.app_context():
            account = factory.create_account(email="test@example.com")
            
            repr_str = repr(account)
            assert "Account" in repr_str
            assert "test@example.com" in repr_str
