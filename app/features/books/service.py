from app.features.books.models import Book
from app.features.books.schemas import BookCreate, BookUpdate
from app.features.books.repository import BookRepository
from app.core.exceptions.base import BookAlreadyExistsError, BookNotFoundError
from app.core.enums import BookStatus


class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def create_book(
        self, 
        book_in: BookCreate
    ) -> Book:
        book = Book(**book_in.model_dump())
        result_get_book_repo = await self.repository.get_by_title_and_author(book)

        if result_get_book_repo is not None:
            raise BookAlreadyExistsError(
                message=f"Книга с заголовком: {book.title} и автором: {book.author} существует."
            )

        result_book = await self.repository.add_book(book)

        return result_book

    async def get_books(
        self,
        status: BookStatus | None = None,
        search: str | None = None
    ) -> list[Book]:
        result_get_all_book_repo = await self.repository.get_all_books(status=status, search=search)

        return result_get_all_book_repo

    async def update_book(
        self, 
        book_id: int, 
        payload: BookUpdate
    ) -> Book:
        book_repo = await self.repository.get_by_id(book_id)

        if book_repo is None:
            raise BookNotFoundError(
                message="Книга не найдена."
            )

        clean_data = payload.model_dump(exclude_unset=True)

        for key, value in clean_data.items():
            setattr(book_repo, key, value)

        result_save = await self.repository.save_book(book_repo)

        return result_save

    async def delete_book(
        self,
        book_id: int
    ):
        book_repo = await self.repository.get_by_id(book_id)

        if book_repo is None:
            raise BookNotFoundError(
                message="Книга не найдена."
            )

        await self.repository.delete_book(book_repo)

        return {
            "status": "success",
            "detail": f"Книга '{book_repo.title}' успешно удалена."
        }

    async def rating_add_book(
        self,
        book_id: int,
        rating: int
    ):
        book_repo = await self.repository.get_by_id(book_id)

        if book_repo is None:
            raise BookNotFoundError(
                message="Книга не найдена"
            )

        result_rating_update = await self.repository.rating_update_book(book_id, rating)

        return result_rating_update