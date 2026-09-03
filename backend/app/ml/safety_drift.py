"""
Safety Drift Check Module for SIH26170.

Compares predicted 168h parameter values against configurable component safety limits.
Calculates safety status (SAFE vs UNSAFE), overflow margins, and mathematical step-by-step trace.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

DEFAULT_SAFETY_DRIFT_THRESHOLD = 30.0 # uA default limit if unspecified

def evaluate_safety_drift(
    features_df: pd.DataFrame,
    override_threshold: float = None
) -> pd.DataFrame:
    """
    Evaluates whether predicted 168h leakage value breaches configured safety limits.
    """
    result_df = features_df.copy()

    def check_row(row):
        pred_168h = row.get("predicted_168h", 0.0)
        # Use row specific safe_drift_limit or nominal_limit if available, else default override
        if override_threshold is not None:
            safe_limit = override_threshold
        elif "safe_drift_limit" in row and not pd.isna(row["safe_drift_limit"]):
            safe_limit = row["safe_drift_limit"]
        elif "nominal_limit" in row and not pd.isna(row["nominal_limit"]):
            safe_limit = row["nominal_limit"] * 0.5
        else:
            safe_limit = DEFAULT_SAFETY_DRIFT_THRESHOLD

        margin = safe_limit - pred_168h
        is_safe = pred_168h <= safe_limit
        drift_status = "SAFE" if is_safe else "UNSAFE"
        
        # Percentage overflow margin
        overflow_pct = 0.0
        if not is_safe:
            overflow_pct = round(((pred_168h - safe_limit) / safe_limit) * 100.0, 2)

        math_trace = f"Predicted 168h ({pred_168h:.2f} µA) vs Safety Threshold ({safe_limit:.2f} µA) -> Margin = {margin:.2f} µA"

        return pd.Series({
            "configured_safety_limit": round(safe_limit, 2),
            "safety_margin": round(margin, 2),
            "drift_status": drift_status,
            "overflow_percentage": overflow_pct,
            "safety_math_trace": math_trace
        })

    eval_cols = result_df.apply(check_row, axis=1)
    for col in eval_cols.columns:
        result_df[col] = eval_cols[col]

    return result_df
