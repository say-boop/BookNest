from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.users.schemas import UserLogin, UserRegister, UserResponse
from app.features.users.repository import UserRepository
from app.features.users.service import UserService


router_users = APIRouter(prefix="/users", tags=["users"])


@router_users.post(
    "",
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