from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations.database import get_async_session

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from sqlalchemy import select
from src.models.sellers import Seller


DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Класс для работы с паролями
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема для запроса аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")  # Схема для запроса аутентификации


SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"
EXPIRATION_TIME = timedelta(minutes=30)


# Создание токена
def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + EXPIRATION_TIME
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


# Верификация токена
def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None


# Проверка токена
async def get_current_user(token: str = Depends(oauth2_scheme), session=Depends(get_async_session)):
    decoded_data = verify_jwt_token(token)
    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await get_user(decoded_data["sub"], session)  # Используйте объект сессии session
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


# Функция возвращает продавца
async def get_user(e_mail: str, session: DBSession):
    seller = await session.execute(select(Seller).filter(Seller.e_mail == e_mail))
    seller = seller.scalars().first()
    return seller


