from typing import Dict, Any
from app.services.analytics_service import get_summary, get_kpis, get_chart_data
from app.ml.predict import get_model_accuracy
from app.utils.file_handler import list_uploads
from app.core.logger import app_logger


def get_dashboard_overview() -> Dict[str, Any]:
    overview: Dict[str, Any] = {}

    try:
        overview["kpis"] = get_kpis()
    except Exception as e:
        overview["kpis"] = {"error": str(e)}

    try:
        overview["summary"] = get_summary()
    except Exception as e:
        overview["summary"] = {"error": str(e)}

    try:
        overview["model_metrics"] = get_model_accuracy()
    except Exception as e:
        overview["model_metrics"] = {"error": str(e)}

    try:
        overview["uploaded_files"] = list_uploads()
    except Exception as e:
        overview["uploaded_files"] = []

    return overview


def get_full_dashboard() -> Dict[str, Any]:
    data = get_dashboard_overview()
    try:
        data["charts"] = get_chart_data()
    except Exception as e:
        data["charts"] = {"error": str(e)}
    return data
