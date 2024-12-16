from sqladmin import Admin, ModelView, expose
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Task, Message, Manager, TaskStatus

class UserAdmin(ModelView, model=User):
    column_list = [User.telegram_id, User.first_name, User.last_name]


class TaskAdmin(ModelView, model=Task):
    column_list = [Task.id, Task.user_id, Task.manager_id, Task.status, Task.close_date]


class MessageAdmin(ModelView, model=Message):
    column_list = [Message.task_id, Message.sender, Message.content, Message.file_name, Message.timestamp]


class ManagerAdmin(ModelView, model=Manager):
    column_list = [Manager.id, Manager.first_name, Manager.last_name]


def setup_admin(app, engine):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(MessageAdmin)
    admin.add_view(ManagerAdmin)