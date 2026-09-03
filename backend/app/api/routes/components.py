"""
Components List & Detail API Route.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.api.routes.upload import PROCESSED_CACHE

router = APIRouter()

@router.get("/components", tags=["Components"])
def get_components(
    decision: Optional[str] = Query(None, description="Filter by decision: PASS, WATCH, EARLY REJECT"),
    lot_id: Optional[str] = Query(None, description="Filter by lot_id"),
    search: Optional[str] = Query(None, description="Search component_id"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    df = PROCESSED_CACHE.get("dataframe")
    if df is None:
        return {"total": 0, "page": page, "limit": limit, "components": []}

    filtered = df.copy()

    if decision:
        filtered = filtered[filtered["decision"].str.upper() == decision.upper()]
    if lot_id:
        filtered = filtered[filtered["lot_id"].str.upper() == lot_id.upper()]
    if search:
        filtered = filtered[filtered["component_id"].str.contains(search, case=False)]

    total = len(filtered)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    sliced = filtered.iloc[start_idx:end_idx]

    records = []
    for _, row in sliced.iterrows():
        records.append({
            "component_id": str(row["component_id"]),
            "lot_id": str(row["lot_id"]),
            "component_type": str(row["component_type"]),
            "current_status": str(row["decision"]),
            "risk_score": int(row["risk_score"]),
            "anomaly_score": float(row["anomaly_score"]),
            "predicted_168h": float(row["predicted_168h"]),
            "leakage_0h": float(row.get("leakage_current_0h", 0.0)),
            "leakage_24h": float(row.get("leakage_current_24h", 0.0)),
            "leakage_96h": float(row.get("leakage_current_96h", 0.0)),
            "drift_status": str(row.get("drift_status", "SAFE")),
            "lot_z_score_0h": float(row.get("lot_z_score_0h", 0.0))
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "components": records
    }

@router.get("/components/{component_id}", tags=["Components"])
def get_component_detail(component_id: str):
    df = PROCESSED_CACHE.get("dataframe")
    if df is None:
        raise HTTPException(status_code=404, detail="No dataset loaded. Please upload CSV or trigger Demo Mode.")

    match = df[df["component_id"] == component_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Component ID '{component_id}' not found.")

    row = match.iloc[0].to_dict()
    xai = row.get("xai_data", {})

    return {
        "component_id": str(row["component_id"]),
        "lot_id": str(row["lot_id"]),
        "component_type": str(row["component_type"]),
        "current_status": str(row["decision"]),
        "risk_score": int(row["risk_score"]),
        "anomaly_score": float(row["anomaly_score"]),
        "anomaly_status": str(row["anomaly_status"]),
        "confidence": float(row.get("confidence", 0.95)),
        "data_quality_score": float(PROCESSED_CACHE.get("reports", {}).get("data_quality_score", 100.0)),
        "measurements": {
            "0h": float(row.get("leakage_current_0h", 0.0)),
            "24h": float(row.get("leakage_current_24h", 0.0)),
            "96h": float(row.get("leakage_current_96h", 0.0)),
            "168h_predicted": float(row.get("predicted_168h", 0.0)),
            "168h_actual": float(row["actual_168h"]) if "actual_168h" in row and not pd.isna(row["actual_168h"]) else None
        },
        "drift_status": str(row.get("drift_status", "SAFE")),
        "configured_safety_limit": float(row.get("configured_safety_limit", 30.0)),
        "lot_z_score_0h": float(row.get("lot_z_score_0h", 0.0)),
        "reasons": row.get("reasons_list", []),
        "sih_explanation": xai.get("sih_explanation", {}),
        "shap_features": xai.get("shap_feature_importance", [])
    }
