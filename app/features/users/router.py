from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.features.users.models import User
from app.features.users.schemas import UserLogin, UserRegister, UserResponse, Token
from app.features.users.repository import UserRepository
from app.features.users.service import UserService


router_users = APIRouter(prefix="/users", tags=["users"])


@router_users.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: UserRegister,
    session: AsyncSession = Depends(get_db)
):
    repository = UserRepository(session)
    service = UserService(repository)
    return await service.register_user(user_in)


@router_users.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db)
):
    repository = UserRepository(session)
    service = UserService(repository)

    user_login_data = UserLogin(
        email=form_data.username,
        password=form_data.password
    )

    token = await service.login_user(user_login_data)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router_users.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def get_user(
    current_user: User = Depends(get_current_user)
):
    return current_user