from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy import select, delete

from app.features.users.models import User
from app.core.generate_jwt import create_access_token

# /users/register
async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/users/register",
        json={
            "email": "new_user@booknest.com",
            "username": "new_user",
            "password": "strongpassword123"
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "new_user@booknest.com"
    assert "id" in data
    assert "password" not in data


async def test_register_duplicate_email(client: AsyncClient, test_user: dict):
    response = await client.post(
        "/users/register",
        json={
            "email": test_user["email"],
            "username": "test_duplicate_email",
            "password": "strongpassword1234"
        }
    )

    assert response.status_code == 409

    data = response.json()
    assert data["code"] == "DUPLICATE_ENTITY"
    assert data["message"] == f"Пользователь с почтой: {test_user["email"]} уже существует."


async def test_register_duplicate_username(client: AsyncClient, test_user: dict):
    response = await client.post(
        "/users/register",
        json={
            "email": "test_duplicate_passwd@booknest.com",
            "username": test_user["username"],
            "password": "strongpassword1234"
        }
    )

    assert response.status_code == 409


async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(
        "/users/register",
        json={
            "email": "test_reg_inval_email",
            "username": "test_reg_inval_email",
            "password": "invalemailpasswd"
        }
    )

    assert response.status_code == 422


async def test_register_short_password(client: AsyncClient):
    response = await client.post(
        "/users/register",
        json={
            "email": "test_reg_short_passwd@booknest.com",
            "username": "test_reg_short_passwd",
            "password": "short"
        }
    )

    assert response.status_code == 422


async def test_register_missing_required_fields(client: AsyncClient):
    response = await client.post(
        "/users/register",
    )

    assert response.status_code == 422


# /users/login
async def test_login_success(client: AsyncClient):
    user_data = {
        "email": "test_login@booknest.com",
        "username": "test_login",
        "password": "testloginpassword"
    }

    await client.post(
        "/users/register",
        json=user_data
    )

    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }

    response = await client.post(
        "/users/login",
        data=login_data
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_password(client: AsyncClient, test_user: dict):
    login_data = {
        "username": test_user["email"],
        "password": "testlogininvalpasswd123"
    }

    response = await client.post(
        "/users/login",
        data=login_data
    )

    assert response.status_code == 400

    data = response.json()
    assert data["code"] == "INCORRECT_DATA"
    assert data["message"] == "Неверная почта или пароль."


async def test_login_user_not_found(client: AsyncClient):
    login_data = {
        "username": "user_not_found@booknest.com",
        "password": "testloginusernotfound123"
    }

    response = await client.post(
        "/users/login",
        data=login_data
    )

    assert response.status_code == 404

    data = response.json()
    assert data["code"] == "NOT_FOUND"
    assert data["message"] == f"Пользователя с email: {login_data["username"]} не существует."


async def test_login_invalid_credentials_format(client: AsyncClient):
    login_data = {
        "username": "user_invalid_credentials_format@booknest.com",
        "password": "testlogininvalcredformat123"
    }

    response = await client.post(
        "/users/login",
        json=login_data
    )

    assert response.status_code == 422


async def test_login_verified_and_not_verified_email_user(db_session, test_user: dict):
    query = select(User).where(User.id == test_user["id"])
    result = await db_session.execute(query)
    user_in_db = result.scalar_one()

    assert user_in_db.is_verified is False

    user_in_db.is_verified = True
    await db_session.commit()

    db_session.expire_all()

    result_check = await db_session.execute(query)
    updated_user = result_check.scalar_one()

    assert updated_user.is_verified is True


# /users/me
async def test_get_me_success(auth_client: AsyncClient, test_user: dict):
    response = await auth_client.get(
        "/users/me"
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]


async def test_get_me_no_token(client: AsyncClient):
    response = await client.get(
        "/users/me"
    )

    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Not authenticated"


async def test_get_me_invalid_token_format(auth_client: AsyncClient):
    auth_client.headers.update({
        "Authorization": "dsadas"
    })

    response = await auth_client.get(
        "/users/me"
    )

    assert response.status_code == 401


async def test_get_me_expired_token(client: AsyncClient, test_user: dict):
    expired_delta = timedelta(minutes=-10)

    expired_token = create_access_token(
        data={
            "sub": test_user["email"]
        },
        expires_delta=expired_delta
    )

    client.headers.update({
        "Authorization": f"Bearer {expired_token}"
    })

    response = await client.get(
        "/users/me"
    )

    assert response.status_code == 401
    assert "detail" in response.json()


async def test_get_me_malformed_signature(client: AsyncClient, test_user: dict):
    valid_token = create_access_token(
        data={
            "sub": test_user["email"]
        }
    )

    malformed_token = valid_token + "xyz_broken"

    client.headers.update({
        "Authorization": f"Bearer {malformed_token}"
    })

    response = await client.get(
        "/users/me"
    )

    assert response.status_code == 401


async def test_get_me_deleted_user(client: AsyncClient, db_session, test_user: dict):
    valid_token = create_access_token(
        data={
            "sub": test_user["email"]
        }
    )

    client.headers.update({
        "Authorization": f"Bearer {valid_token}"
    })

    query = delete(User).where(User.id == test_user["id"])
    await db_session.execute(query)
    await db_session.commit()

    response = await client.get(
        "/users/me"
    )

    assert response.status_code in [401, 404]