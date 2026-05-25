from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Railway injects DATABASE_URL and REDIS_URL automatically
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", os.getenv("REDIS_PRIVATE_URL", ""))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-railway-variables")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")

    APP_NAME: str = "TenderHub"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
