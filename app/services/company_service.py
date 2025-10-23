from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository
from app.schemas.client_company import CompanyCreate, CompanyUpdate
from app.exceptions import (
    ResourceNotFoundException,
    DuplicateResourceException,
    BusinessLogicException
)
from app.core.security import security_service
from app.models.client_company import ClientCompany


class CompanyService:
    """Service for company business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.company_repo = CompanyRepository(db)
        self.user_repo = UserRepository(db)
    
    async def create_company(self, company_data: CompanyCreate) -> ClientCompany:
        """Create a new company with master user"""
        
        # Check for duplicate company name
        existing_company = await self.company_repo.get_by_name(company_data.company_name)
        if existing_company:
            raise DuplicateResourceException(
                "Company",
                "name",
                company_data.company_name
            )
        
        # Check for duplicate company email
        existing_email = await self.company_repo.get_by_email(company_data.company_email)
        if existing_email:
            raise DuplicateResourceException(
                "Company",
                "email",
                company_data.company_email
            )
        
        # Check for duplicate master user email
        existing_user_email = await self.user_repo.get_by_email(company_data.master_user_email)
        if existing_user_email:
            raise DuplicateResourceException(
                "User",
                "email",
                company_data.master_user_email
            )
        
        # Create company
        company_dict = company_data.model_dump(exclude={
            'master_user_email',
            'master_user_firstname',
            'master_user_lastname',
            'master_user_password'
        })
        
        company = await self.company_repo.create(company_dict)
        
        # Create master user
        password = company_data.master_user_password or security_service.generate_password()
        master_user = await self.user_repo.create({
            "username": company_data.master_user_email.split('@')[0],
            "email": company_data.master_user_email,
            "password_hash": security_service.get_password_hash(password),
            "first_name": company_data.master_user_firstname,
            "last_name": company_data.master_user_lastname,
            "role": "master",
            "is_master_user": True,
            "company_id": company.id
        })
        
        await self.db.commit()
        await self.db.refresh(company)
        
        return company
    
    async def get_company(self, company_id: int) -> ClientCompany:
        """Get company by ID"""
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise ResourceNotFoundException("Company", company_id)
        return company
    
    async def get_company_with_details(self, company_id: int) -> ClientCompany:
        """Get company with plan and allocation details"""
        company = await self.company_repo.get_with_plan(company_id)
        if not company:
            raise ResourceNotFoundException("Company", company_id)
        return company
    
    async def update_company(
        self,
        company_id: int,
        company_data: CompanyUpdate
    ) -> ClientCompany:
        """Update company details"""
        company = await self.get_company(company_id)
        
        # Check for duplicate email if being updated
        if company_data.company_email and company_data.company_email != company.company_email:
            existing = await self.company_repo.get_by_email(company_data.company_email)
            if existing:
                raise DuplicateResourceException(
                    "Company",
                    "email",
                    company_data.company_email
                )
        
        update_data = company_data.model_dump(exclude_unset=True)
        updated_company = await self.company_repo.update(company_id, update_data)
        
        await self.db.commit()
        await self.db.refresh(updated_company)
        
        return updated_company
    
    async def delete_company(self, company_id: int) -> bool:
        """Soft delete a company"""
        company = await self.get_company(company_id)
        
        # Check if company has active resources
        # This is where you'd add business logic to prevent deletion
        
        await self.company_repo.soft_delete(company_id)
        await self.db.commit()
        
        return True
    
    async def suspend_company(
        self,
        company_id: int,
        reason: str
    ) -> ClientCompany:
        """Suspend a company account"""
        company = await self.get_company(company_id)
        
        if company.account_status == "suspended":
            raise BusinessLogicException("Company is already suspended")
        
        suspended_company = await self.company_repo.suspend_company(company_id, reason)
        await self.db.commit()
        await self.db.refresh(suspended_company)
        
        return suspended_company
    
    async def activate_company(self, company_id: int) -> ClientCompany:
        """Activate a suspended company"""
        company = await self.get_company(company_id)
        
        if company.account_status == "active":
            raise BusinessLogicException("Company is already active")
        
        activated_company = await self.company_repo.activate_company(company_id)
        await self.db.commit()
        await self.db.refresh(activated_company)
        
        return activated_company
    
    async def get_companies(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> tuple[List[ClientCompany], int]:
        """Get companies with pagination"""
        if status:
            companies = await self.company_repo.get_by_status(status, skip, limit)
            total = await self.company_repo.get_count({"account_status": status})
        else:
            companies = await self.company_repo.get_all(skip, limit)
            total = await self.company_repo.get_count()
        
        return companies, total
    
    async def search_companies(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ClientCompany]:
        """Search companies by name or email"""
        return await self.company_repo.search_companies(query, skip, limit)