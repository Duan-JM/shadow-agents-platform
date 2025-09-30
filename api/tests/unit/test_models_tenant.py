"""
Tenant 模型测试
"""
import pytest
from datetime import datetime

from models.tenant import Tenant, TenantStatus, TenantPlan, TenantAccountJoin, TenantRole
from extensions.ext_database import db


class TestTenantModel:
    """Tenant 模型测试类"""
    
    def test_create_tenant(self, app, factory):
        """测试创建租户"""
        with app.app_context():
            tenant = factory.create_tenant(name="Test Tenant")
            
            # 验证
            assert tenant.id is not None
            assert tenant.name == "Test Tenant"
            assert tenant.plan == TenantPlan.FREE
            assert tenant.status == TenantStatus.ACTIVE
            assert tenant.created_at is not None
            assert tenant.updated_at is not None
    
    def test_tenant_plans(self, app, factory):
        """测试租户套餐"""
        with app.app_context():
            # FREE 套餐
            free_tenant = factory.create_tenant(
                name="Free Tenant",
                plan=TenantPlan.FREE
            )
            assert free_tenant.plan == TenantPlan.FREE
            
            # PRO 套餐
            pro_tenant = factory.create_tenant(
                name="Pro Tenant",
                plan=TenantPlan.PRO
            )
            assert pro_tenant.plan == TenantPlan.PRO
            
            # ENTERPRISE 套餐
            enterprise_tenant = factory.create_tenant(
                name="Enterprise Tenant",
                plan=TenantPlan.ENTERPRISE
            )
            assert enterprise_tenant.plan == TenantPlan.ENTERPRISE
    
    def test_tenant_status(self, app, factory):
        """测试租户状态"""
        with app.app_context():
            # 激活状态
            active_tenant = factory.create_tenant(
                name="Active Tenant",
                status=TenantStatus.ACTIVE
            )
            assert active_tenant.is_active
            
            # 暂停状态
            suspended_tenant = factory.create_tenant(
                name="Suspended Tenant",
                status=TenantStatus.SUSPENDED
            )
            assert not suspended_tenant.is_active
    
    def test_tenant_account_join(self, app, factory):
        """测试租户-账户关联"""
        with app.app_context():
            account = factory.create_account()
            tenant = factory.create_tenant()
            
            # 创建关联
            join = factory.create_tenant_account_join(
                tenant=tenant,
                account=account,
                role=TenantRole.OWNER
            )
            
            # 验证
            assert join.tenant_id == tenant.id
            assert join.account_id == account.id
            assert join.role == TenantRole.OWNER
            assert join.created_at is not None
    
    def test_tenant_multiple_accounts(self, app, factory):
        """测试租户多个成员"""
        with app.app_context():
            tenant = factory.create_tenant()
            owner = factory.create_account(email="owner@example.com")
            admin = factory.create_account(email="admin@example.com")
            member = factory.create_account(email="member@example.com")
            
            # 创建关联
            factory.create_tenant_account_join(tenant, owner, role=TenantRole.OWNER)
            factory.create_tenant_account_join(tenant, admin, role=TenantRole.ADMIN)
            factory.create_tenant_account_join(tenant, member, role=TenantRole.MEMBER)
            
            # 验证
            assert len(tenant.account_joins) == 3
    
    def test_account_multiple_tenants(self, app, factory):
        """测试账户加入多个租户"""
        with app.app_context():
            account = factory.create_account()
            tenant1 = factory.create_tenant(name="Tenant 1")
            tenant2 = factory.create_tenant(name="Tenant 2")
            
            # 创建关联
            factory.create_tenant_account_join(tenant1, account, role=TenantRole.OWNER)
            factory.create_tenant_account_join(tenant2, account, role=TenantRole.MEMBER)
            
            # 验证
            assert len(account.tenant_joins) == 2
    
    def test_tenant_account_unique_constraint(self, app, factory):
        """测试租户-账户唯一性约束"""
        with app.app_context():
            tenant = factory.create_tenant()
            account = factory.create_account()
            
            # 创建第一个关联
            factory.create_tenant_account_join(tenant, account)
            
            # 尝试创建重复关联
            with pytest.raises(Exception):  # IntegrityError
                factory.create_tenant_account_join(tenant, account)
                db.session.commit()
    
    def test_tenant_account_role_properties(self, app, factory):
        """测试角色属性"""
        with app.app_context():
            tenant = factory.create_tenant()
            account = factory.create_account()
            
            # OWNER 角色
            owner_join = factory.create_tenant_account_join(
                tenant, account, role=TenantRole.OWNER
            )
            assert owner_join.is_owner
            assert owner_join.is_admin  # OWNER 也是 ADMIN
            
            # ADMIN 角色
            admin = factory.create_account(email="admin@example.com")
            admin_join = factory.create_tenant_account_join(
                tenant, admin, role=TenantRole.ADMIN
            )
            assert not admin_join.is_owner
            assert admin_join.is_admin
            
            # MEMBER 角色
            member = factory.create_account(email="member@example.com")
            member_join = factory.create_tenant_account_join(
                tenant, member, role=TenantRole.MEMBER
            )
            assert not member_join.is_owner
            assert not member_join.is_admin
    
    def test_tenant_cascade_delete(self, app, factory):
        """测试级联删除"""
        with app.app_context():
            tenant = factory.create_tenant()
            account = factory.create_account()
            factory.create_tenant_account_join(tenant, account)
            
            # 删除租户
            tenant_id = tenant.id
            db.session.delete(tenant)
            db.session.commit()
            
            # 验证关联也被删除
            joins = TenantAccountJoin.query.filter_by(tenant_id=tenant_id).all()
            assert len(joins) == 0
    
    def test_tenant_to_dict(self, app, factory):
        """测试转换为字典"""
        with app.app_context():
            tenant = factory.create_tenant()
            
            data = tenant.to_dict()
            
            # 验证字段
            assert "id" in data
            assert "name" in data
            assert "plan" in data
            assert "status" in data
            assert "created_at" in data
            assert "updated_at" in data
            
            # 验证数据类型
            assert isinstance(data["id"], str)
            assert isinstance(data["name"], str)
            assert isinstance(data["plan"], str)
            assert isinstance(data["status"], str)
