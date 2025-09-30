"""
Account Repository

账户数据访问层
"""
from typing import Optional, List
from uuid import UUID

from models.account import Account, AccountStatus
from repositories.base_repository import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """账户 Repository"""
    
    def __init__(self):
        """初始化"""
        super().__init__(Account)
    
    def get_by_email(self, email: str) -> Optional[Account]:
        """
        根据邮箱获取账户
        
        参数:
            email: 邮箱地址
            
        返回:
            账户实例或 None
        """
        return self.session.query(Account).filter(
            Account.email == email
        ).first()
    
    def get_active_accounts(self, limit: Optional[int] = None) -> List[Account]:
        """
        获取所有激活状态的账户
        
        参数:
            limit: 限制数量
            
        返回:
            账户列表
        """
        query = self.session.query(Account).filter(
            Account.status == AccountStatus.ACTIVE
        )
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_by_status(self, status: AccountStatus) -> List[Account]:
        """
        根据状态获取账户
        
        参数:
            status: 账户状态
            
        返回:
            账户列表
        """
        return self.session.query(Account).filter(
            Account.status == status
        ).all()
    
    def email_exists(self, email: str) -> bool:
        """
        检查邮箱是否已存在
        
        参数:
            email: 邮箱地址
            
        返回:
            是否存在
        """
        return self.session.query(
            self.session.query(Account).filter(
                Account.email == email
            ).exists()
        ).scalar()
    
    def update_status(self, id: UUID, status: AccountStatus) -> Optional[Account]:
        """
        更新账户状态
        
        参数:
            id: 账户 ID
            status: 新状态
            
        返回:
            更新后的账户或 None
        """
        return self.update(id, status=status)
    
    def ban_account(self, id: UUID) -> Optional[Account]:
        """
        封禁账户
        
        参数:
            id: 账户 ID
            
        返回:
            更新后的账户或 None
        """
        return self.update_status(id, AccountStatus.BANNED)
    
    def activate_account(self, id: UUID) -> Optional[Account]:
        """
        激活账户
        
        参数:
            id: 账户 ID
            
        返回:
            更新后的账户或 None
        """
        return self.update_status(id, AccountStatus.ACTIVE)
