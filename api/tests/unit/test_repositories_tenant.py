"""
Tenant Repository 测试
"""
import pytest

from models.tenant import Tenant, TenantStatus, TenantPlan, TenantRole
from repositories.tenant_repository import TenantRepository


class TestTenantRepository:
    """Tenant Repository 测试类"""
    
    def test_create_tenant(self, app, factory):
        """测试创建租户"""
        with app.app_context():
            repo = TenantRepository()
            
            tenant = repo.create(
                name="Test Tenant",
                plan=TenantPlan.FREE
            )
            
            assert tenant.id is not None
            assert tenant.name == "Test Tenant"
            assert tenant.plan == TenantPlan.FREE
    
    def test_get_by_name(self, app, factory):
        """测试根据名称获取"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant(name="Unique Tenant")
            
            found = repo.get_by_name("Unique Tenant")
            
            assert found is not None
            assert found.id == tenant.id
    
    def test_get_active_tenants(self, app, factory):
        """测试获取激活租户"""
        with app.app_context():
            repo = TenantRepository()
            
            factory.create_tenant(name="Active 1", status=TenantStatus.ACTIVE)
            factory.create_tenant(name="Active 2", status=TenantStatus.ACTIVE)
            factory.create_tenant(name="Suspended", status=TenantStatus.SUSPENDED)
            
            active_tenants = repo.get_active_tenants()
            
            assert len(active_tenants) == 2
            assert all(t.status == TenantStatus.ACTIVE for t in active_tenants)
    
    def test_get_by_plan(self, app, factory):
        """测试根据套餐获取"""
        with app.app_context():
            repo = TenantRepository()
            
            factory.create_tenant(name="Free 1", plan=TenantPlan.FREE)
            factory.create_tenant(name="Free 2", plan=TenantPlan.FREE)
            factory.create_tenant(name="Pro", plan=TenantPlan.PRO)
            
            free_tenants = repo.get_by_plan(TenantPlan.FREE)
            
            assert len(free_tenants) == 2
            assert all(t.plan == TenantPlan.FREE for t in free_tenants)
    
    def test_get_tenants_by_account(self, app, factory):
        """测试获取账户的租户"""
        with app.app_context():
            repo = TenantRepository()
            account = factory.create_account()
            tenant1 = factory.create_tenant(name="Tenant 1")
            tenant2 = factory.create_tenant(name="Tenant 2")
            
            factory.create_tenant_account_join(tenant1, account)
            factory.create_tenant_account_join(tenant2, account)
            
            tenants = repo.get_tenants_by_account(account.id)
            
            assert len(tenants) == 2
            assert tenant1.id in [t.id for t in tenants]
            assert tenant2.id in [t.id for t in tenants]
    
    def test_add_member(self, app, factory):
        """测试添加成员"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant()
            account = factory.create_account()
            
            join = repo.add_member(tenant.id, account.id, TenantRole.MEMBER)
            
            assert join is not None
            assert join.tenant_id == tenant.id
            assert join.account_id == account.id
            assert join.role == TenantRole.MEMBER
    
    def test_add_member_duplicate(self, app, factory):
        """测试添加重复成员"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant()
            account = factory.create_account()
            
            # 第一次添加成功
            join1 = repo.add_member(tenant.id, account.id)
            assert join1 is not None
            
            # 第二次添加失败
            join2 = repo.add_member(tenant.id, account.id)
            assert join2 is None
    
    def test_remove_member(self, app, factory):
        """测试移除成员"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant()
            account = factory.create_account()
            factory.create_tenant_account_join(tenant, account)
            
            result = repo.remove_member(tenant.id, account.id)
            
            assert result is True
            assert repo.is_member(tenant.id, account.id) is False
    
    def test_get_member_role(self, app, factory):
        """测试获取成员角色"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant()
            account = factory.create_account()
            factory.create_tenant_account_join(tenant, account, role=TenantRole.ADMIN)
            
            role = repo.get_member_role(tenant.id, account.id)
            
            assert role == TenantRole.ADMIN
    
    def test_update_member_role(self, app, factory):
        """测试更新成员角色"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant()
            account = factory.create_account()
            factory.create_tenant_account_join(tenant, account, role=TenantRole.MEMBER)
            
            updated = repo.update_member_role(tenant.id, account.id, TenantRole.ADMIN)
            
            assert updated is not None
            assert updated.role == TenantRole.ADMIN
    
    def test_get_tenant_members(self, app, factory):
        """测试获取租户成员"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant()
            account1 = factory.create_account(email="user1@example.com")
            account2 = factory.create_account(email="user2@example.com")
            
            factory.create_tenant_account_join(tenant, account1)
            factory.create_tenant_account_join(tenant, account2)
            
            members = repo.get_tenant_members(tenant.id)
            
            assert len(members) == 2
            assert account1.id in [m.id for m in members]
            assert account2.id in [m.id for m in members]
    
    def test_is_member(self, app, factory):
        """测试是否为成员"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant()
            account = factory.create_account()
            factory.create_tenant_account_join(tenant, account)
            
            assert repo.is_member(tenant.id, account.id) is True
    
    def test_update(self, app, factory):
        """测试更新租户"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant(name="Old Name")
            
            updated = repo.update(tenant.id, name="New Name")
            
            assert updated is not None
            assert updated.name == "New Name"
    
    def test_delete(self, app, factory):
        """测试删除租户"""
        with app.app_context():
            repo = TenantRepository()
            tenant = factory.create_tenant()
            
            result = repo.delete(tenant.id)
            
            assert result is True
            assert repo.get_by_id(tenant.id) is None
