"""
Main FastAPI application for the Calendar/Todo app.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from .database import engine, get_db, Base
from .models import Item, ItemType
from .schemas import TaskCreate, EventCreate, ItemUpdate, ItemResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Calendar & Todo API",
    description="A simple API for managing tasks and calendar events",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")


@app.get("/")
def root():
    """
    Root endpoint that returns API information.
    """
    return {
        "message": "Calendar & Todo API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Task endpoints
@app.post("/api/tasks", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task.

    Args:
        task: Task data including title, description, and optional due date
        db: Database session

    Returns:
        The created task with its assigned ID
    """
    db_item = Item(
        title=task.title,
        description=task.description,
        item_type=ItemType.TASK,
        due_date=task.due_date
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/api/tasks", response_model=List[ItemResponse])
def get_tasks(completed: bool = None, db: Session = Depends(get_db)):
    """
    Retrieve all tasks, optionally filtered by completion status.

    Args:
        completed: Optional filter - True for completed, False for incomplete, None for all
        db: Database session

    Returns:
        List of tasks matching the filter criteria
    """
    query = db.query(Item).filter(Item.item_type == ItemType.TASK)
    if completed is not None:
        query = query.filter(Item.completed == completed)
    return query.all()


@app.get("/api/tasks/{task_id}", response_model=ItemResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific task by ID.

    Args:
        task_id: The unique identifier of the task
        db: Database session

    Returns:
        The requested task

    Raises:
        HTTPException: 404 if task is not found
    """
    task = db.query(Item).filter(
        Item.id == task_id,
        Item.item_type == ItemType.TASK
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/api/tasks/{task_id}", response_model=ItemResponse)
def update_task(task_id: int, task_update: ItemUpdate, db: Session = Depends(get_db)):
    """
    Update an existing task.

    Args:
        task_id: The unique identifier of the task to update
        task_update: Fields to update (only provided fields will be updated)
        db: Database session

    Returns:
        The updated task

    Raises:
        HTTPException: 404 if task is not found
    """
    task = db.query(Item).filter(
        Item.id == task_id,
        Item.item_type == ItemType.TASK
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task.

    Args:
        task_id: The unique identifier of the task to delete
        db: Database session

    Raises:
        HTTPException: 404 if task is not found
    """
    task = db.query(Item).filter(
        Item.id == task_id,
        Item.item_type == ItemType.TASK
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()


# Event endpoints
@app.post("/api/events", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Create a new calendar event.

    Args:
        event: Event data including title, description, start time, and end time
        db: Database session

    Returns:
        The created event with its assigned ID

    Raises:
        HTTPException: 400 if end time is before start time
    """
    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=400,
            detail="End time must be after start time"
        )

    db_item = Item(
        title=event.title,
        description=event.description,
        item_type=ItemType.EVENT,
        start_time=event.start_time,
        end_time=event.end_time
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/api/events", response_model=List[ItemResponse])
def get_events(start_date: datetime = None, end_date: datetime = None, db: Session = Depends(get_db)):
    """
    Retrieve all calendar events, optionally filtered by date range.

    Args:
        start_date: Optional - only return events starting on or after this date
        end_date: Optional - only return events starting on or before this date
        db: Database session

    Returns:
        List of events matching the filter criteria
    """
    query = db.query(Item).filter(Item.item_type == ItemType.EVENT)
    if start_date:
        query = query.filter(Item.start_time >= start_date)
    if end_date:
        query = query.filter(Item.start_time <= end_date)
    return query.all()


@app.get("/api/events/{event_id}", response_model=ItemResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific event by ID.

    Args:
        event_id: The unique identifier of the event
        db: Database session

    Returns:
        The requested event

    Raises:
        HTTPException: 404 if event is not found
    """
    event = db.query(Item).filter(
        Item.id == event_id,
        Item.item_type == ItemType.EVENT
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.patch("/api/events/{event_id}", response_model=ItemResponse)
def update_event(event_id: int, event_update: ItemUpdate, db: Session = Depends(get_db)):
    """
    Update an existing event.

    Args:
        event_id: The unique identifier of the event to update
        event_update: Fields to update (only provided fields will be updated)
        db: Database session

    Returns:
        The updated event

    Raises:
        HTTPException: 404 if event is not found
        HTTPException: 400 if updated times are invalid
    """
    event = db.query(Item).filter(
        Item.id == event_id,
        Item.item_type == ItemType.EVENT
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = event_update.model_dump(exclude_unset=True)

    # Validate time constraints if both times are being updated
    start_time = update_data.get("start_time", event.start_time)
    end_time = update_data.get("end_time", event.end_time)
    if start_time and end_time and end_time <= start_time:
        raise HTTPException(
            status_code=400,
            detail="End time must be after start time"
        )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event


@app.delete("/api/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """
    Delete an event.

    Args:
        event_id: The unique identifier of the event to delete
        db: Database session

    Raises:
        HTTPException: 404 if event is not found
    """
    event = db.query(Item).filter(
        Item.id == event_id,
        Item.item_type == ItemType.EVENT
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
