from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "SmartData AI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # JWT
    SECRET_KEY: str = "supersecretkey-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DB: str = "smartdata"

    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "smartdata_nosql"

    # File upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = ["csv", "xlsx", "xls"]

    # ML
    MODEL_PATH: str = "backend/app/ml/model.pkl"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8501", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
