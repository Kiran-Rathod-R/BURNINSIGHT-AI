"""
SQLAlchemy ORM Models for SIH26170.

Defines tables:
- ComponentRecord
- MeasurementRecord
- LotSummary
- PredictionResult
- AnomalyResult
- RiskResult
- AnalysisRun
- SystemSettings
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database.session import Base

class ComponentRecord(Base):
    __tablename__ = "components"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)

    component_id = Column(String(50), unique=True, index=True, nullable=False)
    lot_id = Column(String(50), index=True, nullable=False)
    component_type = Column(String(50), nullable=False)
    nominal_limit = Column(Float, default=50.0)
    safe_drift_limit = Column(Float, default=25.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    measurements = relationship("MeasurementRecord", back_populates="component", cascade="all, delete-orphan")
    prediction = relationship("PredictionResult", back_populates="component", uselist=False, cascade="all, delete-orphan")
    anomaly_result = relationship("AnomalyResult", back_populates="component", uselist=False, cascade="all, delete-orphan")
    risk_result = relationship("RiskResult", back_populates="component", uselist=False, cascade="all, delete-orphan")

class MeasurementRecord(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(String(50), ForeignKey("components.component_id"), nullable=False)
    measurement_time_hours = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=True)
    voltage = Column(Float, nullable=True)
    current = Column(Float, nullable=True)
    leakage_current = Column(Float, nullable=False)
    propagation_delay = Column(Float, nullable=True)
    timestamp = Column(String(50), nullable=True)

    component = relationship("ComponentRecord", back_populates="measurements")

class LotSummary(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(String(50), unique=True, index=True, nullable=False)
    total_components = Column(Integer, default=0)
    healthy_count = Column(Integer, default=0)
    watch_count = Column(Integer, default=0)
    early_reject_count = Column(Integer, default=0)
    lot_health_score = Column(Float, default=100.0)
    mean_leakage_0h = Column(Float, default=0.0)
    std_leakage_0h = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class PredictionResult(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(String(50), ForeignKey("components.component_id"), nullable=False)
    predicted_168h = Column(Float, nullable=False)
    actual_168h = Column(Float, nullable=True)
    model_name = Column(String(50), default="XGBoost")
    drift_status = Column(String(20), default="SAFE")
    safety_margin = Column(Float, default=0.0)

    component = relationship("ComponentRecord", back_populates="prediction")

class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(String(50), ForeignKey("components.component_id"), nullable=False)
    anomaly_score = Column(Float, nullable=False)
    anomaly_status = Column(String(30), nullable=False)
    rank_in_lot = Column(Integer, default=1)
    lot_z_score_0h = Column(Float, default=0.0)

    component = relationship("ComponentRecord", back_populates="anomaly_result")

class RiskResult(Base):
    __tablename__ = "risk_results"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(String(50), ForeignKey("components.component_id"), nullable=False)
    risk_score = Column(Integer, nullable=False)
    decision = Column(String(20), nullable=False)
    confidence = Column(Float, default=0.95)
    reasons_json = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    component = relationship("ComponentRecord", back_populates="risk_result")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(50), unique=True, index=True, nullable=False)
    total_processed = Column(Integer, default=0)
    pass_count = Column(Integer, default=0)
    watch_count = Column(Integer, default=0)
    early_reject_count = Column(Integer, default=0)
    data_quality_score = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemSettings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    safety_drift_threshold = Column(Float, default=30.0)
    anomaly_contamination = Column(Float, default=0.08)
    weight_anomaly = Column(Float, default=0.30)
    weight_drift = Column(Float, default=0.25)
    weight_safety = Column(Float, default=0.25)
    weight_lot_z = Column(Float, default=0.20)
    updated_at = Column(DateTime, default=datetime.utcnow)
