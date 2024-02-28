from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.books import Book
from src.models.sellers import Seller
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook
from src.jwt_auth.auth import get_current_user

books_router = APIRouter(tags=["books"], prefix="/books")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
# Закрыта токеном!
@books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: IncomingBook, session: DBSession, current_user: Seller = Depends(get_current_user)
):
    # Проверяем, есть ли вообще продавец
    if seller := await session.get(Seller, book.seller_id):
        new_book = Book(
            title=book.title,
            author=book.author,
            year=book.year,
            count_pages=book.count_pages,
            seller_id=book.seller_id
        )
        session.add(new_book)
        await session.flush()

        return new_book
    return JSONResponse(content={"erros": "Отсутсвует продавец"})


# Ручка, возвращающая все книги
@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):

    query = select(Book)
    res = await session.execute(query)
    books = res.scalars().all()
    return {"books": books}


# Ручка для получения книги по ее ИД
@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    res = await session.get(Book, book_id)
    return res


# Ручка для удаления книги
@books_router.delete("/{book_id}")
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await session.get(Book, book_id)
    if deleted_book:
        await session.delete(deleted_book)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Ручка для обновления данных о книге
# Закрыта токеном!
@books_router.put("/{book_id}")
async def update_book(book_id: int,
                      new_data: ReturnedBook,
                      session: DBSession,
                      current_user: Seller = Depends(get_current_user)):

    if updated_book := await session.get(Book, book_id):
        updated_book.author = new_data.author
        updated_book.title = new_data.title
        updated_book.year = new_data.year
        updated_book.count_pages = new_data.count_pages

        await session.flush()

        return updated_book

    return Response(status_code=status.HTTP_404_NOT_FOUND)
