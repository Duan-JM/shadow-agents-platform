"""
租户服务测试
"""

from unittest.mock import Mock

import pytest

from models.account import Account
from models.tenant import Tenant, TenantPlan, TenantRole, TenantStatus
from services.exceptions import (
    AuthorizationError,
    BusinessLogicError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from services.tenant_service import TenantService


class TestTenantService:
    """租户服务测试类"""

    @pytest.fixture
    def mock_tenant_repo(self):
        """Mock 租户仓储"""
        return Mock()

    @pytest.fixture
    def mock_account_repo(self):
        """Mock 账户仓储"""
        return Mock()

    @pytest.fixture
    def tenant_service(self, mock_tenant_repo, mock_account_repo):
        """创建租户服务实例"""
        return TenantService(tenant_repo=mock_tenant_repo, account_repo=mock_account_repo)

    def test_create_tenant_success(self, tenant_service, mock_tenant_repo, mock_account_repo):
        """测试创建租户成功"""
        name = "Test Tenant"
        owner_id = "owner-123"
        plan = TenantPlan.FREE

        # Mock 账户存在
        owner = Account(id=owner_id, email="owner@example.com", name="Owner")
        mock_account_repo.get_by_id.return_value = owner

        # Mock 租户名称不存在
        mock_tenant_repo.get_by_name.return_value = None

        # Mock 创建租户
        tenant = Tenant(name=name, plan=plan, status=TenantStatus.ACTIVE)
        mock_tenant_repo.create.return_value = tenant

        # 执行创建
        created_tenant = tenant_service.create_tenant(name, owner_id, plan)

        # 验证结果
        assert created_tenant.name == name
        mock_tenant_repo.create.assert_called_once()
        mock_tenant_repo.add_member.assert_called_once_with(tenant.id, owner_id, TenantRole.OWNER)

    def test_create_tenant_duplicate_name(self, tenant_service, mock_tenant_repo, mock_account_repo):
        """测试创建重名租户"""
        name = "Existing Tenant"

        # Mock 账户存在
        mock_account_repo.get_by_id.return_value = Account(id="123")

        # Mock 租户名称已存在
        mock_tenant_repo.get_by_name.return_value = Tenant(name=name)

        # 执行创建，应该抛出异常
        with pytest.raises(ResourceConflictError) as exc_info:
            tenant_service.create_tenant(name, "owner-123", TenantPlan.FREE)

        assert "already exists" in str(exc_info.value).lower()

    def test_create_tenant_invalid_name(self, tenant_service, mock_tenant_repo, mock_account_repo):
        """测试创建租户名称无效"""
        invalid_names = ["", "   ", "a" * 101]  # 空名称  # 只有空格  # 超长

        mock_account_repo.get_by_id.return_value = Account(id="123")

        for name in invalid_names:
            with pytest.raises(ValidationError) as exc_info:
                tenant_service.create_tenant(name, "owner-123", TenantPlan.FREE)

            assert "name" in str(exc_info.value).lower()

    def test_create_tenant_nonexistent_owner(self, tenant_service, mock_tenant_repo, mock_account_repo):
        """测试创建租户时所有者不存在"""
        # Mock 账户不存在
        mock_account_repo.get_by_id.return_value = None

        with pytest.raises(ResourceNotFoundError) as exc_info:
            tenant_service.create_tenant("Test Tenant", "nonexistent-owner", TenantPlan.FREE)

        assert "account" in str(exc_info.value).lower()

    def test_add_member_success(self, tenant_service, mock_tenant_repo, mock_account_repo):
        """测试添加成员成功"""
        tenant_id = "tenant-123"
        account_id = "account-456"
        role = TenantRole.MEMBER
        operator_id = "operator-789"

        # Mock 租户存在
        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 账户存在
        mock_account_repo.get_by_id.return_value = Account(id=account_id)

        # Mock 操作者是 OWNER
        mock_tenant_repo.get_member_role.return_value = TenantRole.OWNER

        # Mock 成员不存在
        mock_tenant_repo.is_member.return_value = False

        # 执行添加
        tenant_service.add_member(tenant_id, account_id, role, operator_id)

        # 验证调用
        mock_tenant_repo.add_member.assert_called_once_with(tenant_id, account_id, role)

    def test_add_member_insufficient_permission(self, tenant_service, mock_tenant_repo, mock_account_repo):
        """测试添加成员权限不足"""
        tenant_id = "tenant-123"
        account_id = "account-456"
        operator_id = "operator-789"

        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)
        mock_account_repo.get_by_id.return_value = Account(id=account_id)

        # Mock 操作者是 MEMBER（权限不足）
        mock_tenant_repo.get_member_role.return_value = TenantRole.MEMBER

        # 执行添加，应该抛出异常
        with pytest.raises(AuthorizationError):
            tenant_service.add_member(tenant_id, account_id, TenantRole.MEMBER, operator_id)

    def test_add_member_duplicate(self, tenant_service, mock_tenant_repo, mock_account_repo):
        """测试添加重复成员"""
        tenant_id = "tenant-123"
        account_id = "account-456"
        operator_id = "operator-789"

        # 创建 Mock 对象
        mock_tenant = Mock()
        mock_tenant.id = tenant_id
        mock_account = Mock()
        mock_account.id = account_id

        mock_tenant_repo.get_by_id.return_value = mock_tenant
        mock_account_repo.get_by_id.return_value = mock_account
        mock_tenant_repo.get_member_role.return_value = TenantRole.OWNER

        # Mock 成员已存在
        mock_tenant_repo.is_member.return_value = True

        # 执行添加，应该抛出异常
        with pytest.raises(ResourceConflictError) as exc_info:
            tenant_service.add_member(tenant_id, account_id, TenantRole.MEMBER, operator_id)

        assert "already a member" in str(exc_info.value).lower()

    def test_remove_member_success(self, tenant_service, mock_tenant_repo):
        """测试移除成员成功"""
        tenant_id = "tenant-123"
        account_id = "account-456"
        operator_id = "operator-789"

        # Mock 租户存在
        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 操作者是 ADMIN
        mock_tenant_repo.get_member_role.side_effect = [
            TenantRole.ADMIN,  # 操作者角色
            TenantRole.MEMBER,  # 被移除者角色
        ]

        # 执行移除
        tenant_service.remove_member(tenant_id, account_id, operator_id)

        # 验证调用
        mock_tenant_repo.remove_member.assert_called_once_with(tenant_id, account_id)

    def test_remove_member_cannot_remove_owner(self, tenant_service, mock_tenant_repo):
        """测试不能移除 OWNER"""
        tenant_id = "tenant-123"
        owner_id = "owner-456"
        operator_id = "operator-789"

        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 操作者是 OWNER，被移除者也是 OWNER
        mock_tenant_repo.get_member_role.side_effect = [TenantRole.OWNER, TenantRole.OWNER]  # 操作者  # 被移除者

        # 执行移除，应该抛出异常
        with pytest.raises(BusinessLogicError) as exc_info:
            tenant_service.remove_member(tenant_id, owner_id, operator_id)

        assert "owner" in str(exc_info.value).lower()

    def test_remove_member_admin_cannot_remove_admin(self, tenant_service, mock_tenant_repo):
        """测试 ADMIN 不能移除另一个 ADMIN"""
        tenant_id = "tenant-123"
        account_id = "account-456"
        operator_id = "operator-789"

        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 操作者是 ADMIN，被移除者也是 ADMIN
        mock_tenant_repo.get_member_role.side_effect = [TenantRole.ADMIN, TenantRole.ADMIN]  # 操作者  # 被移除者

        # 执行移除，应该抛出异常
        with pytest.raises(AuthorizationError) as exc_info:
            tenant_service.remove_member(tenant_id, account_id, operator_id)

        assert "admin cannot remove another admin" in str(exc_info.value).lower()

    def test_update_member_role_success(self, tenant_service, mock_tenant_repo):
        """测试更新成员角色成功"""
        tenant_id = "tenant-123"
        account_id = "account-456"
        new_role = TenantRole.ADMIN
        operator_id = "operator-789"

        # Mock 租户存在
        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 操作者是 OWNER
        mock_tenant_repo.get_member_role.side_effect = [
            TenantRole.OWNER,  # 操作者角色
            TenantRole.MEMBER,  # 被更新者当前角色
        ]

        # 执行更新
        tenant_service.update_member_role(tenant_id, account_id, new_role, operator_id)

        # 验证调用
        mock_tenant_repo.update_member_role.assert_called_once_with(tenant_id, account_id, new_role)

    def test_update_member_role_only_owner_can_update(self, tenant_service, mock_tenant_repo):
        """测试只有 OWNER 可以更新角色"""
        tenant_id = "tenant-123"
        account_id = "account-456"
        operator_id = "operator-789"

        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 操作者是 ADMIN（不是 OWNER）
        mock_tenant_repo.get_member_role.return_value = TenantRole.ADMIN

        # 执行更新，应该抛出异常
        with pytest.raises(AuthorizationError) as exc_info:
            tenant_service.update_member_role(tenant_id, account_id, TenantRole.ADMIN, operator_id)

        assert "only owner" in str(exc_info.value).lower()

    def test_update_member_role_cannot_modify_owner(self, tenant_service, mock_tenant_repo):
        """测试不能修改 OWNER 角色"""
        tenant_id = "tenant-123"
        owner_id = "owner-456"
        operator_id = "operator-789"

        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 操作者是 OWNER，被更新者也是 OWNER
        mock_tenant_repo.get_member_role.side_effect = [TenantRole.OWNER, TenantRole.OWNER]  # 操作者  # 被更新者

        # 执行更新，应该抛出异常
        with pytest.raises(BusinessLogicError) as exc_info:
            tenant_service.update_member_role(tenant_id, owner_id, TenantRole.ADMIN, operator_id)

        assert "cannot change owner role" in str(exc_info.value).lower()

    def test_update_member_role_cannot_set_to_owner(self, tenant_service, mock_tenant_repo):
        """测试不能将成员设置为 OWNER"""
        tenant_id = "tenant-123"
        account_id = "account-456"
        operator_id = "operator-789"

        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)
        mock_tenant_repo.get_member_role.side_effect = [TenantRole.OWNER, TenantRole.MEMBER]  # 操作者  # 被更新者

        # 执行更新为 OWNER，应该抛出异常
        with pytest.raises(BusinessLogicError) as exc_info:
            tenant_service.update_member_role(tenant_id, account_id, TenantRole.OWNER, operator_id)

        assert "cannot set member to owner" in str(exc_info.value).lower()

    def test_get_tenant_members(self, tenant_service, mock_tenant_repo, mock_account_repo):
        """测试获取租户成员列表"""
        tenant_id = "tenant-123"

        # Mock 租户存在
        mock_tenant = Mock()
        mock_tenant.id = tenant_id
        mock_tenant_repo.get_by_id.return_value = mock_tenant

        # Mock 成员列表（TenantRepository.get_tenant_members 返回 Account 列表）
        mock_accounts = []
        for i in range(1, 4):
            mock_account = Mock()
            mock_account.id = f"account-{i}"
            mock_account.email = f"account-{i}@example.com"
            mock_accounts.append(mock_account)

        mock_tenant_repo.get_tenant_members.return_value = mock_accounts

        # 执行获取
        members = tenant_service.get_tenant_members(tenant_id)

        # 验证结果
        assert len(members) == 3
        assert all(m.email.endswith("@example.com") for m in members)

    def test_get_account_tenants(self, tenant_service, mock_tenant_repo, mock_account_repo):
        """测试获取账户的租户列表"""
        account_id = "account-123"

        # Mock 账户存在
        mock_account = Mock()
        mock_account.id = account_id
        mock_account_repo.get_by_id.return_value = mock_account

        # Mock 租户列表
        mock_tenants = []
        for i in range(1, 3):
            mock_tenant = Mock()
            mock_tenant.id = f"tenant-{i}"
            mock_tenant.name = f"Tenant {i}"
            mock_tenants.append(mock_tenant)

        mock_tenant_repo.get_tenants_by_account.return_value = mock_tenants

        # 执行获取
        result = tenant_service.get_account_tenants(account_id)

        # 验证结果
        assert result == mock_tenants
        assert result[0].name == "Tenant 1"
        assert result[1].name == "Tenant 2"

    def test_check_permission_owner_has_all_permissions(self, tenant_service, mock_tenant_repo):
        """测试 OWNER 拥有所有权限"""
        tenant_id = "tenant-123"
        owner_id = "owner-456"

        # Mock OWNER 角色
        mock_tenant_repo.get_member_role.return_value = TenantRole.OWNER

        # 测试所有角色权限
        assert tenant_service.check_permission(tenant_id, owner_id, TenantRole.OWNER)
        assert tenant_service.check_permission(tenant_id, owner_id, TenantRole.ADMIN)
        assert tenant_service.check_permission(tenant_id, owner_id, TenantRole.MEMBER)

    def test_check_permission_admin_hierarchy(self, tenant_service, mock_tenant_repo):
        """测试 ADMIN 权限层级"""
        tenant_id = "tenant-123"
        admin_id = "admin-456"

        # Mock ADMIN 角色
        mock_tenant_repo.get_member_role.return_value = TenantRole.ADMIN

        # 测试权限
        assert not tenant_service.check_permission(tenant_id, admin_id, TenantRole.OWNER)
        assert tenant_service.check_permission(tenant_id, admin_id, TenantRole.ADMIN)
        assert tenant_service.check_permission(tenant_id, admin_id, TenantRole.MEMBER)

    def test_check_permission_member_hierarchy(self, tenant_service, mock_tenant_repo):
        """测试 MEMBER 权限层级"""
        tenant_id = "tenant-123"
        member_id = "member-456"

        # Mock MEMBER 角色
        mock_tenant_repo.get_member_role.return_value = TenantRole.MEMBER

        # 测试权限
        assert not tenant_service.check_permission(tenant_id, member_id, TenantRole.OWNER)
        assert not tenant_service.check_permission(tenant_id, member_id, TenantRole.ADMIN)
        assert tenant_service.check_permission(tenant_id, member_id, TenantRole.MEMBER)

    def test_update_tenant_success(self, tenant_service, mock_tenant_repo):
        """测试更新租户成功"""
        tenant_id = "tenant-123"
        operator_id = "operator-789"
        updates = {"name": "New Name", "plan": TenantPlan.PRO}

        # Mock 租户存在
        tenant = Tenant(id=tenant_id, name="Old Name")
        mock_tenant_repo.get_by_id.return_value = tenant

        # Mock 操作者是 OWNER
        mock_tenant_repo.get_member_role.return_value = TenantRole.OWNER

        # Mock 更新后的租户
        updated_tenant = Tenant(id=tenant_id, name="New Name", plan=TenantPlan.PRO)
        mock_tenant_repo.update.return_value = updated_tenant

        # 执行更新
        result = tenant_service.update_tenant(tenant_id, operator_id, **updates)

        # 验证结果
        assert result.name == "New Name"
        mock_tenant_repo.update.assert_called_once()

    def test_update_tenant_only_owner_can_update(self, tenant_service, mock_tenant_repo):
        """测试只有 OWNER 可以更新租户"""
        tenant_id = "tenant-123"
        operator_id = "operator-789"

        mock_tenant_repo.get_by_id.return_value = Tenant(id=tenant_id)

        # Mock 操作者不是 OWNER
        mock_tenant_repo.get_member_role.return_value = TenantRole.ADMIN

        # 执行更新，应该抛出异常
        with pytest.raises(AuthorizationError) as exc_info:
            tenant_service.update_tenant(tenant_id, operator_id, name="New Name")

        assert "only owner" in str(exc_info.value).lower()
