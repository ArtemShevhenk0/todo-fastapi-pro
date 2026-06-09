import os

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.database.session import engine, Base
from app.api.v1.tasks import router as tasks_router
from app.api.v1.auth import router as auth_router
import app.models.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код запуска (создание таблиц)
    os.makedirs('static/uploads/tasks', exist_ok=True)
    yield

app = FastAPI(lifespan=lifespan, title="ToDo Pro API")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {"message": "Welcome to ToDo Pro API! Go to /docs for testing."}