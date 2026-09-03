"""
Synthetic Dataset Generator for SIH26170:
AI-Driven Anomaly Detection in Component Burn-In & Screening.

Generates realistic component burn-in data across multiple time points:
0h, 24h, 96h, 168h.

Simulates:
- Normal components
- High-value lot anomalies (within nominal limit but far from lot mean)
- Gradual degradation
- Sudden degradation
- Sensor noise
- Missing values (simulating dropped readings)
- Temperature variations (25°C - 125°C burn-in chamber)

Dataset is explicitly labeled: Synthetic / Demonstration Dataset
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_burnin_dataset(
    num_lots: int = 8,
    components_per_lot: int = 150,
    output_path: str = "ml/datasets/synthetic_burnin_data.csv",
    seed: int = 42
):
    np.random.seed(seed)
    random.seed(seed)

    component_types = {
        "OPAMP_LM741": {
            "base_leakage": 10.0,  # uA
            "leakage_std": 1.2,
            "nominal_limit": 50.0,
            "safe_drift_limit": 25.0,
            "voltage": 15.0,        # V
            "current": 1.7,         # mA
            "prop_delay": 350.0     # ns
        },
        "MICRO_ATMEGA328P": {
            "base_leakage": 5.0,
            "leakage_std": 0.8,
            "nominal_limit": 30.0,
            "safe_drift_limit": 15.0,
            "voltage": 5.0,
            "current": 12.5,
            "prop_delay": 62.5
        },
        "FPGA_XC7A35T": {
            "base_leakage": 18.0,
            "leakage_std": 2.0,
            "nominal_limit": 75.0,
            "safe_drift_limit": 35.0,
            "voltage": 1.0,
            "current": 250.0,
            "prop_delay": 2.4
        },
        "MOSFET_IRFZ44N": {
            "base_leakage": 8.0,
            "leakage_std": 1.0,
            "nominal_limit": 40.0,
            "safe_drift_limit": 20.0,
            "voltage": 60.0,
            "current": 500.0,
            "prop_delay": 45.0
        },
        "ADC_ADS1115": {
            "base_leakage": 3.0,
            "leakage_std": 0.5,
            "nominal_limit": 20.0,
            "safe_drift_limit": 10.0,
            "voltage": 3.3,
            "current": 0.2,
            "prop_delay": 110.0
        }
    }

    hours = [0, 24, 96, 168]
    records = []

    comp_counter = 1000

    for lot_idx in range(1, num_lots + 1):
        lot_id = f"LOT_2026_{lot_idx:02d}"
        comp_type_name = random.choice(list(component_types.keys()))
        specs = component_types[comp_type_name]

        # Lot-specific minor variation
        lot_base_leakage = specs["base_leakage"] + np.random.normal(0, 0.5)

        for _ in range(components_per_lot):
            comp_counter += 1
            component_id = f"C{comp_counter}"

            # Determine component behavior profile
            # 80% Normal, 5% Lot-level anomaly (hidden), 6% Gradual deg, 4% Sudden deg, 3% Noise/Missing, 2% Severe anomaly
            rand_val = random.random()
            if rand_val < 0.78:
                profile = "NORMAL"
            elif rand_val < 0.84:
                profile = "LOT_ANOMALY"        # High static leakage relative to lot, < nominal_limit
            elif rand_val < 0.90:
                profile = "GRADUAL_DEGRADE"    # Deteriorates gradually across 0h -> 168h
            elif rand_val < 0.94:
                profile = "SUDDEN_DEGRADE"     # Spikes after 24h/96h
            elif rand_val < 0.97:
                profile = "SENSOR_NOISE"       # Missing values / noisy
            else:
                profile = "SEVERE_FAILURE"     # Exceeds nominal limit outright

            base_time = datetime(2026, 8, 1, 8, 0, 0) + timedelta(days=random.randint(0, 15))

            # Initial baseline reading at 0h
            if profile == "LOT_ANOMALY":
                # High leakage compared to lot std (e.g. 4.5x lot_std) but below nominal_limit!
                leakage_0h = min(lot_base_leakage + 4.2 * specs["leakage_std"], specs["nominal_limit"] - 3.0)
            elif profile == "SEVERE_FAILURE":
                leakage_0h = specs["nominal_limit"] * np.random.uniform(0.85, 1.25)
            else:
                leakage_0h = max(0.5, lot_base_leakage + np.random.normal(0, specs["leakage_std"]))

            leakage_val = leakage_0h

            for h in hours:
                timestamp = (base_time + timedelta(hours=h)).strftime("%Y-%m-%d %H:%M:%S")
                # Temperature in burn-in chamber increases during 24h-168h
                temp = 25.0 if h == 0 else (125.0 if h in [24, 96] else 85.0)

                # Compute leakage at time h based on profile
                if h == 0:
                    leakage_val = leakage_0h
                elif h == 24:
                    if profile == "GRADUAL_DEGRADE":
                        leakage_val = leakage_0h * np.random.uniform(1.2, 1.4)
                    elif profile == "SUDDEN_DEGRADE":
                        leakage_val = leakage_0h * np.random.uniform(1.05, 1.15)
                    elif profile == "LOT_ANOMALY":
                        leakage_val = leakage_0h + np.random.normal(0.5, 0.3)
                    elif profile == "SEVERE_FAILURE":
                        leakage_val = leakage_0h * 1.3
                    else:
                        leakage_val = leakage_0h + np.random.normal(0.2, 0.2)
                elif h == 96:
                    if profile == "GRADUAL_DEGRADE":
                        leakage_val = leakage_0h * np.random.uniform(1.6, 2.0)
                    elif profile == "SUDDEN_DEGRADE":
                        leakage_val = leakage_0h * np.random.uniform(2.5, 3.8) # Sudden jump!
                    elif profile == "LOT_ANOMALY":
                        leakage_val = leakage_0h + np.random.normal(1.0, 0.4)
                    elif profile == "SEVERE_FAILURE":
                        leakage_val = leakage_0h * 1.8
                    else:
                        leakage_val = leakage_0h + np.random.normal(0.3, 0.3)
                elif h == 168:
                    if profile == "GRADUAL_DEGRADE":
                        leakage_val = leakage_0h * np.random.uniform(2.4, 3.2)
                    elif profile == "SUDDEN_DEGRADE":
                        leakage_val = leakage_0h * np.random.uniform(4.5, 6.0)
                    elif profile == "LOT_ANOMALY":
                        leakage_val = leakage_0h + np.random.normal(1.5, 0.5)
                    elif profile == "SEVERE_FAILURE":
                        leakage_val = leakage_0h * 2.5
                    else:
                        leakage_val = leakage_0h + np.random.normal(0.4, 0.4)

                # Add minor thermal coefficient effect
                temp_factor = 1.0 + (temp - 25.0) * 0.002
                leakage_val = leakage_val * temp_factor

                # Other electrical parameters
                voltage = max(0.1, specs["voltage"] + np.random.normal(0, specs["voltage"] * 0.01))
                current = max(0.01, specs["current"] + (leakage_val / 100.0) + np.random.normal(0, 0.05))
                prop_delay = max(0.1, specs["prop_delay"] + (leakage_val * 0.5) + np.random.normal(0, specs["prop_delay"] * 0.01))

                # Introduce sensor noise / missing value if profile is SENSOR_NOISE
                if profile == "SENSOR_NOISE" and h == 96 and random.random() < 0.6:
                    leakage_val = np.nan
                elif profile == "SENSOR_NOISE" and h == 24 and random.random() < 0.3:
                    voltage = voltage * 2.5 # Noise outlier

                records.append({
                    "component_id": component_id,
                    "lot_id": lot_id,
                    "component_type": comp_type_name,
                    "test_id": f"TEST_{lot_id}_{h}H",
                    "timestamp": timestamp,
                    "temperature": round(temp, 2) if not np.isnan(temp) else np.nan,
                    "voltage": round(voltage, 4) if not np.isnan(voltage) else np.nan,
                    "current": round(current, 4) if not np.isnan(current) else np.nan,
                    "leakage_current": round(leakage_val, 4) if not np.isnan(leakage_val) else np.nan,
                    "propagation_delay": round(prop_delay, 4) if not np.isnan(prop_delay) else np.nan,
                    "measurement_time_hours": h,
                    "nominal_limit": specs["nominal_limit"],
                    "safe_drift_limit": specs["safe_drift_limit"],
                    "synthetic_profile": profile,
                    "dataset_source": "Synthetic / Demonstration Dataset"
                })

    df = pd.DataFrame(records)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[+] Dataset successfully generated! Total rows: {len(df)}, Components: {comp_counter-1000}")
    print(f"    Saved to: {os.path.abspath(output_path)}")
    return df

if __name__ == "__main__":
    generate_synthetic_burnin_dataset()
