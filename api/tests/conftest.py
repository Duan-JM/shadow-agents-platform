"""
测试配置模块

提供测试环境的配置和工具
"""

import os
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from configs.app_config import Config
from extensions.ext_database import db


class TestConfig(Config):
    """测试环境配置"""

    TESTING = True
    DEBUG = True

    # 测试用的密钥
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"

    # 禁用 CSRF 保护
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """使用内存 SQLite 数据库进行测试"""
        return "sqlite:///:memory:"


@pytest.fixture(scope="function")
def app() -> Generator[Flask, None, None]:
    """
    创建测试应用

    每个测试函数都会创建一个新的应用实例
    """
    # 创建应用并直接设置配置
    test_app = Flask(__name__)
    test_config = TestConfig()

    # 手动设置配置项（避免 property 问题）
    test_app.config["TESTING"] = test_config.TESTING
    test_app.config["DEBUG"] = test_config.DEBUG
    test_app.config["SECRET_KEY"] = test_config.SECRET_KEY
    test_app.config["JWT_SECRET_KEY"] = test_config.JWT_SECRET_KEY
    test_app.config["WTF_CSRF_ENABLED"] = test_config.WTF_CSRF_ENABLED
    test_app.config["SQLALCHEMY_DATABASE_URI"] = test_config.SQLALCHEMY_DATABASE_URI  # 会调用 property
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = test_config.SQLALCHEMY_TRACK_MODIFICATIONS

    # 初始化数据库
    db.init_app(test_app)

    # 创建应用上下文
    with test_app.app_context():
        # 创建所有表
        db.create_all()

        yield test_app

        # 清理：删除所有表
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    """
    创建测试客户端

    用于发送 HTTP 请求
    """
    return app.test_client()


@pytest.fixture(scope="function")
def app_with_blueprints() -> Generator[Flask, None, None]:
    """
    创建完整的测试应用（包含蓝图和错误处理器）

    用于集成测试
    """
    from app_factory import create_app

    # 创建测试配置实例
    test_config = TestConfig()

    # 创建应用并手动设置配置
    test_app = Flask(__name__)
    test_app.config["TESTING"] = test_config.TESTING
    test_app.config["DEBUG"] = test_config.DEBUG
    test_app.config["SECRET_KEY"] = test_config.SECRET_KEY
    test_app.config["JWT_SECRET_KEY"] = test_config.JWT_SECRET_KEY
    test_app.config["WTF_CSRF_ENABLED"] = test_config.WTF_CSRF_ENABLED
    test_app.config["SQLALCHEMY_DATABASE_URI"] = test_config.SQLALCHEMY_DATABASE_URI  # 调用 property
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = test_config.SQLALCHEMY_TRACK_MODIFICATIONS

    # 手动初始化扩展和注册蓝图
    db.init_app(test_app)

    # 注册蓝图
    from controllers.console.app import app_bp
    from controllers.console.auth import auth_bp
    from controllers.console.model_provider import model_provider_bp
    from controllers.console.tenant import tenant_bp

    test_app.register_blueprint(auth_bp)
    test_app.register_blueprint(tenant_bp)
    test_app.register_blueprint(app_bp)
    test_app.register_blueprint(model_provider_bp)

    # 注册错误处理器（简化版，直接在这里注册）
    from flask import jsonify

    from services.exceptions import (
        AuthenticationError,
        AuthorizationError,
        BusinessLogicError,
        ResourceConflictError,
        ResourceNotFoundError,
        ServiceError,
        ValidationError,
    )

    @test_app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "VALIDATION_ERROR"}), 400

    @test_app.errorhandler(AuthenticationError)
    def handle_authentication_error(e):
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "AUTHENTICATION_ERROR"}), 401

    @test_app.errorhandler(AuthorizationError)
    def handle_authorization_error(e):
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "AUTHORIZATION_ERROR"}), 403

    @test_app.errorhandler(ResourceNotFoundError)
    def handle_not_found_error(e):
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "NOT_FOUND"}), 404

    @test_app.errorhandler(ResourceConflictError)
    def handle_conflict_error(e):
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "CONFLICT"}), 409

    @test_app.errorhandler(BusinessLogicError)
    def handle_business_logic_error(e):
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "BUSINESS_ERROR"}), 422

    @test_app.errorhandler(ServiceError)
    def handle_service_error(e):
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "SERVICE_ERROR"}), 500

    with test_app.app_context():
        # 创建所有表
        db.create_all()

        yield test_app

        # 清理
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client_integration(app_with_blueprints: Flask) -> FlaskClient:
    """
    创建集成测试客户端
    """
    return app_with_blueprints.test_client()


