"""
Flask 应用工厂模式

创建和配置 Flask 应用实例
"""

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from configs.app_config import Config
from extensions.ext_database import db
from extensions.ext_redis import redis_client
from extensions.ext_storage import storage


def create_app(config_class=Config) -> Flask:
    """
    创建 Flask 应用实例

    参数:
        config_class: 配置类，默认使用 Config

    返回:
        Flask 应用实例
    """
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config_class)

    # 初始化扩展
    initialize_extensions(app)

    # 注册蓝图
    register_blueprints(app)

    # 注册错误处理器
    register_error_handlers(app)

    # 配置 CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get("CORS_ALLOW_ORIGINS", "*"),
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    return app


def initialize_extensions(app: Flask) -> None:
    """
    初始化 Flask 扩展

    参数:
        app: Flask 应用实例
    """
    # 初始化数据库
    db.init_app(app)

    # 初始化数据库迁移
    Migrate(app, db)

    # 初始化 Redis
    redis_client.init_app(app)

    # 初始化存储
    storage.init_app(app)


def register_blueprints(app: Flask) -> None:
    """
    注册所有蓝图

    参数:
        app: Flask 应用实例
    """
    # 注册认证蓝图
    from controllers.console.auth import auth_bp

    app.register_blueprint(auth_bp)

    # 注册租户蓝图
    from controllers.console.tenant import tenant_bp

    app.register_blueprint(tenant_bp)

    # 注册模型提供商蓝图
    from controllers.console.model_provider import model_provider_bp

    app.register_blueprint(model_provider_bp)


def register_error_handlers(app: Flask) -> None:
    """
    注册全局错误处理器

    参数:
        app: Flask 应用实例
    """
    from flask import jsonify

    from libs.errors import APIException
    from services.exceptions import (
        AuthenticationError,
        AuthorizationError,
        BusinessLogicError,
        ResourceConflictError,
        ResourceNotFoundError,
        ServiceError,
        ValidationError,
    )

    @app.errorhandler(APIException)
    def handle_api_exception(e):
        """处理 API 异常"""
        return e.to_response()

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """处理验证错误"""
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "VALIDATION_ERROR"}), 400

    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(e):
        """处理认证错误"""
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "AUTHENTICATION_ERROR"}), 401

    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(e):
        """处理授权错误"""
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "AUTHORIZATION_ERROR"}), 403

    @app.errorhandler(ResourceNotFoundError)
    def handle_not_found_error(e):
        """处理资源未找到错误"""
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "NOT_FOUND"}), 404

    @app.errorhandler(ResourceConflictError)
    def handle_conflict_error(e):
        """处理资源冲突错误"""
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "CONFLICT"}), 409

    @app.errorhandler(BusinessLogicError)
    def handle_business_logic_error(e):
        """处理业务逻辑错误"""
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "BUSINESS_ERROR"}), 422

    @app.errorhandler(ServiceError)
    def handle_service_error(e):
        """处理服务层错误（兜底）"""
        return jsonify({"error": str(e), "code": e.code if hasattr(e, "code") else "SERVICE_ERROR"}), 500

    @app.errorhandler(404)
    def handle_not_found(e):
        """处理 404 错误"""
        return jsonify({"error": "Not Found", "message": str(e)}), 404

    @app.errorhandler(500)
    def handle_internal_error(e):
        """处理 500 错误"""
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
