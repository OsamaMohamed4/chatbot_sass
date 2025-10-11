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
    level_0 = ['system_admins', 'resource_plans']
    level_1 = ['client_companies']
    level_2 = ['resource_allocations', 'websites', 'company_users', 'billing_records']
    level_3 = ['ai_models', 'api_keys', 'user_website_accesses', 'usage_analytics']
    level_4 = ['chat_sessions']
    level_5 = ['chat_messages']
    return level_0 + level_1 + level_2 + level_3 + level_4 + level_5

def sort_tables_by_foreign_key_dependency(metadata):
    """Return a new MetaData object with tables sorted by dependency order"""
    table_order = get_table_order()
    sorted_metadata = MetaData()
    for table_name in table_order:
        if table_name in metadata.tables:
            table = metadata.tables[table_name]
            table.tometadata(sorted_metadata)
    # Add remaining tables
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
    context.configure(connection=connection, target_metadata=target_metadata)
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
