from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from .books import BaseBook

__all__ = ["IncomingSeller", "ReturnedAllSellers",
           "ReturnedSeller", "ReturnedSellerBooks",
           "ReturnedSellerId", "BaseSeller"]


# Базовый класс "Продавец", будет содержать только открытую информацию
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


# Класс для входядщих данных, где есть пароль.
class IncomingSeller(BaseSeller):
    password: str


# Класс ответа на регистрацию
class ReturnedSeller(BaseSeller):
    id: int
    password: str


# Класс ответа 1 пользователя для вывода
class ReturnedSellerId(BaseSeller):
    id: int


# Класс для возврата массива продавцов
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSellerId]


# Класс просмотра продовца с книгами
class ReturnedSellerBooks(BaseSeller):
    id: int
    books: list[BaseBook]