from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["Token"]


# Класс для аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str

