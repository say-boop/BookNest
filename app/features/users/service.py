from app.features.users.models import User
from app.features.users.schemas import UserRegister, UserLogin
from app.features.users.repository import UserRepository

from app.core.security import Argon2HashPassword
from app.core.exceptions.user_exp import UserAlreadyExistsError


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository


    async def register_user(
        self,
        user_in: UserRegister
    ) -> User:
        user_data = user_in.model_dump(exclude={"password"})
        user = User(**user_data)
        
        result_get_user_repo = await self.repository.get_by_email(user_in.email)

        if result_get_user_repo is not None:
            raise UserAlreadyExistsError(
                message=f"Пользователь с почтой: {user_in.email} уже существует."
            )

        user.password_hash = Argon2HashPassword.hash_password(user_in.password)

        result_user = await self.repository.add_user(user)

        return result_user