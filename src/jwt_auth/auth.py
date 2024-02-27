from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations.database import get_async_session

from fastapi import APIRouter, Depends, Response, status, HTTPException
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from sqlalchemy import select
from src.models.sellers import Seller

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Класс для работы с паролями
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Генерация JWT токена
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "secret_key", algorithm="HS256")
    return encoded_jwt


# Схема для запроса аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") # Схема для запроса аутентификации


# Проверка пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Получение пользователя по паролю
async def get_user(password: str):

    seller = await DBSession.execute(select(Seller).filter(Seller.password == password))
    seller = seller.scalars().first()
    return seller


async def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# Получение текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

