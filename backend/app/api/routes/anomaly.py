"""
Anomaly Detection API Route.
"""

from fastapi import APIRouter
from backend.app.api.routes.upload import PROCESSED_CACHE

router = APIRouter()

@router.get("/detect-anomalies", tags=["Anomaly Detection"])
def get_anomaly_summary():
    df = PROCESSED_CACHE.get("dataframe")
    if df is None:
        return {"total_components": 0, "anomalous_count": 0, "components": []}

    anomalous = df[df["anomaly_score"] >= 50.0].sort_values(by="anomaly_score", ascending=False)
    
    results = anomalous[["component_id", "lot_id", "component_type", "anomaly_score", "anomaly_status", "rank_in_lot", "lot_z_score_0h"]].to_dict(orient="records")

    return {
        "total_components": len(df),
        "anomalous_count": len(anomalous),
        "components": results
    }
