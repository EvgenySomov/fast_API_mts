import pytest
from fastapi import status
from src.jwt_auth.auth import verify_jwt_token


# Тест на получение токена
@pytest.mark.asyncio
async def test_create_token(async_client):

    # Создадим пользователя по старинке
    data = {"first_name": "Evgeny", "last_name": "Somov", "e_mail": "somov@mail.ru", "password": "password"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    # Отправим запрос
    response = await async_client.post("/api/v1/token/", json={"e_mail": "somov@mail.ru", "password": "password"})

    assert response.status_code == status.HTTP_200_OK

    token = response.json()["access_token"]
    decode_email = verify_jwt_token(token)

    assert decode_email['sub'] == "somov@mail.ru"


# Тест на доступ к продавцу без токена
@pytest.mark.asyncio
async def test_access_single_seller(async_client):
    response = await async_client.get("/api/v1/sellers/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Тест на создание книги без токена
@pytest.mark.asyncio
async def test_access_create_book(async_client):
    response = await async_client.post("/api/v1/books/", json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Тест на изменение книги без токена
@pytest.mark.asyncio
async def test_access_update_book(async_client):
    response = await async_client.put("/api/v1/books/1", json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
