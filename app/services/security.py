from fastapi.params import Depends
from jose import jwt, JWTError #шифрование
from fastapi import HTTPException
from datetime import datetime,timedelta, timezone #срок годности
from app.core.config import settings #настройки

from fastapi.security import OAuth2PasswordBearer
# Это говорит FastAPI: "Ищи токен в поле Authorization"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data:dict):
    to_encode = data.copy() # 1. Делаем копию входящего словаря data
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)# 2. Вычисляем время смерти токена (текущее время + 30 минут)
    to_encode.update({"exp": expire})# 3. Добавляем это время в наш словарь под ключом "exp"
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)# 4. Кодируем всё это через jwt.encode и возвращаем результат
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="id is wrong")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")