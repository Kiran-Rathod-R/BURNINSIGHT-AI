"""
Database Seeding Script for SIH26170.

Runs dataset generation, executes end-to-end pipeline, and seeds DB tables.
"""

import pandas as pd
from backend.app.services.pipeline_service import pipeline_service
from backend.app.api.routes.upload import seed_db_from_processed
from backend.app.database.session import SessionLocal
from scripts.generate_dataset import generate_synthetic_burnin_dataset

def seed_db():
    print("[*] Generating synthetic dataset...")
    df = generate_synthetic_burnin_dataset(num_lots=8, components_per_lot=150)
    
    print("[*] Running AI Pipeline Analysis...")
    processed_df, meta = pipeline_service.process_burnin_dataset(df)
    
    print("[*] Seeding database tables...")
    db = SessionLocal()
    try:
        seed_db_from_processed(processed_df, db)
        print("[+] Database successfully seeded!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
