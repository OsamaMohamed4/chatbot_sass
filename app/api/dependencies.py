from typing import Annotated
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.company_service import CompanyService
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository


# ========================
# Repository Dependencies
# ========================

def get_company_repository(
    db: AsyncSession = Depends(get_db)
) -> CompanyRepository:
    """Get company repository instance"""
    return CompanyRepository(db)


def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    """Get user repository instance"""
    return UserRepository(db)


# ========================
# Service Dependencies
# ========================

def get_company_service(
    db: AsyncSession = Depends(get_db)
) -> CompanyService:
    """Get company service instance"""
    return CompanyService(db)


# ========================
# Pagination Dependencies
# ========================

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
) -> dict:
    """Get pagination parameters"""
    skip = (page - 1) * page_size
    return {
        "skip": skip,
        "limit": page_size,
        "page": page,
        "page_size": page_size
    }


# ========================
# Type Aliases (for FastAPI dependency injection)
# ========================

CompanyServiceDep = Annotated[CompanyService, Depends(get_company_service)]
CompanyRepositoryDep = Annotated[CompanyRepository, Depends(get_company_repository)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
PaginationDep = Annotated[dict, Depends(get_pagination_params)]
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]