"""
App 模型测试
"""
import pytest
from datetime import datetime

from models.app import App, AppMode, AppStatus, AppModelConfig
from extensions.ext_database import db


class TestAppModel:
    """App 模型测试类"""
    
    def test_create_app(self, app, factory):
        """测试创建应用"""
        with app.app_context():
            tenant = factory.create_tenant()
            application = factory.create_app(
                tenant=tenant,
                name="Test App"
            )
            
            # 验证
            assert application.id is not None
            assert application.name == "Test App"
            assert application.tenant_id == tenant.id
            assert application.mode == AppMode.CHAT
            assert application.status == AppStatus.NORMAL
            assert application.enable_site is True
            assert application.enable_api is True
            assert application.created_at is not None
            assert application.updated_at is not None
    
    def test_app_modes(self, app, factory):
        """测试应用模式"""
        with app.app_context():
            tenant = factory.create_tenant()
            
            # CHAT 模式
            chat_app = factory.create_app(
                tenant=tenant,
                name="Chat App",
                mode=AppMode.CHAT
            )
            assert chat_app.mode == AppMode.CHAT
            
            # COMPLETION 模式
            completion_app = factory.create_app(
                tenant=tenant,
                name="Completion App",
                mode=AppMode.COMPLETION
            )
            assert completion_app.mode == AppMode.COMPLETION
            
            # AGENT 模式
            agent_app = factory.create_app(
                tenant=tenant,
                name="Agent App",
                mode=AppMode.AGENT
            )
            assert agent_app.mode == AppMode.AGENT
            
            # WORKFLOW 模式
            workflow_app = factory.create_app(
                tenant=tenant,
                name="Workflow App",
                mode=AppMode.WORKFLOW
            )
            assert workflow_app.mode == AppMode.WORKFLOW
    
    def test_app_status(self, app, factory):
        """测试应用状态"""
        with app.app_context():
            tenant = factory.create_tenant()
            
            # NORMAL 状态
            normal_app = factory.create_app(
                tenant=tenant,
                name="Normal App",
                status=AppStatus.NORMAL
            )
            assert normal_app.status == AppStatus.NORMAL
            
            # ARCHIVED 状态
            archived_app = factory.create_app(
                tenant=tenant,
                name="Archived App",
                status=AppStatus.ARCHIVED
            )
            assert archived_app.status == AppStatus.ARCHIVED
    
    def test_app_icon_customization(self, app, factory):
        """测试图标自定义"""
        with app.app_context():
            tenant = factory.create_tenant()
            
            # 带图标的应用
            application = factory.create_app(
                tenant=tenant,
                name="Icon App",
                icon="🤖",
                icon_background="#FF0000"
            )
            
            assert application.icon == "🤖"
            assert application.icon_background == "#FF0000"
    
    def test_app_enable_flags(self, app, factory):
        """测试启用标志"""
        with app.app_context():
            tenant = factory.create_tenant()
            
            # 禁用网站和 API
            application = factory.create_app(
                tenant=tenant,
                name="Disabled App",
                enable_site=False,
                enable_api=False
            )
            
            assert application.enable_site is False
            assert application.enable_api is False
    
    def test_app_tenant_relationship(self, app, factory):
        """测试应用-租户关系"""
        with app.app_context():
            tenant = factory.create_tenant()
            
            # 创建多个应用
            app1 = factory.create_app(tenant=tenant, name="App 1")
            app2 = factory.create_app(tenant=tenant, name="App 2")
            
            # 验证关系
            assert len(tenant.apps) == 2
            assert app1 in tenant.apps
            assert app2 in tenant.apps
    
    def test_app_model_config(self, app, factory):
        """测试应用模型配置"""
        with app.app_context():
            tenant = factory.create_tenant()
            application = factory.create_app(tenant=tenant)
            
            # 创建配置
            config = AppModelConfig(
                app_id=application.id,
                provider="openai",
                model="gpt-4",
                configs={
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                opening_statement="Hello! How can I help you?",
                suggested_questions=["What can you do?", "Tell me more"],
                pre_prompt="You are a helpful assistant.",
                user_input_form={
                    "fields": [
                        {"name": "query", "type": "text", "required": True}
                    ]
                }
            )
            db.session.add(config)
            db.session.commit()
            
            # 验证
            assert config.id is not None
            assert config.app_id == application.id
            assert config.provider == "openai"
            assert config.model == "gpt-4"
            assert config.configs["temperature"] == 0.7
            assert config.opening_statement == "Hello! How can I help you?"
            assert len(config.suggested_questions) == 2
    
    def test_app_model_config_relationship(self, app, factory):
        """测试应用-配置一对一关系"""
        with app.app_context():
            tenant = factory.create_tenant()
            application = factory.create_app(tenant=tenant)
            
            # 创建配置
            config = AppModelConfig(
                app_id=application.id,
                provider="anthropic",
                model="claude-3"
            )
            db.session.add(config)
            db.session.commit()
            
            # 验证关系
            assert application.model_config is not None
            assert application.model_config.id == config.id
            assert application.model_config.provider == "anthropic"
    
    def test_app_to_dict(self, app, factory):
        """测试转换为字典"""
        with app.app_context():
            tenant = factory.create_tenant()
            account = factory.create_account()
            application = factory.create_app(
                tenant=tenant,
                name="Test App",
                created_by=account.id
            )
            
            data = application.to_dict()
            
            # 验证字段
            assert "id" in data
            assert "name" in data
            assert "mode" in data
            assert "status" in data
            assert "tenant_id" in data
            assert "created_at" in data
            assert "updated_at" in data
            
            # 验证数据类型
            assert isinstance(data["id"], str)
            assert isinstance(data["name"], str)
            assert isinstance(data["mode"], str)
            assert isinstance(data["status"], str)
    
    def test_app_to_dict_with_config(self, app, factory):
        """测试转换为字典（包含配置）"""
        with app.app_context():
            tenant = factory.create_tenant()
            application = factory.create_app(tenant=tenant)
            
            # 创建配置
            config = AppModelConfig(
                app_id=application.id,
                provider="openai",
                model="gpt-4"
            )
            db.session.add(config)
            db.session.commit()
            
            # 获取字典
            data = application.to_dict()
            
            # 验证包含配置
            assert "model_config" in data
            assert data["model_config"]["provider"] == "openai"
            assert data["model_config"]["model"] == "gpt-4"
    
    def test_app_cascade_delete(self, app, factory):
        """测试级联删除"""
        with app.app_context():
            tenant = factory.create_tenant()
            application = factory.create_app(tenant=tenant)
            
            # 创建配置
            config = AppModelConfig(
                app_id=application.id,
                provider="openai",
                model="gpt-4"
            )
            db.session.add(config)
            db.session.commit()
            
            app_id = application.id
            
            # 删除应用
            db.session.delete(application)
            db.session.commit()
            
            # 验证配置也被删除
            deleted_config = AppModelConfig.query.filter_by(app_id=app_id).first()
            assert deleted_config is None
