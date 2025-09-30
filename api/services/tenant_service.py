"""
租户服务

处理租户创建、成员管理等业务逻辑
"""

from typing import List, Optional
from uuid import UUID

from models.account import Account
from models.tenant import Tenant, TenantPlan, TenantRole, TenantStatus
from repositories.account_repository import AccountRepository
from repositories.tenant_repository import TenantRepository
from services.exceptions import (
    AuthorizationError,
    BusinessLogicError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)


class TenantService:
    """租户服务类"""

    def __init__(
        self, tenant_repo: Optional[TenantRepository] = None, account_repo: Optional[AccountRepository] = None
    ):
        """
        初始化

        参数:
            tenant_repo: 租户仓储
            account_repo: 账户仓储
        """
        self.tenant_repo = tenant_repo or TenantRepository()
        self.account_repo = account_repo or AccountRepository()

    def create_tenant(self, name: str, owner_account_id: UUID, plan: TenantPlan = TenantPlan.FREE) -> Tenant:
        """
        创建租户

        参数:
            name: 租户名称
            owner_account_id: 所有者账户 ID
            plan: 套餐类型

        返回:
            创建的租户

        异常:
            ValidationError: 数据验证失败
            ResourceNotFoundError: 账户不存在
            ResourceConflictError: 租户名称已存在
        """
        # 验证名称
        if not name or len(name.strip()) == 0:
            raise ValidationError("Tenant name is required")

        if len(name.strip()) > 100:
            raise ValidationError("Tenant name is too long (max 100 characters)")

        # 检查账户是否存在
        owner = self.account_repo.get_by_id(owner_account_id)
        if not owner:
            raise ResourceNotFoundError("Account", str(owner_account_id))

        # 检查名称是否已存在
        existing = self.tenant_repo.get_by_name(name.strip())
        if existing:
            raise ResourceConflictError(f"Tenant name already exists: {name}")

        # 创建租户
        tenant = self.tenant_repo.create(name=name.strip(), plan=plan, status=TenantStatus.ACTIVE)

        # 添加所有者
        self.tenant_repo.add_member(tenant.id, owner_account_id, TenantRole.OWNER)

        return tenant

    def add_member(self, tenant_id: UUID, account_id: UUID, role: TenantRole, operator_account_id: UUID) -> None:
        """
        添加租户成员

        参数:
            tenant_id: 租户 ID
            account_id: 要添加的账户 ID
            role: 角色
            operator_account_id: 操作者账户 ID

        异常:
            ResourceNotFoundError: 租户或账户不存在
            AuthorizationError: 无权限操作
            ResourceConflictError: 成员已存在
        """
        # 检查租户是否存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        # 检查账户是否存在
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundError("Account", str(account_id))

        # 检查操作者权限（必须是 OWNER 或 ADMIN）
        operator_role = self.tenant_repo.get_member_role(tenant_id, operator_account_id)
        if not operator_role or operator_role not in [TenantRole.OWNER, TenantRole.ADMIN]:
            raise AuthorizationError("Only owner or admin can add members")

        # 检查是否已是成员
        if self.tenant_repo.is_member(tenant_id, account_id):
            raise ResourceConflictError("Account is already a member of this tenant")

        # 添加成员
        self.tenant_repo.add_member(tenant_id, account_id, role)

    def remove_member(self, tenant_id: UUID, account_id: UUID, operator_account_id: UUID) -> None:
        """
        移除租户成员

        参数:
            tenant_id: 租户 ID
            account_id: 要移除的账户 ID
            operator_account_id: 操作者账户 ID

        异常:
            ResourceNotFoundError: 租户或成员不存在
            AuthorizationError: 无权限操作
            BusinessLogicError: 不能移除所有者
        """
        # 检查租户是否存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        # 检查操作者权限
        operator_role = self.tenant_repo.get_member_role(tenant_id, operator_account_id)
        if not operator_role or operator_role not in [TenantRole.OWNER, TenantRole.ADMIN]:
            raise AuthorizationError("Only owner or admin can remove members")

        # 检查要移除的成员角色
        member_role = self.tenant_repo.get_member_role(tenant_id, account_id)
        if not member_role:
            raise ResourceNotFoundError("Member", str(account_id))

        # 不能移除所有者
        if member_role == TenantRole.OWNER:
            raise BusinessLogicError("Cannot remove tenant owner")

        # ADMIN 只能移除 MEMBER
        if operator_role == TenantRole.ADMIN and member_role == TenantRole.ADMIN:
            raise AuthorizationError("Admin cannot remove another admin")

        # 移除成员
        self.tenant_repo.remove_member(tenant_id, account_id)

    def update_member_role(
        self, tenant_id: UUID, account_id: UUID, new_role: TenantRole, operator_account_id: UUID
    ) -> None:
        """
        更新成员角色

        参数:
            tenant_id: 租户 ID
            account_id: 成员账户 ID
            new_role: 新角色
            operator_account_id: 操作者账户 ID

        异常:
            ResourceNotFoundError: 租户或成员不存在
            AuthorizationError: 无权限操作
            BusinessLogicError: 不能修改所有者角色
        """
        # 检查租户是否存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        # 检查操作者权限（只有 OWNER 可以修改角色）
        operator_role = self.tenant_repo.get_member_role(tenant_id, operator_account_id)
        if operator_role != TenantRole.OWNER:
            raise AuthorizationError("Only owner can update member roles")

        # 检查成员是否存在
        member_role = self.tenant_repo.get_member_role(tenant_id, account_id)
        if not member_role:
            raise ResourceNotFoundError("Member", str(account_id))

        # 不能修改所有者角色
        if member_role == TenantRole.OWNER:
            raise BusinessLogicError("Cannot change owner role")

        # 不能设置为所有者
        if new_role == TenantRole.OWNER:
            raise BusinessLogicError("Cannot set member to owner role")

        # 更新角色
        self.tenant_repo.update_member_role(tenant_id, account_id, new_role)

    def get_tenant_members(self, tenant_id: UUID) -> List[Account]:
        """
        获取租户成员列表

        参数:
            tenant_id: 租户 ID

        返回:
            成员账户列表

        异常:
            ResourceNotFoundError: 租户不存在
        """
        # 检查租户是否存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        return self.tenant_repo.get_tenant_members(tenant_id)

    def get_account_tenants(self, account_id: UUID) -> List[Tenant]:
        """
        获取账户所属的租户列表

        参数:
            account_id: 账户 ID

        返回:
            租户列表

        异常:
            ResourceNotFoundError: 账户不存在
        """
        # 检查账户是否存在
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundError("Account", str(account_id))

        return self.tenant_repo.get_tenants_by_account(account_id)

    def is_member(self, tenant_id: UUID, account_id: UUID) -> bool:
        """
        检查账户是否是租户成员

        参数:
            tenant_id: 租户 ID
            account_id: 账户 ID

        返回:
            是否是成员
        """
        member_role = self.tenant_repo.get_member_role(tenant_id, account_id)
        return member_role is not None

    def check_permission(self, tenant_id: UUID, account_id: UUID, required_role: TenantRole) -> bool:
        """
        检查账户在租户中的权限

        参数:
            tenant_id: 租户 ID
            account_id: 账户 ID
            required_role: 需要的角色

        返回:
            是否有权限
        """
        member_role = self.tenant_repo.get_member_role(tenant_id, account_id)

        if not member_role:
            return False

        # OWNER 拥有所有权限
        if member_role == TenantRole.OWNER:
            return True

        # ADMIN 拥有 ADMIN 和 MEMBER 权限
        if member_role == TenantRole.ADMIN:
            return required_role in [TenantRole.ADMIN, TenantRole.MEMBER]

        # MEMBER 只有 MEMBER 权限
        return required_role == TenantRole.MEMBER

    def update_tenant(self, tenant_id: UUID, operator_account_id: UUID, **updates) -> Tenant:
        """
        更新租户信息

        参数:
            tenant_id: 租户 ID
            operator_account_id: 操作者账户 ID
            **updates: 要更新的字段

        返回:
            更新后的租户

        异常:
            ResourceNotFoundError: 租户不存在
            AuthorizationError: 无权限操作
        """
        # 检查租户是否存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        # 检查操作者权限（只有 OWNER 可以更新租户信息）
        operator_role = self.tenant_repo.get_member_role(tenant_id, operator_account_id)
        if operator_role != TenantRole.OWNER:
            raise AuthorizationError("Only owner can update tenant")

        # 更新租户
        updated_tenant = self.tenant_repo.update(tenant_id, **updates)
        return updated_tenant
