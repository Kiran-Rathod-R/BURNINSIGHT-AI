"""
CSV Upload & Demo Dataset API Route.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import io
import os
from typing import Dict, Any

from backend.app.services.pipeline_service import pipeline_service
from backend.app.database.session import get_db, engine
from backend.app.database.models import ComponentRecord, LotSummary, RiskResult, PredictionResult, AnomalyResult, Base

from scripts.generate_dataset import generate_synthetic_burnin_dataset

router = APIRouter()

# Global in-memory cache for fast interactive frontend queries
PROCESSED_CACHE: Dict[str, Any] = {"dataframe": None, "summary": None, "reports": None}

def seed_db_from_processed(df: pd.DataFrame, db: Session):
    """Populates relational DB tables with processed pipeline results."""
    try:
        # Recreate tables if needed
        Base.metadata.create_all(bind=engine)
        
        # Clear existing data for fresh analysis run
        db.query(RiskResult).delete()
        db.query(AnomalyResult).delete()
        db.query(PredictionResult).delete()
        db.query(ComponentRecord).delete()
        db.query(LotSummary).delete()
        db.commit()

        # Insert Lots
        lot_groups = df.groupby("lot_id")
        for lot_id, group in lot_groups:
            total_comp = len(group)
            pass_c = int((group["decision"] == "PASS").sum())
            watch_c = int((group["decision"] == "WATCH").sum())
            reject_c = int((group["decision"] == "EARLY REJECT").sum())
            health_score = round(((pass_c * 100.0 + watch_c * 60.0) / max(1, total_comp)), 1)
            
            lot_rec = LotSummary(
                lot_id=lot_id,
                total_components=total_comp,
                healthy_count=pass_c,
                watch_count=watch_c,
                early_reject_count=reject_c,
                lot_health_score=health_score,
                mean_leakage_0h=float(group["leakage_current_0h"].mean()),
                std_leakage_0h=float(group["lot_std_0h"].iloc[0])
            )
            db.add(lot_rec)

        # Insert Components
        for _, row in df.iterrows():
            comp = ComponentRecord(
                component_id=str(row["component_id"]),
                lot_id=str(row["lot_id"]),
                component_type=str(row["component_type"]),
                nominal_limit=float(row.get("nominal_limit", 50.0)),
                safe_drift_limit=float(row.get("safe_drift_limit", 25.0))
            )
            db.add(comp)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[!] Warning: DB seeding failed ({e}). System operating in memory-cached mode.")

@router.post("/upload", tags=["Pipeline"])
async def upload_csv_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    processed_df, meta = pipeline_service.process_burnin_dataset(df)
    PROCESSED_CACHE["dataframe"] = processed_df
    PROCESSED_CACHE["summary"] = meta["summary"]
    PROCESSED_CACHE["reports"] = meta["preprocessing_report"]

    seed_db_from_processed(processed_df, db)

    return {
        "message": "Dataset successfully processed through AI pipeline!",
        "filename": file.filename,
        "preprocessing_report": meta["preprocessing_report"],
        "summary": meta["summary"]
    }

@router.post("/demo-data", tags=["Pipeline"])
def trigger_demo_mode(db: Session = Depends(get_db)):
    """Triggers 1-Click Demo Dataset generation and full pipeline execution."""
    df = generate_synthetic_burnin_dataset(num_lots=6, components_per_lot=120)
    processed_df, meta = pipeline_service.process_burnin_dataset(df)

    PROCESSED_CACHE["dataframe"] = processed_df
    PROCESSED_CACHE["summary"] = meta["summary"]
    PROCESSED_CACHE["reports"] = meta["preprocessing_report"]

    seed_db_from_processed(processed_df, db)

    return {
        "message": "Demonstration synthetic dataset generated and analyzed successfully!",
        "filename": "synthetic_burnin_demo.csv",
        "preprocessing_report": meta["preprocessing_report"],
        "summary": meta["summary"]
    }
