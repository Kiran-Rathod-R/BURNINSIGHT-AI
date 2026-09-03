"""
Lot Analysis API Routes.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.app.api.routes.upload import PROCESSED_CACHE

router = APIRouter()

@router.get("/lots", tags=["Lot Analysis"])
def get_lots():
    df = PROCESSED_CACHE.get("dataframe")
    if df is None:
        return {"lots": []}

    lots_data = []
    for lot_id, group in df.groupby("lot_id"):
        total = len(group)
        pass_c = int((group["decision"] == "PASS").sum())
        watch_c = int((group["decision"] == "WATCH").sum())
        reject_c = int((group["decision"] == "EARLY REJECT").sum())
        health_score = round(((pass_c * 100.0 + watch_c * 60.0) / max(1, total)), 1)

        lots_data.append({
            "lot_id": str(lot_id),
            "total_components": total,
            "healthy_count": pass_c,
            "watch_count": watch_c,
            "early_reject_count": reject_c,
            "lot_health_score": health_score,
            "mean_leakage_0h": round(float(group["leakage_current_0h"].mean()), 2),
            "std_leakage_0h": round(float(group["lot_std_0h"].iloc[0]), 2),
            "component_type": str(group["component_type"].iloc[0])
        })

    return {"lots": lots_data}

@router.get("/lots/{lot_id}", tags=["Lot Analysis"])
def get_lot_detail(lot_id: str):
    df = PROCESSED_CACHE.get("dataframe")
    if df is None:
        raise HTTPException(status_code=404, detail="No dataset loaded.")

    match = df[df["lot_id"] == lot_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Lot ID '{lot_id}' not found.")

    total = len(match)
    pass_c = int((match["decision"] == "PASS").sum())
    watch_c = int((match["decision"] == "WATCH").sum())
    reject_c = int((match["decision"] == "EARLY REJECT").sum())
    health_score = round(((pass_c * 100.0 + watch_c * 60.0) / max(1, total)), 1)

    top_suspicious = match.sort_values(by="risk_score", ascending=False).head(5)[
        ["component_id", "decision", "risk_score", "anomaly_score", "predicted_168h", "lot_z_score_0h"]
    ].to_dict(orient="records")

    return {
        "lot_id": lot_id,
        "total_components": total,
        "healthy_count": pass_c,
        "watch_count": watch_c,
        "early_reject_count": reject_c,
        "lot_health_score": health_score,
        "mean_leakage_0h": round(float(match["leakage_current_0h"].mean()), 2),
        "median_leakage_0h": round(float(match["leakage_current_0h"].median()), 2),
        "std_leakage_0h": round(float(match["lot_std_0h"].iloc[0]), 2),
        "top_suspicious_components": top_suspicious
    }
