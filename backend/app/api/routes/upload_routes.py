from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.mysql_db import get_db, save_upload_record
from app.utils.file_handler import save_upload, list_uploads
from app.etl.pipeline import run_pipeline, get_job_status
from app.core.logger import api_logger

router = APIRouter()


@router.post("/csv")
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    file_path = save_upload(file)
    api_logger.info(f"CSV uploaded by {current_user['username']}: {file.filename}")

    # Run ETL asynchronously
    background_tasks.add_task(_run_etl_task, file_path, db, current_user["username"])

    return {"message": "File uploaded. ETL started.", "file": file.filename, "path": file_path}


@router.post("/excel")
async def upload_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    file_path = save_upload(file)
    api_logger.info(f"Excel uploaded by {current_user['username']}: {file.filename}")
    background_tasks.add_task(_run_etl_task, file_path, db, current_user["username"])
    return {"message": "File uploaded. ETL started.", "file": file.filename, "path": file_path}


def _run_etl_task(file_path: str, db: Session, username: str):
    try:
        result = run_pipeline(file_path)
        save_upload_record(db, file_path.split("/")[-1], result["cleaned_rows"], username)
    except Exception as e:
        api_logger.error(f"Background ETL failed: {e}")


@router.get("/files")
def list_uploaded_files(current_user: dict = Depends(get_current_user)):
    return {"files": list_uploads()}


@router.get("/etl/status/{job_id}")
def etl_status(job_id: str, current_user: dict = Depends(get_current_user)):
    return get_job_status(job_id)
