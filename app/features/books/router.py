from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.books.schemas import BookCreate, BookUpdate, BookResponse
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
    return await service.create_book_ser(book_in)


@router_books.get(
    "",
    response_model=list[BookResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_books(
    session: AsyncSession = Depends(get_db)
):
    repository = BookRepository(session)
    service = BookService(repository)
    return await service.get_books_ser()


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
    return await service.update_book_ser(book_id, payload)


@router_books.delete(
    "/{book_id}"
)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_db)
):
    repository = BookRepository(session)
    service = BookService(repository)
    return await service.delete_book_ser(book_id)