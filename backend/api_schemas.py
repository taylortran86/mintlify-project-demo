"""
Pydantic schemas for public API endpoints.
These represent the customer-facing API that would be documented.
"""
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ApiKeyScope(str, Enum):
    """Available scopes for API keys."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class WebhookEvent(str, Enum):
    """Events that can trigger webhooks."""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    EVENT_CREATED = "event.created"
    EVENT_UPDATED = "event.updated"
    EVENT_DELETED = "event.deleted"


# API Key Schemas
class ApiKeyCreate(BaseModel):
    """Schema for creating a new API key."""
    name: str = Field(..., min_length=1, max_length=100, description="Friendly name for the API key")
    scopes: List[ApiKeyScope] = Field(..., description="List of permission scopes for this key")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date for the key")


class ApiKeyResponse(BaseModel):
    """Schema for API key responses."""
    id: str = Field(..., description="Unique identifier for the API key")
    name: str = Field(..., description="Friendly name for the API key")
    key: Optional[str] = Field(None, description="The actual API key (only returned on creation)")
    key_prefix: str = Field(..., description="First 8 characters of the key for identification")
    scopes: List[ApiKeyScope] = Field(..., description="Permission scopes for this key")
    created_at: datetime = Field(..., description="When the key was created")
    expires_at: Optional[datetime] = Field(None, description="When the key expires")
    last_used_at: Optional[datetime] = Field(None, description="Last time the key was used")
    is_active: bool = Field(..., description="Whether the key is currently active")

    class Config:
        from_attributes = True


class ApiKeyListResponse(BaseModel):
    """Schema for listing API keys."""
    keys: List[ApiKeyResponse] = Field(..., description="List of API keys")
    total: int = Field(..., description="Total number of keys")


class ApiKeyUpdate(BaseModel):
    """Schema for updating an API key."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="New friendly name for the API key")


# Webhook Schemas
class WebhookCreate(BaseModel):
    """Schema for creating a new webhook."""
    url: HttpUrl = Field(..., description="The URL to send webhook payloads to")
    events: List[WebhookEvent] = Field(..., description="List of events that trigger this webhook")
    description: Optional[str] = Field(None, max_length=500, description="Optional description of the webhook")
    is_active: bool = Field(True, description="Whether the webhook is active")


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    url: Optional[HttpUrl] = Field(None, description="The URL to send webhook payloads to")
    events: Optional[List[WebhookEvent]] = Field(None, description="List of events that trigger this webhook")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    is_active: Optional[bool] = Field(None, description="Whether the webhook is active")


class WebhookResponse(BaseModel):
    """Schema for webhook responses."""
    id: str = Field(..., description="Unique identifier for the webhook")
    url: str = Field(..., description="The URL webhook payloads are sent to")
    events: List[WebhookEvent] = Field(..., description="Events that trigger this webhook")
    description: Optional[str] = Field(None, description="Description of the webhook")
    is_active: bool = Field(..., description="Whether the webhook is active")
    created_at: datetime = Field(..., description="When the webhook was created")
    last_triggered_at: Optional[datetime] = Field(None, description="Last time the webhook was triggered")

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    """Schema for listing webhooks."""
    webhooks: List[WebhookResponse] = Field(..., description="List of webhooks")
    total: int = Field(..., description="Total number of webhooks")


# Analytics Schemas
class UsageStats(BaseModel):
    """Schema for usage statistics."""
    period: str = Field(..., description="Time period for these stats (e.g., 'last_30_days')")
    tasks_created: int = Field(..., description="Number of tasks created")
    tasks_completed: int = Field(..., description="Number of tasks completed")
    events_created: int = Field(..., description="Number of events created")
    api_calls: int = Field(..., description="Total number of API calls made")
    active_tasks: int = Field(..., description="Current number of active tasks")
    upcoming_events: int = Field(..., description="Number of upcoming events")


class AnalyticsResponse(BaseModel):
    """Schema for analytics data."""
    account_id: str = Field(..., description="Account identifier")
    generated_at: datetime = Field(..., description="When this report was generated")
    usage: UsageStats = Field(..., description="Usage statistics")
    top_categories: List[Dict[str, Any]] = Field(default_factory=list, description="Most used categories/tags")


# Account/User Schemas
class AccountInfo(BaseModel):
    """Schema for account information."""
    account_id: str = Field(..., description="Unique account identifier")
    email: str = Field(..., description="Account email address")
    plan: str = Field(..., description="Current subscription plan")
    created_at: datetime = Field(..., description="When the account was created")
    api_quota: int = Field(..., description="API call quota per month")
    api_usage: int = Field(..., description="API calls used this month")


# Generic Response Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Schema for generic success responses."""
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Success message")
