from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    db_url: str = ""
    db_pool_size: int = 10
    db_echo: bool = False

    # Logging settings
    log_level: str = "INFO"

    # CORS settings
    cors_allow_origins: list[str] = ["*"]
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_expose_headers: list[str] = []
    cors_allow_credentials: bool = False
    cors_max_age: int = 600

    # Pydantic Settings Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @field_validator(
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        "cors_expose_headers",
        mode="before",
    )
    @classmethod
    def _split_csv(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


# Instantiate settings
settings = Settings()
