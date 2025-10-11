from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal

# Base Schema
class WebsiteBase(BaseModel):
    website_name: str = Field(..., min_length=2, max_length=100)
    website_url: HttpUrl
    description: Optional[str] = None
    widget_position: Literal["bottom-right", "bottom-left", "top-right", "top-left"] = "bottom-right"
    widget_color: str = Field(default="#0084ff", pattern=r'^#[0-9A-Fa-f]{6}$')
    welcome_message: Optional[str] = None
    placeholder_text: Optional[str] = Field(default="Type your message...")

# Create Schema
class WebsiteCreate(WebsiteBase):
    company_id: int
    widget_size: Literal["small", "medium", "large"] = "medium"
    show_powered_by: bool = True
    enable_sound: bool = True
    enable_file_upload: bool = False
    allowed_file_types: Optional[list[str]] = []
    business_hours_enabled: bool = False
    business_hours: Optional[dict] = {}
    offline_message: Optional[str] = None

# Update Schema
class WebsiteUpdate(BaseModel):
    website_name: Optional[str] = Field(None, min_length=2, max_length=100)
    website_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    widget_position: Optional[Literal["bottom-right", "bottom-left", "top-right", "top-left"]] = None
    widget_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    widget_icon: Optional[str] = None
    welcome_message: Optional[str] = None
    placeholder_text: Optional[str] = None
    widget_size: Optional[Literal["small", "medium", "large"]] = None
    show_powered_by: Optional[bool] = None
    custom_css: Optional[str] = None
    auto_open_delay: Optional[int] = None
    enable_sound: Optional[bool] = None
    enable_file_upload: Optional[bool] = None
    allowed_file_types: Optional[list[str]] = None
    business_hours_enabled: Optional[bool] = None
    business_hours: Optional[dict] = None
    offline_message: Optional[str] = None
    allowed_domains: Optional[list[str]] = None
    widget_status: Optional[Literal["active", "paused", "disabled"]] = None
    is_active: Optional[bool] = None

# Response Schema
class WebsiteResponse(WebsiteBase):
    id: int
    company_id: int
    domain_verified: bool
    verified_at: Optional[datetime]
    widget_size: str
    show_powered_by: bool
    widget_status: str
    widget_api_key: str
    total_visitors: int
    total_conversations: int
    conversion_rate: Optional[Decimal]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# List Response
class WebsiteListResponse(BaseModel):
    id: int
    website_name: str
    website_url: str
    domain_verified: bool
    widget_status: str
    total_conversations: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Detail Response
class WebsiteDetailResponse(WebsiteResponse):
    ai_models_count: int = 0
    conversations_count: int = 0
    messages_count: int = 0

# Verification Schema
class WebsiteVerificationRequest(BaseModel):
    website_id: int

class WebsiteVerificationResponse(BaseModel):
    verification_token: str
    verification_methods: list[str] = ["meta_tag", "html_file", "dns_record"]
    instructions: dict

# Widget Configuration Schema
class WidgetConfigResponse(BaseModel):
    widget_api_key: str
    widget_position: str
    widget_color: str
    widget_size: str
    widget_icon: Optional[str]
    welcome_message: Optional[str]
    placeholder_text: str
    show_powered_by: bool
    custom_css: Optional[str]
    auto_open_delay: Optional[int]
    enable_sound: bool
    business_hours_enabled: bool
    business_hours: dict
    offline_message: Optional[str]

# Analytics Schemas
class WebsiteAnalyticsResponse(BaseModel):
    id: int
    website_id: int
    date: datetime
    period_type: str
    unique_visitors: int
    returning_visitors: int
    conversations_started: int
    conversations_completed: int
    messages_sent: int
    messages_received: int
    average_response_time: Optional[Decimal]
    average_conversation_duration: Optional[int]
    satisfaction_score: Optional[Decimal]
    engagement_rate: Optional[Decimal]
    
    class Config:
        from_attributes = True

class WebsiteAnalyticsSummary(BaseModel):
    total_visitors: int
    total_conversations: int
    total_messages: int
    average_response_time: Decimal
    satisfaction_score: Decimal
    engagement_rate: Decimal
    conversion_rate: Decimal
    top_countries: list[dict]
    device_breakdown: dict
    hourly_distribution: list[dict]