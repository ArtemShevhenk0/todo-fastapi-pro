from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.user import UserRepository, get_user_repository
from app.services.security import create_access_token
from app.database.session import get_session
from app.models.models import User
from app.schemas.schemas import UserResponse, UserAdd



from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register(
        item: UserAdd,
        user_repo: UserRepository = Depends(get_user_repository)):
    if await user_repo.get_user_by_username(item.user):
        raise HTTPException(status_code=400, detail='User already exists')

    hashed_password = pwd_context.hash(item.password)
    user_data = item.model_dump()
    user_data["password"] = hashed_password
    new_user = await user_repo.create_user(user_data)
    return new_user

@router.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_repo: UserRepository = Depends(get_user_repository)):
    user = await user_repo.get_user_by_username(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"} #Ответ по мировому стандарту
#{
  #"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNCIsImV4cCI6MTc3OTM5MDk3MH0.mx5KRXvbFFcO-V8ut0Ap06KcedRyz-k0Fu4rqw9yyJA",
  #"token_type": "bearer"
#}