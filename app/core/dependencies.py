from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.generate_jwt import verify_access_token
from app.features.users.models import User
from app.features.users.repository import UserRepository
from app.features.users.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Не удалось валидировать учётные данные.",
    headers={
        "WWW-Authenticate": "Bearer"
    },
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> User:
    try:
        repository = UserRepository(session)
        payload = verify_access_token(token)

        if payload is None:
            raise credentials_exception

        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        TokenData(user_id=int(user_id))

    except ValueError:
        raise credentials_exception from None

    user = await repository.get_by_id(int(user_id))

    if user is None:
        raise credentials_exception

    return user
