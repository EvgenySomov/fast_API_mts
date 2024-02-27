from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["User"]


# Класс пользователя для токинизации
class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool = None