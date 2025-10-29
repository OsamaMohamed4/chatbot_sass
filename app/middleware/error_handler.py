from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

from app.exceptions import (
    BaseAPIException,
    ResourceNotFoundException,
    DuplicateResourceException,
    UnauthorizedException,
    ForbiddenException,
    BusinessLogicException,
    ResourceLimitException
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers"""
    
    @app.exception_handler(BaseAPIException)
    async def base_api_exception_handler(request: Request, exc: BaseAPIException):
        """Handle custom API exceptions"""
        logger.error(
            f"API Exception: {exc.message}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "details": exc.details
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.message,
                "details": exc.details,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Validation Error: {request.url.path}",
            extra={"errors": errors}
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "Validation error",
                "details": {"validation_errors": errors},
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors"""
        logger.error(
            f"Database Integrity Error: {str(exc)}",
            extra={"path": request.url.path}
        )
        
        # Parse common integrity errors
        error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        if "duplicate key" in error_msg.lower():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "success": False,
                    "error": "Duplicate record exists",
                    "details": {"database_error": "A record with this information already exists"},
                    "path": str(request.url.path)
                }
            )
        elif "foreign key" in error_msg.lower():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error": "Invalid reference",
                    "details": {"database_error": "Referenced record does not exist"},
                    "path": str(request.url.path)
                }
            )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "details": {"database_error": "A database error occurred"},
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.exception(
            f"Unhandled Exception: {str(exc)}",
            extra={
                "path": request.url.path,
                "exception_type": type(exc).__name__
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "details": {
                    "message": "An unexpected error occurred"
                },
                "path": str(request.url.path)
            }
        )