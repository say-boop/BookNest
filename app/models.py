from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from enum import Enum

from app.core.database import Base


class BookStatus(str, Enum):
    FIRST = "I will be reading"
    SECOND = "Reading"
    THIRD = "I read it"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[BookStatus] = mapped_column(
        SQLEnum(BookStatus),
        default=BookStatus.FIRST,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )