import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1) Determine the project root two levels up from this file
BASE_DIR = Path(__file__).resolve().parents[2]

# 2) Load environment variables from the .env file at the project root
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings:
    """
    Load application configuration from environment variables.

    Attributes:
        DATABASE_URL: Database connection string.
        REDIS_URL: Redis cache connection string.
        VECTOR_STORE_URL: URL for the vector store service.
        OPENAI_API_KEY: API key for OpenAI integrations.
    """
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    REDIS_URL: str | None = os.getenv("REDIS_URL")
    VECTOR_STORE_URL: str | None = os.getenv("VECTOR_STORE_URL")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")


# Instantiate settings for application use
settings = Settings()

# Print loaded settings for debugging purposes (remove or disable in production)
print(settings)
