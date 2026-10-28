from httpx import AsyncClient

from app.features.books.models import Book
from app.features.users.models import User
from app.core.generate_jwt import create_access_token
from app.core.security import Argon2HashPassword


# Filtering and Searching
async def test_get_books_filter_by_status(auth_client: AsyncClient, create_book_factory):
    await create_book_factory(status="read")
    await create_book_factory(status="read")
    await create_book_factory(status="want_to_read")

    response = await auth_client.get(
        "/books?status=read"
    )

    assert response.status_code == 200

    data = response.json()

    for item in data["items"]:
        assert item["status"] == "read"


async def test_get_books_search_buy_title_or_author(auth_client: AsyncClient, create_book_factory):
    await create_book_factory(title="Garry")
    await create_book_factory(author="Rouling")
    await create_book_factory(author="Master")

    response = await auth_client.get(
        "/books?search=garry"
    )

    assert response.status_code == 200

    data = response.json()

    for item in data["items"]:
        assert "garry" in item["title"].lower()


# Sorting and Pagination
async def test_get_books_soting_by_rating_desc(auth_client: AsyncClient, create_book_factory):
    await create_book_factory(rating=3)
    await create_book_factory(rating=4)
    await create_book_factory(rating=5)

    response = await auth_client.get(
        "/books?sort=rating&order=desc"
    )

    assert response.status_code == 200

    count = 5
    data = response.json()

    for item in data["items"]:
        assert item["rating"] == count
        count -= 1


async def test_get_books_pagination(auth_client: AsyncClient, create_book_factory):
    await create_book_factory(title="first")
    await create_book_factory(title="second")
    await create_book_factory(title="three")

    response = await auth_client.get(
        "/books?limit=1&offset=1"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["items"][0]["title"] == "second"


# GET /books/stats
async def test_get_books_stats_success(auth_client: AsyncClient, create_book_factory):
    await create_book_factory(status="read")
    await create_book_factory(status="want_to_read")
    await create_book_factory(status="read")

    response = await auth_client.get(
        "/books/stats"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["want_to_read"] == 1
    assert data["read"] == 2


async def test_get_books_stats_isolation(
    auth_client: AsyncClient, 
    db_session, 
    create_book_factory
):
    await create_book_factory(status="read")
    await create_book_factory(status="read")

    ghost_user = User(
        email="ghost_owner@booknest.com",
        username="ghost_name",
        password_hash="some_hashed_password",
        is_active=True
    )
    db_session.add(ghost_user)
    await db_session.commit()
    await db_session.refresh(ghost_user)

    ghost_book = Book(
        title="Ghost book",
        author="Ghost",
        status="read",
        owner_id=ghost_user.id
    )
    db_session.add(ghost_book)
    await db_session.commit()

    response = await auth_client.get(
        "/books/stats"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["read"] == 2


async def test_get_books_stats_empty(auth_client: AsyncClient):
    response = await auth_client.get(
        "/books/stats"
    )

    assert response.status_code == 200

    data = response.json()

    for key, value in data.items():
        assert value == 0