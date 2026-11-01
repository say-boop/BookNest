from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, SecretStr, Field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str = "127.0.0.1"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int
    REDIS_PASSWORD: SecretStr
    REDIS_DB: int = 0

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASSWORD: SecretStr

    def get_database_url(self) -> str:
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_redis_url(self) -> str:
        password = self.REDIS_PASSWORD.get_secret_value()
        return f"redis://:{password}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_rabbitmq_url(self) -> str:
        password = self.RABBITMQ_DEFAULT_PASSWORD.get_secret_value()
        return f"amqp://{self.RABBITMQ_DEFAULT_USER}:{password}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()