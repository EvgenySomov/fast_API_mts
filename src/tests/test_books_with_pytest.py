import pytest
from fastapi import status
from sqlalchemy import select
from src.models import books
from src.models import sellers
from src.jwt_auth.auth import pwd_context
from src.schemas import ReturnedBook

"""
Так как появилась взаимосвязь двух таблиц, необходим доп тест на наличие продавца.
Был изменен функционал тестов, добавлены продавцы"
"""


# Вспомогательная функция для записи 1 продавца и получения его токена
async def get_token(db_session, async_client):
    auth_data = dict(e_mail="@test.seller",
                     password=pwd_context.hash("passwordtestseller")
                     )

    seller = sellers.Seller(first_name="test_seller",
                            last_name="test_seller",
                            **auth_data
                            )
    db_session.add(seller)
    await db_session.flush()
    auth_data["password"] = "passwordtestseller"

    # Сначала получаем токен
    response = await async_client.post("/api/v1/token/", json=auth_data)
    token = response.json()["access_token"]
    return token, seller


# Вспомогательная функция для записи 2 книг
async def write_book(seller, db_session):
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()
    return book, book_2


# Новый тест на ручку при создании книги без продавца
@pytest.mark.asyncio
async def test_create_book_not_seller(db_session, async_client):
    # получим токен
    token, _ = await get_token(db_session, async_client)

    data = {"title": "Wrong Code", "author": "Robert Martin", "pages": 104, "year": 2007, "seller_id": 0}
    response = await async_client.post("/api/v1/books/", json=data, headers={"Authorization": "Bearer " + token})

    result_data = response.json()

    assert result_data == {"erros": "Отсутсвует продавец"}


# Тест на ручку при созданом продавце
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    token, seller = await get_token(db_session, async_client)

    # Теперь добавляем книгу
    data = {"title": "Wrong Code", "author": "Robert Martin", "pages": 104, "year": 2007, "seller_id": seller.id}
    response = await async_client.post("/api/v1/books/", json=data, headers={"Authorization": "Bearer " + token})

    assert response.status_code == status.HTTP_201_CREATED

    assert response.json() == {"title": "Wrong Code",
                               "author": "Robert Martin",
                               "year": 2007,
                               "seller_id": seller.id,
                               "id": 1,
                               "count_pages": 104}


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    _, seller = await get_token(db_session, async_client)
    book, book_2 = await write_book(seller, db_session)

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    # Избавимся от лишней писанины, воспользуемся магическими методами
    return_book = ReturnedBook(**book.__dict__).dict()
    return_book_2 = ReturnedBook(**book_2.__dict__).dict()

    assert {"books": [return_book, return_book_2]} == response.json()


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):

    _, seller = await get_token(db_session, async_client)
    book, _ = await write_book(seller, db_session)

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    return_book = ReturnedBook(**book.__dict__).dict()

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == return_book


# Тест на ручку удаления книг по порядку
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):

    _, seller = await get_token(db_session, async_client)
    book, book_2 = await write_book(seller, db_session)

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 1

    response = await async_client.delete(f"/api/v1/books/{book_2.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    token, seller = await get_token(db_session, async_client)

    book = books.Book(author="Pushkin", title="Eugeny Onegin", seller_id=seller.id, year=2001, count_pages=104)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={"title": "Mziri", "author": "Lermontov", "count_pages": 100, "year": 2007,
              "seller_id": seller.id, "id": book.id
              },
        headers={"Authorization": "Bearer " + token}
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(books.Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.count_pages == 100
    assert res.year == 2007
    assert res.id == book.id
