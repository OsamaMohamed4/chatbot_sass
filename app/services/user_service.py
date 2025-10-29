from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from app.models.company_user import CompanyUser
from app.models.resource_allocation import ResourceAllocation
from app.exceptions import (
    ResourceNotFoundException,
    DuplicateResourceException,
    BusinessLogicException,
    ResourceLimitException,
    ForbiddenException
)
from app.core.security import security_service


class UserService:
    """Service for user business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.company_repo = CompanyRepository(db)
    
    async def _check_user_limit(self, company_id: int) -> None:
        """Check if company can create more users"""
        company = await self.company_repo.get_with_plan(company_id)
        if not company or not company.resource_plan:
            raise BusinessLogicException("Company has no resource plan")
        
        # Count current users
        result = await self.db.execute(
            select(CompanyUser).where(CompanyUser.company_id == company_id)
        )
        current_count = len(result.scalars().all())
        
        max_users = company.resource_plan.max_users
        if current_count >= max_users:
            raise ResourceLimitException("Users", max_users, current_count)
    
    async def _update_user_count(self, company_id: int) -> None:
        """Update user count in resource allocation"""
        result = await self.db.execute(
            select(ResourceAllocation).where(
                ResourceAllocation.company_id == company_id
            )
        )
        allocation = result.scalar_one_or_none()
        
        if allocation:
            result = await self.db.execute(
                select(CompanyUser).where(
                    CompanyUser.company_id == company_id,
                    CompanyUser.is_active == True
                )
            )
            allocation.current_users = len(result.scalars().all())
            await self.db.flush()
    
    async def create_user(
        self,
        user_data: dict,
        created_by_id: int
    ) -> CompanyUser:
        """Create a new user"""
        # Get creator
        creator = await self.user_repo.get_by_id(created_by_id)
        if not creator:
            raise ResourceNotFoundException("User", created_by_id)
        
        company_id = creator.company_id
        
        # Check user limit
        await self._check_user_limit(company_id)
        
        # Check for duplicates
        if await self.user_repo.exists_username(user_data['username']):
            raise DuplicateResourceException(
                "User", "username", user_data['username']
            )
        
        if await self.user_repo.exists_email(user_data['email']):
            raise DuplicateResourceException(
                "User", "email", user_data['email']
            )
        
        # Set company and creator
        user_data['company_id'] = company_id
        user_data['created_by_id'] = created_by_id
        user_data['is_master_user'] = False  # Only one master user
        
        # Hash password
        if 'password' in user_data:
            user_data['password_hash'] = security_service.get_password_hash(
                user_data.pop('password')
            )
        
        # Create user
        user = await self.user_repo.create(user_data)
        
        # Update allocation
        await self._update_user_count(company_id)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user(self, user_id: int) -> CompanyUser:
        """Get user by ID"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        return user
    
    async def update_user(
        self,
        user_id: int,
        user_data: dict,
        updated_by_id: int
    ) -> CompanyUser:
        """Update user"""
        user = await self.get_user(user_id)
        updater = await self.get_user(updated_by_id)
        
        # Check permissions
        if user.company_id != updater.company_id:
            raise ForbiddenException("Cannot update user from another company")
        
        if not updater.is_master_user and user_id != updated_by_id:
            raise ForbiddenException("Only master users can update other users")
        
        # Handle password change
        if 'password' in user_data:
            user_data['password_hash'] = security_service.get_password_hash(
                user_data.pop('password')
            )
            user_data['password_changed_at'] = datetime.utcnow()
        
        # Update
        updated_user = await self.user_repo.update(user_id, user_data)
        
        await self.db.commit()
        await self.db.refresh(updated_user)
        
        return updated_user
    
    async def delete_user(self, user_id: int, deleted_by_id: int) -> bool:
        """Soft delete user"""
        user = await self.get_user(user_id)
        deleter = await self.get_user(deleted_by_id)
        
        # Permissions
        if user.company_id != deleter.company_id:
            raise ForbiddenException("Cannot delete user from another company")
        
        if not deleter.is_master_user:
            raise ForbiddenException("Only master users can delete users")
        
        if user.is_master_user:
            raise BusinessLogicException("Cannot delete master user")
        
        # Soft delete
        await self.user_repo.soft_delete(user_id)
        await self._update_user_count(user.company_id)
        
        await self.db.commit()
        return True
    
    async def get_company_users(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[CompanyUser], int]:
        """Get all users for a company"""
        users = await self.user_repo.get_by_company(company_id, skip, limit)
        total = await self.user_repo.get_count({"company_id": company_id})
        return users, total
    
    async def get_users_by_role(
        self,
        company_id: int,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyUser]:
        """Get users by role"""
        return await self.user_repo.get_by_role(company_id, role, skip, limit)