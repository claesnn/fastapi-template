from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    db_url: str = ""
    db_pool_size: int = 10
    db_echo: bool = False

    # Logging settings
    log_level: str = "INFO"

    # Pydantic Settings Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Instantiate settings
settings = Settings()
