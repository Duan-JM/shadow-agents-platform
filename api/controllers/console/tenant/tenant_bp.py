"""
租户控制器

处理租户创建、成员管理等 HTTP 请求
"""

from functools import wraps
from typing import Optional
from uuid import UUID

from flask import Blueprint, g, jsonify, request

from controllers.console.auth.auth_bp import jwt_required
from models.tenant import TenantPlan, TenantRole
from services import (
    AuthorizationError,
    ResourceConflictError,
    ResourceNotFoundError,
    TenantService,
    ValidationError,
)

# 创建租户蓝图
tenant_bp = Blueprint("tenant", __name__, url_prefix="/api/console/tenants")


# 初始化服务（延迟初始化）
def get_tenant_service():
    """获取租户服务实例"""
    return TenantService()


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


@tenant_bp.route("", methods=["POST"])
@jwt_required
def create_tenant():
    """
    创建租户

    需要 JWT 认证

    请求体:
        {
            "name": "My Tenant",
            "plan": "free"  # 可选：free/pro/team/enterprise
        }

    响应:
        成功 (201):
        {
            "id": "uuid",
            "name": "My Tenant",
            "plan": "free",
            "status": "active",
            "created_at": "2024-01-01T00:00:00"
        }

        失败:
        - 400: 参数错误/租户名已存在
        - 401: 未认证
    """
    try:
        data = request.get_json()
        tenant_service = get_tenant_service()

        # 获取当前用户（由 @jwt_required 填充）
        account = g.current_account

        # 处理 plan 参数 - 将字符串转换为枚举
        plan_str = data.get("plan", "free")
        try:
            plan = TenantPlan[plan_str.upper()]
        except KeyError:
            return (
                jsonify(
                    {
                        "error": f"Invalid plan: {plan_str}. Must be one of: free, pro, enterprise",
                        "code": "VALIDATION_ERROR",
                    }
                ),
                400,
            )

        # 调用服务层创建租户
        tenant = tenant_service.create_tenant(name=data.get("name"), plan=plan, owner_account_id=account.id)

        return (
            jsonify(
                {
                    "id": str(tenant.id),
                    "name": tenant.name,
                    "plan": tenant.plan.value,
                    "status": tenant.status.value,
                    "created_at": tenant.created_at.isoformat(),
                }
            ),
            201,
        )

    except ValidationError as e:
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except ResourceConflictError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_CONFLICT"}), 409
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@tenant_bp.route("", methods=["GET"])
@jwt_required
def get_tenants():
    """
    获取当前用户的所有租户

    需要 JWT 认证

    响应:
        成功 (200):
        {
            "tenants": [
                {
                    "id": "uuid",
                    "name": "My Tenant",
                    "role": "owner",
                    "plan": "free",
                    "status": "active"
                }
            ]
        }
    """
    try:
        account = g.current_account
        tenant_service = get_tenant_service()

        # 获取用户的所有租户
        tenants = tenant_service.get_account_tenants(account.id)

        # 构建响应（需要为每个租户查询角色）
        result = []
        for tenant in tenants:
            role = tenant_service.tenant_repo.get_member_role(tenant.id, account.id)
            result.append(
                {
                    "id": str(tenant.id),
                    "name": tenant.name,
                    "role": role.value if role else "member",
                    "plan": tenant.plan.value,
                    "status": tenant.status.value,
                }
            )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@tenant_bp.route("/<tenant_id>", methods=["GET"])
