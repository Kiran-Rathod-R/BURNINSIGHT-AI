"""
Application Configuration for SIH26170.

Manages environment variables, database connections (MySQL with SQLite fallback),
ML threshold configurations, and CORS origins.
"""

import os

class Settings:
    PROJECT_NAME: str = "BURNINSIGHT AI: Component Burn-In Anomaly & 168h Prediction Engine"
    API_V1_STR: str = "/api/v1"

    
    # Database Settings (MySQL primary, SQLite fallback)
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "sih_burnin")

    USE_MYSQL: bool = os.getenv("USE_MYSQL", "false").lower() == "true"

    @property
    def DATABASE_URL(self) -> str:
        if self.USE_MYSQL:
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        else:
            # Dual DB Mode: Automatic lightweight SQLite fallback
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sih_burnin.db"))
            return f"sqlite:///{db_path}"

    # Default ML Configurable Thresholds
    SAFETY_DRIFT_THRESHOLD: float = float(os.getenv("SAFETY_DRIFT_THRESHOLD", "30.0"))
    ANOMALY_CONTAMINATION: float = float(os.getenv("ANOMALY_CONTAMINATION", "0.08"))
    WEIGHT_ANOMALY: float = 0.30
    WEIGHT_DRIFT: float = 0.25
    WEIGHT_SAFETY: float = 0.25
    WEIGHT_LOT_Z: float = 0.20

settings = Settings()

