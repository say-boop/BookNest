from typing import Any

import pytest
from httpx import AsyncClient

from app.core.redis_client import get_redis


async def clear_redis() -> None:
    async for redis in get_redis():
        await redis.flushdb()
        break


@pytest.mark.asyncio(loop_scope="function")
async def test_get_books_stats_cache_flow(
    auth_client: AsyncClient,
    create_book_factory: Any,
) -> None:
    await clear_redis()

    await create_book_factory(status="read")
    await create_book_factory(status="reading")

    response_first = await auth_client.get(
        "/books/stats"
    )

    assert response_first.status_code == 200

    first_data = response_first.json()

    await create_book_factory(status="read")

    response_second = await auth_client.get(
        "/books/stats"
    )

    assert response_second.status_code == 200
    assert response_second.json() == first_data


@pytest.mark.asyncio(loop_scope="function")
async def test_get_books_stats_invalidation(
    auth_client: AsyncClient,
    create_book_factory: Any,
) -> None:
    await clear_redis()

    await create_book_factory(status="read")

    response_before = await auth_client.get(
        "/books/stats"
    )

    assert response_before.status_code == 200

    data_before = response_before.json()

    new_book_data = {
        "title": "Unique New Book",
        "author": "Unique New Author",
        "status": "reading",
        "rating": 4,
        "note": "Some note"
    }

    post_response = await auth_client.post(
        "/books",
        json=new_book_data
    )

    assert post_response.status_code == 201

    response_after = await auth_client.get(
        "/books/stats"
    )

    assert response_after.status_code == 200

    data_after = response_after.json()

    assert data_after != data_before
    assert data_after.get("reading", 0) == data_before.get("reading", 0) + 1
