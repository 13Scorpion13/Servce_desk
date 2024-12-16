import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Статусы обращения
class TaskStatus(enum.Enum):
    OPEN = "открыто"
    IN_PROGRESS = "в работе"
    CLOSED = "закрыто"

# Модель пользователя
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    tasks = relationship("Task", back_populates="user")

# Модель менеджера
class Manager(Base):
    __tablename__ = "managers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="manager")
    messages = relationship("Message", back_populates="operator")

# Модель обращения
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.OPEN)
    close_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tasks")
    manager = relationship("Manager", back_populates="tasks")
    messages = relationship("Message", back_populates="task")

    @property
    def status_display(self):
        return self.status.value

# Модель сообщения
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    sender = Column(String, nullable=False)
    content = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    operator_id = Column(Integer, ForeignKey("managers.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="messages")
    operator = relationship("Manager", back_populates="messages")
