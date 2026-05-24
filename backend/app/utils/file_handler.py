import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from app.core.logger import app_logger


def save_upload(file: UploadFile, destination_dir: str = None) -> str:
    dest_dir = Path(destination_dir or settings.UPLOAD_DIR)
    dest_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '.{ext}' not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}")

    dest_path = dest_dir / file.filename
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_mb = dest_path.stat().st_size / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        dest_path.unlink()
        raise HTTPException(status_code=413, detail=f"File too large ({size_mb:.1f} MB). Max {settings.MAX_FILE_SIZE_MB} MB")

    app_logger.info(f"File saved: {dest_path} ({size_mb:.2f} MB)")
    return str(dest_path)


def delete_file(file_path: str):
    p = Path(file_path)
    if p.exists():
        p.unlink()
        app_logger.info(f"Deleted file: {file_path}")


def list_uploads() -> list:
    d = Path(settings.UPLOAD_DIR)
    if not d.exists():
        return []
    return [
        {"name": f.name, "size_kb": round(f.stat().st_size / 1024, 2), "modified": f.stat().st_mtime}
        for f in sorted(d.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
        if f.suffix.lower().lstrip(".") in settings.ALLOWED_EXTENSIONS
    ]
