from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.website_repository import WebsiteRepository
from app.repositories.company_repository import CompanyRepository
from app.models.website import Website
from app.models.resource_allocation import ResourceAllocation
from app.exceptions import (
    ResourceNotFoundException,
    DuplicateResourceException,
    BusinessLogicException,
    ResourceLimitException
)
from app.core.security import security_service


class WebsiteService:
    """Service for website business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.website_repo = WebsiteRepository(db)
        self.company_repo = CompanyRepository(db)
    
    async def _check_website_limit(self, company_id: int) -> None:
        """Check if company can create more websites"""
        # Get company with plan and allocation
        company = await self.company_repo.get_with_plan(company_id)
        if not company:
            raise ResourceNotFoundException("Company", company_id)
        
        if not company.resource_plan:
            raise BusinessLogicException("Company has no resource plan assigned")
        
        # Get current website count
        current_count = await self.website_repo.count_by_company(company_id)
        
        # Check limit
        max_websites = company.resource_plan.max_websites
        if current_count >= max_websites:
            raise ResourceLimitException(
                "Websites",
                max_websites,
                current_count
            )
    
    async def _update_website_count(self, company_id: int) -> None:
        """Update website count in resource allocation"""
        result = await self.db.execute(
            select(ResourceAllocation).where(
                ResourceAllocation.company_id == company_id
            )
        )
        allocation = result.scalar_one_or_none()
        
        if allocation:
            current_count = await self.website_repo.count_by_company(company_id)
            allocation.current_websites = current_count
            await self.db.flush()
    
    async def create_website(
        self,
        website_data: dict,
        company_id: int
    ) -> Website:
        """Create a new website"""
        # Check website limit
        await self._check_website_limit(company_id)
        
        # Check for duplicate domain
        if website_data.get('domain'):
            existing_domain = await self.website_repo.get_by_domain(
                website_data['domain']
            )
            if existing_domain:
                raise DuplicateResourceException(
                    "Website",
                    "domain",
                    website_data['domain']
                )
        
        # Extract domain from URL if not provided
        if not website_data.get('domain'):
            from urllib.parse import urlparse
            parsed_url = urlparse(str(website_data['website_url']))
            website_data['domain'] = parsed_url.netloc
        
        # Set company_id
        website_data['company_id'] = company_id
        
        # Generate embed code and API endpoint
        website_data['embed_code'] = self._generate_embed_code()
        website_data['api_endpoint'] = f"/api/v1/chat/widget/{company_id}"
        
        # Create website
        website = await self.website_repo.create(website_data)
        
        # Update resource allocation
        await self._update_website_count(company_id)
        
        await self.db.commit()
        await self.db.refresh(website)
        
        return website
    
    async def get_website(self, website_id: int) -> Website:
        """Get website by ID"""
        website = await self.website_repo.get_by_id(website_id)
        if not website:
            raise ResourceNotFoundException("Website", website_id)
        return website
    
    async def get_website_with_details(self, website_id: int) -> Website:
        """Get website with AI models"""
        website = await self.website_repo.get_with_models(website_id)
        if not website:
            raise ResourceNotFoundException("Website", website_id)
        return website
    
    async def update_website(
        self,
        website_id: int,
        website_data: dict
    ) -> Website:
        """Update website"""
        website = await self.get_website(website_id)
        
        # Check for duplicate domain if being updated
        if website_data.get('domain') and website_data['domain'] != website.domain:
            existing = await self.website_repo.get_by_domain(website_data['domain'])
            if existing and existing.id != website_id:
                raise DuplicateResourceException(
                    "Website",
                    "domain",
                    website_data['domain']
                )
        
        # Update website
        updated_website = await self.website_repo.update(website_id, website_data)
        
        await self.db.commit()
        await self.db.refresh(updated_website)
        
        return updated_website
    
    async def delete_website(self, website_id: int) -> bool:
        """Soft delete a website"""
        website = await self.get_website(website_id)
        
        # Soft delete
        await self.website_repo.soft_delete(website_id)
        
        # Update resource allocation
        await self._update_website_count(website.company_id)
        
        await self.db.commit()
        
        return True
    
    async def get_company_websites(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> tuple[List[Website], int]:
        """Get all websites for a company"""
        if active_only:
            websites = await self.website_repo.get_active_by_company(
                company_id, skip, limit
            )
            total = await self.website_repo.get_count({
                "company_id": company_id,
                "is_active": True
            })
        else:
            websites = await self.website_repo.get_by_company(
                company_id, skip, limit
            )
            total = await self.website_repo.count_by_company(company_id)
        
        return websites, total
    
    async def search_websites(
        self,
        company_id: int,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Website]:
        """Search websites"""
        return await self.website_repo.search_websites(
            company_id, query, skip, limit
        )
    
    def _generate_embed_code(self) -> str:
        """Generate widget embed code"""
        widget_id = security_service.generate_api_key()[:16]
        return f'<script src="/widget.js" data-widget-id="{widget_id}"></script>'