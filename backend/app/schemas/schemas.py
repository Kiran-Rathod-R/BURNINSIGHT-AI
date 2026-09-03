"""
Pydantic Schemas for FastAPI REST API endpoints in SIH26170.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PreprocessingReportSchema(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    missing_values_count: int
    duplicates_removed: int
    outliers_detected: int
    data_quality_score: float

class SIHExplanationSchema(BaseModel):
    why: List[str]
    what_changed: List[str]
    what_will_happen: str
    why_unsafe: str

class SHAPFeatureImportanceSchema(BaseModel):
    feature: str
    importance: float
    impact: str

class ComponentDetailSchema(BaseModel):
    component_id: str
    lot_id: str
    component_type: str
    current_status: str
    risk_score: int
    anomaly_score: float
    anomaly_status: str
    confidence: float
    data_quality_score: float
    leakage_0h: float
    leakage_24h: float
    leakage_96h: float
    predicted_168h: float
    actual_168h: Optional[float] = None
    drift_status: str
    configured_safety_limit: float
    lot_z_score_0h: float
    reasons: List[str]
    sih_explanation: Optional[SIHExplanationSchema] = None
    shap_features: Optional[List[SHAPFeatureImportanceSchema]] = None

class LotSummarySchema(BaseModel):
    lot_id: str
    total_components: int
    healthy_count: int
    watch_count: int
    early_reject_count: int
    lot_health_score: float
    mean_leakage_0h: float
    std_leakage_0h: float

class DashboardSummarySchema(BaseModel):
    total_components: int
    pass_count: int
    watch_count: int
    early_reject_count: int
    high_risk_count: int
    total_lots: int
    average_data_quality: float
    risk_distribution: Dict[str, int]
    decision_distribution: Dict[str, int]
    top_anomalous_components: List[ComponentDetailSchema]

class ModelPerformanceMetricsSchema(BaseModel):
    mae: float
    rmse: float
    r2: float

class ModelPerformanceSchema(BaseModel):
    best_prediction_model: str
    models_evaluated: Dict[str, ModelPerformanceMetricsSchema]
    anomaly_algorithm: str
    anomaly_contamination: float
    feature_columns: List[str]

class SettingsUpdateSchema(BaseModel):
    safety_drift_threshold: Optional[float] = Field(default=30.0, ge=1.0, le=500.0)
    anomaly_contamination: Optional[float] = Field(default=0.08, ge=0.01, le=0.30)

class UploadResponseSchema(BaseModel):
    message: str
    filename: str
    preprocessing_report: PreprocessingReportSchema
    summary: DashboardSummarySchema

class HealthCheckSchema(BaseModel):
    status: str
    project: str
    version: str
    database: str
    models_loaded: bool
