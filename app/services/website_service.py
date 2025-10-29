from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from urllib.parse import urlparse

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
        company = await self.company_repo.get_with_plan(company_id)
        if not company:
            raise ResourceNotFoundException("Company", company_id)
        
        if not company.resource_plan:
            raise BusinessLogicException("Company has no resource plan assigned")
        
        current_count = await self.website_repo.count_by_company(company_id)
        max_websites = company.resource_plan.max_websites
        
        if current_count >= max_websites:
            raise ResourceLimitException("Websites", max_websites, current_count)
    
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
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc or parsed.path
    
    def _generate_api_key(self) -> str:
        """Generate unique API key for widget"""
        return f"wgt_{security_service.generate_api_key()[:32]}"
    
    def _generate_embed_code(self, api_key: str, company_id: int) -> str:
        """Generate widget embed code"""
        return f'''<script>
  (function(w,d,s,o,f,js,fjs){{
    w['ChatbotWidget']=o;w[o]=w[o]||function(){{(w[o].q=w[o].q||[]).push(arguments)}};
    js=d.createElement(s),fjs=d.getElementsByTagName(s)[0];
    js.id=o;js.src=f;js.async=1;fjs.parentNode.insertBefore(js,fjs);
  }}(window,document,'script','chatbot','/widget.js'));
  chatbot('init', {{
    apiKey: '{api_key}',
    companyId: {company_id}
  }});
</script>'''
    
    async def create_website(
        self,
        website_data: dict,
        company_id: int
    ) -> Website:
        """Create a new website"""
        # Check website limit
        await self._check_website_limit(company_id)
        
        # Extract domain from URL
        domain = self._extract_domain(str(website_data.get('website_url', '')))
        
        # Check for duplicate domain
        if domain:
            existing_domain = await self.website_repo.get_by_domain(domain)
            if existing_domain:
                raise DuplicateResourceException("Website", "domain", domain)
        
        # Prepare data for database - convert URL to string
        db_data = {
            "website_name": website_data.get("website_name"),
            "website_url": str(website_data.get("website_url")),
            "domain": domain,
            "description": website_data.get("description"),
            "company_id": company_id,
            
            # Widget Configuration
            "widget_color": website_data.get("widget_color", "#0084ff"),
            "widget_size": website_data.get("widget_size", "medium"),
            "widget_position": "bottom-right",  # Default value
            "placeholder_text": website_data.get("placeholder_text", "Type your message..."),
            "show_powered_by": website_data.get("show_powered_by", True),
            "enable_sound": website_data.get("enable_sound", True),
            "enable_file_upload": website_data.get("enable_file_upload", False),
            "allowed_file_types": website_data.get("allowed_file_types", []),
            "widget_status": "active",
            
            # Business Hours
            "business_hours_enabled": website_data.get("business_hours_enabled", False),
            "business_hours": website_data.get("business_hours", {}),
            "welcome_message": website_data.get("welcome_message"),
            "offline_message": website_data.get("offline_message"),
            
            # Verification & Security
            "domain_verified": False,
            "widget_api_key": self._generate_api_key(),
            "allowed_domains": [],
            
            # Analytics
            "total_visitors": 0,
            "total_conversations": 0,
            
            # Status
            "is_active": True
        }
        
        # Generate embed code and API endpoint
        db_data["embed_code"] = self._generate_embed_code(
            db_data["widget_api_key"],
            company_id
        )
        db_data["api_endpoint"] = f"/api/v1/chat/widget/{db_data['widget_api_key']}"
        
        # Create website
        website = await self.website_repo.create(db_data)
        
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
        
        # Convert URL to string if present
        if "website_url" in website_data:
            website_data["website_url"] = str(website_data["website_url"])
            # Update domain
            website_data["domain"] = self._extract_domain(website_data["website_url"])
        
        # Check for duplicate domain if being updated
        if website_data.get('domain') and website_data['domain'] != website.domain:
            existing = await self.website_repo.get_by_domain(website_data['domain'])
            if existing and existing.id != website_id:
                raise DuplicateResourceException("Website", "domain", website_data['domain'])
        
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