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
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None, min_length=1, max_length=150)
    rating: int | None = Field(default=None, ge=1, le=10)
    status: BookStatus | None = None


class BookRatingUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=10)


class BookResponse(BookBase):
    id: int
    rating: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )