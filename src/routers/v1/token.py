from typing import Annotated
from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import Token
from datetime import datetime, timedelta
from src.jwt_auth.auth import OAuth2PasswordRequestForm, authenticate_user, create_access_token


token_router = APIRouter(tags=["token"], prefix="/token")

# Подключение к базе
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


#response_model=Token
# Проверка токена и аутентификация пользователя
@token_router.post("/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # user = await authenticate_user(form_data.username, form_data.password)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    #
    # access_token_expires = timedelta(minutes=30)
    # access_token = create_access_token(
    #     data={"sub": user.username}, expires_delta=access_token_expires
    # )
    # return {"access_token": access_token, "token_type": "bearer"}
    return({"pas": form_data.username})