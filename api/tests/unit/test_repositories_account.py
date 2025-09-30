"""
Account Repository 测试
"""
import pytest
from werkzeug.security import generate_password_hash

from models.account import Account, AccountStatus
from repositories.account_repository import AccountRepository


class TestAccountRepository:
    """Account Repository 测试类"""
    
    def test_create_account(self, app, factory):
        """测试创建账户"""
        with app.app_context():
            repo = AccountRepository()
            
            account = repo.create(
                email="test@example.com",
                password_hash=generate_password_hash("password123"),
                name="Test User"
            )
            
            assert account.id is not None
            assert account.email == "test@example.com"
            assert account.name == "Test User"
    
    def test_get_by_id(self, app, factory):
        """测试根据 ID 获取"""
        with app.app_context():
            repo = AccountRepository()
            account = factory.create_account()
            
            found = repo.get_by_id(account.id)
            
            assert found is not None
            assert found.id == account.id
            assert found.email == account.email
    
    def test_get_by_email(self, app, factory):
        """测试根据邮箱获取"""
        with app.app_context():
            repo = AccountRepository()
            account = factory.create_account(email="unique@example.com")
            
            found = repo.get_by_email("unique@example.com")
            
            assert found is not None
            assert found.id == account.id
            assert found.email == "unique@example.com"
    
    def test_email_exists(self, app, factory):
        """测试邮箱是否存在"""
        with app.app_context():
            repo = AccountRepository()
            factory.create_account(email="exists@example.com")
            
            assert repo.email_exists("exists@example.com") is True
            assert repo.email_exists("notexists@example.com") is False
    
    def test_get_active_accounts(self, app, factory):
        """测试获取激活账户"""
        with app.app_context():
            repo = AccountRepository()
            
            # 创建不同状态的账户
            factory.create_account(email="active1@example.com", status=AccountStatus.ACTIVE)
            factory.create_account(email="active2@example.com", status=AccountStatus.ACTIVE)
            factory.create_account(email="banned@example.com", status=AccountStatus.BANNED)
            
            active_accounts = repo.get_active_accounts()
            
            assert len(active_accounts) == 2
            assert all(acc.status == AccountStatus.ACTIVE for acc in active_accounts)
    
    def test_get_by_status(self, app, factory):
        """测试根据状态获取"""
        with app.app_context():
            repo = AccountRepository()
            
            factory.create_account(email="banned1@example.com", status=AccountStatus.BANNED)
            factory.create_account(email="banned2@example.com", status=AccountStatus.BANNED)
            factory.create_account(email="active@example.com", status=AccountStatus.ACTIVE)
            
            banned_accounts = repo.get_by_status(AccountStatus.BANNED)
            
            assert len(banned_accounts) == 2
            assert all(acc.status == AccountStatus.BANNED for acc in banned_accounts)
    
    def test_update(self, app, factory):
        """测试更新账户"""
        with app.app_context():
            repo = AccountRepository()
            account = factory.create_account(name="Old Name")
            
            updated = repo.update(account.id, name="New Name")
            
            assert updated is not None
            assert updated.name == "New Name"
    
    def test_update_status(self, app, factory):
        """测试更新状态"""
        with app.app_context():
            repo = AccountRepository()
            account = factory.create_account(status=AccountStatus.ACTIVE)
            
            updated = repo.update_status(account.id, AccountStatus.INACTIVE)
            
            assert updated is not None
            assert updated.status == AccountStatus.INACTIVE
    
    def test_ban_account(self, app, factory):
        """测试封禁账户"""
        with app.app_context():
            repo = AccountRepository()
            account = factory.create_account(status=AccountStatus.ACTIVE)
            
            banned = repo.ban_account(account.id)
            
            assert banned is not None
            assert banned.status == AccountStatus.BANNED
    
    def test_activate_account(self, app, factory):
        """测试激活账户"""
        with app.app_context():
            repo = AccountRepository()
            account = factory.create_account(status=AccountStatus.INACTIVE)
            
            activated = repo.activate_account(account.id)
            
            assert activated is not None
            assert activated.status == AccountStatus.ACTIVE
    
    def test_delete(self, app, factory):
        """测试删除账户"""
        with app.app_context():
            repo = AccountRepository()
            account = factory.create_account()
            
            result = repo.delete(account.id)
            
            assert result is True
            assert repo.get_by_id(account.id) is None
    
    def test_count(self, app, factory):
        """测试统计数量"""
        with app.app_context():
            repo = AccountRepository()
            
            factory.create_account(email="user1@example.com")
            factory.create_account(email="user2@example.com")
            factory.create_account(email="user3@example.com")
            
            count = repo.count()
            
            assert count == 3
    
    def test_exists(self, app, factory):
        """测试记录是否存在"""
        with app.app_context():
            repo = AccountRepository()
            account = factory.create_account()
            
            assert repo.exists(account.id) is True
    
    def test_get_all(self, app, factory):
        """测试获取所有记录"""
        with app.app_context():
            repo = AccountRepository()
            
            factory.create_account(email="user1@example.com")
            factory.create_account(email="user2@example.com")
            
            all_accounts = repo.get_all()
            
            assert len(all_accounts) == 2
