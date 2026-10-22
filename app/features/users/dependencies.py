from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.generate_jwt import verify_access_token
from app.features.users.schemas import TokenData
from app.features.users.repository import UserRepository
from app.core.database import get_db


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
):
    try:
        repository = UserRepository(session)
        payload = verify_access_token(token)

        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=int(user_id))
            
    except ValueError:
        raise credentials_exception

    user = await repository.get_by_id(token_data.user_id)

    if user is None:
        raise credentials_exception

    return user