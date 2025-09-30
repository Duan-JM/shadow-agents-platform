"""
模型提供商配置 REST API

提供模型提供商配置管理的 HTTP 接口
"""

import uuid

from flask import Blueprint, g, jsonify, request

from controllers.console.auth.auth_bp import jwt_required
from models import ProviderType
from services import ModelProviderService
from services.exceptions import (
    BusinessLogicError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)

# 创建蓝图
model_provider_bp = Blueprint("model_provider", __name__, url_prefix="/api/console/tenants/<tenant_id>/model-providers")

# 创建服务实例
model_provider_service = ModelProviderService()


@model_provider_bp.route("", methods=["POST"])
@jwt_required
def add_provider(tenant_id: str):
    """
    添加模型提供商配置

    POST /api/console/tenants/:tenant_id/model-providers
    """
    account = g.account
    try:
        tenant_uuid = uuid.UUID(tenant_id)
    except ValueError:
        return jsonify({"error": "Invalid tenant ID format"}), 400

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # 验证必填字段
    name = data.get("name")
    if not name:
        return jsonify({"error": "Provider name is required"}), 400

    provider_type_str = data.get("provider_type")
    if not provider_type_str:
        return jsonify({"error": "Provider type is required"}), 400

    # 转换提供商类型
    try:
        provider_type = ProviderType[provider_type_str.upper()]
    except KeyError:
        return jsonify({"error": f"Invalid provider type: {provider_type_str}"}), 400

    credentials = data.get("credentials")
    if not credentials:
        return jsonify({"error": "Credentials are required"}), 400

    config = data.get("config")
    quota_config = data.get("quota_config")

    try:
        # 调用服务层添加提供商
        provider = model_provider_service.add_provider(
            tenant_id=tenant_uuid,
            name=name,
            provider_type=provider_type,
            credentials=credentials,
            config=config,
            quota_config=quota_config,
            created_by=account.id,
        )

        # 返回结果（不包含敏感凭证）
        return (
            jsonify(
                {
                    "id": str(provider.id),
                    "tenant_id": str(provider.tenant_id),
                    "name": provider.name,
                    "provider_type": provider.provider_type.value,
                    "is_active": provider.is_active,
                    "config": provider.config,
                    "quota_config": provider.quota_config,
                    "created_at": provider.created_at.isoformat(),
                    "created_by": str(provider.created_by) if provider.created_by else None,
                }
            ),
            201,
        )

    except ValidationError as e:
        return jsonify({"error": e.message}), 400
    except ResourceNotFoundError as e:
        return jsonify({"error": e.message}), 404
    except ResourceConflictError as e:
        return jsonify({"error": e.message}), 409
    except BusinessLogicError as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@model_provider_bp.route("", methods=["GET"])
@jwt_required
def list_providers(tenant_id: str):
    """
    获取模型提供商配置列表

    GET /api/console/tenants/:tenant_id/model-providers
    Query params:
        - include_inactive: bool (是否包含停用的配置)
        - provider_type: str (过滤提供商类型)
    """
    try:
        tenant_uuid = uuid.UUID(tenant_id)
    except ValueError:
        return jsonify({"error": "Invalid tenant ID format"}), 400

    # 获取查询参数
    include_inactive = request.args.get("include_inactive", "false").lower() == "true"
    provider_type_str = request.args.get("provider_type")

    provider_type = None
    if provider_type_str:
        try:
            provider_type = ProviderType[provider_type_str.upper()]
        except KeyError:
            return jsonify({"error": f"Invalid provider type: {provider_type_str}"}), 400

    try:
        # 调用服务层获取列表
        providers = model_provider_service.list_providers(
            tenant_id=tenant_uuid, include_inactive=include_inactive, provider_type=provider_type
        )

        # 返回结果
        return jsonify(
            {
                "data": [
                    {
                        "id": str(p.id),
                        "tenant_id": str(p.tenant_id),
                        "name": p.name,
                        "provider_type": p.provider_type.value,
                        "is_active": p.is_active,
                        "config": p.config,
                        "quota_config": p.quota_config,
                        "created_at": p.created_at.isoformat(),
                        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                    }
                    for p in providers
                ],
                "total": len(providers),
            }
        )

    except ResourceNotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@model_provider_bp.route("/<provider_id>", methods=["GET"])
@jwt_required
def get_provider(tenant_id: str, provider_id: str):
    """
    获取模型提供商配置详情

    GET /api/console/tenants/:tenant_id/model-providers/:provider_id
    Query params:
        - include_credentials: bool (是否包含凭证信息)
    """
    try:
        tenant_uuid = uuid.UUID(tenant_id)
        provider_uuid = uuid.UUID(provider_id)
    except ValueError:
        return jsonify({"error": "Invalid ID format"}), 400

    include_credentials = request.args.get("include_credentials", "false").lower() == "true"

    try:
        # 调用服务层获取配置
        provider = model_provider_service.get_provider(tenant_uuid, provider_uuid)

        # 构建响应数据
        response_data = provider.to_dict(include_credentials=include_credentials)

        return jsonify(response_data)

    except ResourceNotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@model_provider_bp.route("/<provider_id>", methods=["PUT"])
