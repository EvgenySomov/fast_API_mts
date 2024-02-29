import pytest
from fastapi import status
from sqlalchemy import select
from src.models import books
from src.models import sellers
from src.jwt_auth.auth import pwd_context


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


# Тест для проверки регистрации продавца
@pytest.mark.asyncio
async def test_create_seller(db_session, async_client):
    data = {"first_name": "Evgeny", "last_name": "Somov", "e_mail": "somov@mail.ru", "password": "password"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    await db_session.flush()
    assert response.status_code == status.HTTP_201_CREATED

    # Получим из базы записанного продавца, что бы взять его ID
    # Так как каждый тест выдает сквозное ID

    all_sellers = await db_session.execute(select(sellers.Seller))
    seller = all_sellers.scalars().first()

    # Проверим пароль
    result_data = response.json()
    assert pwd_context.verify(data["password"], result_data["password"])

    del data["password"]
    del result_data["password"]

    # Получим id из базы
    data["id"] = seller.id

    assert result_data == data


# Тест для проверки списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):

    seller = sellers.Seller(first_name="first_Test_1", last_name="last_test_1", e_mail="test1@ru", password="pass1")
    seller_2 = sellers.Seller(first_name="first_Test_2", last_name="last_test_2", e_mail="test1@ru", password="pass2")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {"sellers": [{"first_name": seller.first_name,
                                            "last_name": seller.last_name,
                                            "e_mail": seller.e_mail,
                                            "id": seller.id},
                                           {"first_name": seller_2.first_name,
                                            "last_name": seller_2.last_name,
                                            "e_mail": seller_2.e_mail,
                                            "id": seller_2.id}
                                           ]
                               }


# Тест для проверки 1 продавца с книгами и без
@pytest.mark.asyncio
async def test_get_single_sellers(db_session, async_client):
    token, _ = await get_token(db_session, async_client)
    # Добавим пару продавцов
    seller = sellers.Seller(first_name="first_Test_1", last_name="last_test_1", e_mail="test1@ru", password="pass1")
    seller_2 = sellers.Seller(first_name="first_Test_2", last_name="last_test_2", e_mail="test1@ru", password="pass2")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}", headers={"Authorization": "Bearer " + token})

    # Проверим без книг первого
    assert response.json() == {"first_name": seller.first_name,
                               "last_name": seller.last_name,
                               "e_mail": seller.e_mail,
                               "id": seller.id,
                               "books": []
                               }

    # Теперь добавим пару книнг 2 продавцу
    dict_book = dict(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_2.id)
    dict_book_2 = dict(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    book = books.Book(**dict_book)
    book_2 = books.Book(**dict_book_2)

    db_session.add_all([book, book_2])
    await db_session.flush()

    # Переиспользуем словарь для теста, немного подправим данные которые нам нужны
    del dict_book["seller_id"]
    dict_book["id"] = book.id

    response = await async_client.get(f"/api/v1/sellers/{seller_2.id}", headers={"Authorization": "Bearer " + token})

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {"first_name": seller_2.first_name,
                               "last_name": seller_2.last_name,
                               "e_mail": seller_2.e_mail,
                               "id": seller_2.id,
                               "books": [dict_book]
                               }


# Тест для проверки изменения информации о продавце
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    token, _ = await get_token(db_session, async_client)
    # Добавим пару продавцов
    seller = sellers.Seller(first_name="first_Test_1", last_name="last_test_1", e_mail="test1@ru", password="pass1")
    seller_2 = sellers.Seller(first_name="first_Test_2", last_name="last_test_2", e_mail="test1@ru", password="pass2")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    # Теперь добавим пару книг продавцам
    dict_book = dict(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    dict_book_2 = dict(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller_2.id)

    book = books.Book(**dict_book)
    book_2 = books.Book(**dict_book_2)

    db_session.add_all([book, book_2])
    await db_session.flush()

    # Переиспользуем словарь для теста, немного подправим данные которые нам нужны
    del dict_book["seller_id"]
    dict_book["id"] = book.id

    dict_new_seller_info = dict(first_name="New_First1",
                                last_name="New_Last1",
                                e_mail="new@1")

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json=dict_new_seller_info)

    assert response.status_code == status.HTTP_200_OK

    response = await async_client.get(f"/api/v1/sellers/{seller.id}", headers={"Authorization": "Bearer " + token})

    # Проверяем, что обновились все поля не затронув книги
    assert response.json() == {**dict_new_seller_info,
                               "id": seller.id,
                               "books": [dict_book]
                               }


# Тест на удаление продавцов и его книг
@pytest.mark.asyncio
async def test_delete_sellers(db_session, async_client):
    seller = sellers.Seller(first_name="first_Test_1",
                            last_name="last_test_1",
                            e_mail="test1@ru",
                            password="pass1")

    db_session.add(seller)
    await db_session.flush()

    dict_book = dict(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book = books.Book(**dict_book)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")
    await db_session.flush()

    assert response.status_code == status.HTTP_204_NO_CONTENT

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0

