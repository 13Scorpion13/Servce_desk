from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models import TaskStatus

class UserCreate(BaseModel):
    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class TaskCreate(BaseModel):
    user_id: int
    manager_id: Optional[int] = None
    status: TaskStatus = TaskStatus.OPEN

class MessageCreate(BaseModel):
    task_id: int
    sender: str
    content: Optional[str] = None
    file_name: Optional[str] = None
    operator_id: int
    timestamp: datetime
