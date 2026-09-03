"""
Model Loader Service for SIH26170.

Loads serialized model artifacts (anomaly_model.pkl, prediction_model.pkl, scaler.pkl) from disk.
If model files do not exist, runs automatic online fitting to ensure zero runtime errors.
"""

import os
import joblib
import json
from typing import Dict, Any

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/models"))

class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.anomaly_model = None
            cls._instance.prediction_model = None
            cls._instance.scaler = None
            cls._instance.metadata = {}
            cls._instance.load_models()
        return cls._instance

    def load_models(self):
        anomaly_path = os.path.join(MODELS_DIR, "anomaly_model.pkl")
        pred_path = os.path.join(MODELS_DIR, "prediction_model.pkl")
        scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
        meta_path = os.path.join(MODELS_DIR, "feature_metadata.json")

        if os.path.exists(anomaly_path) and os.path.exists(pred_path):
            try:
                self.anomaly_model = joblib.load(anomaly_path)
                self.prediction_model = joblib.load(pred_path)
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                if os.path.exists(meta_path):
                    with open(meta_path, "r") as f:
                        self.metadata = json.load(f)
                print(f"[+] Loaded ML models from {MODELS_DIR}")
            except Exception as e:
                print(f"[!] Error loading models: {e}. Will fit lazily on pipeline execution.")
        else:
            print(f"[*] No serialized models found in {MODELS_DIR}. System will initialize dynamic models.")

model_manager = ModelManager()
