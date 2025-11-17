"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "CantiereTrack API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # Database
    DATABASE_URL: str = "postgresql://cantieretrack:cantieretrack@db:5432/cantieretrack"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days

    # Security
    PASSWORD_MIN_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_DIGIT: bool = True
    REQUIRE_SPECIAL_CHAR: bool = False

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    LOGIN_RATE_LIMIT: str = "5/minute"  # Max 5 login attempts per minute
    REGISTER_RATE_LIMIT: str = "3/minute"  # Max 3 registrations per minute

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://frontend:3000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_secret_key(self) -> None:
        """Validate that SECRET_KEY has been changed in production"""
        insecure_keys = [
            "your-secret-key-change-in-production-min-32-chars-long",
            "change-me",
            "secret",
            "password",
        ]

        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY in insecure_keys or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "CRITICAL: Insecure SECRET_KEY detected in production! "
                    "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )

    @staticmethod
    def generate_secret_key() -> str:
        """Generate a secure random secret key"""
        return secrets.token_urlsafe(32)


settings = Settings()

# Validate configuration on import
if settings.ENVIRONMENT == "production":
    settings.validate_secret_key()
