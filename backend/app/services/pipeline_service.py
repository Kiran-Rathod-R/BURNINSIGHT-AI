"""
Master End-to-End Pipeline Service for SIH26170.

Orchestrates complete ML pipeline:
1. CSV Preprocessing & Quality Scoring
2. Lot-level Feature Engineering & Z-Score calculation
3. Isolation Forest Anomaly Scoring
4. 168-Hour XGBoost/RF/LinearReg Prediction
5. Configurable Safety Drift Check
6. Transparent 0-100 Risk Scoring Engine
7. SHAP Explainability & natural language AI Decision Explanations
8. Rule-based Decision Engine (PASS / WATCH / EARLY REJECT)
9. Database persistence
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, Any, Tuple, List

from backend.app.ml.preprocessing import preprocess_burnin_data
from backend.app.ml.feature_engineering import create_component_features
from backend.app.ml.anomaly_detection import AnomalyDetector
from backend.app.ml.prediction import PredictionPipeline
from backend.app.ml.safety_drift import evaluate_safety_drift
from backend.app.ml.risk_scoring import RiskScoringEngine
from backend.app.ml.explainability import SHAPExplainer
from backend.app.ml.decision_engine import evaluate_final_decision

class MasterPipelineService:
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.prediction_pipeline = PredictionPipeline()
        self.risk_engine = RiskScoringEngine()
        self.shap_explainer = SHAPExplainer()

    def process_burnin_dataset(
        self,
        df: pd.DataFrame,
        safety_threshold_override: float = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Executes complete 11-stage AI processing pipeline on uploaded/demo dataset.
        """
        # Stage 1: Preprocessing & Cleaning
        cleaned_df, prep_report = preprocess_burnin_data(df)
        
        # Stage 2: Feature Engineering & Lot Statistics
        features_df = create_component_features(cleaned_df)

        # Stage 3: Lot-Aware Anomaly Detection
        self.anomaly_detector.fit(features_df)
        anomaly_df = self.anomaly_detector.predict_scores(features_df)

        # Stage 4: 168-Hour Measurement Prediction
        self.prediction_pipeline.train_and_evaluate(anomaly_df)
        pred_df = self.prediction_pipeline.predict_168h(anomaly_df)

        # Stage 5: Safety Drift Check
        safety_df = evaluate_safety_drift(pred_df, override_threshold=safety_threshold_override)

        # Stage 6: Risk Scoring Engine
        risk_df = self.risk_engine.calculate_risk(safety_df, data_quality_score=prep_report.data_quality_score)

        # Stage 7: Rule Engine & Final Decision
        final_df = evaluate_final_decision(risk_df)

        # Stage 8: Generate XAI & SHAP Explanations
        sih_explanations = []
        for idx, row in final_df.iterrows():
            exp = self.shap_explainer.generate_explanation(row)
            sih_explanations.append(exp)
        
        final_df["xai_data"] = sih_explanations

        # Compute High-level Summary Statistics
        summary = {
            "total_components": len(final_df),
            "pass_count": int((final_df["decision"] == "PASS").sum()),
            "watch_count": int((final_df["decision"] == "WATCH").sum()),
            "early_reject_count": int((final_df["decision"] == "EARLY REJECT").sum()),
            "high_risk_count": int((final_df["risk_score"] >= 70).sum()),
            "total_lots": int(final_df["lot_id"].nunique()),
            "average_data_quality": prep_report.data_quality_score,
            "best_prediction_model": self.prediction_pipeline.best_model_name,
            "prediction_metrics": self.prediction_pipeline.metrics
        }

        return final_df, {
            "preprocessing_report": prep_report.to_dict(),
            "summary": summary
        }

pipeline_service = MasterPipelineService()
