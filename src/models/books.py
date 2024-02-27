from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from .base import BaseModel


class Book(BaseModel):
    __tablename__ = "books_table"
    id: Mapped[int] = mapped_column(primary_key=True)

    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers_table.id"))

    title: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)

    year: Mapped[int]
    count_pages: Mapped[int]