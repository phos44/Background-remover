from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Triumf Background Remover"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_level: str = "INFO"
    max_image_size_mb: int = Field(default=12, ge=1, le=64)
    max_image_pixels: int = Field(default=12_000_000, ge=1_000_000)
    allowed_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    rembg_model: str = "bria-rmbg"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
