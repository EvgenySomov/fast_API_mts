from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedSellerBooks, BaseSeller
from src.models.books import Book

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

# Подключение к базе
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о продавце. Возвращает нового продавца.
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(
    seller: IncomingSeller, session: DBSession
):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        e_mail=seller.e_mail,
        password=seller.password,
    )
    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка, возвращающая всех продавцов.
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_seller(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


# Ручка, возвращающая продавца и его книги.
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerBooks)
async def get_seller(seller_id: int, session: DBSession):

    if seller := await session.get(Seller, seller_id):
        books = await session.execute(select(Book).filter(Book.seller_id == seller_id))

        books = books.scalars().all()

        # Думаю это костыль, так-как не совсем понял, как красиво объяснить модели, что нужно показать :(
        res = dict(books=books, **seller.__dict__)
        return res
    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о продавце.
@sellers_router.put("/{seller_id}")
async def update_seller(seller_id: int, new_data: BaseSeller, session: DBSession):

    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.e_mail = new_data.e_mail
        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для продавца.
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    if deleted_seller := await session.get(Seller, seller_id):
        await session.delete(deleted_seller)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return Response(status_code=status.HTTP_404_NOT_FOUND)

