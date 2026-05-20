from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "KOSH Saving API"
    environment: str = "development"

    secret_key: str = "change-this-secret-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7

    database_url: str = "sqlite:///./coop.db"
    cors_origins: str = "http://localhost:3000"

    auto_create_tables: bool = True

    upload_dir: str = "uploads"
    public_upload_base_url: str = "http://localhost:8000/uploads"
    monthly_saving_amount: int = 1000

    

    google_client_id: str | None = None

    google_admin_emails: str = ""

    google_enabled: bool = False
    google_sheet_id: str | None = None
    google_service_account_file: str | None = None
    google_service_account_json: str | None = None
    google_drive_folder_id: str | None = None
    google_drive_public_links: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    
    @property
    def google_admin_email_list(self) -> list[str]:
        return [
            email.strip().lower()
            for email in self.google_admin_emails.split(",")
            if email.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()