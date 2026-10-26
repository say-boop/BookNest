from app.features.users.models import User
from app.features.users.schemas import UserRegister, UserLogin
from app.features.users.repository import UserRepository

from app.core.security import Argon2HashPassword
from app.core.exceptions.user_exp import UserAlreadyExistsError, UserNotFoundError, UserIncorrectData, UserNotVerifiedEmail
from app.core.generate_jwt import create_access_token, verify_access_token


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

        result_get_duplicate_username = await self.repository.get_by_username(user_in.username)

        if result_get_duplicate_username is not None:
            raise UserAlreadyExistsError(
                message=f"Пользователь с таким именем: {user_in.username} уже существует."
            )

        user.password_hash = Argon2HashPassword.hash_password(user_in.password)

        result_user = await self.repository.add_user(user)

        return result_user


    async def login_user(
        self,
        user_login: UserLogin
    ) -> str:
        user = await self.repository.get_by_email(user_login.email)

        if user is None:
            raise UserNotFoundError(
                message=f"Пользователя с email: {user_login.email} не существует."
            )

        check_password = Argon2HashPassword.verify_password(user_login.password, user.password_hash)

        if not check_password:
            raise UserIncorrectData(
                message=f"Неверная почта или пароль."
            )

        if user.is_verified:
            raise UserNotVerifiedEmail(
                message=f"Почта: {user_login.email} не подтверждена."
            )

        token = create_access_token(
            data={"sub": str(user.id)}
        )
        
        return token