from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.core.logger import app_logger
from app.api.routes import auth_routes, upload_routes, analytics_routes, prediction_routes, report_routes
from app.database.mysql_db import init_mysql

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered ETL Analytics Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Register routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload_routes.router, prefix="/api/upload", tags=["File Upload"])
app.include_router(analytics_routes.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(prediction_routes.router, prefix="/api/predict", tags=["ML Predictions"])
app.include_router(report_routes.router, prefix="/api/report", tags=["Reports"])


@app.on_event("startup")
async def startup():
    app_logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        init_mysql()
        app_logger.info("MySQL tables initialized")
    except Exception as e:
        app_logger.warning(f"MySQL init skipped: {e}")


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
