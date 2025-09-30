"""
Tenant Repository

租户数据访问层
"""

from typing import List, Optional
from uuid import UUID

from models.account import Account
from models.tenant import (
    Tenant,
    TenantAccountJoin,
    TenantPlan,
    TenantRole,
    TenantStatus,
)
from repositories.base_repository import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """租户 Repository"""

    def __init__(self):
        """初始化"""
        super().__init__(Tenant)

    def get_by_name(self, name: str) -> Optional[Tenant]:
        """
        根据名称获取租户

        参数:
            name: 租户名称

        返回:
            租户实例或 None
        """
        return self.session.query(Tenant).filter(Tenant.name == name).first()

    def get_active_tenants(self) -> List[Tenant]:
        """
        获取所有激活状态的租户

        返回:
            租户列表
        """
        return self.session.query(Tenant).filter(Tenant.status == TenantStatus.ACTIVE).all()

    def get_by_plan(self, plan: TenantPlan) -> List[Tenant]:
        """
        根据套餐获取租户

        参数:
            plan: 套餐类型

        返回:
            租户列表
        """
        return self.session.query(Tenant).filter(Tenant.plan == plan).all()

    def get_tenants_by_account(self, account_id: UUID) -> List[Tenant]:
        """
        获取账户所属的所有租户

        参数:
            account_id: 账户 ID

        返回:
            租户列表
        """
        return (
            self.session.query(Tenant).join(TenantAccountJoin).filter(TenantAccountJoin.account_id == account_id).all()
        )

    def add_member(
        self, tenant_id: UUID, account_id: UUID, role: TenantRole = TenantRole.MEMBER
    ) -> Optional[TenantAccountJoin]:
        """
        添加租户成员

        参数:
            tenant_id: 租户 ID
            account_id: 账户 ID
            role: 角色

        返回:
            关联记录或 None
        """
        # 检查是否已存在
        existing = (
            self.session.query(TenantAccountJoin)
            .filter(TenantAccountJoin.tenant_id == tenant_id, TenantAccountJoin.account_id == account_id)
            .first()
        )

        if existing:
            return None

        # 创建关联
        join = TenantAccountJoin(tenant_id=tenant_id, account_id=account_id, role=role)
        self.session.add(join)
        self.session.commit()
        self.session.refresh(join)
        return join

    def remove_member(self, tenant_id: UUID, account_id: UUID) -> bool:
        """
        移除租户成员

        参数:
            tenant_id: 租户 ID
            account_id: 账户 ID

        返回:
            是否删除成功
        """
        join = (
            self.session.query(TenantAccountJoin)
            .filter(TenantAccountJoin.tenant_id == tenant_id, TenantAccountJoin.account_id == account_id)
            .first()
        )

        if not join:
            return False

        self.session.delete(join)
        self.session.commit()
        return True

    def get_member_role(self, tenant_id: UUID, account_id: UUID) -> Optional[TenantRole]:
        """
        获取成员角色

        参数:
            tenant_id: 租户 ID
            account_id: 账户 ID

        返回:
            角色或 None
        """
        join = (
            self.session.query(TenantAccountJoin)
            .filter(TenantAccountJoin.tenant_id == tenant_id, TenantAccountJoin.account_id == account_id)
            .first()
        )

        return join.role if join else None

    def get_member_join(self, tenant_id: UUID, account_id: UUID) -> Optional[TenantAccountJoin]:
        """
        获取成员关联记录

        参数:
            tenant_id: 租户 ID
            account_id: 账户 ID

        返回:
            TenantAccountJoin 对象或 None
        """
        return (
            self.session.query(TenantAccountJoin)
            .filter(TenantAccountJoin.tenant_id == tenant_id, TenantAccountJoin.account_id == account_id)
            .first()
        )

    def update_member_role(self, tenant_id: UUID, account_id: UUID, role: TenantRole) -> Optional[TenantAccountJoin]:
        """
        更新成员角色

        参数:
            tenant_id: 租户 ID
            account_id: 账户 ID
            role: 新角色

        返回:
            更新后的关联记录或 None
        """
        join = (
            self.session.query(TenantAccountJoin)
            .filter(TenantAccountJoin.tenant_id == tenant_id, TenantAccountJoin.account_id == account_id)
            .first()
        )

        if not join:
            return None

        join.role = role
        self.session.commit()
        self.session.refresh(join)
        return join

    def get_tenant_members(self, tenant_id: UUID) -> List[Account]:
        """
        获取租户所有成员

        参数:
            tenant_id: 租户 ID

        返回:
            账户列表
        """
        return (
            self.session.query(Account).join(TenantAccountJoin).filter(TenantAccountJoin.tenant_id == tenant_id).all()
        )

    def is_member(self, tenant_id: UUID, account_id: UUID) -> bool:
        """
        检查是否为租户成员

        参数:
            tenant_id: 租户 ID
            account_id: 账户 ID

        返回:
            是否为成员
        """
        return self.session.query(
            self.session.query(TenantAccountJoin)
            .filter(TenantAccountJoin.tenant_id == tenant_id, TenantAccountJoin.account_id == account_id)
            .exists()
        ).scalar()
