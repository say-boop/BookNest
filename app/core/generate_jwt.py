from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.core.config import settings


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        str(settings.SECRET_KEY),
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_access_token(
    token: str
) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            str(settings.SECRET_KEY),
            algorithms=settings.ALGORITHM
        )
        return payload
    except JWTError:
        return None