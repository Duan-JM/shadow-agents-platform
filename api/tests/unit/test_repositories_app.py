"""
App Repository 测试
"""
import pytest

from models.app import App, AppMode, AppStatus
from repositories.app_repository import AppRepository


class TestAppRepository:
    """App Repository 测试类"""
    
    def test_create_app(self, app, factory):
        """测试创建应用"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            
            application = repo.create(
                name="Test App",
                tenant_id=tenant.id,
                mode=AppMode.CHAT
            )
            
            assert application.id is not None
            assert application.name == "Test App"
            assert application.mode == AppMode.CHAT
    
    def test_get_by_tenant(self, app, factory):
        """测试获取租户的应用"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            
            app1 = factory.create_app(tenant, name="App 1")
            app2 = factory.create_app(tenant, name="App 2")
            
            apps = repo.get_by_tenant(tenant.id)
            
            assert len(apps) == 2
            assert app1.id in [a.id for a in apps]
            assert app2.id in [a.id for a in apps]
    
    def test_get_active_apps_by_tenant(self, app, factory):
        """测试获取租户的正常应用"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            
            factory.create_app(tenant, name="Active 1", status=AppStatus.NORMAL)
            factory.create_app(tenant, name="Active 2", status=AppStatus.NORMAL)
            factory.create_app(tenant, name="Archived", status=AppStatus.ARCHIVED)
            
            active_apps = repo.get_active_apps_by_tenant(tenant.id)
            
            assert len(active_apps) == 2
            assert all(a.status == AppStatus.NORMAL for a in active_apps)
    
    def test_get_by_mode(self, app, factory):
        """测试根据模式获取应用"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            
            factory.create_app(tenant, name="Chat 1", mode=AppMode.CHAT)
            factory.create_app(tenant, name="Chat 2", mode=AppMode.CHAT)
            factory.create_app(tenant, name="Agent", mode=AppMode.AGENT)
            
            chat_apps = repo.get_by_mode(AppMode.CHAT)
            
            assert len(chat_apps) == 2
            assert all(a.mode == AppMode.CHAT for a in chat_apps)
    
    def test_get_by_status(self, app, factory):
        """测试根据状态获取应用"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            
            factory.create_app(tenant, name="Archived 1", status=AppStatus.ARCHIVED)
            factory.create_app(tenant, name="Archived 2", status=AppStatus.ARCHIVED)
            factory.create_app(tenant, name="Normal", status=AppStatus.NORMAL)
            
            archived_apps = repo.get_by_status(AppStatus.ARCHIVED)
            
            assert len(archived_apps) == 2
            assert all(a.status == AppStatus.ARCHIVED for a in archived_apps)
    
    def test_archive(self, app, factory):
        """测试归档应用"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            application = factory.create_app(tenant, status=AppStatus.NORMAL)
            
            archived = repo.archive(application.id)
            
            assert archived is not None
            assert archived.status == AppStatus.ARCHIVED
    
    def test_unarchive(self, app, factory):
        """测试取消归档"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            application = factory.create_app(tenant, status=AppStatus.ARCHIVED)
            
            unarchived = repo.unarchive(application.id)
            
            assert unarchived is not None
            assert unarchived.status == AppStatus.NORMAL
    
    def test_get_with_config(self, app, factory):
        """测试获取应用及配置"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            application = factory.create_app(tenant)
            
            # 注意：需要通过数据库添加配置
            from models.app import AppModelConfig
            from extensions.ext_database import db
            
            config = AppModelConfig(
                app_id=application.id,
                provider="openai",
                model="gpt-4"
            )
            db.session.add(config)
            db.session.commit()
            
            found = repo.get_with_config(application.id)
            
            assert found is not None
            assert found.model_config is not None
            assert found.model_config.provider == "openai"
    
    def test_create_with_config(self, app, factory):
        """测试创建应用及配置"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            
            app_data = {
                "name": "Test App",
                "tenant_id": tenant.id,
                "mode": AppMode.CHAT
            }
            config_data = {
                "provider": "openai",
                "model": "gpt-4",
                "configs": {"temperature": 0.7}
            }
            
            application = repo.create_with_config(app_data, config_data)
            
            assert application.id is not None
            assert application.name == "Test App"
            
            # 验证配置
            found = repo.get_with_config(application.id)
            assert found.model_config is not None
            assert found.model_config.provider == "openai"
    
    def test_update_config(self, app, factory):
        """测试更新配置"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            application = factory.create_app(tenant)
            
            config_data = {
                "provider": "anthropic",
                "model": "claude-3"
            }
            
            config = repo.update_config(application.id, config_data)
            
            assert config is not None
            assert config.provider == "anthropic"
            assert config.model == "claude-3"
    
    def test_count_by_tenant(self, app, factory):
        """测试统计租户应用数"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            
            factory.create_app(tenant, name="App 1")
            factory.create_app(tenant, name="App 2")
            factory.create_app(tenant, name="App 3")
            
            count = repo.count_by_tenant(tenant.id)
            
            assert count == 3
    
    def test_enable_site(self, app, factory):
        """测试启用网站"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            application = factory.create_app(tenant, enable_site=False)
            
            enabled = repo.enable_site(application.id, True)
            
            assert enabled is not None
            assert enabled.enable_site is True
    
    def test_enable_api(self, app, factory):
        """测试启用API"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            application = factory.create_app(tenant, enable_api=False)
            
            enabled = repo.enable_api(application.id, True)
            
            assert enabled is not None
            assert enabled.enable_api is True
    
    def test_update(self, app, factory):
        """测试更新应用"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            application = factory.create_app(tenant, name="Old Name")
            
            updated = repo.update(application.id, name="New Name")
            
            assert updated is not None
            assert updated.name == "New Name"
    
    def test_delete(self, app, factory):
        """测试删除应用"""
        with app.app_context():
            repo = AppRepository()
            tenant = factory.create_tenant()
            application = factory.create_app(tenant)
            
            result = repo.delete(application.id)
            
            assert result is True
            assert repo.get_by_id(application.id) is None
