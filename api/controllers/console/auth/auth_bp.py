"""
认证控制器

处理用户注册、登录、登出等认证相关的 HTTP 请求
"""
from flask import Blueprint, request, jsonify, g
from functools import wraps
from typing import Optional
import jwt

from services import AuthService, ValidationError, AuthenticationError, ResourceConflictError
from configs.app_config import Config


# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/console/auth')

# 初始化服务（延迟初始化，在请求时获取配置）
def get_auth_service():
    """获取认证服务实例"""
    from flask import current_app
    return AuthService(
        secret_key=current_app.config.get('SECRET_KEY', 'change-me-in-production'),
        token_expiry_hours=current_app.config.get('JWT_TOKEN_EXPIRY_HOURS', 24)
    )


def jwt_required(f):
    """JWT 认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 从请求头获取 token
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Missing or invalid authorization header',
                'code': 'UNAUTHORIZED'
            }), 401
        
        token = auth_header[7:]  # 移除 'Bearer ' 前缀
        
        try:
            # 验证 token
            account = get_auth_service().verify_token(token)
            g.current_account = account  # 将账户信息存入 Flask g 对象
            return f(*args, **kwargs)
        except AuthenticationError as e:
            return jsonify({
                'error': str(e),
                'code': 'UNAUTHORIZED'
            }), 401
        except Exception as e:
            return jsonify({
                'error': 'Internal server error',
                'code': 'INTERNAL_ERROR'
            }), 500
    
    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    
    请求体:
        {
            "email": "user@example.com",
            "password": "password123",
            "name": "User Name"
        }
    
    响应:
        成功 (201):
        {
            "id": "uuid",
            "email": "user@example.com",
            "name": "User Name",
            "status": "active"
        }
        
        失败 (400/409):
        {
            "error": "error message",
            "code": "ERROR_CODE"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'INVALID_REQUEST'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        # 验证必需字段
        if not all([email, password, name]):
            return jsonify({
                'error': 'Email, password, and name are required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        # 调用服务层注册
        account = get_auth_service().register(email, password, name)
        
        return jsonify({
            'id': str(account.id),
            'email': account.email,
            'name': account.name,
            'status': account.status.value
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except ResourceConflictError as e:
        return jsonify({
            'error': str(e),
            'code': 'RESOURCE_CONFLICT'
        }), 409
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求体:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    
    响应:
        成功 (200):
        {
            "account": {
                "id": "uuid",
                "email": "user@example.com",
                "name": "User Name",
                "status": "active"
            },
            "token": "jwt_token_string"
        }
        
        失败 (401):
        {
            "error": "error message",
            "code": "AUTHENTICATION_ERROR"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'INVALID_REQUEST'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({
                'error': 'Email and password are required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        # 调用服务层登录
        account, token = get_auth_service().login(email, password)
        
        return jsonify({
            'account': {
                'id': str(account.id),
                'email': account.email,
                'name': account.name,
                'status': account.status.value,
                'avatar': account.avatar
            },
            'token': token
        }), 200
        
    except AuthenticationError as e:
        return jsonify({
            'error': str(e),
            'code': 'AUTHENTICATION_ERROR'
        }), 401
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user():
    """
    获取当前用户信息
    
    需要 JWT 认证
    
    响应:
        成功 (200):
        {
            "id": "uuid",
            "email": "user@example.com",
            "name": "User Name",
            "status": "active",
            "avatar": "avatar_url",
            "created_at": "2024-01-01T00:00:00"
        }
    """
    try:
        account = g.current_account
        
        return jsonify({
            'id': str(account.id),
            'email': account.email,
            'name': account.name,
            'status': account.status.value,
            'avatar': account.avatar,
            'created_at': account.created_at.isoformat() if account.created_at else None,
            'last_login_at': account.last_login_at.isoformat() if account.last_login_at else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """
    用户登出
    
    需要 JWT 认证
    
    注意: JWT 是无状态的，服务端不存储 token，所以这个接口主要用于客户端清除 token
    实际的 token 失效由过期时间控制
    
    响应:
        成功 (200):
        {
            "message": "Logged out successfully"
        }
    """
    return jsonify({
        'message': 'Logged out successfully'
    }), 200


@auth_bp.route('/password/change', methods=['POST'])
@jwt_required
def change_password():
    """
    修改密码
    
    需要 JWT 认证
    
    请求体:
        {
            "old_password": "old_password",
            "new_password": "new_password"
        }
    
    响应:
        成功 (200):
        {
            "message": "Password changed successfully"
        }
        
        失败 (400/401):
        {
            "error": "error message",
            "code": "ERROR_CODE"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'INVALID_REQUEST'
            }), 400
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not all([old_password, new_password]):
            return jsonify({
                'error': 'Old password and new password are required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        account = g.current_account
        
        # 调用服务层修改密码
        get_auth_service().change_password(account.id, old_password, new_password)
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except AuthenticationError as e:
        return jsonify({
            'error': str(e),
            'code': 'AUTHENTICATION_ERROR'
        }), 401
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@auth_bp.route('/password/reset', methods=['POST'])
def reset_password():
    """
    重置密码
    
    请求体:
        {
            "email": "user@example.com",
            "new_password": "new_password",
            "verification_code": "code"  # 实际场景需要验证码验证
        }
    
    注意: 生产环境中应该先通过邮件/短信发送验证码，验证通过后才能重置密码
    这里简化处理，仅做示例
    
    响应:
        成功 (200):
        {
            "message": "Password reset successfully"
        }
        
        失败 (400):
        {
            "error": "error message",
            "code": "ERROR_CODE"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'INVALID_REQUEST'
            }), 400
        
        email = data.get('email')
        new_password = data.get('new_password')
        # verification_code = data.get('verification_code')  # 实际应验证
        
        if not all([email, new_password]):
            return jsonify({
                'error': 'Email and new password are required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        # TODO: 实际场景中应该验证 verification_code
        
        # 调用服务层重置密码
        get_auth_service().reset_password(email, new_password)
        
        return jsonify({
            'message': 'Password reset successfully'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500
