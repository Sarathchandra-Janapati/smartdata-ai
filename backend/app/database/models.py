from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime


# ── Auth schemas ──────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Upload schemas ────────────────────────────────────────────────────────────

class UploadedFileRecord(BaseModel):
    file_name: str
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"
    row_count: Optional[int] = None
    columns: Optional[List[str]] = None


# ── ETL schemas ───────────────────────────────────────────────────────────────

class ETLStatus(BaseModel):
    job_id: str
    status: str          # pending | running | completed | failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    errors: List[str] = []


class ETLLog(BaseModel):
    job_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    message: str


# ── Analytics schemas ─────────────────────────────────────────────────────────

class KPISummary(BaseModel):
    total_records: int
    clean_records: int
    missing_rate: float
    duplicate_rate: float
    numeric_columns: int
    categorical_columns: int


class ChartData(BaseModel):
    chart_type: str
    title: str
    data: Dict[str, Any]


# ── Prediction schemas ────────────────────────────────────────────────────────

class PredictionInput(BaseModel):
    features: Dict[str, Any]


class PredictionResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    prediction: Any
    confidence: Optional[float] = None
    label: Optional[str] = None
    model_version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelMetrics(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    model_type: str
    trained_at: str
