# backend/app/core/config.py

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1) Locate the project root (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parents[2]

# 2) Load the .env file into environment variables
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    # You can change these strings directly to suit your local/dev environment
    DATABASE_URL     = "sqlite:///./shakers.db"
    REDIS_URL        = "redis://localhost:6379/0"
    VECTOR_STORE_URL = "http://localhost:8000"
    OPENAI_API_KEY   = ""
settings = Settings()
