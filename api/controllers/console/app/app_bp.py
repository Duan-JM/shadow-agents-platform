"""
应用控制器

处理应用创建、管理等 HTTP 请求
"""

from typing import Optional
from uuid import UUID

from flask import Blueprint, g, jsonify, request

from controllers.console.auth.auth_bp import jwt_required
from models.app import AppMode, AppStatus
from services import (
    AppService,
    AuthorizationError,
    BusinessLogicError,
    ResourceNotFoundError,
    ValidationError,
)

# 创建应用蓝图
app_bp = Blueprint("app", __name__, url_prefix="/api/console/apps")


# 初始化服务（延迟初始化）
def get_app_service():
    """获取应用服务实例"""
    return AppService()


def parse_uuid(uuid_string: str, name: str = "ID") -> Optional[UUID]:
    """
    解析 UUID 字符串

    参数:
        uuid_string: UUID 字符串
        name: 参数名称（用于错误消息）

    返回:
        UUID 对象或 None（如果解析失败）

    抛出:
        ValueError: 如果 UUID 格式不正确
    """
    import uuid as uuid_module

    try:
        return uuid_module.UUID(uuid_string)
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid {name}: {uuid_string}")


@app_bp.route("", methods=["POST"])
@jwt_required
def create_app():
    """
    创建应用

    需要 JWT 认证，且用户必须是租户的成员

    请求体:
        {
            "tenant_id": "uuid",
            "name": "My App",
            "mode": "chat",  # chat/completion/agent/workflow
            "description": "App description",  # 可选
            "icon": "🤖",  # 可选
            "icon_background": "#E0F2FE"  # 可选
        }

    响应:
        成功 (201):
        {
            "id": "uuid",
            "name": "My App",
            "mode": "chat",
            "description": "...",
            "icon": "🤖",
            "icon_background": "#E0F2FE",
            "status": "normal",
            "enable_site": true,
            "enable_api": true,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }

        失败:
        - 400: 参数错误
        - 401: 未认证
        - 403: 无权限（不是租户成员）
        - 404: 租户不存在
    """
    try:
        data = request.get_json()
        app_service = get_app_service()
        account = g.current_account

        # 解析租户 ID
        tenant_id_str = data.get("tenant_id")
        if not tenant_id_str:
            return jsonify({"error": "tenant_id is required", "code": "VALIDATION_ERROR"}), 400

        try:
            tenant_id = parse_uuid(tenant_id_str, "tenant ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        # 解析应用模式
        mode_str = data.get("mode", "chat")
        try:
            mode = AppMode[mode_str.upper()]
        except KeyError:
            return (
                jsonify(
                    {
                        "error": f"Invalid mode: {mode_str}. Must be one of: chat, completion, agent, workflow",
                        "code": "VALIDATION_ERROR",
                    }
                ),
                400,
            )

        # 调用服务层创建应用
        app = app_service.create_app(
            tenant_id=tenant_id,
            account_id=account.id,
            name=data.get("name"),
            mode=mode,
            description=data.get("description"),
            icon=data.get("icon"),
            icon_background=data.get("icon_background"),
        )

        return (
            jsonify(
                {
                    "id": str(app.id),
                    "name": app.name,
                    "mode": app.mode.value,
                    "description": app.description,
                    "icon": app.icon,
                    "icon_background": app.icon_background,
                    "status": app.status.value,
                    "enable_site": app.enable_site,
                    "enable_api": app.enable_api,
                    "created_at": app.created_at.isoformat(),
                    "updated_at": app.updated_at.isoformat(),
                }
            ),
            201,
        )

    except ValidationError as e:
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("", methods=["GET"])
@jwt_required
def get_apps():
    """
    获取租户下的应用列表

    需要 JWT 认证

    查询参数:
        tenant_id: 租户 ID (必需)
        include_archived: 是否包含已归档应用 (可选，默认 false)

    响应:
        成功 (200):
        [
            {
                "id": "uuid",
                "name": "My App",
                "mode": "chat",
                "icon": "🤖",
                "icon_background": "#E0F2FE",
                "status": "normal"
            }
        ]
    """
    try:
        account = g.current_account
        app_service = get_app_service()

        # 获取查询参数
        tenant_id_str = request.args.get("tenant_id")
        if not tenant_id_str:
            return jsonify({"error": "tenant_id is required", "code": "VALIDATION_ERROR"}), 400

        try:
            tenant_id = parse_uuid(tenant_id_str, "tenant ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        include_archived = request.args.get("include_archived", "false").lower() == "true"

        # 获取应用列表
        apps = app_service.get_tenant_apps(tenant_id, account.id, include_archived)

        # 构建响应
        result = []
        for app in apps:
            result.append(
                {
                    "id": str(app.id),
                    "name": app.name,
                    "mode": app.mode.value,
                    "icon": app.icon,
                    "icon_background": app.icon_background,
                    "status": app.status.value,
                }
            )

        return jsonify(result), 200

    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("/<app_id>", methods=["GET"])
@jwt_required
def get_app(app_id):
    """
    获取应用详情

    需要 JWT 认证，且用户必须是租户成员

    响应:
        成功 (200):
        {
            "id": "uuid",
            "name": "My App",
            "mode": "chat",
            "description": "...",
            "icon": "🤖",
            "icon_background": "#E0F2FE",
            "status": "normal",
            "enable_site": true,
            "enable_api": true,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }

        失败:
        - 400: UUID 格式错误
        - 403: 无权限
        - 404: 应用不存在
    """
    try:
        # 解析 UUID
        try:
            app_uuid = parse_uuid(app_id, "app ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        app_service = get_app_service()

        # 获取应用详情
        app = app_service.get_app_detail(app_uuid, account.id)

        return (
            jsonify(
                {
                    "id": str(app.id),
                    "name": app.name,
                    "mode": app.mode.value,
                    "description": app.description,
                    "icon": app.icon,
                    "icon_background": app.icon_background,
                    "status": app.status.value,
                    "enable_site": app.enable_site,
                    "enable_api": app.enable_api,
                    "created_at": app.created_at.isoformat(),
                    "updated_at": app.updated_at.isoformat(),
                }
            ),
            200,
        )

    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("/<app_id>", methods=["PUT"])
@jwt_required
def update_app(app_id):
    """
    更新应用信息

    需要 JWT 认证，且用户必须是租户成员

    请求体:
        {
            "name": "New Name",  # 可选
            "description": "New description",  # 可选
            "icon": "🚀",  # 可选
            "icon_background": "#FEE"  # 可选
        }

    响应:
        成功 (200):
        {
            "id": "uuid",
            "name": "New Name",
            ...
        }

        失败:
        - 400: 参数错误/UUID格式错误
        - 403: 无权限
        - 404: 应用不存在
    """
    try:
        # 解析 UUID
        try:
            app_uuid = parse_uuid(app_id, "app ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        data = request.get_json()
        account = g.current_account
        app_service = get_app_service()

        # 调用服务层更新
        app = app_service.update_app(app_id=app_uuid, account_id=account.id, **data)

        return (
            jsonify(
                {
                    "id": str(app.id),
                    "name": app.name,
                    "mode": app.mode.value,
                    "description": app.description,
                    "icon": app.icon,
                    "icon_background": app.icon_background,
                    "status": app.status.value,
                    "enable_site": app.enable_site,
                    "enable_api": app.enable_api,
                    "updated_at": app.updated_at.isoformat(),
                }
            ),
            200,
        )

    except ValidationError as e:
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("/<app_id>", methods=["DELETE"])
@jwt_required
def delete_app(app_id):
    """
    删除应用

    需要 JWT 认证，且用户必须是租户成员

    响应:
        成功 (204): 无内容

        失败:
        - 400: UUID格式错误
        - 403: 无权限
        - 404: 应用不存在
    """
    try:
        # 解析 UUID
        try:
            app_uuid = parse_uuid(app_id, "app ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        app_service = get_app_service()

        # 调用服务层删除
        app_service.delete_app(app_id=app_uuid, account_id=account.id)

        return "", 204

    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("/<app_id>/archive", methods=["POST"])
@jwt_required
def archive_app(app_id):
    """
    归档应用

    需要 JWT 认证，且用户必须是租户成员

    响应:
        成功 (200):
        {
            "id": "uuid",
            "status": "archived",
            ...
        }

        失败:
        - 400: UUID格式错误
        - 403: 无权限
        - 404: 应用不存在
    """
    try:
        # 解析 UUID
        try:
            app_uuid = parse_uuid(app_id, "app ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        app_service = get_app_service()

        # 调用服务层归档
        app = app_service.archive_app(app_id=app_uuid, account_id=account.id)

        return (
            jsonify(
                {
                    "id": str(app.id),
                    "name": app.name,
                    "status": app.status.value,
                }
            ),
            200,
        )

    except BusinessLogicError as e:
        return jsonify({"error": str(e), "code": "BUSINESS_LOGIC_ERROR"}), 400
    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("/<app_id>/unarchive", methods=["POST"])
@jwt_required
def unarchive_app(app_id):
    """
    取消归档应用

    需要 JWT 认证，且用户必须是租户成员

    响应:
        成功 (200):
        {
            "id": "uuid",
            "status": "normal",
            ...
        }

        失败:
        - 400: UUID格式错误
        - 403: 无权限
        - 404: 应用不存在
    """
    try:
        # 解析 UUID
        try:
            app_uuid = parse_uuid(app_id, "app ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        app_service = get_app_service()

        # 调用服务层取消归档
        app = app_service.unarchive_app(app_id=app_uuid, account_id=account.id)

        return (
            jsonify(
                {
                    "id": str(app.id),
                    "name": app.name,
                    "status": app.status.value,
                }
            ),
            200,
        )

    except BusinessLogicError as e:
        return jsonify({"error": str(e), "code": "BUSINESS_LOGIC_ERROR"}), 400
    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("/<app_id>/site/enable", methods=["POST"])
@jwt_required
def enable_site(app_id):
    """
    启用站点访问

    需要 JWT 认证，且用户必须是租户成员

    响应:
        成功 (200):
        {
            "id": "uuid",
            "enable_site": true
        }
    """
    try:
        # 解析 UUID
        try:
            app_uuid = parse_uuid(app_id, "app ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        app_service = get_app_service()

        # 调用服务层
        app = app_service.toggle_site(app_id=app_uuid, account_id=account.id, enable=True)

        return jsonify({"id": str(app.id), "enable_site": app.enable_site}), 200

    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("/<app_id>/site/disable", methods=["POST"])
@jwt_required
def disable_site(app_id):
    """
    禁用站点访问

    需要 JWT 认证，且用户必须是租户成员

    响应:
        成功 (200):
        {
            "id": "uuid",
            "enable_site": false
        }
    """
    try:
        # 解析 UUID
        try:
            app_uuid = parse_uuid(app_id, "app ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        app_service = get_app_service()

        # 调用服务层
        app = app_service.toggle_site(app_id=app_uuid, account_id=account.id, enable=False)

        return jsonify({"id": str(app.id), "enable_site": app.enable_site}), 200

    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("/<app_id>/api/enable", methods=["POST"])
@jwt_required
def enable_api(app_id):
    """
    启用 API 访问

    需要 JWT 认证，且用户必须是租户成员

    响应:
        成功 (200):
        {
            "id": "uuid",
            "enable_api": true
        }
    """
    try:
        # 解析 UUID
        try:
            app_uuid = parse_uuid(app_id, "app ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        app_service = get_app_service()

        # 调用服务层
        app = app_service.toggle_api(app_id=app_uuid, account_id=account.id, enable=True)

        return jsonify({"id": str(app.id), "enable_api": app.enable_api}), 200

    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@app_bp.route("/<app_id>/api/disable", methods=["POST"])
@jwt_required
def disable_api(app_id):
    """
    禁用 API 访问

    需要 JWT 认证，且用户必须是租户成员

    响应:
        成功 (200):
        {
            "id": "uuid",
            "enable_api": false
        }
    """
    try:
        # 解析 UUID
        try:
            app_uuid = parse_uuid(app_id, "app ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        app_service = get_app_service()

        # 调用服务层
        app = app_service.toggle_api(app_id=app_uuid, account_id=account.id, enable=False)

        return jsonify({"id": str(app.id), "enable_api": app.enable_api}), 200

    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500
