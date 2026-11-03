import io
import json
from datetime import UTC, datetime
from typing import Any, cast

import pandas as pd
from redis.asyncio import Redis

from app.core.enums import BookStatus
from app.core.exceptions.book_exp import (
    BookAlreadyExistsError,
    BookIncorrectFileFormatImport,
    BookNoRequiredColumnsImport,
    BookNotFoundError,
    BookRatingIsNone,
)
from app.features.books.models import Book
from app.features.books.repository import BookRepository
from app.features.books.schemas import BookCreate, BookResponse, BookUpdate


class BookService:
    def __init__(self, repository: BookRepository, redis: Redis):
        self.repository = repository
        self.redis = redis


    async def create_book(
        self,
        book_in: BookCreate,
        user_id: int
    ) -> Book:
        book = Book(**book_in.model_dump())
        result_get_book_repo = await self.repository.get_by_title_and_author(book)

        if result_get_book_repo is not None:
            raise BookAlreadyExistsError(
                message=f"Книга с заголовком: {book.title} и автором: {book.author} существует."
            )

        result_book = await self.repository.add_book(book, user_id)

        await self.redis.delete(f"stats:{user_id}")

        return result_book


    async def get_books(
        self,
        user_id: int,
        status: BookStatus | None = None,
        search: str | None = None,
        sort: str | None = None,
        order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ) -> dict[str, Any]:
        result_get_all_book_repo = await self.repository.get_all_books(
            user_id=user_id,
            status=status,
            search=search,
            sort=sort,
            order=order,
            limit=limit,
            offset=offset
        )

        return result_get_all_book_repo


    async def update_book(
        self,
        book_id: int,
        user_id: int,
        payload: BookUpdate
    ) -> Book:
        book_repo = await self.repository.get_by_id(book_id, user_id)

        if book_repo is None:
            raise BookNotFoundError(
                message="Книга не найдена."
            )

        clean_data = payload.model_dump(exclude_unset=True)
        old_status = book_repo.status
        new_status = clean_data.get("status")

        for key, value in clean_data.items():
            setattr(book_repo, key, value)

        if new_status is not None:
            if old_status != BookStatus.read and new_status == BookStatus.read:
                book_repo.finished_at = datetime.now(UTC).replace(microsecond=0)
            elif old_status == BookStatus.read and new_status != BookStatus.read:
                book_repo.finished_at = None

        result_save = await self.repository.save_book(book_repo)

        await self.redis.delete(f"stats:{user_id}")

        return result_save


    async def delete_book(
        self,
        book_id: int,
        user_id: int
    ) -> dict[str, str]:
        book_repo = await self.repository.get_by_id(book_id, user_id)

        if book_repo is None:
            raise BookNotFoundError(
                message="Книга не найдена."
            )

        await self.repository.delete_book(book_repo)

        await self.redis.delete(f"stats:{user_id}")

        return {
            "status": "success",
            "detail": f"Книга '{book_repo.title}' успешно удалена."
        }


    async def rating_add_book(
        self,
        book_id: int,
        rating: int | None,
        user_id: int
    ) -> BookResponse | None:
        if rating is None:
            raise BookRatingIsNone(
                message="Не указан рейтинг"
            )

        book_repo = await self.repository.get_by_id(book_id, user_id)

        if book_repo is None:
            raise BookNotFoundError(
                message="Книга не найдена"
            )

        result_rating_update = await self.repository.rating_update_book(book_id, rating)

        await self.redis.delete(f"stats:{user_id}")

        return BookResponse.model_validate(result_rating_update)


    async def get_stats(
        self,
        user_id: int
    ) -> dict[str, int]:
        cached_key = f"stats:{user_id}"

        cached_stats = await self.redis.get(cached_key)

        if cached_stats:
            return cast(dict[str, int], json.loads(cached_stats))

        list_status = await self.repository.get_by_count_read(user_id)
        result = {}

        for i in list_status:
            result[str(i.get("status"))] = int(i.get("count", 0))

        await self.redis.set(cached_key, json.dumps(result), ex=120)

        return result


    async def get_export_books(
        self,
        user_id: int
    ) -> io.BytesIO:
        user_books = await self.repository.get_all_books_for_export(user_id)

        books_data = []

        for book in user_books:
            books_data.append({
                "Title": book.title,
                "Author": book.author,
                "Status": book.status.value if book.status else "There is no status",
                "Note": book.note if book.note else "There are no records",
                "Created_At": book.created_at,
                "Finished_At": book.finished_at
                if book.finished_at
                else "There is no end date for reading"
            })

        df = pd.DataFrame(books_data)

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="My Books")

        buffer.seek(0)
        return buffer


    async def import_books(
        self,
        user_id: int,
        filename: str | None,
        file_bytes: bytes
    ) -> dict[str, Any]:
        if filename is None:
            raise BookIncorrectFileFormatImport(
                message="Неверный формат"
            )

        fname_lower = filename.lower()

        if fname_lower.endswith(".xlsx"):
            file_type = "excel"
        elif fname_lower.endswith(".csv"):
            file_type = "csv"
        else:
            raise BookIncorrectFileFormatImport(
                message="Неверный формат"
            )

        buffer = io.BytesIO(file_bytes)

        if file_type == "excel":
            df = pd.read_excel(buffer, engine="openpyxl")
        else:
            df = pd.read_csv(buffer)

        df.columns = [str(col).strip().lower() for col in df.columns]

        required_columns = {"title", "author"}

        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise BookNoRequiredColumnsImport(
                message=f"В файле отсутствуют обязательные колонки: {', '.join(missing)}"
            )

        df = df.replace({pd.NA: None, float("nan"): None})

        books_to_create = []

        for _, row in df.iterrows():
            if not row["title"] or not row["author"]:
                continue

            books_to_create.append({
                "title": row["title"].strip(),
                "author": row["author"].strip(),
                "owner_id": user_id,
            })

        await self.repository.bulk_create(books_to_create)

        return {
            "status": "success",
            "len": len(books_to_create)
        }
