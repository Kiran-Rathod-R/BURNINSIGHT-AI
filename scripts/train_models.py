"""
Model Training & Artifact Serialization Script for SIH26170.

Workflow:
1. Generates synthetic dataset (or loads existing ml/datasets/synthetic_burnin_data.csv)
2. Runs Preprocessing & Feature Engineering
3. Trains Isolation Forest Anomaly Detection Model
4. Trains & Evaluates 168h Prediction Models (Linear Regression, Random Forest, XGBoost)
5. Reports actual performance metrics (MAE, RMSE, R²)
6. Serializes champion models & scalers to ml/models/
"""

import os
import joblib
import json
import pandas as pd
import numpy as np

from backend.app.ml.preprocessing import preprocess_burnin_data
from backend.app.ml.feature_engineering import create_component_features
from backend.app.ml.anomaly_detection import AnomalyDetector
from backend.app.ml.prediction import PredictionPipeline
from scripts.generate_dataset import generate_synthetic_burnin_dataset

def run_model_training_pipeline(dataset_path: str = "ml/datasets/synthetic_burnin_data.csv", models_dir: str = "ml/models"):
    print("=== [SIH26170 Model Training Pipeline] ===")

    # 1. Dataset Check / Generation
    if not os.path.exists(dataset_path):
        print(f"[*] Dataset not found at {dataset_path}. Generating synthetic dataset...")
        df = generate_synthetic_burnin_dataset(output_path=dataset_path)
    else:
        print(f"[*] Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)

    # 2. Preprocessing & Cleaning
    print("[*] Running Data Preprocessing & Validation...")
    cleaned_df, prep_report = preprocess_burnin_data(df)
    print(f"    Data Quality Score: {prep_report.data_quality_score}%")

    # 3. Feature Engineering
    print("[*] Extracting Component Lot-level Features & Temporal Dynamics...")
    features_df = create_component_features(cleaned_df)
    print(f"    Engineered features for {len(features_df)} components.")

    # 4. Train Anomaly Detector (Isolation Forest)
    print("[*] Training Isolation Forest Lot-level Anomaly Detector...")
    anomaly_detector = AnomalyDetector(contamination=0.08)
    anomaly_detector.fit(features_df)
    scored_features = anomaly_detector.predict_scores(features_df)

    # 5. Train 168h Prediction Models (LR vs RF vs XGBoost)
    print("[*] Training & Evaluating 168h Temporal Prediction Models...")
    predictor = PredictionPipeline()
    metrics_summary = predictor.train_and_evaluate(scored_features)

    print("\n--- Model Performance Evaluation Summary ---")
    for model_name, metrics in metrics_summary["metrics"].items():
        print(f"  > {model_name:18s} | MAE: {metrics['mae']:.4f} | RMSE: {metrics['rmse']:.4f} | R²: {metrics['r2']:.4f}")

    print(f"\n[CHAMPION] CHAMPION MODEL SELECTED: {metrics_summary['best_model']}")

    # 6. Serialize Models & Scalers to disk
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(anomaly_detector.iso_forest, os.path.join(models_dir, "anomaly_model.pkl"))
    joblib.dump(anomaly_detector.scaler, os.path.join(models_dir, "scaler.pkl"))
    joblib.dump(predictor.best_model, os.path.join(models_dir, "prediction_model.pkl"))

    metadata = {
        "best_prediction_model": metrics_summary["best_model"],
        "metrics": metrics_summary["metrics"],
        "anomaly_contamination": anomaly_detector.contamination,
        "feature_columns": predictor.feature_cols,
        "trained_timestamp": pd.Timestamp.now().isoformat()
    }

    with open(os.path.join(models_dir, "feature_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"\n[+] Trained models and metadata successfully saved to: {os.path.abspath(models_dir)}")
    return metadata

if __name__ == "__main__":
    run_model_training_pipeline()
