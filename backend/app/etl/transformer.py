import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from app.core.logger import etl_logger
from typing import Tuple, Dict, Any


def drop_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    etl_logger.info(f"Removed {removed} duplicate rows")
    return df, removed


def handle_missing_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    missing_report: Dict[str, int] = {}
    for col in df.columns:
        n_missing = df[col].isna().sum()
        if n_missing == 0:
            continue
        missing_report[col] = int(n_missing)
        if df[col].dtype in [np.float64, np.int64, float, int]:
            df[col] = df[col].fillna(df[col].median())
        else:
            mode_val = df[col].mode()
            fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
            df[col] = df[col].fillna(fill_val)
    etl_logger.info(f"Handled missing values in columns: {list(missing_report.keys())}")
    return df, missing_report


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    return df


def encode_categoricals(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, list]]:
    encoders: Dict[str, list] = {}
    for col in df.select_dtypes(include=["object", "category"]).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = list(le.classes_)
    etl_logger.info(f"Encoded categorical columns: {list(encoders.keys())}")
    return df, encoders


def remove_outliers_iqr(df: pd.DataFrame, factor: float = 1.5) -> Tuple[pd.DataFrame, int]:
    before = len(df)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        df = df[(df[col] >= q1 - factor * iqr) & (df[col] <= q3 + factor * iqr)]
    removed = before - len(df)
    etl_logger.info(f"Removed {removed} outlier rows")
    return df, removed


def scale_numeric(df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
    scaler = StandardScaler()
    numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
    if numeric_cols:
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    etl_logger.info(f"Scaled numeric columns: {numeric_cols}")
    return df, numeric_cols


def transform(df: pd.DataFrame, scale: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    report: Dict[str, Any] = {}

    df = normalize_column_names(df)
    df, dup_removed = drop_duplicates(df)
    report["duplicates_removed"] = dup_removed

    df, missing = handle_missing_values(df)
    report["missing_handled"] = missing

    df, encoders = encode_categoricals(df)
    report["encoded_columns"] = list(encoders.keys())

    df, outliers = remove_outliers_iqr(df)
    report["outliers_removed"] = outliers

    if scale:
        df, scaled = scale_numeric(df)
        report["scaled_columns"] = scaled

    report["final_shape"] = df.shape
    etl_logger.info(f"Transformation complete. Final shape: {df.shape}")
    return df, report