@jwt_required
def update_provider(tenant_id: str, provider_id: str):
    """
    更新模型提供商配置

    PUT /api/console/tenants/:tenant_id/model-providers/:provider_id
    """
    account = g.account
    try:
        tenant_uuid = uuid.UUID(tenant_id)
        provider_uuid = uuid.UUID(provider_id)
    except ValueError:
        return jsonify({"error": "Invalid ID format"}), 400

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # 提取可更新字段
    name = data.get("name")
    credentials = data.get("credentials")
    config = data.get("config")
    quota_config = data.get("quota_config")

    try:
        # 调用服务层更新配置
        provider = model_provider_service.update_provider(
            tenant_id=tenant_uuid,
            provider_id=provider_uuid,
            name=name,
            credentials=credentials,
            config=config,
            quota_config=quota_config,
            updated_by=account.id,
        )

        # 返回结果
        return jsonify(
            {
                "id": str(provider.id),
                "tenant_id": str(provider.tenant_id),
                "name": provider.name,
                "provider_type": provider.provider_type.value,
                "is_active": provider.is_active,
                "config": provider.config,
                "quota_config": provider.quota_config,
                "updated_at": provider.updated_at.isoformat() if provider.updated_at else None,
                "updated_by": str(provider.updated_by) if provider.updated_by else None,
            }
        )

    except ValidationError as e:
        return jsonify({"error": e.message}), 400
    except ResourceNotFoundError as e:
        return jsonify({"error": e.message}), 404
    except ResourceConflictError as e:
        return jsonify({"error": e.message}), 409
    except BusinessLogicError as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@model_provider_bp.route("/<provider_id>", methods=["DELETE"])
@jwt_required
def delete_provider(tenant_id: str, provider_id: str):
    """
    删除模型提供商配置

    DELETE /api/console/tenants/:tenant_id/model-providers/:provider_id
    """
    try:
        tenant_uuid = uuid.UUID(tenant_id)
        provider_uuid = uuid.UUID(provider_id)
    except ValueError:
        return jsonify({"error": "Invalid ID format"}), 400

    try:
        # 调用服务层删除配置
        result = model_provider_service.delete_provider(tenant_uuid, provider_uuid)

        if result:
            return jsonify({"message": "Provider deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete provider"}), 500

    except ResourceNotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@model_provider_bp.route("/<provider_id>/test", methods=["POST"])
@jwt_required
def test_provider_connection(tenant_id: str, provider_id: str):
    """
    测试模型提供商连接

    POST /api/console/tenants/:tenant_id/model-providers/:provider_id/test
    """
    try:
        tenant_uuid = uuid.UUID(tenant_id)
        provider_uuid = uuid.UUID(provider_id)
    except ValueError:
        return jsonify({"error": "Invalid ID format"}), 400

    try:
        # 调用服务层测试连接
        result = model_provider_service.test_connection(tenant_uuid, provider_uuid)

        return jsonify(result), 200

    except ResourceNotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@model_provider_bp.route("/<provider_id>/activate", methods=["POST"])
@jwt_required
def activate_provider(tenant_id: str, provider_id: str):
    """
    激活模型提供商配置

    POST /api/console/tenants/:tenant_id/model-providers/:provider_id/activate
    """
    try:
        tenant_uuid = uuid.UUID(tenant_id)
        provider_uuid = uuid.UUID(provider_id)
    except ValueError:
        return jsonify({"error": "Invalid ID format"}), 400

    try:
        # 调用服务层激活配置
        provider = model_provider_service.activate_provider(tenant_uuid, provider_uuid)

        return jsonify(
            {
                "id": str(provider.id),
                "name": provider.name,
                "is_active": provider.is_active,
                "updated_at": provider.updated_at.isoformat() if provider.updated_at else None,
            }
        )

    except ResourceNotFoundError as e:
        return jsonify({"error": e.message}), 404
    except BusinessLogicError as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@model_provider_bp.route("/<provider_id>/deactivate", methods=["POST"])
@jwt_required
def deactivate_provider(tenant_id: str, provider_id: str):
    """
    停用模型提供商配置

    POST /api/console/tenants/:tenant_id/model-providers/:provider_id/deactivate
    """
    try:
        tenant_uuid = uuid.UUID(tenant_id)
        provider_uuid = uuid.UUID(provider_id)
    except ValueError:
        return jsonify({"error": "Invalid ID format"}), 400

    try:
        # 调用服务层停用配置
        provider = model_provider_service.deactivate_provider(tenant_uuid, provider_uuid)

        return jsonify(
            {
                "id": str(provider.id),
                "name": provider.name,
                "is_active": provider.is_active,
                "updated_at": provider.updated_at.isoformat() if provider.updated_at else None,
            }
        )

    except ResourceNotFoundError as e:
        return jsonify({"error": e.message}), 404
    except BusinessLogicError as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
