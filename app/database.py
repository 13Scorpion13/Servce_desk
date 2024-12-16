from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from app.models import Base, User, Task, Message, Manager, TaskStatus

DATABASE_URL = "sqlite:///./service_desk.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("База данных и таблицы успешно созданы!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
