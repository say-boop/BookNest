from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.features.books.models import Book
from app.core.enums import BookStatus


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_book(
        self,
        book: Book
    ) -> Book:
        self.session.add(book)
        await self.session.commit()
        await self.session.refresh(book)

        return book

    async def get_by_title_and_author(
        self,
        book: Book
    ) -> Book | None:
        query = select(Book).where(Book.title == book.title, Book.author == book.author)
        result = await self.session.execute(query)
        existing_book = result.scalar_one_or_none()

        return existing_book

    async def get_all_books(
        self,
        status: BookStatus | None = None,
        search: str | None = None
    ) -> list[Book]:
        if status is not None:
            query = select(Book).where(Book.status == status)
        elif search is not None and search.strip():
            query = select(Book).where(or_(Book.title.like(f"%{search}%"), Book.author.like(f"%{search}%")))
        else:
            query = select(Book)
        
        result = await self.session.execute(query)
        books = result.scalars().all()

        return books

    async def get_by_id(
        self,
        book_id: int
    ) -> Book | None:
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        book = result.scalar_one_or_none()

        return book

    async def save_book(
        self,
        book: Book
    ) -> Book:
        await self.session.commit()
        await self.session.refresh(book)

        return book

    async def delete_book(
        self,
        book: Book
    ) -> Book:
        await self.session.delete(book)
        await self.session.commit()

        return book

    async def rating_update_book(
        self,
        book_id: int,
        rating: int
    ) -> Book | None:
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        book = result.scalar_one_or_none()

        if book:
            book.rating = rating
            await self.session.commit()
            await self.session.refresh(book)

        return book