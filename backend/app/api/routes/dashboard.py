"""
Dashboard Summary API Route.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.app.api.routes.upload import PROCESSED_CACHE

router = APIRouter()

@router.get("/dashboard/summary", tags=["Dashboard"])
def get_dashboard_summary():
    df = PROCESSED_CACHE.get("dataframe")
    if df is None:
        return {
            "total_components": 0,
            "pass_count": 0,
            "watch_count": 0,
            "early_reject_count": 0,
            "high_risk_count": 0,
            "total_lots": 0,
            "average_data_quality": 100.0,
            "decision_distribution": {"PASS": 0, "WATCH": 0, "EARLY REJECT": 0},
            "top_anomalous_components": [],
            "status": "NO_DATA_LOADED"
        }

    top_anomalies = (
        df.sort_values(by="risk_score", ascending=False)
        .head(10)[["component_id", "lot_id", "component_type", "decision", "risk_score", "anomaly_score", "predicted_168h", "lot_z_score_0h"]]
        .to_dict(orient="records")
    )

    decision_dist = df["decision"].value_counts().to_dict()

    return {
        "total_components": len(df),
        "pass_count": int(decision_dist.get("PASS", 0)),
        "watch_count": int(decision_dist.get("WATCH", 0)),
        "early_reject_count": int(decision_dist.get("EARLY REJECT", 0)),
        "high_risk_count": int((df["risk_score"] >= 70).sum()),
        "total_lots": int(df["lot_id"].nunique()),
        "average_data_quality": PROCESSED_CACHE.get("reports", {}).get("data_quality_score", 100.0),
        "decision_distribution": decision_dist,
        "top_anomalous_components": top_anomalies,
        "status": "ACTIVE"
    }
