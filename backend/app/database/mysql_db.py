from sqlalchemy import create_engine, text, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import OperationalError
from datetime import datetime
from app.core.config import settings
from app.core.logger import app_logger
from typing import Generator

DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── ORM Models ────────────────────────────────────────────────────────────────

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)


class UploadedFileORM(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(100), default="pending")
    row_count = Column(Integer, nullable=True)
    uploaded_by = Column(String(255), nullable=True)


class PredictionORM(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_result = Column(String(255))
    confidence = Column(Float, nullable=True)
    input_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255), nullable=True)


# ── DB helpers ────────────────────────────────────────────────────────────────

def init_mysql():
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("MySQL tables created/verified.")
    except OperationalError as e:
        app_logger.warning(f"MySQL init error: {e}")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_username(db: Session, username: str) -> UserORM | None:
    return db.query(UserORM).filter(UserORM.username == username).first()


def get_user_by_email(db: Session, email: str) -> UserORM | None:
    return db.query(UserORM).filter(UserORM.email == email).first()


def create_user(db: Session, username: str, email: str, hashed_password: str, role: str = "user") -> UserORM:
    user = UserORM(username=username, email=email, password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_upload_record(db: Session, file_name: str, row_count: int, uploaded_by: str) -> UploadedFileORM:
    record = UploadedFileORM(file_name=file_name, row_count=row_count, status="processed", uploaded_by=uploaded_by)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def save_prediction(db: Session, result: str, confidence: float, input_data: str, created_by: str) -> PredictionORM:
    pred = PredictionORM(prediction_result=result, confidence=confidence, input_data=input_data, created_by=created_by)
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


def get_all_uploads(db: Session) -> list:
    return db.query(UploadedFileORM).order_by(UploadedFileORM.upload_time.desc()).all()


def get_all_predictions(db: Session) -> list:
    return db.query(PredictionORM).order_by(PredictionORM.created_at.desc()).all()
