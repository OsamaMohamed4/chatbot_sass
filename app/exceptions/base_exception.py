from typing import Optional, Dict, Any
from fastapi import status


class BaseAPIException(Exception):
    """Base exception for all API errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BaseAPIException):
    """Exception for validation errors"""
    
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class ResourceNotFoundException(BaseAPIException):
    """Exception for resource not found errors"""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)}
        )


class DuplicateResourceException(BaseAPIException):
    """Exception for duplicate resource errors"""
    
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": resource, "field": field, "value": str(value)}
        )


class UnauthorizedException(BaseAPIException):
    """Exception for unauthorized access"""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenException(BaseAPIException):
    """Exception for forbidden access"""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class BusinessLogicException(BaseAPIException):
    """Exception for business logic violations"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class ResourceLimitException(BaseAPIException):
    """Exception for resource limit violations"""
    
    def __init__(self, resource: str, limit: int, current: int):
        super().__init__(
            message=f"{resource} limit exceeded. Limit: {limit}, Current: {current}",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"resource": resource, "limit": limit, "current": current}
        )