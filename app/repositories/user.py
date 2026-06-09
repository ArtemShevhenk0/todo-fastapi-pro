from typing import Optional

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_session
from app.models.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    async def get_user_by_username(self, username: str) -> Optional[User]:
        query = select(User).filter_by(user=username)
        result = await self.session.execute(query)  # запрос к базе данных
        return result.scalars().first()

    async def create_user(self, user_data: dict) -> User:
        new_user = User(**user_data)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

async def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)





