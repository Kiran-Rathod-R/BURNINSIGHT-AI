"""
System Settings API Route.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.config import settings

router = APIRouter()

class SettingsPayload(BaseModel):
    safety_drift_threshold: float = 30.0
    anomaly_contamination: float = 0.08

CURRENT_SETTINGS = {
    "safety_drift_threshold": settings.SAFETY_DRIFT_THRESHOLD,
    "anomaly_contamination": settings.ANOMALY_CONTAMINATION,
    "weights": {
        "anomaly": settings.WEIGHT_ANOMALY,
        "drift": settings.WEIGHT_DRIFT,
        "safety": settings.WEIGHT_SAFETY,
        "lot_z": settings.WEIGHT_LOT_Z
    }
}

@router.get("/settings", tags=["Settings"])
def get_settings():
    return CURRENT_SETTINGS

@router.post("/settings", tags=["Settings"])
def update_settings(payload: SettingsPayload):
    CURRENT_SETTINGS["safety_drift_threshold"] = payload.safety_drift_threshold
    CURRENT_SETTINGS["anomaly_contamination"] = payload.anomaly_contamination
    return {
        "message": "System threshold configurations updated successfully!",
        "settings": CURRENT_SETTINGS
    }
