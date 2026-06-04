import os

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.api.tasks import router as tasks_router
from app.api.auth import router as auth_router
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код запуска (создание таблиц)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    os.makedirs('static/uploads/tasks', exist_ok=True)
    yield

app = FastAPI(lifespan=lifespan, title="ToDo Pro API")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {"message": "Welcome to ToDo Pro API! Go to /docs for testing."}