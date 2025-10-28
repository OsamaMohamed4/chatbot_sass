import asyncio
from logging.config import fileConfig
from sqlalchemy import pool, MetaData
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import your models
from app.core.database import Base
from app.models import *  # Import all models
from app.core.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -----------------------------
# 🧩 1. Define sorting utilities
# -----------------------------
def get_table_order():
    """Define correct order for table creation based on foreign key dependencies"""
    # Level 0: No dependencies
    level_0 = ['system_admins', 'resource_plans']
    
    # Level 1: Depends on level 0
    level_1 = ['client_companies']
    
    # Level 2: Depends on level 0 and 1
    level_2 = ['resource_allocations', 'company_users', 'billing_records']
    
    # Level 3: Depends on level 2 (websites needs client_companies)
    level_3 = ['websites']
    
    # Level 4: Depends on level 3 (ai_models needs websites)
    level_4 = ['ai_models', 'api_keys', 'usage_analytics']
    
    # Level 5: Depends on level 4 (chat_sessions needs ai_models)
    level_5 = ['chat_sessions']
    
    # Level 6: Depends on level 2 and 3 (user_website_access needs company_users and websites)
    level_6 = ['user_website_access']
    
    # Level 7: Depends on level 5
    level_7 = ['chat_messages']
    
    return level_0 + level_1 + level_2 + level_3 + level_4 + level_5 + level_6 + level_7

def sort_tables_by_foreign_key_dependency(metadata):
    """Return a new MetaData object with tables sorted by dependency order"""
    table_order = get_table_order()
    sorted_metadata = MetaData()
    
    # Add tables in the correct order
    for table_name in table_order:
        if table_name in metadata.tables:
            table = metadata.tables[table_name]
            table.tometadata(sorted_metadata)
    
    # Add any remaining tables not in our order
    for table_name, table in metadata.tables.items():
        if table_name not in table_order:
            table.tometadata(sorted_metadata)
    
    return sorted_metadata

# ✅ Apply sorted metadata
target_metadata = sort_tables_by_foreign_key_dependency(Base.metadata)

# -----------------------------
# 🧩 2. Database connection URL
# -----------------------------
def get_url():
    """Get database URL from environment or config"""
    return os.getenv(
        "DATABASE_URL",
        config.get_main_option("sqlalchemy.url", settings.DATABASE_URL)
    )

# -----------------------------
# 🧩 3. Migration Runners
# -----------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Run actual migrations in connected mode"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

# -----------------------------
# 🧩 4. Entry Point
# -----------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()