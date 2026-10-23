from __future__ import annotations
from sqlalchemy import String, func, CheckConstraint, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.database import Base
from app.core.enums import BookStatus


if TYPE_CHECKING:
    from app.features.users.models import User


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
    finished_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship(back_populates="books")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 10", name="check_rating_range"),
    )