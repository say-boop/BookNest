import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.database import async_session
from app.features.books.models import Book


async def run_check_abandoned_books(db_session: AsyncSession) -> str:
    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)

    query = select(Book).where(
        Book.status == "want_to_read",
        Book.created_at < thirty_days_ago
    )
    result = await db_session.execute(query)
    books = result.scalars().all()

    for book in books:
        print(f"- User_ID: {book.owner_id} | Name: {book.title}")

    return f"Processed {len(books)} books"


@celery_app.task(name="app.features.books.tasks.check_abandoned_books") # type: ignore[untyped-decorator]
def check_abandoned_books() -> str:
    async def main_runner() -> str:
        async with async_session() as session:
            return await run_check_abandoned_books(session)

    return asyncio.run(main_runner())
