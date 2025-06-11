# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings


print("▶ DATABASE_URL =", settings.DATABASE_URL)  # <— add this
database_url = str(settings.DATABASE_URL)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(
    database_url,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
