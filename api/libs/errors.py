"""
错误处理模块

定义 API 异常类
"""
from typing import Optional, Dict, Any
from flask import jsonify


class APIException(Exception):
    """API 异常基类"""
    
    code = 400
    message = 'Bad Request'
    
    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, data: Optional[Dict[str, Any]] = None):
        """
        初始化异常
        
        参数:
            message: 错误消息
            code: HTTP 状态码
            data: 额外的错误数据
        """
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        self.data = data or {}
        super().__init__(self.message)
    
    def to_response(self):
        """转换为 Flask Response"""
        response = {
            'error': self.__class__.__name__,
            'message': self.message
        }
        if self.data:
            response['data'] = self.data
        return jsonify(response), self.code


class BadRequestError(APIException):
    """400 错误请求"""
    code = 400
    message = 'Bad Request'


class UnauthorizedError(APIException):
    """401 未授权"""
    code = 401
    message = 'Unauthorized'


class ForbiddenError(APIException):
    """403 禁止访问"""
    code = 403
    message = 'Forbidden'


class NotFoundError(APIException):
    """404 未找到"""
    code = 404
    message = 'Not Found'


class ConflictError(APIException):
    """409 冲突"""
    code = 409
    message = 'Conflict'


class InternalServerError(APIException):
    """500 服务器内部错误"""
    code = 500
    message = 'Internal Server Error'
