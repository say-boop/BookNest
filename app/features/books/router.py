from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.enums import BookStatus
from app.core.dependencies import get_current_user
from app.core.redis_client import get_redis
from app.features.books.schemas import BookCreate, BookUpdate, BookResponse, BookRatingUpdate, BookPaginatedResponse, BookStatsResponse
from app.features.books.service import BookService
from app.features.books.repository import BookRepository
from app.features.users.models import User


router_books = APIRouter(prefix="/books", tags=["books"])


def get_book_service(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    repository = BookRepository(session)
    return BookService(repository, redis)


@router_books.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_book(
    book_in: BookCreate,
    current_user: User = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    return await service.create_book(book_in, current_user.id)


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
    current_user: User = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    return await service.get_books(
        user_id=current_user.id,
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
    current_user: User = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    return await service.get_stats(current_user.id)


@router_books.get(
    "/export",
    status_code=status.HTTP_200_OK
)
async def get_export_books(
    current_user: User = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    excel_file = await service.get_export_books(current_user.id)
    
    headers = {
        "Content-Disposition": f"attachment; filename=books_user_{current_user.id}.xlsx"
    }

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )


@router_books.patch(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK
)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    current_user: User = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    return await service.update_book(book_id, current_user.id, payload)


@router_books.delete(
    "/{book_id}"
)
async def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    return await service.delete_book(book_id, current_user.id)


@router_books.patch(
    "/{book_id}/rating"
)
async def add_rating_book(
    book_id: int,
    rating: BookRatingUpdate,
    current_user: User = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    return await service.rating_add_book(book_id, rating=rating.rating, user_id=current_user.id)