@pytest.fixture(scope="function")
def db_session(app: Flask):
    """
    创建数据库会话

    提供数据库操作的会话
    """
    with app.app_context():
        yield db.session

        # 回滚事务
        db.session.rollback()


class ModelFactory:
    """
    模型工厂类

    提供创建测试数据的便捷方法
    """

    @staticmethod
    def create_account(
        email: str = "test@example.com", password: str = "password123", name: str = "Test User", **kwargs
    ):
        """
        创建测试账户

        参数:
            email: 邮箱
            password: 密码（明文）
            name: 用户名
            **kwargs: 其他属性

        返回:
            Account 实例
        """
        from werkzeug.security import generate_password_hash

        from models.account import Account, AccountStatus

        account = Account(
            email=email,
            password_hash=generate_password_hash(password),
            name=name,
            status=kwargs.get("status", AccountStatus.ACTIVE),
            **{k: v for k, v in kwargs.items() if k not in ["email", "password", "name", "status"]},
        )
        db.session.add(account)
        db.session.commit()
        return account

    @staticmethod
    def create_tenant(name: str = "Test Tenant", **kwargs):
        """
        创建测试租户

        参数:
            name: 租户名称
            **kwargs: 其他属性

        返回:
            Tenant 实例
        """
        from models.tenant import Tenant, TenantPlan, TenantStatus

        tenant = Tenant(
            name=name,
            plan=kwargs.get("plan", TenantPlan.FREE),
            status=kwargs.get("status", TenantStatus.ACTIVE),
            **{k: v for k, v in kwargs.items() if k not in ["name", "plan", "status"]},
        )
        db.session.add(tenant)
        db.session.commit()
        return tenant

    @staticmethod
    def create_tenant_account_join(tenant, account, **kwargs):
        """
        创建租户-账户关联

        参数:
            tenant: 租户实例
            account: 账户实例
            **kwargs: 其他属性

        返回:
            TenantAccountJoin 实例
        """
        from models.tenant import TenantAccountJoin, TenantRole

        join = TenantAccountJoin(
            tenant_id=tenant.id,
            account_id=account.id,
            role=kwargs.get("role", TenantRole.OWNER),
            **{k: v for k, v in kwargs.items() if k not in ["tenant_id", "account_id", "role"]},
        )
        db.session.add(join)
        db.session.commit()
        return join

    @staticmethod
    def create_app(tenant, name: str = "Test App", **kwargs):
        """
        创建测试应用

        参数:
            tenant: 租户实例
            name: 应用名称
            **kwargs: 其他属性

        返回:
            App 实例
        """
        from models.app import App, AppMode, AppStatus

        app = App(
            tenant_id=tenant.id,
            name=name,
            mode=kwargs.get("mode", AppMode.CHAT),
            status=kwargs.get("status", AppStatus.NORMAL),
            **{k: v for k, v in kwargs.items() if k not in ["tenant_id", "name", "mode", "status"]},
        )
        db.session.add(app)
        db.session.commit()
        return app


@pytest.fixture
def factory():
    """提供模型工厂"""
    return ModelFactory


# ============= 集成测试专用 Fixtures =============


@pytest.fixture(scope="function")
def session(app_with_blueprints: Flask):
    """
    提供数据库会话（用于集成测试）
    """
    with app_with_blueprints.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture(scope="function")
def test_account(session):
    """
    创建测试账户

    用于集成测试中需要已存在用户的场景
    """
    import uuid

    from werkzeug.security import generate_password_hash

    from models.account import Account, AccountStatus

    account = Account(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=generate_password_hash("test_password"),
        name="Test User",
        status=AccountStatus.ACTIVE,
    )
    session.add(account)
    session.commit()

    return account


@pytest.fixture(scope="function")
def auth_headers(test_account):
    """
    创建认证头

    用于需要 JWT 认证的测试
    """
    from datetime import datetime, timedelta

    import jwt

    # 使用测试配置中的 SECRET_KEY
    test_config = TestConfig()

    # 生成 JWT token
    token = jwt.encode(
        {
            "account_id": str(test_account.id),
            "email": test_account.email,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        },
        test_config.SECRET_KEY,
        algorithm="HS256",
    )

    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
