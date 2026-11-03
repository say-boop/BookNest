from datetime import UTC, datetime, timedelta
from typing import Any

from app.features.books.tasks import run_check_abandoned_books


async def test_check_abandonetd_book_with_fixtures(
    db_session: Any,
    create_book_factory: Any
) -> None:
    now = datetime.now(UTC)

    await create_book_factory(
        title="First book",
        status="want_to_read",
        created_at=now - timedelta(days=35)
    )

    await create_book_factory(
        title="Second book",
        status="want_to_read",
        created_at=now - timedelta(days=5)
    )

    await create_book_factory(
        title="Third book",
        status="reading",
        created_at=now - timedelta(days=40)
    )

    result = await run_check_abandoned_books(db_session)

    assert result == "Processed 1 books"
