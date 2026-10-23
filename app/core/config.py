from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, SecretStr, Field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    POSTGRES_USER: str = "booknest_user"
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str = "booknestdb"
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "127.0.0.1"

    def get_database_url(self) -> str:
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()