from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException

from app.api.dependencies import PaginationDep, DatabaseDep
from app.api.deps import AuthDependencies
from app.services.website_service import WebsiteService
from app.schemas.website import (
    WebsiteCreate,
    WebsiteUpdate,
    WebsiteResponse,
    WebsiteListResponse
)
from app.schemas.responses import (
    SuccessResponse,
    PaginatedResponse,
    MessageResponse,
    success_response,
    paginated_response
)
from app.models.company_user import CompanyUser
from app.models.system_admin import SystemAdmin

router = APIRouter()
auth_deps = AuthDependencies()


# ========================
# Endpoints
# ========================

@router.post(
    "",
    response_model=SuccessResponse[WebsiteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create new website",
    description="Create a new website for the company"
)
async def create_website(
    website_data: WebsiteCreate,
    db: DatabaseDep,
    current_user: CompanyUser = Depends(auth_deps.get_current_company_user)
):
    """
    Create a new website:
    - Checks website limit based on plan
    - Generates embed code
    - Creates API endpoint
    - Updates resource allocation
    """
    service = WebsiteService(db)
    
    # Use company_id from website_data or current user's company
    company_id = website_data.company_id if hasattr(website_data, 'company_id') else current_user.company_id
    
    # Check if user has permission
    if company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create website for another company"
        )
    
    website = await service.create_website(
        website_data.model_dump(exclude_unset=True),
        company_id
    )
    
    return success_response(
        data=WebsiteResponse.model_validate(website),
        message="Website created successfully"
    )


@router.get(
    "",
    response_model=PaginatedResponse[WebsiteListResponse],
    summary="List websites",
    description="Get all websites for the current user's company"
)
async def list_websites(
    db: DatabaseDep,
    pagination: PaginationDep,
    active_only: bool = Query(False, description="Show only active websites"),
    current_user: CompanyUser = Depends(auth_deps.get_current_company_user)
):
    """Get all websites for the company"""
    service = WebsiteService(db)
    
    websites, total = await service.get_company_websites(
        current_user.company_id,
        skip=pagination["skip"],
        limit=pagination["limit"],
        active_only=active_only
    )
    
    website_responses = [
        WebsiteListResponse.model_validate(w) for w in websites
    ]
    
    return paginated_response(
        data=website_responses,
        total=total,
        page=pagination["page"],
        page_size=pagination["page_size"]
    )


@router.get(
    "/search",
    response_model=SuccessResponse[List[WebsiteListResponse]],
    summary="Search websites",
    description="Search websites by name or domain"
)
async def search_websites(
    db: DatabaseDep,
    pagination: PaginationDep,
    current_user: CompanyUser = Depends(auth_deps.get_current_company_user),
    q: str = Query(..., min_length=2, description="Search query")
):
    """Search websites"""
    service = WebsiteService(db)
    
    websites = await service.search_websites(
        current_user.company_id,
        q,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    website_responses = [
        WebsiteListResponse.model_validate(w) for w in websites
    ]
    
    return success_response(
        data=website_responses,
        message=f"Found {len(website_responses)} websites"
    )


@router.get(
    "/{website_id}",
    response_model=SuccessResponse[WebsiteResponse],
    summary="Get website details",
    description="Get detailed information about a specific website"
)
async def get_website(
    website_id: int,
    db: DatabaseDep,
    current_user: CompanyUser = Depends(auth_deps.get_current_company_user)
):
    """Get website by ID"""
    service = WebsiteService(db)
    website = await service.get_website_with_details(website_id)
    
    # Check if user has access
    if website.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this website"
        )
    
    return success_response(
        data=WebsiteResponse.model_validate(website)
    )


@router.put(
    "/{website_id}",
    response_model=SuccessResponse[WebsiteResponse],
    summary="Update website",
    description="Update website information"
)
async def update_website(
    website_id: int,
    website_data: WebsiteUpdate,
    db: DatabaseDep,
    current_user: CompanyUser = Depends(auth_deps.get_current_company_user)
):
    """Update website"""
    service = WebsiteService(db)
    website = await service.get_website(website_id)
    
    # Check permissions
    if website.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this website"
        )
    
    updated_website = await service.update_website(
        website_id,
        website_data.model_dump(exclude_unset=True)
    )
    
    return success_response(
        data=WebsiteResponse.model_validate(updated_website),
        message="Website updated successfully"
    )


@router.delete(
    "/{website_id}",
    response_model=MessageResponse,
    summary="Delete website",
    description="Soft delete a website"
)
async def delete_website(
    website_id: int,
    db: DatabaseDep,
    current_user: CompanyUser = Depends(auth_deps.require_master_user)
):
    """Delete website (requires master user)"""
    service = WebsiteService(db)
    website = await service.get_website(website_id)
    
    # Check permissions
    if website.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this website"
        )
    
    await service.delete_website(website_id)
    
    return {
        "success": True,
        "message": "Website deleted successfully"
    }


# ========================
# Admin Endpoints
# ========================

@router.get(
    "/admin/company/{company_id}",
    response_model=PaginatedResponse[WebsiteListResponse],
    summary="[Admin] List company websites",
    description="Admin: Get all websites for any company"
)
async def admin_list_company_websites(
    company_id: int,
    db: DatabaseDep,
    pagination: PaginationDep,
    current_admin: SystemAdmin = Depends(auth_deps.get_current_admin)
):
    """Admin: Get all websites for a company"""
    service = WebsiteService(db)
    
    websites, total = await service.get_company_websites(
        company_id,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    website_responses = [
        WebsiteListResponse.model_validate(w) for w in websites
    ]
    
    return paginated_response(
        data=website_responses,
        total=total,
        page=pagination["page"],
        page_size=pagination["page_size"]
    )