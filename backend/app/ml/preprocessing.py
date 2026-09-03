"""
Data Preprocessing Module for SIH26170.

Performs:
- Schema validation
- Data type coercion
- Missing value imputation (time-series linear interpolation & group medians)
- Duplicate handling
- Outlier detection (IQR / Z-score bounds)
- Quality confidence score calculation (0-100%)
- Preprocessing report generation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

REQUIRED_COLUMNS = [
    "component_id", "lot_id", "component_type",
    "measurement_time_hours", "leakage_current",
    "voltage", "current", "propagation_delay"
]

NUMERIC_COLUMNS = [
    "leakage_current", "voltage", "current",
    "propagation_delay", "temperature"
]

class PreprocessingReport:
    def __init__(self):
        self.total_rows: int = 0
        self.valid_rows: int = 0
        self.invalid_rows: int = 0
        self.missing_values_count: int = 0
        self.duplicates_removed: int = 0
        self.outliers_detected: int = 0
        self.data_quality_score: float = 100.0
        self.details: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "invalid_rows": self.invalid_rows,
            "missing_values_count": self.missing_values_count,
            "duplicates_removed": self.duplicates_removed,
            "outliers_detected": self.outliers_detected,
            "data_quality_score": round(self.data_quality_score, 2),
            "details": self.details
        }

def validate_csv_schema(df: pd.DataFrame) -> Tuple[bool, str]:
    """Checks if mandatory columns exist in the uploaded dataset."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}"
    return True, "Schema validation successful"

def preprocess_burnin_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, PreprocessingReport]:
    """
    Cleans, imputes, and formats the raw burn-in dataset.
    Generates a detailed PreprocessingReport.
    """
    report = PreprocessingReport()
    report.total_rows = len(df)

    cleaned_df = df.copy()

    # 1. Schema Validation
    is_valid, msg = validate_csv_schema(cleaned_df)
    if not is_valid:
        report.invalid_rows = len(cleaned_df)
        report.data_quality_score = 0.0
        report.details["error"] = msg
        return cleaned_df, report

    # 2. Duplicate Detection (component_id + measurement_time_hours)
    dup_mask = cleaned_df.duplicated(subset=["component_id", "measurement_time_hours"], keep="first")
    report.duplicates_removed = int(dup_mask.sum())
    cleaned_df = cleaned_df[~dup_mask].copy()

    # 3. Numeric Type Coercion
    for col in NUMERIC_COLUMNS:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")

    # 4. Missing Values Detection
    avail_num_cols = [c for c in NUMERIC_COLUMNS if c in cleaned_df.columns]
    missing_count = int(cleaned_df[avail_num_cols].isna().sum().sum())
    report.missing_values_count = missing_count

    # Time-series interpolation per component
    cleaned_df = cleaned_df.sort_values(by=["component_id", "measurement_time_hours"])
    for col in avail_num_cols:
        cleaned_df[col] = cleaned_df.groupby("component_id")[col].transform(
            lambda group: group.interpolate(method="linear").bfill().ffill()
        )
        # Global median fallback for any lingering NaNs (e.g. single measurement component)
        if cleaned_df[col].isna().any():
            cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())


    # 5. Outlier Detection (Statistical 3*IQR bound check per component_type)
    outlier_count = 0
    for comp_type, group in cleaned_df.groupby("component_type"):
        for col in ["leakage_current", "voltage", "current"]:
            q1 = group[col].quantile(0.25)
            q3 = group[col].quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower = q1 - 3 * iqr
                upper = q3 + 3 * iqr
                outliers = group[(group[col] < lower) | (group[col] > upper)]
                outlier_count += len(outliers)

    report.outliers_detected = outlier_count
    report.valid_rows = len(cleaned_df)
    report.invalid_rows = report.total_rows - report.valid_rows

    # Data quality score deduction formula
    deductions = (report.missing_values_count * 1.5 + report.duplicates_removed * 2.0 + report.invalid_rows * 5.0)
    report.data_quality_score = max(30.0, 100.0 - (deductions / max(1, report.total_rows) * 100.0))

    return cleaned_df, report
