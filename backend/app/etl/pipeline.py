import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from app.etl.extractor import extract_file
from app.etl.transformer import transform
from app.etl.loader import load_to_mongodb, load_to_csv
from app.database.mongodb import save_etl_log
from app.core.logger import etl_logger
from app.core.config import settings

# In-memory job store (replace with Redis for production)
_jobs: Dict[str, Dict] = {}


def get_job_status(job_id: str) -> Dict:
    return _jobs.get(job_id, {"error": "Job not found"})


def run_pipeline(file_path: str, scale: bool = False) -> Dict[str, Any]:
    job_id = str(uuid.uuid4())
    started_at = datetime.utcnow()

    _jobs[job_id] = {
        "job_id": job_id,
        "status": "running",
        "started_at": started_at.isoformat(),
        "file": Path(file_path).name,
    }

    def _log(level: str, msg: str):
        log_entry = {
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": msg,
        }
        try:
            save_etl_log(log_entry)
        except Exception:
            pass
        getattr(etl_logger, level.lower(), etl_logger.info)(f"[{job_id}] {msg}")

    try:
        _log("info", f"ETL started for {Path(file_path).name}")

        # Extract
        df = extract_file(file_path)
        _log("info", f"Extracted {len(df)} rows, {len(df.columns)} columns")

        # Transform
        df_clean, report = transform(df, scale=scale)
        _log("info", f"Transform complete: {report}")

        # Load
        mongo_count = 0
        try:
            mongo_count = load_to_mongodb(df_clean, job_id)
            _log("info", f"Loaded {mongo_count} records to MongoDB")
        except Exception as e:
            _log("warning", f"MongoDB load skipped: {e}")

        # Save cleaned CSV
        clean_path = str(Path(settings.UPLOAD_DIR) / f"cleaned_{job_id}.csv")
        load_to_csv(df_clean, clean_path)
        _log("info", f"Cleaned CSV saved: {clean_path}")

        completed_at = datetime.utcnow()
        result = {
            "job_id": job_id,
            "status": "completed",
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "original_rows": int(df.shape[0]),
            "cleaned_rows": int(df_clean.shape[0]),
            "columns": list(df_clean.columns),
            "transform_report": {k: str(v) for k, v in report.items()},
            "mongo_records": mongo_count,
            "cleaned_csv": clean_path,
        }

        _jobs[job_id].update(result)
        _log("info", "ETL pipeline completed successfully")
        return result

    except Exception as e:
        error_msg = str(e)
        _log("error", f"ETL failed: {error_msg}")
        _jobs[job_id].update({"status": "failed", "error": error_msg})
        raise
