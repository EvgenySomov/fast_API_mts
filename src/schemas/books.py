from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["IncomingBook", "ReturnedAllBooks", "ReturnedBook"]


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int
    seller_id: int


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingBook(BaseBook):
    year: int = 2000
    count_pages: int = Field(
        alias="pages",
        default=300,
    )


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBook(BaseBook):
    id: int
    count_pages: int


# Класс для возврата массива объектов "Книга"
class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]
