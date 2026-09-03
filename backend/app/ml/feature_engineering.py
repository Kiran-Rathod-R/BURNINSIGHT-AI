"""
Feature Engineering Module for SIH26170.

Transforms long-format time-series burn-in measurements into component-level
wide tabular features containing:
- Baseline (0h), 24h, 96h, and 168h parameter values
- Absolute & percentage temporal drift (drift_0_24, drift_24_96, etc.)
- Rate of change & degradation acceleration
- Lot-level statistics (lot mean, median, std)
- Lot relative Z-scores (z_score_leakage_0h, z_score_leakage_24h, z_score_leakage_96h)
- Distance from lot mean
- Temperature-adjusted electrical parameters
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def create_component_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot long-format burn-in measurement records into a wide per-component
    feature dataset with full lot-level statistical context and temporal dynamics.
    """
    # 1. Pivot parameter measurements by time (0, 24, 96, 168)
    params = ["leakage_current", "voltage", "current", "propagation_delay", "temperature"]
    available_params = [p for p in params if p in df.columns]

    # Meta info per component
    meta_cols = ["component_id", "lot_id", "component_type"]
    if "nominal_limit" in df.columns:
        meta_cols.append("nominal_limit")
    if "safe_drift_limit" in df.columns:
        meta_cols.append("safe_drift_limit")

    meta_df = df[meta_cols].drop_duplicates(subset=["component_id"]).set_index("component_id")

    # Pivot table per measurement_time_hours
    pivoted = df.pivot(
        index="component_id",
        columns="measurement_time_hours",
        values=available_params
    )

    # Flatten column MultiIndex (e.g. leakage_current_0h, leakage_current_24h)
    pivoted.columns = [f"{param}_{h}h" for param, h in pivoted.columns]

    # Merge metadata
    features_df = meta_df.join(pivoted, how="inner").reset_index()

    # 2. Compute Temporal Features for Primary Parameter (leakage_current)
    # Drift features
    if "leakage_current_0h" in features_df.columns and "leakage_current_24h" in features_df.columns:
        features_df["drift_0_24"] = features_df["leakage_current_24h"] - features_df["leakage_current_0h"]
        features_df["pct_drift_0_24"] = (features_df["drift_0_24"] / (features_df["leakage_current_0h"].abs() + 1e-6)) * 100.0
        features_df["rate_0_24"] = features_df["drift_0_24"] / 24.0

    if "leakage_current_24h" in features_df.columns and "leakage_current_96h" in features_df.columns:
        features_df["drift_24_96"] = features_df["leakage_current_96h"] - features_df["leakage_current_24h"]
        features_df["pct_drift_24_96"] = (features_df["drift_24_96"] / (features_df["leakage_current_24h"].abs() + 1e-6)) * 100.0
        features_df["rate_24_96"] = features_df["drift_24_96"] / 72.0

    if "drift_0_24" in features_df.columns and "drift_24_96" in features_df.columns:
        features_df["total_drift_0_96"] = features_df["leakage_current_96h"] - features_df["leakage_current_0h"]
        features_df["pct_drift_0_96"] = (features_df["total_drift_0_96"] / (features_df["leakage_current_0h"].abs() + 1e-6)) * 100.0
        features_df["degrade_acceleration"] = features_df["rate_24_96"] - features_df["rate_0_24"]

    if "leakage_current_168h" in features_df.columns and "leakage_current_96h" in features_df.columns:
        features_df["drift_96_168"] = features_df["leakage_current_168h"] - features_df["leakage_current_96h"]
        features_df["rate_96_168"] = features_df["drift_96_168"] / 72.0

    # Component-level statistical summary across hours 0, 24, 96
    time_cols = [c for c in ["leakage_current_0h", "leakage_current_24h", "leakage_current_96h"] if c in features_df.columns]
    if time_cols:
        features_df["leakage_mean_0_96"] = features_df[time_cols].mean(axis=1)
        features_df["leakage_max_0_96"] = features_df[time_cols].max(axis=1)
        features_df["leakage_min_0_96"] = features_df[time_cols].min(axis=1)
        features_df["leakage_std_0_96"] = features_df[time_cols].std(axis=1).fillna(0.0)

    # 3. Compute Lot-Level Relative Statistics & Z-Scores
    # This is the CORE SIH innovation!
    lot_stats = features_df.groupby("lot_id")["leakage_current_0h"].agg(
        lot_mean_0h="mean",
        lot_median_0h="median",
        lot_std_0h="std"
    ).reset_index()
    lot_stats["lot_std_0h"] = lot_stats["lot_std_0h"].replace(0, 1e-5) # Prevent divide by zero

    features_df = features_df.merge(lot_stats, on="lot_id", how="left")
    features_df["dist_from_lot_mean_0h"] = features_df["leakage_current_0h"] - features_df["lot_mean_0h"]
    features_df["lot_z_score_0h"] = (features_df["leakage_current_0h"] - features_df["lot_mean_0h"]) / features_df["lot_std_0h"]

    if "leakage_current_96h" in features_df.columns:
        lot_stats_96 = features_df.groupby("lot_id")["leakage_current_96h"].agg(
            lot_mean_96h="mean",
            lot_std_96h="std"
        ).reset_index()
        lot_stats_96["lot_std_96h"] = lot_stats_96["lot_std_96h"].replace(0, 1e-5)
        features_df = features_df.merge(lot_stats_96, on="lot_id", how="left")
        features_df["lot_z_score_96h"] = (features_df["leakage_current_96h"] - features_df["lot_mean_96h"]) / features_df["lot_std_96h"]

    # Thermal adjustment normalization
    if "temperature_24h" in features_df.columns:
        # Standardize leakage to nominal 25°C base thermal coefficient
        temp_delta = (features_df["temperature_24h"] - 25.0).clip(lower=0)
        features_df["temp_adj_leakage_24h"] = features_df["leakage_current_24h"] / (1.0 + 0.002 * temp_delta)

    return features_df
