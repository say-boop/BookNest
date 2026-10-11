from app.features.books.models import Book
from app.features.books.schemas import BookCreate, BookUpdate
from app.features.books.repository import BookRepository
from app.core.exceptions.base import BookAlreadyExistsError, BookNotFoundError


class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def create_book_ser(
        self, 
        book_in: BookCreate
    ) -> Book:
        book = Book(**book_in.model_dump())
        result_get_book_repo = await self.repository.get_by_title_and_author_rep(book)

        if result_get_book_repo is not None:
            raise BookAlreadyExistsError(
                message=f"Книга с заголовком: {book.title} и автором: {book.author} существует."
            )

        result_book = await self.repository.add_book_rep(book)

        return result_book

    async def get_books_ser(
        self
    ) -> list[Book]:
        result_get_all_book_repo = await self.repository.get_all_books_rep()

        if len(result_get_all_book_repo) <= 0:
            raise BookNotFoundError(
                message="Книги не найдены."
            )

        return result_get_all_book_repo

    async def update_book_ser(
        self, 
        book_id: int, 
        payload: BookUpdate
    ) -> Book:
        book_repo = await self.repository.get_by_id_rep(book_id)

        if book_repo is None:
            raise BookNotFoundError(
                message="Книга не найдена."
            )

        clean_data = payload.model_dump(exclude_unset=True)

        for key, value in clean_data.items():
            setattr(book_repo, key, value)

        result_save = await self.repository.save_update_repo(book_repo)

        return result_save