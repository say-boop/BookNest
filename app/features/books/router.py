from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

from app.core.database import get_db
from app.core.enums import BookStatus
from app.features.books.schemas import BookCreate, BookUpdate, BookResponse, BookRatingUpdate, BookPaginatedResponse, BookStatsResponse
from app.features.books.service import BookService
from app.features.books.repository import BookRepository


router_books = APIRouter(prefix="/books", tags=["books"])


@router_books.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_book(
    book_in: BookCreate,
    session: AsyncSession = Depends(get_db)
):
    repository = BookRepository(session)
    service = BookService(repository)
    return await service.create_book(book_in)


@router_books.get(
    "",
    response_model=BookPaginatedResponse,
    status_code=status.HTTP_200_OK
)
async def get_all_books(
    status: BookStatus | None = None,
    search: str | None = None,
    sort: Literal["created_at", "rating"] | None = None,
    order: Literal["asc", "desc"] = "asc",
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db)
):
    repository = BookRepository(session)
    service = BookService(repository)
    return await service.get_books(
        status=status, 
        search=search, 
        sort=sort, 
        order=order,
        limit=limit,
        offset=offset
    )


@router_books.get(
    "/stats",
    response_model=BookStatsResponse
)
async def get_stats(
    session: AsyncSession = Depends(get_db)
):
    repository = BookRepository(session)
    service = BookService(repository)
    return await service.get_stats()


@router_books.patch(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK
)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    session: AsyncSession = Depends(get_db)
):
    repository = BookRepository(session)
    service = BookService(repository)
    return await service.update_book(book_id, payload)


@router_books.delete(
    "/{book_id}"
)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_db)
):
    repository = BookRepository(session)
    service = BookService(repository)
    return await service.delete_book(book_id)


@router_books.patch(
    "/{book_id}/rating"
)
async def add_rating_book(
    book_id: int,
    rating: BookRatingUpdate,
    session: AsyncSession = Depends(get_db)
):
    repository = BookRepository(session)
    service = BookService(repository)
    return await service.rating_add_book(book_id, rating=rating.rating)