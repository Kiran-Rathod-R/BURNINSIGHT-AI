"""
168-Hour Measurement Prediction Module for SIH26170.

Trains and evaluates 3 regression algorithms:
1. Linear Regression (Baseline)
2. Random Forest Regressor
3. XGBoost Regressor

Selects champion model based on validation metrics (MAE, RMSE, R²).
Strictly prevents data leakage by using only <=96h measurements.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

PREDICTION_INPUT_FEATURES = [
    "leakage_current_0h", "leakage_current_24h", "leakage_current_96h",
    "voltage_0h", "voltage_24h", "voltage_96h",
    "current_0h", "current_24h", "current_96h",
    "drift_0_24", "drift_24_96", "total_drift_0_96",
    "rate_0_24", "rate_24_96", "degrade_acceleration",
    "lot_z_score_0h", "lot_z_score_96h", "dist_from_lot_mean_0h"
]

TARGET_COL = "leakage_current_168h"

class PredictionPipeline:
    def __init__(self):
        self.models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
            "XGBoost": XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.08, random_state=42)
        }
        self.best_model_name = "XGBoost"
        self.best_model = None
        self.metrics = {}
        self.feature_cols = PREDICTION_INPUT_FEATURES
        self.is_trained = False

    def train_and_evaluate(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Splits data into Train (80%) and Test (20%), trains all 3 models,
        evaluates performance metrics, and selects champion model.
        """
        # Filter rows that have target 168h available for training
        train_df = features_df.dropna(subset=[TARGET_COL]).copy()
        
        avail_features = [f for f in PREDICTION_INPUT_FEATURES if f in train_df.columns]
        X = train_df[avail_features].fillna(0.0).values
        y = train_df[TARGET_COL].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        results = {}
        best_r2 = -float("inf")

        for name, model in self.models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            mae = mean_absolute_error(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            r2 = r2_score(y_test, preds)

            results[name] = {
                "mae": round(float(mae), 4),
                "rmse": round(float(rmse), 4),
                "r2": round(float(r2), 4)
            }

            if r2 > best_r2:
                best_r2 = r2
                self.best_model_name = name
                self.best_model = model

        self.metrics = results
        self.feature_cols = avail_features
        self.is_trained = True

        return {
            "best_model": self.best_model_name,
            "metrics": self.metrics,
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        }

    def predict_168h(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates 168h predicted parameter values for all components.
        """
        if not self.is_trained:
            self.train_and_evaluate(features_df)

        avail_features = [f for f in self.feature_cols if f in features_df.columns]
        X = features_df[avail_features].fillna(0.0).values

        predictions = self.best_model.predict(X)
        
        result_df = features_df.copy()
        result_df["predicted_168h"] = np.round(predictions, 4)
        
        # Calculate residual margin if actual 168h is present
        if TARGET_COL in result_df.columns:
            result_df["actual_168h"] = result_df[TARGET_COL]
            result_df["prediction_error"] = np.round(np.abs(result_df["actual_168h"] - result_df["predicted_168h"]), 4)

        return result_df
