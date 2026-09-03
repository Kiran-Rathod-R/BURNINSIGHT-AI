"""
Final Decision Engine Module for SIH26170.

Rule-based decision tree generating:
- PASS
- WATCH
- EARLY REJECT

along with decision confidence and explicit reason codes.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

def evaluate_final_decision(df: pd.DataFrame) -> pd.DataFrame:
    result_df = df.copy()

    def determine_decision(row):
        anomaly_score = row.get("anomaly_score", 0.0)
        drift_status = row.get("drift_status", "SAFE")
        risk_score = row.get("risk_score", 0)
        lot_z = abs(row.get("lot_z_score_0h", 0.0))
        pct_drift = row.get("pct_drift_0_96", 0.0)
        confidence = row.get("confidence", 0.95)

        reasons = []

        # Early Reject conditions
        is_early_reject = False

        if drift_status == "UNSAFE":
            is_early_reject = True
            reasons.append("Predicted 168h value exceeds configured safety limit")

        if anomaly_score >= 70.0:
            is_early_reject = True
            reasons.append("High lot-level anomaly detected by Isolation Forest")

        if lot_z >= 4.0:
            is_early_reject = True
            reasons.append(f"Extreme lot deviation detected ({lot_z:.1f}σ above lot mean)")

        if pct_drift >= 100.0:
            is_early_reject = True
            reasons.append(f"Severe temporal degradation trend (+{pct_drift:.0f}% drift)")

        if is_early_reject:
            decision = "EARLY REJECT"
        else:
            # Watch conditions
            is_watch = False
            if anomaly_score >= 40.0:
                is_watch = True
                reasons.append("Moderate anomaly score flagged")
            if lot_z >= 2.5:
                is_watch = True
                reasons.append(f"Moderate lot Z-score deviation ({lot_z:.1f}σ)")
            if pct_drift >= 40.0:
                is_watch = True
                reasons.append("Noticeable parameter drift trend")
            if risk_score >= 45:
                is_watch = True
                reasons.append(f"Elevated overall risk score ({risk_score}/100)")

            if is_watch:
                decision = "WATCH"
            else:
                decision = "PASS"
                reasons.append("All electrical parameters and drift trends within nominal lot limits")

        return pd.Series({
            "decision": decision,
            "reason_codes": str(reasons),
            "reasons_list": reasons
        })

    decision_cols = result_df.apply(determine_decision, axis=1)
    for col in decision_cols.columns:
        result_df[col] = decision_cols[col]

    return result_df
