from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.features.users.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_user(
        self,
        user: User
    ) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user


    async def get_by_email(
        self,
        email: str
    ) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        existing_user = result.scalar_one_or_none()

        return existing_user


    async def get_by_id(
        self,
        user_id: int
    ) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        existing_user = result.scalar_one_or_none()

        return existing_user

    async def get_by_username(
        self,
        username: str
    ) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        existing_user = result.scalar_one_or_none()

        return existing_user