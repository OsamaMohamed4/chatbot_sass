import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.security import security_service
from app.models.system_admin import SystemAdmin
from app.models.client_company import ResourcePlan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_initial_superuser(db: AsyncSession) -> None:
    """Create the first superuser if it doesn't exist"""
    result = await db.execute(
        select(SystemAdmin).where(
            SystemAdmin.email == settings.FIRST_SUPERUSER_EMAIL
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = SystemAdmin(
            username="superadmin",
            email=settings.FIRST_SUPERUSER_EMAIL,
            password_hash=security_service.get_password_hash(
                settings.FIRST_SUPERUSER_PASSWORD
            ),
            first_name=settings.FIRST_SUPERUSER_FIRSTNAME,
            last_name=settings.FIRST_SUPERUSER_LASTNAME,
            is_superuser=True,
            is_active=True
        )
        db.add(user)
        await db.commit()
        logger.info(f"Superuser created: {settings.FIRST_SUPERUSER_EMAIL}")
    else:
        logger.info(f"Superuser already exists: {settings.FIRST_SUPERUSER_EMAIL}")

async def create_default_resource_plans(db: AsyncSession) -> None:
    """Create default resource plans"""
    plans = [
        {
            "plan_name": "Starter",
            "plan_type": "starter",
            "max_ai_models": 1,
            "max_users": 3,
            "max_websites": 1,
            "max_monthly_requests": 1000,
            "max_storage_gb": 1,
            "max_training_hours": 5,
            "monthly_cost": 29.99,
            "yearly_cost": 299.99,
            "features": {
                "basic_analytics": True,
                "email_support": True,
                "custom_branding": False,
                "api_access": False,
                "priority_support": False,
                "advanced_analytics": False,
                "white_label": False
            }
        },
        {
            "plan_name": "Professional",
            "plan_type": "professional",
            "max_ai_models": 3,
            "max_users": 10,
            "max_websites": 3,
            "max_monthly_requests": 10000,
            "max_storage_gb": 10,
            "max_training_hours": 20,
            "monthly_cost": 99.99,
            "yearly_cost": 999.99,
            "features": {
                "basic_analytics": True,
                "email_support": True,
                "custom_branding": True,
                "api_access": True,
                "priority_support": True,
                "advanced_analytics": True,
                "white_label": False
            }
        },
        {
            "plan_name": "Enterprise",
            "plan_type": "enterprise",
            "max_ai_models": 10,
            "max_users": 50,
            "max_websites": 10,
            "max_monthly_requests": 100000,
            "max_storage_gb": 100,
            "max_training_hours": 100,
            "monthly_cost": 499.99,
            "yearly_cost": 4999.99,
            "features": {
                "basic_analytics": True,
                "email_support": True,
                "custom_branding": True,
                "api_access": True,
                "priority_support": True,
                "advanced_analytics": True,
                "white_label": True
            }
        }
    ]
    
    for plan_data in plans:
        result = await db.execute(
            select(ResourcePlan).where(
                ResourcePlan.plan_name == plan_data["plan_name"]
            )
        )
        existing_plan = result.scalar_one_or_none()
        
        if not existing_plan:
            plan = ResourcePlan(**plan_data)
            db.add(plan)
            logger.info(f"Resource plan created: {plan_data['plan_name']}")
        else:
            logger.info(f"Resource plan already exists: {plan_data['plan_name']}")
    
    await db.commit()

async def init_db() -> None:
    """Initialize database with default data"""
    logger.info("Creating initial data...")
    
    async with AsyncSessionLocal() as db:
        await create_initial_superuser(db)
        await create_default_resource_plans(db)
    
    logger.info("Initial data created successfully")

if __name__ == "__main__":
    asyncio.run(init_db())