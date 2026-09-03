"""
Health Check API Route.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.config import settings

router = APIRouter()

@router.get("/health", tags=["System"])
def get_health_status(db: Session = Depends(get_db)):
    db_status = "Connected"
    try:
        db.execute("SELECT 1")
    except Exception:
        db_status = "Disconnected/Fallback"

    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "database": db_status,
        "db_engine": "MySQL" if settings.USE_MYSQL else "SQLite Fallback",
        "models_loaded": True
    }
