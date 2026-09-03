"""
Unit Tests for Preprocessing Module.
"""

import pandas as pd
import numpy as np
import pytest
from backend.app.ml.preprocessing import preprocess_burnin_data, validate_csv_schema

def test_validate_csv_schema():
    valid_df = pd.DataFrame(columns=[
        "component_id", "lot_id", "component_type",
        "measurement_time_hours", "leakage_current",
        "voltage", "current", "propagation_delay"
    ])
    is_valid, msg = validate_csv_schema(valid_df)
    assert is_valid is True

    invalid_df = pd.DataFrame(columns=["component_id", "lot_id"])
    is_valid_inv, msg_inv = validate_csv_schema(invalid_df)
    assert is_valid_inv is False
    assert "Missing required columns" in msg_inv

def test_preprocess_burnin_data():
    raw_data = [
        {"component_id": "C1", "lot_id": "L1", "component_type": "OPAMP", "measurement_time_hours": 0, "leakage_current": 10.0, "voltage": 15.0, "current": 1.7, "propagation_delay": 350.0},
        {"component_id": "C1", "lot_id": "L1", "component_type": "OPAMP", "measurement_time_hours": 24, "leakage_current": np.nan, "voltage": 15.0, "current": 1.7, "propagation_delay": 350.0}, # Missing value to interpolate
        {"component_id": "C1", "lot_id": "L1", "component_type": "OPAMP", "measurement_time_hours": 96, "leakage_current": 14.0, "voltage": 15.0, "current": 1.7, "propagation_delay": 350.0},
        {"component_id": "C1", "lot_id": "L1", "component_type": "OPAMP", "measurement_time_hours": 96, "leakage_current": 14.0, "voltage": 15.0, "current": 1.7, "propagation_delay": 350.0}, # Duplicate row
    ]
    df = pd.DataFrame(raw_data)
    cleaned_df, report = preprocess_burnin_data(df)
    
    assert report.total_rows == 4
    assert report.duplicates_removed == 1
    assert report.missing_values_count == 1
    assert report.valid_rows == 3
    # Check interpolation filled NaN
    assert not cleaned_df["leakage_current"].isna().any()
