from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.sql import Select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get all records with pagination and optional filters"""
        query = select(self.model)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get total count of records with optional filters"""
        query = select(func.count()).select_from(self.model)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        id: int,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Update an existing record"""
        # Remove None values
        update_data = {k: v for k, v in obj_in.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(id)
        
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .returning(self.model)
        )
        
        result = await self.db.execute(stmt)
        await self.db.flush()
        
        return result.scalar_one_or_none()
    
    async def delete(self, id: int) -> bool:
        """Delete a record (hard delete)"""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        await self.db.flush()
        
        return result.rowcount > 0
    
    async def soft_delete(self, id: int) -> Optional[ModelType]:
        """Soft delete a record (set is_active to False)"""
        if not hasattr(self.model, 'is_active'):
            raise AttributeError(f"{self.model.__name__} does not support soft delete")
        
        return await self.update(id, {"is_active": False})
    
    async def get_by_field(
        self,
        field: str,
        value: Any
    ) -> Optional[ModelType]:
        """Get a single record by any field"""
        if not hasattr(self.model, field):
            raise AttributeError(f"{self.model.__name__} has no attribute {field}")
        
        result = await self.db.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalar_one_or_none()
    
    async def exists(self, id: int) -> bool:
        """Check if a record exists"""
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)
        )
        return result.scalar_one() > 0
    
    async def get_active(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get all active records (is_active=True)"""
        if not hasattr(self.model, 'is_active'):
            return await self.get_all(skip, limit)
        
        result = await self.db.execute(
            select(self.model)
            .where(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def bulk_create(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records at once"""
        db_objects = [self.model(**obj) for obj in objects]
        self.db.add_all(db_objects)
        await self.db.flush()
        
        for obj in db_objects:
            await self.db.refresh(obj)
        
        return db_objects