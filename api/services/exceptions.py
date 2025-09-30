"""
服务层异常

定义业务逻辑异常
"""


class ServiceError(Exception):
    """服务层基础异常"""

    def __init__(self, message: str, code: str = "SERVICE_ERROR"):
        """
        初始化

        参数:
            message: 错误消息
            code: 错误代码
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(ServiceError):
    """数据验证异常"""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class AuthenticationError(ServiceError):
    """认证异常"""

    def __init__(self, message: str):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(ServiceError):
    """授权异常"""

    def __init__(self, message: str):
        super().__init__(message, "AUTHORIZATION_ERROR")


class ResourceNotFoundError(ServiceError):
    """资源不存在异常"""

    def __init__(self, resource: str, identifier: str):
        message = f"{resource} not found: {identifier}"
        super().__init__(message, "RESOURCE_NOT_FOUND")
        self.resource = resource
        self.identifier = identifier


class ResourceConflictError(ServiceError):
    """资源冲突异常"""

    def __init__(self, message: str):
        super().__init__(message, "RESOURCE_CONFLICT")


class BusinessLogicError(ServiceError):
    """业务逻辑异常"""

    def __init__(self, message: str):
        super().__init__(message, "BUSINESS_LOGIC_ERROR")
