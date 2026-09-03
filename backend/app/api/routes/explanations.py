"""
Explainable AI (XAI) & SHAP Explanations API Route.
"""

from fastapi import APIRouter, HTTPException
from backend.app.api.routes.upload import PROCESSED_CACHE

router = APIRouter()

@router.get("/explanations/{component_id}", tags=["Explainability"])
def get_component_explanation(component_id: str):
    df = PROCESSED_CACHE.get("dataframe")
    if df is None:
        raise HTTPException(status_code=404, detail="No dataset loaded. Please upload CSV or trigger Demo Mode.")

    match = df[df["component_id"] == component_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Component ID '{component_id}' not found.")

    row = match.iloc[0].to_dict()
    xai_data = row.get("xai_data", {})

    return {
        "component_id": component_id,
        "lot_id": row["lot_id"],
        "decision": row["decision"],
        "risk_score": row["risk_score"],
        "sih_explanation": xai_data.get("sih_explanation", {}),
        "shap_features": xai_data.get("shap_feature_importance", [])
    }
