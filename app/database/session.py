from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

#DB_URL = "postgresql+asyncpg://artem:prikol@localhost:5432/fastapi_todo"
engine = create_async_engine(settings.DATABASE_URL)
new_session = async_sessionmaker(
    bind=engine,           # Привязываем к нашему двигателю
    expire_on_commit=False # Чтобы объекты не "протухали" после сохранения
)

class Base(DeclarativeBase):
    pass

async def get_session():
    async with new_session() as session:
        yield session