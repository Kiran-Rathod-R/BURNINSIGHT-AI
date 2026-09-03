# BURNINSIGHT AI: AI-Driven Anomaly Detection in Component Burn-In & Screening


[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026-blue.svg)](https://sih.gov.in)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-cyan.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-emerald.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/Frontend-React%2019-indigo.svg)](https://react.dev/)
[![ML Models](https://img.shields.io/badge/ML-IsolationForest%20%7C%20XGBoost-orange.svg)](https://xgboost.readthedocs.io/)

> **Problem Statement SIH26170**: AI-Driven Anomaly Detection in Component Burn-In & Screening  
> **Core Innovation**: Lot-relative statistical anomaly detection (flagging hidden anomalies operating within nominal safety limits), temporal degradation prediction at 168 hours ($\le 96\text{h}$ measurements), configurable safety drift checks, transparent 0–100 composite risk scoring, and SHAP-based Explainable AI (XAI) with natural language presentation explanations.

---

## 1. Executive Summary & Paradigm Shift

In high-reliability electronic component screening (e.g. space/defense applications), components undergo thermal burn-in at specified time intervals ($0\text{h}$, $24\text{h}$, $96\text{h}$, $168\text{h}$).

### Traditional Approach vs. SIH26170 Innovation

```
TRADITIONAL SCREENING:
   "Is the measurement below the fixed maximum safety limit?"
   Example: Limit = 50 µA. Leakage = 45 µA -> [ PASS ] (Misses hidden defect!)

SIH26170 AI SOLUTION:
   "Is this component behaving abnormally compared with its manufacturing lot,
    is its temporal trajectory deteriorating, and will it exceed safe limits at 168 hours?"
   Example: Lot Mean = 10 µA (std = 1.5 µA). Leakage = 45 µA -> Z-score = +23.3σ -> [ EARLY REJECT ]
```

---

## 2. System Architecture & Data Flow

```
+-------------------------------------------------------------------------+
|                  Uploaded CSV / Synthetic Dataset                        |
|        (0h, 24h, 96h, 168h Time-Series Electrical Measurements)         |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                    Stage 1: Preprocessing & Data Validation             |
|          (Schema validation, missing interpolation, quality score)       |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|              Stage 2: Lot-Relative Feature Engineering                   |
|     (Lot Mean, Median, Std, Z-Score, 0-24h & 24-96h Temporal Drift)      |
+-------------------------------------------------------------------------+
                 │                                        │
                 ▼                                        ▼
+---------------------------------+      +---------------------------------+
| Stage 3: Anomaly Detection      |      | Stage 4: 168h Prediction Model  |
| (Isolation Forest, LOF, OC-SVM) |      | (XGBoost / RF / LinearReg)      |
| 0-100 Anomaly Score             |      | Predicts 168h Leakage (<=96h)   |
+---------------------------------+      +---------------------------------+
                 │                                        │
                 └──────────────────┬─────────────────────┘
                                    ▼
+-------------------------------------------------------------------------+
|                 Stage 5: Configurable Safety Drift Check                |
|           (Compare Predicted 168h vs Safety Threshold Margin)           |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                  Stage 6: Transparent 0-100 Risk Scoring                |
|    Risk = 30% Anomaly + 25% Drift + 25% Safety Margin + 20% Lot Z-Score|
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|             Stage 7: Explainable AI & Rule Decision Engine              |
|        SHAP Attributions & 4-Part "Why Flagged?" Explanations           |
|                     [ PASS / WATCH / EARLY REJECT ]                     |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|           FastAPI REST APIs + SQLite / MySQL Database Storage            |
|                  React Aerospace-Grade Dark Dashboard                   |
+-------------------------------------------------------------------------+
```

---

## 3. Technology Stack

- **Machine Learning & Data Science**: Python 3.11+, Pandas, NumPy, Scikit-learn, XGBoost, SHAP, SciPy, Joblib
- **Backend API**: FastAPI, Pydantic v2, Uvicorn, SQLAlchemy ORM
- **Database**: Dual-Mode Support — Production MySQL 8.0 with automatic SQLite fallback
- **Frontend**: React 19, Vite, Tailwind CSS, Lucide Icons, Recharts
- **Deployment**: Docker, Docker Compose

---

## 4. Key Features & Modules

1. **Lot-Aware Anomaly Detection**:
   - Primary model: **Isolation Forest**.
   - Computes Z-scores relative to manufacturing batch lots ($Z = \frac{x - \mu_{\text{lot}}}{\sigma_{\text{lot}}}$).
   - Calibrates decision scores into a human-friendly 0–100 anomaly index.
2. **168-Hour Predictive Analytics**:
   - Supervised regression models (**Linear Regression**, **Random Forest**, **XGBoost**).
   - Evaluated on test validation splits via MAE, RMSE, and $R^2$.
   - **Zero Data Leakage**: Models predict $168\text{h}$ values using strictly $\le 96\text{h}$ measurements.
3. **Transparent Risk Engine**:
   - Composite 0–100 Risk Score combining weighted inputs:
     $$\text{Risk Score} = 0.30 \cdot \text{Anomaly} + 0.25 \cdot \text{Drift} + 0.25 \cdot \text{Safety} + 0.20 \cdot Z_{\text{lot}}$$
4. **Judge-Friendly Explainable AI (XAI)**:
   - SHAP feature importance attributions.
   - 4-Part SIH Presentation Explanation:
     - **WHY FLAGGED?**: Lot deviation breakdown.
     - **WHAT CHANGED?**: Temporal drift acceleration between test intervals.
     - **WHAT WILL HAPPEN?**: AI model $168\text{h}$ projection.
     - **WHY UNSAFE?**: Safety threshold violation margin.
5. **1-Click SIH Presentation Demo Mode**:
   - Generates realistic synthetic screening datasets containing normal components, subtle lot outliers, gradual degradation, sudden degradation, sensor noise, and missing values.

---

## 5. Directory Structure

```
sih26170/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI main application
│   │   ├── config.py                   # Environment & threshold config
│   │   ├── api/routes/
│   │   │   ├── upload.py               # CSV upload & Demo mode trigger
│   │   │   ├── dashboard.py            # Summary KPIs & distributions
│   │   │   ├── components.py           # Component search & detail
│   │   │   ├── lots.py                 # Lot stats & lot health index
│   │   │   ├── prediction.py           # ML performance metrics
│   │   │   ├── anomaly.py              # Isolation Forest scores
│   │   │   ├── explanations.py         # SHAP & natural language XAI
│   │   │   ├── settings.py             # Threshold configuration
│   │   │   ├── health.py               # System health endpoint
│   │   │   └── export.py               # Results CSV exporter
│   │   ├── database/
│   │   │   ├── session.py              # SQLAlchemy engine
│   │   │   └── models.py               # ORM database models
│   │   ├── ml/
│   │   │   ├── preprocessing.py        # Schema validation & cleaning
│   │   │   ├── feature_engineering.py  # Lot Z-scores & temporal drift
│   │   │   ├── anomaly_detection.py    # Isolation Forest & LOF
│   │   │   ├── prediction.py           # XGBoost/RF/LR prediction
│   │   │   ├── safety_drift.py         # Safety threshold checker
│   │   │   ├── risk_scoring.py         # 0-100 Risk engine
│   │   │   ├── explainability.py       # SHAP attributions & XAI
│   │   │   └── decision_engine.py      # PASS / WATCH / EARLY REJECT
│   │   └── schemas/
│   │       └── schemas.py              # Pydantic data contracts
│   ├── tests/
│   │   ├── test_preprocessing.py
│   │   └── test_ml_pipeline.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/                 # Header & Sidebar navigation
│   │   ├── pages/                      # 10 React Dashboard pages
│   │   ├── services/api.js             # Axios REST client
│   │   ├── App.jsx                     # Root application wrapper
│   │   └── index.css                   # Industrial dark theme
│   ├── package.json
│   └── Dockerfile
│
├── ml/
│   ├── datasets/                       # Synthetic burn-in datasets
│   └── models/                         # Serialized trained artifacts (.pkl)
│
├── scripts/
│   ├── generate_dataset.py             # Realistic synthetic data generator
│   ├── train_models.py                 # Model training pipeline
│   └── seed_database.py                # Database seeder
│
├── docker-compose.yml                  # Docker deployment manifest
├── .env.example                        # Environment variables template
└── README.md                           # Documentation
```

---

## 6. Installation & Quick Start

### Quick Run (Local Environment)

1. **Clone & Setup Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate

   pip install -r backend/requirements.txt
   ```

2. **Generate Synthetic Data & Train Models**:
   ```bash
   python scripts/generate_dataset.py
   python scripts/train_models.py
   ```

3. **Start FastAPI Backend Server**:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   API interactive documentation available at: `http://localhost:8000/docs`

4. **Start React Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open dashboard at: `http://localhost:5173`

---

## 7. Docker Deployment

Launch full production stack (MySQL + FastAPI Backend + React Frontend) using Docker Compose:

```bash
docker-compose up --build
```

- **React Dashboard**: `http://localhost:5173`
- **FastAPI REST API**: `http://localhost:8000`
- **MySQL Database**: `localhost:3306`

---

## 8. SIH Presentation Guide & Demo Workflow

1. Open `http://localhost:5173`.
2. Click **1-Click SIH Demo Mode** in the top header.
3. Observe the live preprocessing report, lot Z-scores, and decision breakdown.
4. Navigate to **Component Analysis**, select component `C104` (or any EARLY REJECT component).
5. Highlight the **AI Decision Explanation** card to demonstrate the 4 key questions to judges:
   - *Why Flagged?*
   - *What Changed?*
   - *What Will Happen?*
   - *Why Unsafe?*
6. Show the **Time-Series Projection Graph** displaying measured points ($0\text{h}$, $24\text{h}$, $96\text{h}$), predicted $168\text{h}$ value, and the safety threshold boundary line.
