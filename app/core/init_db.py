import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.security import security_service
from app.models.system_admin import SystemAdmin
from app.models.resource_plan import ResourcePlan
from app.models.client_company import ClientCompany
from app.models.company_user import CompanyUser
from app.models.resource_allocation import ResourceAllocation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========================================
# 1. Create Initial Superuser
# ========================================
async def create_initial_superuser(db: AsyncSession) -> None:
    """Create the first superuser if it doesn't exist"""
    try:
        result = await db.execute(
            select(SystemAdmin).where(
                SystemAdmin.email == settings.FIRST_SUPERUSER_EMAIL
            )
        )
        existing_admin = result.scalar_one_or_none()
        
        if not existing_admin:
            admin = SystemAdmin(
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
            db.add(admin)
            await db.flush()
            logger.info(f"✅ Superuser created: {settings.FIRST_SUPERUSER_EMAIL}")
        else:
            logger.info(f"ℹ️  Superuser already exists: {settings.FIRST_SUPERUSER_EMAIL}")
    
    except Exception as e:
        logger.error(f"❌ Error creating superuser: {str(e)}")
        raise


# ========================================
# 2. Create Default Resource Plans
# ========================================
async def create_default_resource_plans(db: AsyncSession) -> None:
    """Create default resource plans"""
    plans_data = [
        {
            "plan_name": "Starter",
            "plan_type": "starter",
            "max_ai_models": 1,
            "max_users": 3,
            "max_websites": 1,
            "max_monthly_requests": 1000,
            "max_storage_gb": 1.0,
            "max_training_hours": 5,
            "monthly_cost": 29.99,
            "yearly_cost": 299.99,
            "overage_cost_per_request": 0.001,
            "overage_cost_per_gb": 0.10,
            "features": {
                "basic_analytics": True,
                "email_support": True,
                "custom_branding": False,
                "api_access": False,
                "priority_support": False,
                "advanced_analytics": False,
                "white_label": False
            },
            "is_active": True
        },
        {
            "plan_name": "Professional",
            "plan_type": "professional",
            "max_ai_models": 3,
            "max_users": 10,
            "max_websites": 3,
            "max_monthly_requests": 10000,
            "max_storage_gb": 10.0,
            "max_training_hours": 20,
            "monthly_cost": 99.99,
            "yearly_cost": 999.99,
            "overage_cost_per_request": 0.001,
            "overage_cost_per_gb": 0.10,
            "features": {
                "basic_analytics": True,
                "email_support": True,
                "custom_branding": True,
                "api_access": True,
                "priority_support": True,
                "advanced_analytics": True,
                "white_label": False
            },
            "is_active": True
        },
        {
            "plan_name": "Enterprise",
            "plan_type": "enterprise",
            "max_ai_models": 10,
            "max_users": 50,
            "max_websites": 10,
            "max_monthly_requests": 100000,
            "max_storage_gb": 100.0,
            "max_training_hours": 100,
            "monthly_cost": 499.99,
            "yearly_cost": 4999.99,
            "overage_cost_per_request": 0.001,
            "overage_cost_per_gb": 0.10,
            "features": {
                "basic_analytics": True,
                "email_support": True,
                "custom_branding": True,
                "api_access": True,
                "priority_support": True,
                "advanced_analytics": True,
                "white_label": True
            },
            "is_active": True
        }
    ]
    
    try:
        for plan_data in plans_data:
            result = await db.execute(
                select(ResourcePlan).where(
                    ResourcePlan.plan_name == plan_data["plan_name"]
                )
            )
            existing_plan = result.scalar_one_or_none()
            
            if not existing_plan:
                plan = ResourcePlan(**plan_data)
                db.add(plan)
                await db.flush()
                logger.info(f"✅ Resource plan created: {plan_data['plan_name']}")
            else:
                logger.info(f"ℹ️  Resource plan already exists: {plan_data['plan_name']}")
        
    except Exception as e:
        logger.error(f"❌ Error creating resource plans: {str(e)}")
        raise


# ========================================
# 3. Create Demo Company (Optional)
# ========================================
async def create_demo_company(db: AsyncSession) -> None:
    """Create a demo company with master user for testing"""
    try:
        # Check if demo company exists
        result = await db.execute(
            select(ClientCompany).where(
                ClientCompany.company_email == "demo@chatbot-saas.com"
            )
        )
        existing_company = result.scalar_one_or_none()
        
        if existing_company:
            logger.info("ℹ️  Demo company already exists")
            return
        
        # Get Starter plan
        result = await db.execute(
            select(ResourcePlan).where(ResourcePlan.plan_name == "Starter")
        )
        starter_plan = result.scalar_one_or_none()
        
        if not starter_plan:
            logger.warning("⚠️  Starter plan not found, skipping demo company creation")
            return
        
        # Get superadmin
        result = await db.execute(
            select(SystemAdmin).where(
                SystemAdmin.email == settings.FIRST_SUPERUSER_EMAIL
            )
        )
        admin = result.scalar_one_or_none()
        
        # Create demo company
        demo_company = ClientCompany(
            company_name="Demo Company",
            company_email="demo@chatbot-saas.com",
            contact_person="Demo User",
            phone="+1234567890",
            address="123 Demo Street, Demo City",
            industry="Technology",
            company_size="small",
            account_status="active",
            resource_plan_id=starter_plan.id,
            admin_id=admin.id if admin else None,
            is_active=True
        )
        db.add(demo_company)
        await db.flush()
        await db.refresh(demo_company)
        
        # Create master user for demo company
        master_user = CompanyUser(
            username="demo_master",
            email="demo@chatbot-saas.com",
            password_hash=security_service.get_password_hash("demo123"),
            first_name="Demo",
            last_name="Master",
            role="master",
            is_master_user=True,
            company_id=demo_company.id,
            is_active=True
        )
        db.add(master_user)
        await db.flush()
        
        # Create resource allocation
        now = datetime.utcnow()
        allocation = ResourceAllocation(
            company_id=demo_company.id,
            plan_id=starter_plan.id,
            current_ai_models=0,
            current_users=1,  # Master user
            current_websites=0,
            current_monthly_requests=0,
            current_storage_gb=0.0,
            billing_period_start=now,
            billing_period_end=now + timedelta(days=30),
            overage_requests=0,
            overage_storage_gb=0.0,
            is_active=True
        )
        db.add(allocation)
        await db.flush()
        
        logger.info("✅ Demo company created successfully")
        logger.info("   📧 Email: demo@chatbot-saas.com")
        logger.info("   🔑 Password: demo123")
        
    except Exception as e:
        logger.error(f"❌ Error creating demo company: {str(e)}")
        raise


# ========================================
# Main Initialization Function
# ========================================
async def init_db() -> None:
    """Initialize database with default data"""
    logger.info("🚀 Starting database initialization...")
    logger.info("=" * 60)
    
    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Create superuser
            logger.info("\n📝 Step 1: Creating system superuser...")
            await create_initial_superuser(db)
            
            # Step 2: Create resource plans
            logger.info("\n📝 Step 2: Creating resource plans...")
            await create_default_resource_plans(db)
            
            # Step 3: Create demo company (optional)
            logger.info("\n📝 Step 3: Creating demo company...")
            await create_demo_company(db)
            
            # Commit all changes
            await db.commit()
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ Database initialization completed successfully!")
            logger.info("=" * 60)
            logger.info("\n🔑 Default Credentials:")
            logger.info(f"   Admin: {settings.FIRST_SUPERUSER_EMAIL} / {settings.FIRST_SUPERUSER_PASSWORD}")
            logger.info("   Demo:  demo@chatbot-saas.com / demo123")
            logger.info("\n")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"\n❌ Database initialization failed: {str(e)}")
            logger.error("=" * 60)
            raise


# ========================================
# Entry Point
# ========================================
if __name__ == "__main__":
    asyncio.run(init_db())