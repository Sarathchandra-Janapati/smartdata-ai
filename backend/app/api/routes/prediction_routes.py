from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.core.security import get_current_user
from app.database.mysql_db import get_db, save_prediction
from app.database.models import PredictionInput
from app.ml.predict import predict, get_model_accuracy
from app.core.logger import api_logger

router = APIRouter()


@router.post("/")
def run_prediction(
    payload: PredictionInput,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = predict(payload.features)

        # Persist to MySQL
        try:
            save_prediction(
                db,
                result=str(result["label"]),
                confidence=result["confidence"],
                input_data=json.dumps(payload.features),
                created_by=current_user["username"],
            )
        except Exception as e:
            api_logger.warning(f"Prediction save to DB failed: {e}")

        api_logger.info(f"Prediction by {current_user['username']}: {result['label']} ({result['confidence']})")
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        api_logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/accuracy")
def model_accuracy(current_user: dict = Depends(get_current_user)):
    metrics = get_model_accuracy()
    if "error" in metrics:
        raise HTTPException(status_code=404, detail=metrics["error"])
    return metrics
