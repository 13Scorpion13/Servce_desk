import uuid
import os
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import get_db, engine, init_db
from app.models import User, Task, Message, Manager, TaskStatus
from app.schemas import UserCreate, TaskCreate, MessageCreate
from app.operator_router import router as operator_router
from datetime import datetime
from typing import List, Optional


app = FastAPI()
app.mount("/static", StaticFiles(directory="./app/static/img"), name="static")


@app.on_event("startup")
def startup_event():
    while True:
        k = input("Создать новую базу данных Y/N")
        if k == "Y":
            init_db()
            return
        elif k == "N":
            return


# Основные маршруты
@app.get("/users", response_model=List[UserCreate])
def get_users(db: Session = Depends(get_db)):
    result = db.execute(select(User))
    return result.scalars().unique().all()


@app.post("/users", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(telegram_id=user.telegram_id, first_name=user.first_name, last_name=user.last_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/tasks", response_model=List[TaskCreate])
def get_tasks(db: Session = Depends(get_db)):
    result = db.execute(select(Task))
    return result.scalars().unique().all()


@app.post("/tasks", response_model=TaskCreate)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(user_id=task.user_id, manager_id=task.manager_id, status=task.status)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/messages", response_model=List[MessageCreate])
def get_messages_by_task(task_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Message).filter(Message.task_id == task_id))
    messages = result.scalars().unique().all()

    if not messages:
        raise HTTPException(status_code=404, detail=f"Сообщения для обращения с {task_id} не найдены")

    return messages


@app.post("/messages", response_model=MessageCreate)
def create_message(message: MessageCreate, file: UploadFile = File(None), db: Session = Depends(get_db)):
    if file:
        file_name = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join("static", "img", file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        db_message = Message(
            task_id=message.task_id,
            sender=message.sender,
            file_name=file_name
        )
    else:
        db_message = Message(
            task_id=message.task_id,
            sender=message.sender,
            content=message.content
        )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message


# Подключение маршрутов оператора
app.include_router(operator_router, prefix="/operator", tags=["operator"])