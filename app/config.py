from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings as PydanticSettings
from pydantic_settings import SettingsConfigDict

from app.core.enums import AppEnvEnum
from app.core.logging import Logger


class BaseSettings(PydanticSettings):
    model_config = SettingsConfigDict(extra="allow", env_file=".env", env_file_encoding="utf-8")


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_prefix="DATABASE_")

    host: str = "localhost"
    user: str = "fastapi-template"
    password: str = "fastapi-template-password"
    port: int = 5432
    name: str = "fastapi-template"

    pool_size: int = 20
    max_overflow: int = 15

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.name}"


class CORSSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_prefix="CORS_")

    origins: list[str] = ["*"]
    headers: list[str] = ["*"]
    methods: list[str] = ["*"]
    allow_credentials: bool = True


class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    cors: CORSSettings = CORSSettings()

    environment: AppEnvEnum = AppEnvEnum.PRODUCTION
    log_level: Literal["INFO", "DEBUG", "WARN", "ERROR"] = "INFO"
    log_json_format: bool = False

    docs_url: str = "/"

    @property
    def title(self) -> str:
        return "FastAPI Template"

    @property
    def debug(self) -> bool:
        """
        Flag to check if the environment is debug or not.

        :return: Boolean indicating if the environment is debug or not.
        """
        return self.environment in [AppEnvEnum.LOCAL, AppEnvEnum.TEST]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


config: Settings = get_settings()
log = Logger(json_logs=config.log_json_format, log_level=config.log_level).setup_logging()
