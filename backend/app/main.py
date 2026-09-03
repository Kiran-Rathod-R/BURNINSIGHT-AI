"""
FastAPI Main Application Entrypoint for SIH26170.

AI-Driven Anomaly Detection in Component Burn-In & Screening.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.app.config import settings
from backend.app.database.session import engine, Base
from backend.app.api.routes import (
    health, upload, dashboard, components,
    lots, prediction, anomaly, explanations, settings as sys_settings, export
)

# Initialize database schema
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[!] DB Initialization note: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Smart India Hackathon 2026 Solution for Problem Statement SIH26170: AI-Driven Anomaly Detection in Component Burn-In & Screening.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router Modules
app.include_router(health.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(components.router, prefix="/api/v1")
app.include_router(lots.router, prefix="/api/v1")
app.include_router(prediction.router, prefix="/api/v1")
app.include_router(anomaly.router, prefix="/api/v1")
app.include_router(explanations.router, prefix="/api/v1")
app.include_router(sys_settings.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")

@app.get("/")
def root_api():
    return {
        "message": "Welcome to SIH26170 AI Component Burn-In & Screening Engine REST API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
