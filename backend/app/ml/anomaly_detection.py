"""
Anomaly Detection Module for SIH26170.

Implements lot-aware unsupervised anomaly detection:
- Primary: Isolation Forest
- Secondary: Local Outlier Factor (LOF) & One-Class SVM

Converts raw decision function outputs into a calibrated 0-100 Anomaly Score:
  0 - 30 : Normal
 30 - 60 : Slightly Unusual
 60 - 80 : Suspicious
 80 - 100: Highly Anomalous
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.ensemble import IsolationForest

from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

ANOMALY_FEATURE_COLS = [
    "leakage_current_0h", "leakage_current_24h", "leakage_current_96h",
    "drift_0_24", "drift_24_96", "total_drift_0_96", "degrade_acceleration",
    "lot_z_score_0h", "lot_z_score_96h", "dist_from_lot_mean_0h"
]

class AnomalyDetector:
    def __init__(self, contamination: float = 0.08):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.iso_forest = IsolationForest(
            n_estimators=150,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1
        )
        self.oc_svm = OneClassSVM(nu=self.contamination, kernel="rbf", gamma="scale")
        self.feature_cols = ANOMALY_FEATURE_COLS
        self.is_fitted = False

    def prepare_features(self, features_df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """Ensures all feature columns exist and imputes missing columns with median."""
        avail_cols = [c for c in self.feature_cols if c in features_df.columns]
        X_df = features_df[avail_cols].copy()
        
        # Fill any missing values with median
        for c in avail_cols:
            if X_df[c].isna().any():
                X_df[c] = X_df[c].fillna(X_df[c].median())

        return X_df.values, avail_cols

    def fit(self, features_df: pd.DataFrame) -> "AnomalyDetector":
        """Fits Scaler, Isolation Forest, and OneClassSVM on baseline component features."""
        X, avail_cols = self.prepare_features(features_df)
        self.feature_cols = avail_cols
        
        X_scaled = self.scaler.fit_transform(X)
        self.iso_forest.fit(X_scaled)
        self.oc_svm.fit(X_scaled)
        self.is_fitted = True
        return self

    def predict_scores(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates 0-100 scaled anomaly scores and labels.
        """
        if not self.is_fitted:
            self.fit(features_df)

        X, _ = self.prepare_features(features_df)
        X_scaled = self.scaler.transform(X)

        # Isolation Forest decision function (higher is normal, lower is anomalous)
        raw_scores = self.iso_forest.decision_function(X_scaled)

        # Calibrate raw Isolation Forest decision score (-0.3 to +0.2 typical range) into 0-100 Anomaly Score
        # Inverse mapping: low score -> high anomaly
        min_s, max_s = -0.35, 0.25
        normalized = np.clip((max_s - raw_scores) / (max_s - min_s), 0.0, 1.0)
        anomaly_score = normalized * 100.0

        # OneClassSVM score for comparison
        svm_raw = self.oc_svm.decision_function(X_scaled)
        svm_score = np.clip((0.5 - svm_raw) * 50.0, 0.0, 100.0)

        # Rank within Lot calculation
        result_df = features_df.copy()
        result_df["anomaly_score"] = np.round(anomaly_score, 2)
        result_df["svm_anomaly_score"] = np.round(svm_score, 2)

        # Map scores to human interpretation status
        def get_anomaly_status(score: float) -> str:
            if score < 30.0:
                return "NORMAL"
            elif score < 60.0:
                return "SLIGHTLY_UNUSUAL"
            elif score < 80.0:
                return "SUSPICIOUS"
            else:
                return "HIGHLY_ANOMALOUS"

        result_df["anomaly_status"] = result_df["anomaly_score"].apply(get_anomaly_status)

        # Calculate rank within lot (1 = most anomalous in lot)
        result_df["rank_in_lot"] = result_df.groupby("lot_id")["anomaly_score"].rank(ascending=False, method="min").astype(int)

        return result_df
