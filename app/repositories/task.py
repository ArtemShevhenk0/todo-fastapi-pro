from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_session
from app.models.models import Task

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    async def create_task(self, task_data: dict) -> Task:
        new_task = Task(**task_data)
        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)
        return new_task
    async def get_active_tasks(self, user_id: int) -> list[Task]:
        query = select(Task).where(Task.user_id == user_id, Task.done == False)
        result = await self.session.execute(query)
        return result.scalars().all()

async def get_task_repository(session: AsyncSession = Depends(get_session)) -> TaskRepository:
    return TaskRepository(session)