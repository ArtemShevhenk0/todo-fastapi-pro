from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class TaskAdd(BaseModel):
    title: str = Field(min_length=5, max_length=50)
    description: str | None = Field(None, max_length=500)
    priority: int = Field(default=1, ge = 1, le=5)
    done: bool = Field(default=False)
    image_path: str | None = Field(None)


class TaskResponse(TaskAdd):
    id: int
    user_id: int
    class Config():
        form_attributes = True

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None,min_length=5, max_length=50)
    description: Optional[str] = Field(None,max_length=500)
    priority: Optional[int] = Field(None, ge=1, le=5)
    done: Optional[bool] = None

class UserBase(BaseModel):
    user: str = Field(min_length=5, max_length=50)
    email: EmailStr

class UserAdd(UserBase):
    password: str = Field(min_length=5, max_length=70)

class UserResponse(UserBase):
    id: int
    class Config():
        form_attributes = True

class UserLogin(BaseModel):
    user: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=5, max_length=70)

