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
    return await service.create_book(book_in)


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
    return await service.get_books()