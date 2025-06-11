from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Print the database URL on startup for debugging (remove in production)
print("▶ DATABASE_URL =", settings.DATABASE_URL)

# Prepare database connection URL and SQLite-specific args
database_url = str(settings.DATABASE_URL)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

# Create the SQLAlchemy engine with pooling and future compatibility
engine = create_engine(
    database_url,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

# Configure the session factory and base class for models
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_db():
    """
    Yield a database session and ensure it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
