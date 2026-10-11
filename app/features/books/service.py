from app.features.books.models import Book
from app.features.books.schemas import BookCreate
from app.features.books.repository import BookRepository
from app.core.exceptions.base import BookAlreadyExistsError, BookNotFoundError


class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def create_book(self, book_in: BookCreate):
        book = Book(**book_in.model_dump())
        result_get_book_repo = await self.repository.get_by_title_and_author(book)

        if result_get_book_repo is not None:
            raise BookAlreadyExistsError(
                message=f"Книга с заголовком: {book.title} и автором: {book.author} существует."
            )

        result_book = await self.repository.add_book(book)

        return result_book

    async def get_books(self):
        result_get_all_book_repo = await self.repository.get_all_books()

        if len(result_get_all_book_repo) <= 0:
            raise BookNotFoundError(
                message=f"Книги не найдены."
            )

        return result_get_all_book_repo