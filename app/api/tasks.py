from fastapi import APIRouter, Depends, HTTPException, Path, status
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
        item: TaskAdd,
        current_user_id: str = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    task_data = item.model_dump()
    task_data["user_id"] = int(current_user_id)
    new_task = Task(**task_data)
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return {"status": "success", "task_id": new_task.id}

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(session: AsyncSession = Depends(get_session),
                    user_id: str = Depends(get_current_user)):
    query = select(Task).filter_by(user_id = int(user_id))
    result = await session.execute(query)
    tasks = result.scalars().all()
    return tasks

@router.delete("/{task_id}")
async def delete_task(
        task_id: int,
        session: AsyncSession = Depends(get_session),
        current_user_id: str = Depends(get_current_user)):
    task = await session.get(Task, task_id)
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