from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.client_company import ClientCompany
from app.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[ClientCompany]):
    """Repository for ClientCompany operations"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ClientCompany, db)
    
    async def get_by_email(self, email: str) -> Optional[ClientCompany]:
        """Get company by email"""
        result = await self.db.execute(
            select(ClientCompany).where(ClientCompany.company_email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[ClientCompany]:
        """Get company by name"""
        result = await self.db.execute(
            select(ClientCompany).where(ClientCompany.company_name == name)
        )
        return result.scalar_one_or_none()
    
    async def search_companies(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ClientCompany]:
        """Search companies by name or email"""
        result = await self.db.execute(
            select(ClientCompany)
            .where(
                or_(
                    ClientCompany.company_name.ilike(f"%{query}%"),
                    ClientCompany.company_email.ilike(f"%{query}%")
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_with_plan(self, id: int) -> Optional[ClientCompany]:
        """Get company with resource plan"""
        result = await self.db.execute(
            select(ClientCompany)
            .options(selectinload(ClientCompany.resource_plan))
            .where(ClientCompany.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_allocation(self, id: int) -> Optional[ClientCompany]:
        """Get company with resource allocation"""
        result = await self.db.execute(
            select(ClientCompany)
            .options(selectinload(ClientCompany.resource_allocation))
            .where(ClientCompany.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_companies_by_admin(
        self,
        admin_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ClientCompany]:
        """Get all companies managed by a specific admin"""
        result = await self.db.execute(
            select(ClientCompany)
            .where(ClientCompany.admin_id == admin_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ClientCompany]:
        """Get companies by account status"""
        result = await self.db.execute(
            select(ClientCompany)
            .where(ClientCompany.account_status == status)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def suspend_company(
        self,
        id: int,
        reason: str
    ) -> Optional[ClientCompany]:
        """Suspend a company account"""
        return await self.update(id, {
            "account_status": "suspended",
            "suspension_reason": reason
        })
    
    async def activate_company(self, id: int) -> Optional[ClientCompany]:
        """Activate a company account"""
        return await self.update(id, {
            "account_status": "active",
            "suspension_reason": None
        })