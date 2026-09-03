"""
CSV Export API Route.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from backend.app.api.routes.upload import PROCESSED_CACHE

router = APIRouter()

@router.get("/export/results", tags=["Export"])
def export_processed_csv():
    df = PROCESSED_CACHE.get("dataframe")
    if df is None:
        raise HTTPException(status_code=404, detail="No dataset loaded to export.")

    export_cols = [c for c in df.columns if c != "xai_data"]
    csv_bytes = df[export_cols].to_csv(index=False).encode("utf-8")

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sih26170_burnin_analysis_results.csv"}
    )
