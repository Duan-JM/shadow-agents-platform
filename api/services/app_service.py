"""
应用服务

处理应用创建、配置、管理等业务逻辑
"""

from typing import Dict, List, Optional
from uuid import UUID

from models.app import App, AppMode, AppStatus
from models.tenant import TenantRole
from repositories.app_repository import AppRepository
from repositories.tenant_repository import TenantRepository
from services.exceptions import (
    AuthorizationError,
    BusinessLogicError,
    ResourceNotFoundError,
    ValidationError,
)


class AppService:
    """应用服务类"""

    def __init__(self, app_repo: Optional[AppRepository] = None, tenant_repo: Optional[TenantRepository] = None):
        """
        初始化

        参数:
            app_repo: 应用仓储
            tenant_repo: 租户仓储
        """
        self.app_repo = app_repo or AppRepository()
        self.tenant_repo = tenant_repo or TenantRepository()

    def create_app(
        self,
        tenant_id: UUID,
        account_id: UUID,
        name: str,
        mode: AppMode,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        icon_background: Optional[str] = None,
    ) -> App:
        """
        创建应用

        参数:
            tenant_id: 租户 ID
            account_id: 创建者账户 ID
            name: 应用名称
            mode: 应用模式
            description: 描述
            icon: 图标
            icon_background: 图标背景色

        返回:
            创建的应用

        异常:
            ValidationError: 数据验证失败
            ResourceNotFoundError: 租户不存在
            AuthorizationError: 无权限操作
        """
        # 验证名称
        if not name or len(name.strip()) == 0:
            raise ValidationError("App name is required")

        if len(name.strip()) > 100:
            raise ValidationError("App name is too long (max 100 characters)")

        # 检查租户是否存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        # 检查权限（至少是 MEMBER）
        if not self.tenant_repo.is_member(tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        # 创建应用
        app = self.app_repo.create(
            name=name.strip(),
            tenant_id=tenant_id,
            mode=mode,
            description=description,
            icon=icon or "🤖",
            icon_background=icon_background or "#E0F2FE",
            enable_site=True,
            enable_api=True,
            status=AppStatus.NORMAL,
            created_by=account_id,
        )

        return app

    def create_app_with_config(
        self, tenant_id: UUID, account_id: UUID, app_data: Dict, config_data: Optional[Dict] = None
    ) -> App:
        """
        创建应用及配置

        参数:
            tenant_id: 租户 ID
            account_id: 创建者账户 ID
            app_data: 应用数据
            config_data: 模型配置数据

        返回:
            创建的应用

        异常:
            ValidationError: 数据验证失败
            ResourceNotFoundError: 租户不存在
            AuthorizationError: 无权限操作
        """
        # 检查租户是否存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        # 检查权限
        if not self.tenant_repo.is_member(tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        # 添加必要字段
        app_data["tenant_id"] = tenant_id
        app_data["created_by"] = account_id

        # 设置默认值
        if "icon" not in app_data:
            app_data["icon"] = "🤖"
        if "icon_background" not in app_data:
            app_data["icon_background"] = "#E0F2FE"
        if "enable_site" not in app_data:
            app_data["enable_site"] = True
        if "enable_api" not in app_data:
            app_data["enable_api"] = True
        if "status" not in app_data:
            app_data["status"] = AppStatus.NORMAL

        # 创建应用及配置
        app = self.app_repo.create_with_config(app_data, config_data)

        return app

    def update_app(self, app_id: UUID, account_id: UUID, **updates) -> App:
        """
        更新应用

        参数:
            app_id: 应用 ID
            account_id: 操作者账户 ID
            **updates: 要更新的字段

        返回:
            更新后的应用

        异常:
            ResourceNotFoundError: 应用不存在
            AuthorizationError: 无权限操作
        """
        # 检查应用是否存在
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ResourceNotFoundError("App", str(app_id))

        # 检查权限（租户成员）
        if not self.tenant_repo.is_member(app.tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        # 更新应用
        updated_app = self.app_repo.update(app_id, **updates)
        return updated_app

    def update_app_config(self, app_id: UUID, account_id: UUID, config_data: Dict) -> App:
        """
        更新应用模型配置

        参数:
            app_id: 应用 ID
            account_id: 操作者账户 ID
            config_data: 配置数据

        返回:
            更新后的应用

        异常:
            ResourceNotFoundError: 应用不存在
            AuthorizationError: 无权限操作
        """
        # 检查应用是否存在
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ResourceNotFoundError("App", str(app_id))

        # 检查权限
        if not self.tenant_repo.is_member(app.tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        # 更新配置
        self.app_repo.update_config(app_id, config_data)

        # 返回更新后的应用
        return self.app_repo.get_with_config(app_id)

    def delete_app(self, app_id: UUID, account_id: UUID) -> None:
        """
        删除应用

        参数:
            app_id: 应用 ID
            account_id: 操作者账户 ID

        异常:
            ResourceNotFoundError: 应用不存在
            AuthorizationError: 无权限操作
        """
        # 检查应用是否存在
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ResourceNotFoundError("App", str(app_id))

        # 检查权限（需要 ADMIN 或 OWNER）
        member_role = self.tenant_repo.get_member_role(app.tenant_id, account_id)
        if member_role not in [TenantRole.OWNER, TenantRole.ADMIN]:
            raise AuthorizationError("Only admin or owner can delete apps")

        # 删除应用
        self.app_repo.delete(app_id)

    def archive_app(self, app_id: UUID, account_id: UUID) -> App:
        """
        归档应用

        参数:
            app_id: 应用 ID
            account_id: 操作者账户 ID

        返回:
            归档后的应用

        异常:
            ResourceNotFoundError: 应用不存在
            AuthorizationError: 无权限操作
        """
        # 检查应用是否存在
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ResourceNotFoundError("App", str(app_id))

        # 检查权限
        if not self.tenant_repo.is_member(app.tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        # 归档应用
        archived_app = self.app_repo.archive(app_id)
        return archived_app

    def unarchive_app(self, app_id: UUID, account_id: UUID) -> App:
        """
        取消归档应用

        参数:
            app_id: 应用 ID
            account_id: 操作者账户 ID

        返回:
            取消归档后的应用

        异常:
            ResourceNotFoundError: 应用不存在
            AuthorizationError: 无权限操作
        """
        # 检查应用是否存在
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ResourceNotFoundError("App", str(app_id))

        # 检查权限
        if not self.tenant_repo.is_member(app.tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        # 取消归档
        unarchived_app = self.app_repo.unarchive(app_id)
        return unarchived_app

    def get_tenant_apps(self, tenant_id: UUID, account_id: UUID, include_archived: bool = False) -> List[App]:
        """
        获取租户的应用列表

        参数:
            tenant_id: 租户 ID
            account_id: 账户 ID
            include_archived: 是否包含已归档的应用

        返回:
            应用列表

        异常:
            ResourceNotFoundError: 租户不存在
            AuthorizationError: 无权限操作
        """
        # 检查租户是否存在
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ResourceNotFoundError("Tenant", str(tenant_id))

        # 检查权限
        if not self.tenant_repo.is_member(tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        # 获取应用列表
        if include_archived:
            apps = self.app_repo.get_by_tenant(tenant_id)
        else:
            apps = self.app_repo.get_active_apps_by_tenant(tenant_id)

        return apps

    def get_app_detail(self, app_id: UUID, account_id: UUID) -> App:
        """
        获取应用详情（包含配置）

        参数:
            app_id: 应用 ID
            account_id: 账户 ID

        返回:
            应用详情

        异常:
            ResourceNotFoundError: 应用不存在
            AuthorizationError: 无权限操作
        """
        # 检查应用是否存在
        app = self.app_repo.get_with_config(app_id)
        if not app:
            raise ResourceNotFoundError("App", str(app_id))

        # 检查权限
        if not self.tenant_repo.is_member(app.tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        return app

    def toggle_site(self, app_id: UUID, account_id: UUID, enable: bool) -> App:
        """
        启用/禁用网站访问

        参数:
            app_id: 应用 ID
            account_id: 账户 ID
            enable: 是否启用

        返回:
            更新后的应用

        异常:
            ResourceNotFoundError: 应用不存在
            AuthorizationError: 无权限操作
        """
        # 检查应用是否存在
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ResourceNotFoundError("App", str(app_id))

        # 检查权限
        if not self.tenant_repo.is_member(app.tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        # 切换状态
        updated_app = self.app_repo.enable_site(app_id, enable)
        return updated_app

    def toggle_api(self, app_id: UUID, account_id: UUID, enable: bool) -> App:
        """
        启用/禁用 API 访问

        参数:
            app_id: 应用 ID
            account_id: 账户 ID
            enable: 是否启用

        返回:
            更新后的应用

        异常:
            ResourceNotFoundError: 应用不存在
            AuthorizationError: 无权限操作
        """
        # 检查应用是否存在
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ResourceNotFoundError("App", str(app_id))

        # 检查权限
        if not self.tenant_repo.is_member(app.tenant_id, account_id):
            raise AuthorizationError("Not a member of this tenant")

        # 切换状态
        updated_app = self.app_repo.enable_api(app_id, enable)
        return updated_app
