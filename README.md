# SmartData AI Platform

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

> An end-to-end AI-powered ETL analytics platform — upload raw data, run automated pipelines, generate ML predictions, and export reports. Built with FastAPI, Streamlit, scikit-learn, MySQL, MongoDB, and Docker.

---

## Features

| Feature | Details |
|---|---|
| **Automated ETL Pipeline** | Upload CSV/Excel → auto Extract, Transform (dedup, fill, encode, scale), Load |
| **ML Predictions** | RandomForest customer churn model with confidence scores and probability charts |
| **Interactive Dashboard** | Dark-theme Streamlit app with Plotly bar, line, heatmap, gauge, and pie charts |
| **REST API + Swagger** | FastAPI backend with full interactive docs at `/docs` |
| **JWT Authentication** | Secure register/login with role-based access (user / admin) |
| **Report Generation** | One-click PDF (ReportLab) and CSV export |
| **Dual Database** | MySQL (users, uploads, predictions) + MongoDB (ETL logs, analytics, reports) |
| **Dockerized** | Single `docker-compose up` deploys all 4 services |

---

## Screenshots

> Dashboard Overview — real-time KPIs, ETL activity chart, data health donut, ML metrics

> Analytics Page — bar chart, line trend, correlation heatmap, histogram from uploaded data

> AI Predictions — feature inputs, prediction badge, confidence gauge, class probabilities

> Reports Page — one-click PDF/CSV download with dataset statistics

---

## Architecture

```
Browser
  │
  ▼
Streamlit Dashboard  :8501   (dark-theme, Plotly, JWT session)
  │
  │  HTTP / REST
  ▼
FastAPI Backend  :8000
  │
  ├─ ETL Module        Pandas extract → clean → encode → scale → load
  ├─ ML Module         RandomForest (300 trees, class_weight=balanced)
  ├─ Analytics Service  KPIs, chart data, statistical summary
  ├─ Report Service    ReportLab PDF + pandas CSV
  │
  ├─ MySQL :3306       users · uploaded_files · predictions
  └─ MongoDB :27017    cleaned_data · etl_logs · analytics_logs · reports
```

---

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/yourusername/smartdata-ai.git
cd smartdata-ai

docker-compose up --build
```

| Service | URL |
|---|---|
| Dashboard | http://localhost:8501 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API ReDoc | http://localhost:8000/redoc |

### Local Development

**Requirements:** Python 3.12, MySQL 8, MongoDB 7

```bash
# Clone
git clone https://github.com/yourusername/smartdata-ai.git
cd smartdata-ai

# Backend
pip install -r backend/requirements.txt

# Start MySQL and MongoDB (Docker)
docker run -d --name smartdata_mysql -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=smartdata -p 3306:3306 mysql:8
docker run -d --name smartdata_mongo -p 27017:27017 mongo:7

# Generate sample dataset
python datasets/generate_sample.py

# Train ML model
cd backend
python -m app.ml.train_model

# Start backend
uvicorn app.main:app --reload --port 8000

# Start dashboard (new terminal)
cd dashboard
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## Project Structure

```
smartdata-ai/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # auth, upload, analytics, predict, report
│   │   ├── core/                # config (pydantic-settings), security (JWT+bcrypt), logger
│   │   ├── database/            # SQLAlchemy ORM (MySQL) + PyMongo helpers
│   │   ├── etl/                 # extractor.py → transformer.py → loader.py → pipeline.py
│   │   ├── ml/                  # preprocessing.py, train_model.py, predict.py
│   │   ├── services/            # analytics_service, report_service, dashboard_service
│   │   ├── utils/               # file_handler, validators, helpers
│   │   ├── tests/               # pytest suite (auth, ETL, ML)
│   │   └── main.py              # FastAPI app, CORS, router registration, DB init
│   ├── requirements.txt
│   └── Dockerfile
├── dashboard/
│   ├── app_pages/               # home, upload, analytics, prediction, reports, login
│   ├── components/              # ui_helpers (api_get, api_post, metric_card)
│   ├── streamlit_app.py         # dark CSS, JWT session state, sidebar nav
│   └── Dockerfile
├── datasets/
│   └── generate_sample.py       # synthetic 2,000-row churn dataset
├── docker-compose.yml
├── .env
└── README.md
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | No | Create account |
| POST | `/api/auth/login` | No | Login → JWT token |
| GET | `/api/auth/profile` | Yes | Current user info |
| POST | `/api/upload/csv` | Yes | Upload CSV + trigger ETL |
| POST | `/api/upload/excel` | Yes | Upload Excel + trigger ETL |
| GET | `/api/upload/files` | Yes | List uploaded files |
| GET | `/api/analytics/summary` | Yes | Row/column stats + describe |
| GET | `/api/analytics/charts` | Yes | Chart data (bar, line, heatmap, histogram) |
| GET | `/api/analytics/kpis` | Yes | KPI metrics |
| POST | `/api/predict/` | Yes | Run churn prediction |
| GET | `/api/predict/model/accuracy` | Yes | Model metrics (accuracy, F1, etc.) |
| GET | `/api/report/pdf` | Yes | Download PDF report |
| GET | `/api/report/csv` | Yes | Download cleaned CSV |

Full interactive docs: **http://localhost:8000/docs**

---

## ML Model

- **Algorithm:** Random Forest Classifier (300 estimators, `class_weight=balanced`)
- **Task:** Binary classification — customer churn (Yes / No)
- **Training Data:** 2,000-record synthetic telco-style dataset
- **Features:** tenure, monthly charges, total charges, contract type, internet service, payment method, products, support calls
- **Preprocessing:** label encoding, standard scaling, IQR outlier clipping, stratified train/test split

Retrain with your own data:
```bash
# Replace datasets/churn_dataset.csv, then:
cd backend
python -m app.ml.train_model
```

---

## ETL Pipeline

```
Upload (CSV / Excel)
  └─ Extractor      → pandas DataFrame
  └─ Transformer    → drop duplicates, fill nulls, label-encode categoricals,
                       standard-scale numerics, clip IQR outliers
  └─ Loader         → save cleaned_*.csv to uploads/, log to MongoDB
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(set in .env)* | JWT signing secret |
| `MYSQL_HOST` | `localhost` | MySQL host |
| `MYSQL_PORT` | `3306` | MySQL port |
| `MYSQL_USER` | `root` | MySQL user |
| `MYSQL_PASSWORD` | `password` | MySQL password |
| `MYSQL_DB` | `smartdata` | Database name |
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection URI |
| `MONGO_DB` | `smartdata` | MongoDB database name |
| `UPLOAD_DIR` | `uploads` | Directory for uploaded files |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT expiry |

---

## Running Tests

```bash
cd backend
pytest app/tests/ -v --tb=short
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit + Plotly |
| Machine Learning | scikit-learn, pandas, NumPy |
| Databases | MySQL 8 (SQLAlchemy ORM) + MongoDB 7 (PyMongo) |
| Authentication | JWT (python-jose) + bcrypt |
| PDF Reports | ReportLab |
| Containerization | Docker + Docker Compose |
| Testing | Pytest |

---

## License

MIT License — free for personal and commercial use.
