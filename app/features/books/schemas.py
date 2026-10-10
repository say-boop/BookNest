from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.core.enums import BookStatus


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=150)
    status: BookStatus


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None
    author: str | None
    status: BookStatus | None


class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )