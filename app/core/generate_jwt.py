from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        str(settings.SECRET_KEY),
        algorithm=settings.ALGORITHM
    )

    return str(encoded_jwt)


def verify_access_token(
    token: str
) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            str(settings.SECRET_KEY),
            algorithms=settings.ALGORITHM
        )
        return dict(payload)
    except JWTError:
        return None
