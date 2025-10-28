"""initial commit

Revision ID: REPLACE_WITH_YOUR_REVISION_ID
Revises: 
Create Date: REPLACE_WITH_DATE

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'REPLACE_WITH_YOUR_REVISION_ID'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================
    # LEVEL 0: Tables with no dependencies
    # ============================================
    
    # Create system_admins table
    op.create_table('system_admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=True),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=True),
        sa.Column('two_factor_secret', sa.String(length=32), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_admins_id'), 'system_admins', ['id'], unique=False)
    op.create_index(op.f('ix_system_admins_username'), 'system_admins', ['username'], unique=True)
    op.create_index(op.f('ix_system_admins_email'), 'system_admins', ['email'], unique=True)
    
    # Create resource_plans table
    op.create_table('resource_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_name', sa.String(length=50), nullable=False),
        sa.Column('plan_type', sa.String(length=20), nullable=False),
        sa.Column('max_ai_models', sa.Integer(), nullable=False),
        sa.Column('max_users', sa.Integer(), nullable=False),
        sa.Column('max_websites', sa.Integer(), nullable=False),
        sa.Column('max_monthly_requests', sa.Integer(), nullable=False),
        sa.Column('max_storage_gb', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('max_training_hours', sa.Integer(), nullable=True),
        sa.Column('monthly_cost', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('yearly_cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('overage_cost_per_request', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('overage_cost_per_gb', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plan_name')
    )
    op.create_index(op.f('ix_resource_plans_id'), 'resource_plans', ['id'], unique=False)
    
    # ============================================
    # LEVEL 1: Tables depending on Level 0
    # ============================================
    
    # Create client_companies table
    op.create_table('client_companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=100), nullable=False),
        sa.Column('company_email', sa.String(length=100), nullable=False),
        sa.Column('contact_person', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('industry', sa.String(length=50), nullable=True),
        sa.Column('company_size', sa.String(length=20), nullable=True),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('account_status', sa.String(length=20), nullable=True),
        sa.Column('suspension_reason', sa.String(length=255), nullable=True),
        sa.Column('admin_id', sa.Integer(), nullable=True),
        sa.Column('resource_plan_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['system_admins.id'], ),
        sa.ForeignKeyConstraint(['resource_plan_id'], ['resource_plans.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_email'),
        sa.UniqueConstraint('company_name')
    )
    op.create_index(op.f('ix_client_companies_id'), 'client_companies', ['id'], unique=False)
    
    # ============================================
    # LEVEL 2: Tables depending on Level 1
    # ============================================
    
    # Create resource_allocations table
    op.create_table('resource_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('current_ai_models', sa.Integer(), nullable=True),
        sa.Column('current_users', sa.Integer(), nullable=True),
        sa.Column('current_websites', sa.Integer(), nullable=True),
        sa.Column('current_monthly_requests', sa.Integer(), nullable=True),
        sa.Column('current_storage_gb', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('billing_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('billing_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('overage_requests', sa.Integer(), nullable=True),
        sa.Column('overage_storage_gb', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['client_companies.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['resource_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resource_allocations_id'), 'resource_allocations', ['id'], unique=False)
    
    # Create company_users table
    op.create_table('company_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_master_user', sa.Boolean(), nullable=True),
        sa.Column('custom_permissions', sa.JSON(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=True),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['client_companies.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['company_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_company_users_id'), 'company_users', ['id'], unique=False)
    op.create_index(op.f('ix_company_users_username'), 'company_users', ['username'], unique=True)
    op.create_index(op.f('ix_company_users_email'), 'company_users', ['email'], unique=True)
    
    # Create billing_records table
    op.create_table('billing_records',
        sa.Column('billing_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('billing_period', sa.String(length=50), nullable=False),
        sa.Column('billing_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('usage_details', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['client_companies.id'], ),
        sa.PrimaryKeyConstraint('billing_id')
    )
    op.create_index(op.f('ix_billing_records_billing_date'), 'billing_records', ['billing_date'], unique=False)
    
    # ============================================
    # LEVEL 3: websites table
    # ============================================
    
    op.create_table('websites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('website_name', sa.String(length=100), nullable=False),
        sa.Column('website_url', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=100), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('widget_config', sa.JSON(), nullable=True),
        sa.Column('business_hours', sa.JSON(), nullable=True),
        sa.Column('welcome_message', sa.String(length=500), nullable=True),
        sa.Column('offline_message', sa.String(length=500), nullable=True),
        sa.Column('embed_code', sa.String(length=1000), nullable=True),
        sa.Column('api_endpoint', sa.String(length=255), nullable=True),
        sa.Column('webhook_url', sa.String(length=255), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('primary_ai_model_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['client_companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_websites_id'), 'websites', ['id'], unique=False)
    op.create_index(op.f('ix_websites_domain'), 'websites', ['domain'], unique=False)
    
    # ============================================
    # LEVEL 4: Tables depending on websites
    # ============================================
    
    # Create ai_models table
    op.create_table('ai_models',
        sa.Column('model_id', sa.Integer(), nullable=False),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('model_type', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('model_config', sa.JSON(), nullable=True),
        sa.Column('training_data_config', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('last_trained_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ),
        sa.PrimaryKeyConstraint('model_id')
    )
    op.create_index(op.f('ix_ai_models_model_id'), 'ai_models', ['model_id'], unique=False)
    op.create_index(op.f('ix_ai_models_model_name'), 'ai_models', ['model_name'], unique=False)
    
    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('key_id', sa.Integer(), nullable=False),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.Column('key_name', sa.String(length=255), nullable=False),
        sa.Column('api_key_hash', sa.String(length=255), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ),
        sa.PrimaryKeyConstraint('key_id')
    )
    op.create_index(op.f('ix_api_keys_api_key_hash'), 'api_keys', ['api_key_hash'], unique=True)
    
    # Create usage_analytics table
    op.create_table('usage_analytics',
        sa.Column('analytics_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('website_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('usage_date', sa.Date(), nullable=False),
        sa.Column('total_requests', sa.Integer(), nullable=False),
        sa.Column('total_tokens_used', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total_sessions', sa.Integer(), nullable=False),
        sa.Column('avg_response_time_ms', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['client_companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['company_users.id'], ),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ),
        sa.PrimaryKeyConstraint('analytics_id')
    )
    op.create_index(op.f('ix_usage_analytics_usage_date'), 'usage_analytics', ['usage_date'], unique=False)
    
    # ============================================
    # LEVEL 5: chat_sessions table
    # ============================================
    
    op.create_table('chat_sessions',
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=False),
        sa.Column('session_name', sa.String(length=255), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('session_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.model_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['company_users.id'], ),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ),
        sa.PrimaryKeyConstraint('session_id')
    )
    
    # ============================================
    # LEVEL 6: user_website_access table
    # ============================================
    
    op.create_table('user_website_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('website_id', sa.Integer(), nullable=True),
        sa.Column('permission_level', sa.String(length=20), nullable=False),
        sa.Column('custom_permissions', sa.JSON(), nullable=True),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('granted_by_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['granted_by_id'], ['company_users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['company_users.id'], ),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_website_access_id'), 'user_website_access', ['id'], unique=False)
    
    # ============================================
    # LEVEL 7: chat_messages table
    # ============================================
    
    op.create_table('chat_messages',
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=False),
        sa.Column('message_content', sa.Text(), nullable=False),
        sa.Column('message_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('tokens_used', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('is_user_message', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('message_id')
    )
    
    # Add foreign key for websites.primary_ai_model_id (circular reference)
    op.create_foreign_key(
        'fk_websites_primary_ai_model',
        'websites',
        'ai_models',
        ['primary_ai_model_id'],
        ['model_id']
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('chat_messages')
    op.drop_table('user_website_access')
    op.drop_table('chat_sessions')
    op.drop_table('usage_analytics')
    op.drop_table('api_keys')
    op.drop_table('ai_models')
    op.drop_table('websites')
    op.drop_table('billing_records')
    op.drop_table('company_users')
    op.drop_table('resource_allocations')
    op.drop_table('client_companies')
    op.drop_table('resource_plans')
    op.drop_table('system_admins')
