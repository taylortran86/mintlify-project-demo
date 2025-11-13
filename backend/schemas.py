"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .models import ItemType


class ItemBase(BaseModel):
    """Base schema with common fields for items."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = ""
    item_type: ItemType


class TaskCreate(ItemBase):
    """Schema for creating a new task."""
    item_type: ItemType = ItemType.TASK
    due_date: Optional[datetime] = None


class EventCreate(ItemBase):
    """Schema for creating a new calendar event."""
    item_type: ItemType = ItemType.EVENT
    start_time: datetime
    end_time: datetime


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ItemResponse(ItemBase):
    """Schema for item responses."""
    id: int
    completed: bool
    due_date: Optional[datetime]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
