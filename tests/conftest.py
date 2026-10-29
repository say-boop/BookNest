from sqlalchemy.ext.asyncio import create_async_engine
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
import os
import asyncio
import sys

from app.core.config import settings

os.environ["POSTGRES_DB"] = "booknest_test_db"
os.environ["POSTGRES_HOST"] = settings.POSTGRES_HOST

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from app.main import app
from app.core.database import Base, async_session, get_db
from app.features.users.models import User
from app.features.books.models import Book
from app.core.security import Argon2HashPassword

test_engine = create_async_engine(settings.get_database_url())


@pytest_asyncio.fixture(
    scope="session",
    autouse=True
)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(
    scope="function",
    autouse=True
)
async def db_session():
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        async with async_session(bind=connection) as session:
            yield session

        await transaction.rollback()


@pytest_asyncio.fixture(
    scope="function"
)
async def client(db_session):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(
    scope="function"
)
async def test_user(db_session):
    raw_password = "supersecretpassword123"
    hashed_password = Argon2HashPassword.hash_password(raw_password)

    user = User(
        email="test_user@booknest.com",
        username="test_user",
        password_hash=hashed_password
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "password": raw_password
    }


@pytest_asyncio.fixture(
    scope="function"
)
async def auth_client(
    client: AsyncClient,
    test_user
):
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }

    login_response = await client.post(
        "/users/login",
        data=login_data
    )

    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]

    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    yield client


@pytest_asyncio.fixture(
    scope="function"
)
def create_book_factory(
    db_session,
    test_user
):
    async def _make_book(**kwargs):
        default_data = {
            "title": "Test book",
            "author": "Test author",
            "rating": 5,
            "note": "Test note",
            "status": "want_to_read",
            "owner_id": test_user["id"]
        }

        final_data = {**default_data, **kwargs}

        db_book = Book(**final_data)

        db_session.add(db_book)
        await db_session.commit()
        await db_session.refresh(db_book)

        return {
            "id": db_book.id,
            "title": db_book.title,
            "author": db_book.author,
            "rating": db_book.rating,
            "note": db_book.note,
            "status": db_book.status,
            "owner_id": db_book.owner_id
        }

    return _make_book