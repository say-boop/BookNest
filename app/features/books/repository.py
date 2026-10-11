from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.features.books.models import Book


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_book_rep(
        self,
        book: Book
    ) -> Book:
        self.session.add(book)
        await self.session.commit()
        await self.session.refresh(book)

        return book

    async def get_by_title_and_author_rep(
        self,
        book: Book
    ) -> Book | None:
        query = select(Book).where(Book.title == book.title, Book.author == book.author)
        result = await self.session.execute(query)
        existing_book = result.scalar_one_or_none()

        return existing_book

    async def get_all_books_rep(
        self
    ) -> list[Book]:
        query = select(Book)
        result = await self.session.execute(query)
        books = result.scalars().all()

        return books

    async def get_by_id_rep(
        self,
        book_id: int
    ) -> Book | None:
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        book = result.scalar_one_or_none()

        return book

    async def save_update_book_repo(
        self,
        book: Book
    ) -> Book:
        await self.session.commit()
        await self.session.refresh(book)

        return book

    async def delete_book_repo(
        self,
        book: Book
    ) -> Book:
        await self.session.delete(book)
        await self.session.commit()

        return book