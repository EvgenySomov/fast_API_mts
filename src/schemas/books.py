from pydantic import BaseModel, Field

__all__ = ["IncomingBook",
           "ReturnedAllBooks",
           "ReturnedBook",
           "BaseBookSeller",
           "ReturnedBookNotSellers"]


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int


# Базовый класс "Книги" с продавцом
class BaseBookSeller(BaseBook):
    seller_id: int


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingBook(BaseBookSeller):
    year: int = 2000
    count_pages: int = Field(
        alias="pages",
        default=300,
    )


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBook(BaseBookSeller):
    id: int
    count_pages: int


# Класс для вывода у продавца без его ID
class ReturnedBookNotSellers(BaseBook):
    id: int
    year: int
    count_pages: int


# Класс для возврата массива объектов "Книга"
class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]
