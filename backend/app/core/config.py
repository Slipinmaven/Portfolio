from functools import lru_cache
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Portfolio API"
    app_env: str = "development"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://portfolio:change-me@localhost:5432/portfolio"
    jwt_secret_key: str = "development-only-change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=15, ge=1)
    refresh_token_expire_days: int = Field(default=30, ge=1)
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=10, ge=0)
    db_pool_timeout: int = Field(default=30, ge=1)
    db_pool_recycle: int = Field(default=1800, ge=0)
    db_pool_pre_ping: bool = True
    db_echo: bool = False
    log_level: str = "INFO"
    log_retention_days: int = Field(default=30, ge=1)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

   
    @field_validator("jwt_secret_key")
    @classmethod
    def reject_unsafe_production_secret(cls, value: str, info: Any) -> str:
        if info.data.get("app_env") == "production" and (len(value) < 32 or value == "development-only-change-this-secret"):
            raise ValueError("JWT_SECRET_KEY must be a strong, unique secret in production")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
