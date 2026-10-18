from sqlalchemy import String, func, CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from datetime import datetime

from app.core.database import Base
from app.core.enums import BookStatus


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(150), nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[BookStatus] = mapped_column(
        SQLEnum(BookStatus),
        default=BookStatus.want_to_read,
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

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 10", name="check_rating_range"),
    )