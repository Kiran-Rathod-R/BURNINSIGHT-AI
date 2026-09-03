"""
Unit Tests for End-to-End ML Pipeline Modules.
"""

import pandas as pd
import numpy as np
import pytest
from backend.app.ml.feature_engineering import create_component_features
from backend.app.ml.anomaly_detection import AnomalyDetector
from backend.app.ml.prediction import PredictionPipeline
from backend.app.ml.safety_drift import evaluate_safety_drift
from backend.app.ml.risk_scoring import RiskScoringEngine
from backend.app.ml.decision_engine import evaluate_final_decision

def generate_sample_features():
    records = []
    # Create 10 normal components in LOT_A and 1 lot outlier
    for i in range(1, 11):
        comp_id = f"C10{i}"
        leakage_0h = 10.0 + np.random.normal(0, 0.5)
        if comp_id == "C104":
            leakage_0h = 45.0 # Hidden lot outlier! (< nominal_limit 50, but >> lot mean 10)

        
        for h in [0, 24, 96, 168]:
            records.append({
                "component_id": comp_id,
                "lot_id": "LOT_A",
                "component_type": "OPAMP",
                "measurement_time_hours": h,
                "leakage_current": leakage_0h if h == 0 else (leakage_0h * 1.1 if h < 168 else leakage_0h * 1.3),
                "voltage": 15.0,
                "current": 1.7,
                "propagation_delay": 350.0,
                "temperature": 25.0,
                "nominal_limit": 50.0,
                "safe_drift_limit": 25.0
            })
    return pd.DataFrame(records)

def test_full_ml_pipeline_flow():
    raw_df = generate_sample_features()
    
    # 1. Feature Engineering
    features_df = create_component_features(raw_df)
    assert "lot_z_score_0h" in features_df.columns
    assert "drift_0_24" in features_df.columns
    
    # Verify C104 has high lot z-score
    c104_z = features_df[features_df["component_id"] == "C104"]["lot_z_score_0h"].iloc[0]
    assert c104_z > 2.5


    # 2. Anomaly Detection
    detector = AnomalyDetector()
    detector.fit(features_df)
    anom_df = detector.predict_scores(features_df)
    assert "anomaly_score" in anom_df.columns
    
    # 3. 168h Prediction
    predictor = PredictionPipeline()
    predictor.train_and_evaluate(anom_df)
    pred_df = predictor.predict_168h(anom_df)
    assert "predicted_168h" in pred_df.columns

    # 4. Safety Drift Check
    safety_df = evaluate_safety_drift(pred_df)
    assert "drift_status" in safety_df.columns

    # 5. Risk Scoring Engine
    risk_engine = RiskScoringEngine()
    risk_df = risk_engine.calculate_risk(safety_df)
    assert "risk_score" in risk_df.columns

    # 6. Final Decision Engine
    final_df = evaluate_final_decision(risk_df)
    assert "decision" in final_df.columns
    
    c104_decision = final_df[final_df["component_id"] == "C104"]["decision"].iloc[0]
    assert c104_decision in ["EARLY REJECT", "WATCH"]
