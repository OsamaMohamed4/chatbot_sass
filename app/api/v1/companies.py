
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import CompanyServiceDep, PaginationDep
from app.api.deps import AuthDependencies
from app.schemas.client_company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse
)
from app.schemas.responses import (
    SuccessResponse,
    PaginatedResponse,
    MessageResponse,
    success_response,
    paginated_response
)
from app.models.system_admin import SystemAdmin

router = APIRouter()
auth_deps = AuthDependencies()


@router.post(
    "",
    response_model=SuccessResponse[CompanyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create new company",
    description="Create a new company with master user account"
)
async def create_company(
    company_data: CompanyCreate,
    service: CompanyServiceDep,
    current_admin: SystemAdmin = Depends(auth_deps.get_current_admin)
):
    """
    Create a new company:
    - Creates company record
    - Creates master user account
    - Assigns resource plan
    - Initializes resource allocation
    """
    company = await service.create_company(company_data)
    return success_response(
        data=CompanyResponse.model_validate(company),
        message="Company created successfully"
    )


@router.get(
    "",
    response_model=PaginatedResponse[CompanyResponse],
    summary="List all companies",
    description="Get paginated list of all companies"
)
async def list_companies(
    service: CompanyServiceDep,
    pagination: PaginationDep,
    status_filter: Optional[str] = Query(None, description="Filter by account status"),
    current_admin: SystemAdmin = Depends(auth_deps.get_current_admin)
):
    """
    Get all companies with pagination and optional filters:
    - Supports pagination
    - Filter by account status (active, suspended, cancelled)
    - Returns total count
    """
    companies, total = await service.get_companies(
        skip=pagination["skip"],
        limit=pagination["limit"],
        status=status_filter
    )
    
    company_responses = [CompanyResponse.model_validate(c) for c in companies]
    
    return paginated_response(
        data=company_responses,
        total=total,
        page=pagination["page"],
        page_size=pagination["page_size"]
    )


@router.get(
    "/search",
    response_model=SuccessResponse[List[CompanyResponse]],
    summary="Search companies",
    description="Search companies by name or email"
)
async def search_companies(
    service: CompanyServiceDep,
    pagination: PaginationDep,
    current_admin: SystemAdmin = Depends(auth_deps.get_current_admin),
    q: str = Query(..., min_length=2, description="Search query")
):
    """
    Search companies by name or email
    """
    companies = await service.search_companies(
        query=q,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    company_responses = [CompanyResponse.model_validate(c) for c in companies]
    
    return success_response(
        data=company_responses,
        message=f"Found {len(company_responses)} companies"
    )


@router.get(
    "/{company_id}",
    response_model=SuccessResponse[CompanyResponse],
    summary="Get company details",
    description="Get detailed information about a specific company"
)
async def get_company(
    company_id: int,
    service: CompanyServiceDep,
    current_admin: SystemAdmin = Depends(auth_deps.get_current_admin)
):
    """
    Get company by ID with all details:
    - Company information
    - Resource plan
    - Resource allocation
    - Account status
    """
    company = await service.get_company_with_details(company_id)
    return success_response(
        data=CompanyResponse.model_validate(company)
    )


@router.put(
    "/{company_id}",
    response_model=SuccessResponse[CompanyResponse],
    summary="Update company",
    description="Update company information"
)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    service: CompanyServiceDep,
    current_admin: SystemAdmin = Depends(auth_deps.get_current_admin)
):
    """
    Update company information:
    - Contact details
    - Business information
    - Company size
    - Industry
    """
    company = await service.update_company(company_id, company_data)
    return success_response(
        data=CompanyResponse.model_validate(company),
        message="Company updated successfully"
    )


@router.delete(
    "/{company_id}",
    response_model=MessageResponse,
    summary="Delete company",
    description="Soft delete a company (sets is_active to False)"
)
async def delete_company(
    company_id: int,
    service: CompanyServiceDep,
    current_admin: SystemAdmin = Depends(auth_deps.require_superuser)
):
    """
    Soft delete a company:
    - Sets is_active to False
    - Company data is retained
    - Requires superuser privileges
    """
    await service.delete_company(company_id)
    return {
        "success": True,
        "message": "Company deleted successfully"
    }


@router.post(
    "/{company_id}/suspend",
    response_model=SuccessResponse[CompanyResponse],
    summary="Suspend company",
    description="Suspend a company account"
)
async def suspend_company(
    company_id: int,
    service: CompanyServiceDep,
    current_admin: SystemAdmin = Depends(auth_deps.get_current_admin),
    reason: str = Query(..., min_length=10, description="Reason for suspension")
):
    """
    Suspend a company account:
    - Sets account_status to 'suspended'
    - Records suspension reason
    - Disables all company access
    """
    company = await service.suspend_company(company_id, reason)
    return success_response(
        data=CompanyResponse.model_validate(company),
        message="Company suspended successfully"
    )


@router.post(
    "/{company_id}/activate",
    response_model=SuccessResponse[CompanyResponse],
    summary="Activate company",
    description="Activate a suspended company account"
)
async def activate_company(
    company_id: int,
    service: CompanyServiceDep,
    current_admin: SystemAdmin = Depends(auth_deps.get_current_admin)
):
    """
    Activate a suspended company:
    - Sets account_status to 'active'
    - Clears suspension reason
    - Restores company access
    """
    company = await service.activate_company(company_id)
    return success_response(
        data=CompanyResponse.model_validate(company),
        message="Company activated successfully"
    )