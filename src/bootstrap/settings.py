from typing import Literal

from pydantic import Field,model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: Literal['development','test', 'production'] = 'development'
    database_url: str = 'postgresql+asyncpg://mealdi:mealdi@localhost:5432/mildinet_db'
    sql_echo: bool = False

    s3_endpoint: str = 'http://localhost:9000'
    s3_access_key: str = 'minio'
    s3_secret_key: str = 'minio_password'
    s3_bucket: str = 'media'

    jwt_secret: str = Field(default="development-only-change-me", min_length=24)
    jwt_issuer: str = "mildinet"
    jwt_audience: str = "mildinet-web"
    access_token_ttl_minutes: int = Field(default=15, ge=1, le=1440)
    refresh_token_ttl_days: int = Field(default=14, ge=1, le=90)

    cors_origins: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    cookie_secure: bool = False
    cookie_domain: str | None = None

    max_image_size_mb: int = Field(default=20, ge=1)
    max_video_size_mb: int = Field(default=200, ge=1)
    max_audio_size_mb: int = Field(default=20, ge=1)
    max_document_size_mb: int = Field(default=200, ge=1)

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='MILDINET_',
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def reject_development_secret_in_production(self) -> Settings:
        if (
            self.environment == "production"
            and self.jwt_secret == "development-only-change-me"
        ):
            raise ValueError("JWT_SECRET must be set in production")

        return self