from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.features.books.models import Book


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