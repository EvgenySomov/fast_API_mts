from pydantic import BaseModel
from .books import ReturnedBookNotSellers

__all__ = ["IncomingSeller", "ReturnedAllSellers",
           "ReturnedSeller", "ReturnedSellerBooks",
           "ReturnedSellerId", "BaseSeller"]


# Базовый класс "Продавец", будет содержать только открытую информацию
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


# Класс для входящих данных, где есть пароль.
class IncomingSeller(BaseSeller):
    password: str


# Класс ответа на регистрацию.
class ReturnedSeller(BaseSeller):
    id: int
    password: str


# Класс ответа 1 пользователя для вывода.
class ReturnedSellerId(BaseSeller):
    id: int


# Класс для возврата массива продавцов.
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSellerId]


# Класс просмотра продавца с книгами.
class ReturnedSellerBooks(BaseSeller):
    id: int
    books: list[ReturnedBookNotSellers]

