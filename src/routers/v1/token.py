from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import Token
from src.jwt_auth.auth import create_jwt_token, get_user, pwd_context,  get_current_user
from src.schemas import AuthToken
from src.models.sellers import Seller

token_router = APIRouter(tags=["token"], prefix="/token")

# Подключение к базе
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка на получения токена
@token_router.post("/", response_model=Token)
async def authenticate_user(auth_data: AuthToken, session: DBSession):
    user = await get_user(auth_data.e_mail, session)  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    is_password_correct = pwd_context.verify(auth_data.password, user.password)
    if not is_password_correct:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    jwt_token = create_jwt_token({"sub": user.e_mail})
    return {"access_token": jwt_token, "token_type": "bearer"}