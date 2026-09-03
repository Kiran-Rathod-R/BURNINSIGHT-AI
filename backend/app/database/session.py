"""
Database Session Management for SIH26170.

Supports SQLAlchemy ORM session factory with SQLite & MySQL fallback handling.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

db_url = settings.DATABASE_URL
connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}

engine = create_engine(db_url, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for API endpoint database session acquisition."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
