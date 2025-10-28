import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import access_logger, api_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start time
        start_time = time.time()
        
        # Log request
        api_logger.info(
            f"Incoming Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            api_logger.exception(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path
                }
            )
            raise
        
        # Calculate process time
        process_time = time.time() - start_time
        
        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        # Log response
        access_logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": f"{process_time:.4f}s",
                "client_host": request.client.host if request.client else None
            }
        )
        
        # Log slow requests (> 1 second)
        if process_time > 1.0:
            api_logger.warning(
                f"Slow request detected: {process_time:.4f}s",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": process_time
                }
            )
        
        return response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add request context to all logs"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract user info from token if present
        user_id = None
        user_type = None
        company_id = None
        
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                # Extract token from "Bearer <token>"
                token = auth_header.split(" ")[1]
                
                # Import here to avoid circular imports
                from app.core.security import security_service
                
                # Decode token and extract user info
                payload = security_service.decode_token(token)
                if payload:
                    user_id = payload.get("sub")
                    user_type = payload.get("user_type")
                    company_id = payload.get("company_id")
                    
                    # Log authentication info
                    api_logger.debug(
                        "Request authenticated",
                        extra={
                            "user_id": user_id,
                            "user_type": user_type,
                            "company_id": company_id
                        }
                    )
            except Exception as e:
                # Log token decode error but don't block request
                api_logger.warning(
                    f"Failed to decode auth token: {str(e)}",
                    extra={
                        "path": request.url.path,
                        "error": str(e)
                    }
                )
        
        # Store context in request state for use in other parts of the app
        request.state.user_id = user_id
        request.state.user_type = user_type
        request.state.company_id = company_id
        
        response = await call_next(request)
        return response