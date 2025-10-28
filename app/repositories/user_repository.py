from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_user import CompanyUser
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[CompanyUser]):
    """Repository for CompanyUser operations"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(CompanyUser, db)
    
    async def get_by_username(self, username: str) -> Optional[CompanyUser]:
        """Get user by username"""
        result = await self.db.execute(
            select(CompanyUser).where(CompanyUser.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[CompanyUser]:
        """Get user by email"""
        result = await self.db.execute(
            select(CompanyUser).where(CompanyUser.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyUser]:
        """Get all users in a company"""
        result = await self.db.execute(
            select(CompanyUser)
            .where(CompanyUser.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_master_user(self, company_id: int) -> Optional[CompanyUser]:
        """Get the master user of a company"""
        result = await self.db.execute(
            select(CompanyUser)
            .where(
                CompanyUser.company_id == company_id,
                CompanyUser.is_master_user == True
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_role(
        self,
        company_id: int,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyUser]:
        """Get users by role in a company"""
        result = await self.db.execute(
            select(CompanyUser)
            .where(
                CompanyUser.company_id == company_id,
                CompanyUser.role == role
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def exists_username(self, username: str) -> bool:
        """Check if username exists"""
        user = await self.get_by_username(username)
        return user is not None
    
    async def exists_email(self, email: str) -> bool:
        """Check if email exists"""
        user = await self.get_by_email(email)
        return user is not None