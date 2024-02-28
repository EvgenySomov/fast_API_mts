from pydantic import BaseModel


__all__ = ["User"]


# Класс пользователя для токинизации
class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool = None