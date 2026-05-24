from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.services.analytics_service import get_summary, get_chart_data, get_kpis
from app.core.logger import api_logger

router = APIRouter()


@router.get("/summary")
def analytics_summary(
    file_path: str = None,
    current_user: dict = Depends(get_current_user),
):
    try:
        return get_summary(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No processed data found. Upload a file first.")
    except Exception as e:
        api_logger.error(f"Analytics summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts")
def analytics_charts(
    file_path: str = None,
    current_user: dict = Depends(get_current_user),
):
    try:
        return get_chart_data(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No processed data found. Upload a file first.")
    except Exception as e:
        api_logger.error(f"Analytics charts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis")
def analytics_kpis(
    file_path: str = None,
    current_user: dict = Depends(get_current_user),
):
    try:
        return get_kpis(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No processed data found. Upload a file first.")
    except Exception as e:
        api_logger.error(f"KPI error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
