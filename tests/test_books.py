from httpx import AsyncClient
import pandas as pd
import io

from app.core.generate_jwt import create_access_token
from app.core.security import Argon2HashPassword
from app.features.users.models import User


# POST /books
async def test_create_book_success(auth_client: AsyncClient):
    response = await auth_client.post(
        "/books",
        json={
            "title": "Test create book_title",
            "author": "Test create book_author",
            "status": "want_to_read",
            "note": "Test create book_note"
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["note"] == "Test create book_note"
    assert data["title"] == "Test create book_title"
    assert data["author"] == "Test create book_author"


async def test_create_book_unauthorized(client: AsyncClient):
    response = await client.post(
        "/books",
        json={
            "title": "Test create book_title",
            "author": "Test create book_author",
            "status": "want_to_read",
            "note": "Test create book_note"
        }
    )

    assert response.status_code == 401
    
    data = response.json()
    assert data["detail"] == "Not authenticated"


async def test_create_book_invalid_data(auth_client: AsyncClient):
    response = await auth_client.post(
        "/books",
        json={
            "title": "",
            "author": "",
            "status": "want_to_read",
            "note": "Test create book_note"
        }
    )

    assert response.status_code == 422


# GET /books
async def test_get_books_empty(auth_client: AsyncClient):
    response = await auth_client.get(
        "/books"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


# GET /books/export
async def test_export_books_success(auth_client: AsyncClient, test_user, create_book_factory):
    await create_book_factory(
        title="first book",
        author="first author"
    )
    await create_book_factory(
        title="second book",
        author="second author"
    )

    response = await auth_client.get(
        "/books/export"
    )

    assert response.status_code == 200

    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    assert "attachment" in response.headers["content-disposition"]
    assert f"books_user_{test_user["id"]}" in response.headers["content-disposition"]

    df = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
    assert len(df) == 2
    assert list(df.columns) == ['Title', 'Author', 'Status', 'Note', 'Created_At', 'Finished_At']
    

# POST /books/import
async def test_import_books_xlsx_success(auth_client: AsyncClient):
    df = pd.DataFrame({
        "title": ["New Book"],
        "author": ["New Author"]
    })
    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    excel_buffer.seek(0)

    response = await auth_client.post(
        "/books/import",
        files={
            "file": (
                "test_import.xlsx", 
                excel_buffer, 
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["len"] == 1


async def test_import_books_csv_success(auth_client: AsyncClient):
    csv_data = "title,author\nBook CSV,Author CSV"
    csv_buffer = io.BytesIO(csv_data.encode("utf-8"))

    response = await auth_client.post(
        "/books/import",
        files={
            "file": (
                "test_import.csv",
                csv_buffer,
                "test/csv"
            )
        }
    )

    assert response.status_code == 200


async def test_import_books_invalid_format(auth_client: AsyncClient):
    bad_buffer = io.BytesIO(b"fake image data")

    response = await auth_client.post(
        "/books/import",
        files={
            "file": (
                "avatar.png",
                bad_buffer,
                "image/png"
            )
        }
    )

    assert response.status_code == 415


# PATCH /books/{book_id}
async def test_update_book_by_owner(auth_client: AsyncClient, create_book_factory):
    book = await create_book_factory()

    response = await auth_client.patch(
        f"/books/{book["id"]}",
        json={
            "title": "New Name book"
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "New Name book"


async def test_update_book_not_owner(
    client: AsyncClient,
    db_session,
    create_book_factory
):
    book = await create_book_factory(title="Original Name")

    raw_password = "anotherpassword123"
    hashed_password = Argon2HashPassword.hash_password(raw_password)

    other_user = User(
        email="hacker_user@booknest.com",
        username="hacker_bob",
        password_hash=hashed_password,
        is_active=True
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    other_user_token = create_access_token(
        data={
            "sub": str(other_user.id)
        }
    )
    headers = {
        "Authorization": f"Bearer {other_user_token}"
    }

    response = await client.patch(
        f"/books/{book["id"]}",
        json={
            "title": "Hacked Title"
        },
        headers=headers
    )

    assert response.status_code == 404

    data = response.json()
    assert data["code"] == "NOT_FOUND"


async def test_update_book_not_found(auth_client: AsyncClient):
    response = await auth_client.patch(
        f"/books/{999}",
        json={
            "title": "Error id book"
        },
    )

    assert response.status_code == 404

    data = response.json()
    assert data["code"] == "NOT_FOUND"


# DELETE /books/{book_id}
async def test_delete_book_by_owner(auth_client: AsyncClient, create_book_factory):
    book = await create_book_factory()
    
    response = await auth_client.delete(
        f"/books/{book["id"]}"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"


async def test_delete_book_not_owner(
    client: AsyncClient,
    db_session,
    create_book_factory
):
    book = await create_book_factory(title="Original Client")

    raw_password = "anotherpassword123"
    hashed_password = Argon2HashPassword.hash_password(raw_password)

    other_user = User(
        email="other_user@booknest.com",
        username="other_user",
        password_hash=hashed_password,
        is_active=True
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    other_user_token = create_access_token(
        data={
            "sub": str(other_user.id)
        }
    )
    headers = {
        "Authorization": f"Bearer {other_user_token}"
    }

    response = await client.delete(
        f"/books/{book["id"]}",
        headers=headers
    )

    assert response.status_code == 404

    data = response.json()
    assert data["code"] == "NOT_FOUND"


async def test_delete_book_not_found(auth_client: AsyncClient):
    response = await auth_client.delete(
        f"/books/{999}"
    )

    assert response.status_code == 404

    data = response.json()
    assert data["code"] == "NOT_FOUND"


# PATCH /books/{book_id}/rating
async def test_update_rating_success(auth_client: AsyncClient, create_book_factory):
    book = await create_book_factory()

    response = await auth_client.patch(
        f"/books/{book["id"]}/rating",
        json={
            "rating": 5
        }
    )
    
    assert response.status_code == 200

    data = response.json()
    assert data["rating"] == 5


async def test_update_rating_out_of_bounds(auth_client: AsyncClient, create_book_factory):
    book = await create_book_factory()

    response = await auth_client.patch(
        f"/books/{book["id"]}/rating",
        json={
            "rating": 15
        }
    )
    
    assert response.status_code == 422