from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.website import Website
from app.repositories.base_repository import BaseRepository


class WebsiteRepository(BaseRepository[Website]):
    """Repository for Website operations"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Website, db)
    
    async def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Website]:
        """Get all websites for a company"""
        result = await self.db.execute(
            select(Website)
            .where(Website.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_domain(self, domain: str) -> Optional[Website]:
        """Get website by domain"""
        result = await self.db.execute(
            select(Website).where(Website.domain == domain)
        )
        return result.scalar_one_or_none()
    
    async def get_by_url(self, url: str) -> Optional[Website]:
        """Get website by URL"""
        result = await self.db.execute(
            select(Website).where(Website.website_url == url)
        )
        return result.scalar_one_or_none()
    
    async def search_websites(
        self,
        company_id: int,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Website]:
        """Search websites by name or domain"""
        result = await self.db.execute(
            select(Website)
            .where(
                Website.company_id == company_id,
                or_(
                    Website.website_name.ilike(f"%{query}%"),
                    Website.domain.ilike(f"%{query}%"),
                    Website.website_url.ilike(f"%{query}%")
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_with_models(self, id: int) -> Optional[Website]:
        """Get website with AI models"""
        result = await self.db.execute(
            select(Website)
            .options(selectinload(Website.ai_models))
            .where(Website.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Website]:
        """Get all active websites for a company"""
        result = await self.db.execute(
            select(Website)
            .where(
                Website.company_id == company_id,
                Website.is_active == True
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def count_by_company(self, company_id: int) -> int:
        """Count websites for a company"""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count())
            .select_from(Website)
            .where(Website.company_id == company_id)
        )
        return result.scalar_one()