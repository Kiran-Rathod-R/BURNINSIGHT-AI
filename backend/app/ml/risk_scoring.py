"""
Risk Scoring Engine for SIH26170.

Calculates a transparent, human-explainable 0-100 Risk Score combining:
- Weighted Anomaly Score (30%)
- Temporal Drift Rate & Acceleration (25%)
- Safety Threshold Violation Overflow (25%)
- Lot-Level Z-Score Severity (20%)
Adjusted by Data Quality Confidence Score.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class RiskScoringEngine:
    def __init__(
        self,
        weight_anomaly: float = 0.30,
        weight_drift: float = 0.25,
        weight_safety: float = 0.25,
        weight_lot_z: float = 0.20
    ):
        self.w_anomaly = weight_anomaly
        self.w_drift = weight_drift
        self.w_safety = weight_safety
        self.w_lot_z = weight_lot_z

    def calculate_risk(self, df: pd.DataFrame, data_quality_score: float = 100.0) -> pd.DataFrame:
        result_df = df.copy()

        def compute_component_risk(row):
            # 1. Anomaly Score Contribution (0-100)
            anomaly_val = row.get("anomaly_score", 0.0)

            # 2. Temporal Drift Contribution
            rate_0_96 = row.get("rate_24_96", 0.0)
            accel = row.get("degrade_acceleration", 0.0)
            drift_score = np.clip((abs(rate_0_96) * 150.0 + max(0, accel) * 200.0), 0.0, 100.0)

            # 3. Safety Violation Contribution
            drift_status = row.get("drift_status", "SAFE")
            overflow_pct = row.get("overflow_percentage", 0.0)
            if drift_status == "UNSAFE":
                safety_score = np.clip(60.0 + overflow_pct * 1.5, 60.0, 100.0)
            else:
                safety_score = np.clip(row.get("predicted_168h", 0.0) / (row.get("configured_safety_limit", 1.0) + 1e-6) * 50.0, 0.0, 50.0)

            # 4. Lot Z-score Contribution
            lot_z = abs(row.get("lot_z_score_0h", 0.0))
            lot_z_score_contrib = np.clip((lot_z / 4.0) * 100.0, 0.0, 100.0)

            # Weighted sum
            raw_risk = (
                self.w_anomaly * anomaly_val +
                self.w_drift * drift_score +
                self.w_safety * safety_score +
                self.w_lot_z * lot_z_score_contrib
            )

            # Confidence penalty adjustment
            confidence = max(0.5, data_quality_score / 100.0)
            final_risk = np.clip(raw_risk, 0.0, 100.0)

            return pd.Series({
                "risk_score": int(round(final_risk)),
                "confidence": round(confidence, 2),
                "risk_contrib_anomaly": round(self.w_anomaly * anomaly_val, 1),
                "risk_contrib_drift": round(self.w_drift * drift_score, 1),
                "risk_contrib_safety": round(self.w_safety * safety_score, 1),
                "risk_contrib_lot_z": round(self.w_lot_z * lot_z_score_contrib, 1)
            })

        risk_cols = result_df.apply(compute_component_risk, axis=1)
        for col in risk_cols.columns:
            result_df[col] = risk_cols[col]

        return result_df
