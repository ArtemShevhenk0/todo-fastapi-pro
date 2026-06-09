import math
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, status, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.repositories.task import TaskRepository, get_task_repository
from app.services.ai_logic import AIService, get_ai_service
from app.services.file_service import FileService, get_file_service
#Для задач
from app.services.security import get_current_user
from app.database.session import get_session
from app.models.models import Task
from app.schemas.schemas import TaskUpdate, TaskListResponse, TaskResponse, ChatRequest

# prefix="/tasks" значит, что нам больше не нужно писать /tasks в каждом роуте!
# tags=["Tasks"] — это для красоты в Swagger
router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model= TaskResponse)
async def create_task(
        title: str = Form(min_length=5, max_length=50),
        description: str = Form(None, max_length=500),
        priority: int = Form(default=1, ge = 1, le=5),
        file: UploadFile = File(None),
        task_repo: TaskRepository = Depends(get_task_repository),
        file_service: FileService = Depends(get_file_service),
        ai_service: AIService = Depends(get_ai_service),
        user_id: str = Depends(get_current_user)
):
    filename = None
    if file and file.filename:
        try:
            filename = await file_service.save_task_image(file)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))


    ai_data = await ai_service.analyze_task(title,description)
    task_data = {
        "title": title,
        "description": description,
        "priority": priority,
        "image_path": filename,
        "user_id": int(user_id),
        "ai_summary": ai_data['summary'],
        "ai_tags": ai_data['tags'],
        "ai_difficulty": ai_data['difficulty'],
    }
    new_task = await task_repo.create_task(task_data)
    return new_task



@router.get("/", response_model=TaskListResponse)
async def get_tasks(session: AsyncSession = Depends(get_session),
                    page: int = 1,
                    search: str = None,
                    user_id: str = Depends(get_current_user)):

    per_page = 5
    skip = (page - 1) * per_page

    query = select(Task).where(Task.user_id == int(user_id))
    if search:
        query = query.where(Task.title.ilike(f"{search}%"))

    total = await session.scalar(
        select(func.count()).select_from(query.subquery())
    )

    result = await session.execute(
        query.order_by(Task.id.desc()).limit(per_page).offset(skip)
    )
    tasks = result.scalars().all()

    total_pages = math.ceil(total / per_page)
    return {
        "items": tasks,
        "total": total,
        "page": page,
        "pages": total_pages,
    }

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

@router.post("/chat")
async def chat_manager(
        item: ChatRequest,
        user_id: str = Depends(get_current_user),
        task_repo: TaskRepository = Depends(get_task_repository),
        ai_service: AIService = Depends(get_ai_service)
        ):
    tasks = await task_repo.get_active_tasks(int(user_id))
    request = await ai_service.chat_with_manager(item.message, tasks)
    return request