@jwt_required
def get_tenant(tenant_id):
    """
    获取租户详情

    需要 JWT 认证，且用户必须是该租户的成员

    响应:
        成功 (200):
        {
            "id": "uuid",
            "name": "My Tenant",
            "plan": "free",
            "status": "active",
            "created_at": "2024-01-01T00:00:00"
        }

        失败:
        - 400: UUID 格式错误
        - 403: 无权限（不是成员）
        - 404: 租户不存在
    """
    try:
        # 解析 UUID
        try:
            tenant_uuid = parse_uuid(tenant_id, "tenant ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        tenant_service = get_tenant_service()

        # 先检查租户是否存在
        from repositories import TenantRepository

        tenant = TenantRepository().get_by_id(tenant_uuid)
        if not tenant:
            return jsonify({"error": "Tenant not found", "code": "RESOURCE_NOT_FOUND"}), 404

        # 检查用户是否是成员
        if not tenant_service.is_member(tenant_uuid, account.id):
            return jsonify({"error": "You are not a member of this tenant", "code": "AUTHORIZATION_ERROR"}), 403

        # 返回租户信息
        return (
            jsonify(
                {
                    "id": str(tenant.id),
                    "name": tenant.name,
                    "plan": tenant.plan.value,
                    "status": tenant.status.value,
                    "created_at": tenant.created_at.isoformat(),
                    "updated_at": tenant.updated_at.isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@tenant_bp.route("/<tenant_id>", methods=["PUT"])
@jwt_required
def update_tenant(tenant_id):
    """
    更新租户信息

    需要 JWT 认证，且用户必须是 owner

    请求体:
        {
            "name": "New Name"  # 可选
        }

    响应:
        成功 (200):
        {
            "id": "uuid",
            "name": "New Name",
            "plan": "free",
            "status": "active"
        }

        失败:
        - 400: 参数错误/UUID格式错误
        - 403: 无权限（不是owner）
        - 404: 租户不存在
    """
    try:
        # 解析 UUID
        try:
            tenant_uuid = parse_uuid(tenant_id, "tenant ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        data = request.get_json()
        account = g.current_account
        tenant_service = get_tenant_service()

        # 调用服务层更新（会检查权限）
        tenant = tenant_service.update_tenant(
            tenant_id=tenant_uuid, name=data.get("name"), operator_account_id=account.id
        )

        return (
            jsonify(
                {
                    "id": str(tenant.id),
                    "name": tenant.name,
                    "plan": tenant.plan.value,
                    "status": tenant.status.value,
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


@tenant_bp.route("/<tenant_id>/members", methods=["GET"])
@jwt_required
def get_tenant_members(tenant_id):
    """
    获取租户成员列表

    需要 JWT 认证，且用户必须是该租户的成员

    响应:
        成功 (200):
        {
            "members": [
                {
                    "id": "account_uuid",
                    "email": "user@example.com",
                    "name": "User Name",
                    "role": "owner",
                    "joined_at": "2024-01-01T00:00:00"
                }
            ]
        }

        失败:
        - 400: UUID格式错误
        - 403: 无权限（不是成员）
        - 404: 租户不存在
    """
    try:
        # 解析 UUID
        try:
            tenant_uuid = parse_uuid(tenant_id, "tenant ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account
        tenant_service = get_tenant_service()

        # 检查权限（必须是成员）
        if not tenant_service.is_member(tenant_uuid, account.id):
            return jsonify({"error": "You are not a member of this tenant", "code": "AUTHORIZATION_ERROR"}), 403

        # 获取成员列表
        members = tenant_service.get_tenant_members(tenant_uuid)

        # 构建响应（需要包含角色信息）
        result = []
        for member in members:
            join = tenant_service.tenant_repo.get_member_join(tenant_uuid, member.id)
            result.append(
                {
                    "id": str(member.id),
                    "email": member.email,
                    "name": member.name,
                    "role": join.role.value if join else "member",
                    "joined_at": join.created_at.isoformat() if join else None,
                }
            )

        return jsonify(result), 200

    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@tenant_bp.route("/<tenant_id>/members", methods=["POST"])
@jwt_required
def add_member(tenant_id):
    """
    添加租户成员

    需要 JWT 认证，且用户必须是 owner 或 admin

    请求体:
        {
            "account_id": "uuid",
            "role": "member"  # member/admin
        }

    响应:
        成功 (201):
        {
            "message": "Member added successfully"
        }

        失败:
        - 400: 参数错误/成员已存在/UUID格式错误
        - 403: 无权限
        - 404: 租户或账号不存在
    """
    try:
        # 解析 UUID
        try:
            tenant_uuid = parse_uuid(tenant_id, "tenant ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        data = request.get_json()
        account_id_to_add = data.get("account_id")

        # 解析 account_id
        try:
            account_uuid_to_add = parse_uuid(account_id_to_add, "account ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        role_str = data.get("role", "member")

        # 将字符串转换为枚举
        try:
            role = TenantRole[role_str.upper()]
        except KeyError:
            return (
                jsonify(
                    {
                        "error": f"Invalid role: {role_str}. Must be one of: member, admin",
                        "code": "VALIDATION_ERROR",
                    }
                ),
                400,
            )

        account = g.current_account
        tenant_service = get_tenant_service()

        # 调用服务层添加成员（会检查权限和业务规则）
        tenant_service.add_member(
            tenant_id=tenant_uuid, account_id=account_uuid_to_add, role=role, operator_account_id=account.id
        )

        return jsonify({"message": "Member added successfully"}), 201

    except ValidationError as e:
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except ResourceConflictError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_CONFLICT"}), 409
    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@tenant_bp.route("/<tenant_id>/members/<account_id>", methods=["DELETE"])
@jwt_required
def remove_member(tenant_id, account_id):
    """
    移除租户成员

    需要 JWT 认证，且用户必须是 owner 或 admin
    不能移除 owner

    响应:
        成功 (200):
        {
            "message": "Member removed successfully"
        }

        失败:
        - 400: 不能移除owner/UUID格式错误
        - 403: 无权限
        - 404: 租户或成员不存在
    """
    try:
        # 解析 UUID
        try:
            tenant_uuid = parse_uuid(tenant_id, "tenant ID")
            account_uuid = parse_uuid(account_id, "account ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        account = g.current_account

        # 调用服务层移除成员（会检查权限和业务规则）
        get_tenant_service().remove_member(
            tenant_id=tenant_uuid, account_id=account_uuid, operator_account_id=account.id
        )

        return jsonify({"message": "Member removed successfully"}), 200

    except ValidationError as e:
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500


@tenant_bp.route("/<tenant_id>/members/<account_id>/role", methods=["PUT"])
@jwt_required
def update_member_role(tenant_id, account_id):
    """
    更新成员角色

    需要 JWT 认证，且用户必须是 owner
    不能修改 owner 的角色

    请求体:
        {
            "role": "admin"  # member/admin
        }

    响应:
        成功 (200):
        {
            "message": "Role updated successfully"
        }

        失败:
        - 400: 参数错误/不能修改owner角色/UUID格式错误
        - 403: 无权限（不是owner）
        - 404: 租户或成员不存在
    """
    try:
        # 解析 UUID
        try:
            tenant_uuid = parse_uuid(tenant_id, "tenant ID")
            account_uuid = parse_uuid(account_id, "account ID")
        except ValueError as e:
            return jsonify({"error": str(e), "code": "INVALID_UUID"}), 400

        data = request.get_json()
        role_str = data.get("role")

        # 将字符串转换为枚举
        try:
            new_role = TenantRole[role_str.upper()]
        except KeyError:
            return (
                jsonify(
                    {
                        "error": f"Invalid role: {role_str}. Must be one of: member, admin",
                        "code": "VALIDATION_ERROR",
                    }
                ),
                400,
            )

        account = g.current_account
        tenant_service = get_tenant_service()

        # 调用服务层更新角色（会检查权限和业务规则）
        tenant_service.update_member_role(
            tenant_id=tenant_uuid, account_id=account_uuid, new_role=new_role, operator_account_id=account.id
        )

        return jsonify({"message": "Role updated successfully"}), 200

    except ValidationError as e:
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except AuthorizationError as e:
        return jsonify({"error": str(e), "code": "AUTHORIZATION_ERROR"}), 403
    except ResourceNotFoundError as e:
        return jsonify({"error": str(e), "code": "RESOURCE_NOT_FOUND"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}), 500
