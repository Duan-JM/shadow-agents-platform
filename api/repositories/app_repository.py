"""
App Repository

应用数据访问层
"""
from typing import Optional, List
from uuid import UUID

from models.app import App, AppMode, AppStatus, AppModelConfig
from repositories.base_repository import BaseRepository


class AppRepository(BaseRepository[App]):
    """应用 Repository"""
    
    def __init__(self):
        """初始化"""
        super().__init__(App)
    
    def get_by_tenant(self, tenant_id: UUID) -> List[App]:
        """
        获取租户的所有应用
        
        参数:
            tenant_id: 租户 ID
            
        返回:
            应用列表
        """
        return self.session.query(App).filter(
            App.tenant_id == tenant_id
        ).all()
    
    def get_active_apps_by_tenant(self, tenant_id: UUID) -> List[App]:
        """
        获取租户的所有正常状态应用
        
        参数:
            tenant_id: 租户 ID
            
        返回:
            应用列表
        """
        return self.session.query(App).filter(
            App.tenant_id == tenant_id,
            App.status == AppStatus.NORMAL
        ).all()
    
    def get_by_mode(self, mode: AppMode) -> List[App]:
        """
        根据模式获取应用
        
        参数:
            mode: 应用模式
            
        返回:
            应用列表
        """
        return self.session.query(App).filter(
            App.mode == mode
        ).all()
    
    def get_by_status(self, status: AppStatus) -> List[App]:
        """
        根据状态获取应用
        
        参数:
            status: 应用状态
            
        返回:
            应用列表
        """
        return self.session.query(App).filter(
            App.status == status
        ).all()
    
    def archive(self, id: UUID) -> Optional[App]:
        """
        归档应用
        
        参数:
            id: 应用 ID
            
        返回:
            更新后的应用或 None
        """
        return self.update(id, status=AppStatus.ARCHIVED)
    
    def unarchive(self, id: UUID) -> Optional[App]:
        """
        取消归档应用
        
        参数:
            id: 应用 ID
            
        返回:
            更新后的应用或 None
        """
        return self.update(id, status=AppStatus.NORMAL)
    
    def get_with_config(self, id: UUID) -> Optional[App]:
        """
        获取应用及其模型配置
        
        参数:
            id: 应用 ID
            
        返回:
            应用实例或 None
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(App).options(
            joinedload(App.model_config)
        ).filter(App.id == id).first()
    
    def create_with_config(
        self,
        app_data: dict,
        config_data: Optional[dict] = None
    ) -> App:
        """
        创建应用及其模型配置
        
        参数:
            app_data: 应用数据
            config_data: 模型配置数据
            
        返回:
            创建的应用实例
        """
        # 创建应用
        app = App(**app_data)
        self.session.add(app)
        self.session.flush()  # 获取 app.id
        
        # 创建模型配置
        if config_data:
            config = AppModelConfig(app_id=app.id, **config_data)
            self.session.add(config)
        
        self.session.commit()
        self.session.refresh(app)
        return app
    
    def update_config(self, app_id: UUID, config_data: dict) -> Optional[AppModelConfig]:
        """
        更新应用模型配置
        
        参数:
            app_id: 应用 ID
            config_data: 配置数据
            
        返回:
            更新后的配置或 None
        """
        config = self.session.query(AppModelConfig).filter(
            AppModelConfig.app_id == app_id
        ).first()
        
        if not config:
            # 如果配置不存在，创建新配置
            config = AppModelConfig(app_id=app_id, **config_data)
            self.session.add(config)
        else:
            # 更新现有配置
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        self.session.commit()
        self.session.refresh(config)
        return config
    
    def count_by_tenant(self, tenant_id: UUID) -> int:
        """
        统计租户的应用数量
        
        参数:
            tenant_id: 租户 ID
            
        返回:
            应用数量
        """
        return self.session.query(App).filter(
            App.tenant_id == tenant_id
        ).count()
    
    def enable_site(self, id: UUID, enable: bool = True) -> Optional[App]:
        """
        启用/禁用网站访问
        
        参数:
            id: 应用 ID
            enable: 是否启用
            
        返回:
            更新后的应用或 None
        """
        return self.update(id, enable_site=enable)
    
    def enable_api(self, id: UUID, enable: bool = True) -> Optional[App]:
        """
        启用/禁用 API 访问
        
        参数:
            id: 应用 ID
            enable: 是否启用
            
        返回:
            更新后的应用或 None
        """
        return self.update(id, enable_api=enable)
