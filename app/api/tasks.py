import os
import uuid
from pickletools import TAKEN_FROM_ARGUMENT1

from fastapi import APIRouter, Depends, HTTPException, Path, status, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


#Для задач
from app.auth_utils import get_current_user
from app.database import get_session
from app.models import Task
from app.schemas import TaskAdd, TaskResponse, TaskUpdate

# prefix="/tasks" значит, что нам больше не нужно писать /tasks в каждом роуте!
# tags=["Tasks"] — это для красоты в Swagger
router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/")
async def create_task(
        title: str = Form(min_length=5, max_length=50),
        description: str = Form(None, max_length=500),
        priority: int = Form(default=1, ge = 1, le=5),
        file: UploadFile = File(None),
        session: AsyncSession = Depends(get_session),
        user_id: str = Depends(get_current_user)
):
    filename = None

    if file and file.filename != '':
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Format .{ext} not allowed")

        filename = f"task_{uuid.uuid4().hex[:8]}.{ext}"
        save_path = os.path.join('static/uploads/tasks', filename)

        content = await file.read()
        with open(save_path, 'wb') as f:
            f.write(content)
    try:
        new_task = Task(
            title = title,
            description = description,
            priority = priority,
            image_path=filename,
            user_id = int(user_id)

        )
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
    except Exception as e:
        await session.rollback()
        print(f"DATABASE ERROR: {e}")
        raise HTTPException(status_code=500, detail="Database save error")


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(session: AsyncSession = Depends(get_session),
                    user_id: str = Depends(get_current_user)):
    query = select(Task).filter_by(user_id = int(user_id))
    result = await session.execute(query)
    tasks = result.scalars().all()
    return tasks

@router.delete("/{id}")
async def delete_task(
        id: int,
        session: AsyncSession = Depends(get_session),
        current_user_id: str = Depends(get_current_user)):
    task = await session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Not Found")
    if task.user_id != int(current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await session.delete(task)
    await session.commit()
    return {"status": "success", "task_deleted": task.id}

@router.patch("/{task_id}")
async def update_task(
        task_id: int,
        item: TaskUpdate,
        current_user_id: str = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    task = await session.get(Task,task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != int(current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    update_data = item.model_dump(exclude_unset = True)
    for key, value in update_data.items():
        setattr(task,key,value)
    await session.commit()
    return {"status": "success", "updated_fields": list(update_data.keys())}

@router.get("/priority/{level}")
async def get_tasks_priority(
        level: int = Path(ge=1, le=5),
        session: AsyncSession = Depends(get_session)):
    query = select(Task).filter_by(priority = level)
    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks