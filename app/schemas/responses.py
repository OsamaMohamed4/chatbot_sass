from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper"""
    success: bool = True
    data: T
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "name": "Example"},
                "message": "Operation completed successfully",
                "timestamp": "2025-10-22T12:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response wrapper"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Resource not found",
                "details": {"resource": "Company", "id": 123},
                "path": "/api/v1/companies/123",
                "timestamp": "2025-10-22T12:00:00Z"
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper"""
    success: bool = True
    data: List[T]
    pagination: "PaginationMeta"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [{"id": 1, "name": "Item 1"}],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "page_size": 10,
                    "total_pages": 10
                },
                "timestamp": "2025-10-22T12:00:00Z"
            }
        }


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    @classmethod
    def create(cls, total: int, page: int, page_size: int) -> "PaginationMeta":
        """Create pagination metadata"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


class MessageResponse(BaseModel):
    """Simple message response"""
    success: bool = True
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "timestamp": "2025-10-22T12:00:00Z"
            }
        }


# Helper functions for creating responses
def success_response(data: Any, message: Optional[str] = None) -> dict:
    """Create a success response"""
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow()
    }


def error_response(
    error: str,
    details: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None
) -> dict:
    """Create an error response"""
    return {
        "success": False,
        "error": error,
        "details": details,
        "path": path,
        "timestamp": datetime.utcnow()
    }


def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int
) -> dict:
    """Create a paginated response"""
    return {
        "success": True,
        "data": data,
        "pagination": PaginationMeta.create(total, page, page_size).dict(),
        "timestamp": datetime.utcnow()
    }