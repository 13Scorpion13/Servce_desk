import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from app.models import User, Task, Manager, TaskStatus, Message
from app.database import get_db
from app.connection_bot import send_message, send_photo
from datetime import datetime
from typing import Optional


router = APIRouter()

templates = Jinja2Templates(directory="./app/templates")


# Просмотр обращения оператором
@router.get("/tasks", response_class=HTMLResponse)
def operator_view_tasks(request: Request, db: Session = Depends(get_db)):
    result = db.execute(select(Task).options(joinedload(Task.messages)))
    tasks = result.unique().scalars().all()

    managers_result = db.execute(select(Manager))
    managers = managers_result.scalars().all()

    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "managers": managers})


# Просмотр подробной информации об обращении
@router.get("/tasks/{task_id}", response_class=HTMLResponse)
def get_task_detail(request: Request, task_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Task).filter(Task.id == task_id).options(joinedload(Task.messages)))
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    
    return templates.TemplateResponse("task_detail.html", {"request": request, "task": task})


# Назначение менеджера на обращение
@router.post("/tasks/{task_id}/assign")
def assign_manager_to_task(
        task_id: int, 
        manager_id: int = Form(...),
        db: Session = Depends(get_db)):

    result = db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Обращение не найдено")

    task.manager_id = manager_id
    task.status = TaskStatus.IN_PROGRESS
    db.commit()

    return {"message": f"Обращение {task_id} теперь в работе и назначен менеджер {manager_id}."}


# Обновление статуса обращения
@router.post("/tasks/{task_id}/status")
def update_task_status(
        task_id: int, 
        status: TaskStatus = Form(...), 
        db: Session = Depends(get_db)):
    
    result = db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Обращение не найдено")

    task.status = status

    if status == TaskStatus.CLOSED:
        task.close_date = datetime.utcnow()

    db.commit()

    return {"message": f"Обращение {task_id} обновлен на статус {status}."}


# Ответ на обращение оператором
@router.post("/tasks/{task_id}/reply") 
async def reply_to_task(
    task_id: int, 
    content: str = Form(...), 
    operator_id: int = Form(...), 
    image: Optional[UploadFile] = Form(None),
    db: Session = Depends(get_db),):

    result = db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Обращение не найдено")

    file_name = None
    file_path = None

    if image and image.filename:
        file_name = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join("static", "img", file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        image_content = await image.read()
        if image_content:
            with open(file_path, "wb") as buffer:
                buffer.write(image_content)
        else:
            file_name = None

    db_message = Message(task_id=task_id, sender="manager", content=content, operator_id=operator_id, file_name=file_name)
    db.add(db_message)
    db.commit()

    user_result = db.execute(select(User).filter(User.id == task.user_id))
    user = user_result.scalar_one_or_none()

    try:
        if user:
            if content:
                await send_message(chat_id=user.telegram_id, text=content)

            if file_name:
                await send_photo(chat_id=user.telegram_id, photo=open(file_path, 'rb'))
    except:
        return {"message": "Сообщение записано, но не отправлено"}

    return {"message": "Ответ успешно отправлен."}
