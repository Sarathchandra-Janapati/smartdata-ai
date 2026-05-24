import joblib
import numpy as np
import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logger import ml_logger

_HERE = Path(__file__).parent
MODEL_PATH = _HERE / "model.pkl"
METRICS_PATH = _HERE / "metrics.json"

_model_cache: Optional[dict] = None


def _load_model() -> dict:
    global _model_cache
    if _model_cache is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train_model.py first.")
        _model_cache = joblib.load(MODEL_PATH)
        ml_logger.info("Model loaded from disk")
    return _model_cache


def predict(features: Dict[str, Any]) -> Dict[str, Any]:
    bundle = _load_model()
    model = bundle["model"]
    meta = bundle["meta"]

    expected_features = meta["features"]
    input_vec = []

    for feat in expected_features:
        val = features.get(feat, 0)
        try:
            input_vec.append(float(val))
        except (ValueError, TypeError):
            input_vec.append(0.0)

    X = np.array([input_vec])
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    confidence = float(np.max(probabilities))

    label = None
    if meta.get("target_classes"):
        try:
            label = meta["target_classes"][int(prediction)]
        except (IndexError, TypeError):
            label = str(prediction)

    ml_logger.info(f"Prediction: {prediction} (confidence={confidence:.3f})")

    return {
        "prediction": int(prediction) if isinstance(prediction, (np.integer,)) else prediction,
        "confidence": round(confidence, 4),
        "label": label or str(prediction),
        "probabilities": {
            str(meta["target_classes"][i]) if meta.get("target_classes") else str(i): round(float(p), 4)
            for i, p in enumerate(probabilities)
        },
    }


def get_model_accuracy() -> Dict[str, Any]:
    if METRICS_PATH.exists():
        with open(METRICS_PATH) as f:
            return json.load(f)
    return {"error": "Model metrics not found. Train the model first."}
