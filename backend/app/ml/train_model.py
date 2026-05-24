import joblib
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from app.ml.preprocessing import load_dataset, preprocess
from app.core.logger import ml_logger
from app.core.config import settings

# Resolve model path relative to this file so it works regardless of CWD
_HERE = Path(__file__).parent
_PROJECT_ROOT = _HERE.parent.parent.parent  # smartdata-ai/
MODEL_PATH = _HERE / "model.pkl"
METRICS_PATH = _HERE / "metrics.json"
_DEFAULT_DATASET = _PROJECT_ROOT / "datasets" / "churn_dataset.csv"


def train(dataset_path: str = None, target_col: str = "churn") -> dict:
    if dataset_path is None:
        dataset_path = str(_DEFAULT_DATASET)
    ml_logger.info(f"Training on {dataset_path}, target={target_col}")

    df = load_dataset(dataset_path)
    X_train, X_test, y_train, y_test, meta = preprocess(df, target_col)

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "model_type": "RandomForestClassifier",
        "features": meta["features"],
        "target_classes": meta["target_classes"],
        "n_features": meta["n_features"],
        "train_size": meta["train_size"],
        "test_size": meta["test_size"],
        "trained_at": datetime.utcnow().isoformat(),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "meta": meta}, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    ml_logger.info(f"Model saved. Accuracy={metrics['accuracy']:.4f}")
    return metrics


def load_metrics() -> dict:
    if METRICS_PATH.exists():
        with open(METRICS_PATH) as f:
            return json.load(f)
    return {}


if __name__ == "__main__":
    result = train()
    print(json.dumps(result, indent=2))
