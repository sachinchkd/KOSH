from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "COOP Saving API"
    environment: str = "development"
    secret_key: str = "change-this-secret-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7

    database_url: str = "sqlite:///./coop.db"
    cors_origins: list[str] = ["http://localhost:3000"]
    auto_create_tables: bool = True

    upload_dir: str = "uploads"
    public_upload_base_url: str = "http://localhost:8000/uploads"
    monthly_saving_amount: int = 1000

    admin_email: str = "admin@coop.local"
    admin_password: str = "admin12345"

    google_enabled: bool = False
    google_sheet_id: str | None = None
    google_service_account_file: str | None = None
    google_service_account_json: str | None = None
    google_drive_folder_id: str | None = None
    google_drive_public_links: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
