from pydantic import BaseModel

__all__ = ["Token", "AuthToken"]


# Класс для аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str


class AuthToken(BaseModel):
    e_mail: str
    password: str
