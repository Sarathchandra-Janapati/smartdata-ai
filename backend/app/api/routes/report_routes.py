from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import io

from app.core.security import get_current_user
from app.services.report_service import generate_pdf_report, generate_csv_report
from app.core.logger import api_logger

router = APIRouter()


@router.get("/pdf")
def download_pdf_report(
    file_path: str = None,
    current_user: dict = Depends(get_current_user),
):
    try:
        pdf_path = generate_pdf_report(file_path)
        return FileResponse(pdf_path, media_type="application/pdf", filename="smartdata_report.pdf")
    except Exception as e:
        api_logger.error(f"PDF report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/csv")
def download_csv_report(
    file_path: str = None,
    current_user: dict = Depends(get_current_user),
):
    try:
        csv_buffer = generate_csv_report(file_path)
        return StreamingResponse(
            io.StringIO(csv_buffer),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=smartdata_report.csv"},
        )
    except Exception as e:
        api_logger.error(f"CSV report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
