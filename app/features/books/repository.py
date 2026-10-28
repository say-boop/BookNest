from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, and_

from app.features.books.models import Book
from app.core.enums import BookStatus


SORT_MAPPING = {
    "created_at": Book.created_at,
    "rating": Book.rating
}

DEFAULT_SORT_COLUMN = Book.created_at


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    

    async def add_book(
        self,
        book: Book,
        user_id: int
    ) -> Book:
        book.owner_id = user_id
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
        user_id: int,
        status: BookStatus | None = None,
        search: str | None = None,
        sort: str | None = None,
        order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ) -> list[Book]:
        query = select(Book).where(Book.owner_id == user_id).offset(offset).limit(limit)
        
        if status is not None:
            query = query.where(Book.status == status)
        
        if search is not None and search.strip():
            ts_query = func.plainto_tsquery('russian', search)
            query = query.where(Book.search_vector.op("@@")(ts_query))

            if sort is None:
                query = query.order_by(func.ts_rank(Book.search_vector, ts_query).desc())
            
        if sort is not None:
            sort_column = SORT_MAPPING.get(sort, DEFAULT_SORT_COLUMN)

            if order.lower() == "desc":
                query = query.order_by(sort_column.desc().nulls_last())
            else:
                query = query.order_by(sort_column.asc().nulls_last())
        
        result = await self.session.execute(query)
        books = result.scalars().all()

        return {
            "total": len(books),
            "items": books
        }


    async def get_by_id(
        self,
        book_id: int,
        user_id: int
    ) -> Book | None:
        query = select(Book).where(and_(Book.id == book_id, Book.owner_id == user_id))
        result = await self.session.execute(query)
        book = result.scalar_one_or_none()

        return book


    async def get_by_count_read(
        self,
        user_id: int
    ):
        query = select(Book.status, func.count(Book.id).label("count")).where(Book.owner_id == user_id).group_by(Book.status)
        result = await self.session.execute(query)
        rows = result.all()

        return [{
            "status": row.status,
            "count": row.count
        } for row in rows]


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