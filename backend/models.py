"""
Database models for tasks and calendar events.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from datetime import datetime
import enum
from .database import Base


class ItemType(str, enum.Enum):
    """Enum for distinguishing between tasks and events."""
    TASK = "task"
    EVENT = "event"


class Item(Base):
    """
    Unified model for both tasks and calendar events.

    Attributes:
        id: Unique identifier for the item
        title: Title or name of the task/event
        description: Detailed description
        item_type: Whether this is a task or calendar event
        completed: For tasks - whether the task is complete
        due_date: For tasks - when the task is due
        start_time: For events - when the event starts
        end_time: For events - when the event ends
        created_at: When the item was created
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    item_type = Column(Enum(ItemType), nullable=False)
    completed = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
