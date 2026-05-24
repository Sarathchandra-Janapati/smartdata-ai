import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple, Dict, Any


def load_dataset(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def preprocess(df: pd.DataFrame, target_col: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Separate target
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found. Available: {list(df.columns)}")

    y = df[target_col].values
    X = df.drop(columns=[target_col])

    # Drop all-null columns
    X = X.dropna(axis=1, how="all")

    # Drop ID-like columns (object columns where every value is unique)
    for col in X.select_dtypes(include=["object", "category"]).columns:
        if X[col].nunique() == len(X):
            X = X.drop(columns=[col])

    # Fill numeric medians (pandas 3.0-safe)
    for col in X.select_dtypes(include=[np.number]).columns:
        X[col] = X[col].fillna(X[col].median())

    # Encode categoricals
    encoders: Dict[str, LabelEncoder] = {}
    for col in X.select_dtypes(include=["object", "category"]).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    # Encode target if needed
    target_le = None
    if y.dtype == object or str(y.dtype) == "object":
        target_le = LabelEncoder()
        y = target_le.fit_transform(y)

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

    meta = {
        "features": list(X.columns),
        "target": target_col,
        "target_classes": list(target_le.classes_) if target_le else None,
        "n_features": X_scaled.shape[1],
        "train_size": len(X_train),
        "test_size": len(X_test),
    }

    return X_train, X_test, y_train, y_test, meta
