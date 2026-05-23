from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.auth_utils import create_access_token
from app.database import get_session
from app.models import User
from app.schemas import UserResponse, UserAdd



from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register(
        item: UserAdd,
        session: AsyncSession = Depends(get_session)):
    hashed_password = pwd_context.hash(item.password)
    user_data = item.model_dump()
    user_data["password"] = hashed_password
    new_user = User(**user_data)
    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except Exception as e:
            await session.rollback()
            # Тут мы позже добавим проверку "Логин уже занят" (код 400)
            raise HTTPException(status_code=500, detail="Database error")

@router.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)):
    query = select(User).filter_by(user = form_data.username)
    result = await session.execute(query) # запрос к базе данных
    user = result.scalars().first() # Достаем самого юзера ( первого)
    if not user or not pwd_context.verify(form_data.password, user.password): # проверка есть ли усер и правильный ли пароль
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"} #Ответ по мировому стандарту
#{
  #"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNCIsImV4cCI6MTc3OTM5MDk3MH0.mx5KRXvbFFcO-V8ut0Ap06KcedRyz-k0Fu4rqw9yyJA",
  #"token_type": "bearer"
#}