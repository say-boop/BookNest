from fastapi import FastAPI, Depends, status, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, engine, init_db
from app.models import Book
from app.schemas import BookCreate, BookResponse, BookUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_books(
    book_in: BookCreate,
    session: AsyncSession = Depends(get_db)
):
    new_book = Book(**book_in.model_dump())

    session.add(new_book)
    await session.commit()

    await session.refresh(new_book)

    return new_book


@app.get(
    "/books",
    response_model=list[BookResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_books(session: AsyncSession = Depends(get_db)):
    query = select(Book)
    result = await session.execute(query)

    books = result.scalars().all()

    return books


@app.patch(
    "/books/{book_id}",
    response_model=BookResponse
)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    session: AsyncSession = Depends(get_db)
):
    query = select(Book).where(Book.id == book_id)
    result = await session.execute(query)
    book = result.scalar_one_or_none()

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с id {book_id} не найдена."
        )

    clean_data = payload.model_dump(exclude_unset=True)

    for key, value in clean_data.items():
        setattr(book, key, value)

    await session.commit()
    await session.refresh(book)

    return book


@app.delete(
    "/books/{book_id}"
)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_db)
):
    query = select(Book).where(Book.id == book_id)
    result = await session.execute(query)
    book = result.scalar_one_or_none()

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с id {book_id} не найдена. Удаление невозможно."
        )

    await session.delete(book)
    await session.commit()

    return {
        "status": "success",
        "detail": f"Книга '{book.title}' успешно удалена."
    }