import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logger import app_logger


def _load_latest_cleaned(file_path: Optional[str] = None) -> pd.DataFrame:
    if file_path and Path(file_path).exists():
        return pd.read_csv(file_path)

    upload_dir = Path(settings.UPLOAD_DIR)
    cleaned_files = sorted(upload_dir.glob("cleaned_*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not cleaned_files:
        raise FileNotFoundError("No cleaned data files found. Run ETL first.")
    return pd.read_csv(cleaned_files[0])


def get_summary(file_path: Optional[str] = None) -> Dict[str, Any]:
    df = _load_latest_cleaned(file_path)

    numeric_df = df.select_dtypes(include=[np.number])
    cat_df = df.select_dtypes(exclude=[np.number])

    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "numeric_columns": len(numeric_df.columns),
        "categorical_columns": len(cat_df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "describe": numeric_df.describe().round(4).to_dict() if not numeric_df.empty else {},
    }
    return summary


def get_kpis(file_path: Optional[str] = None) -> Dict[str, Any]:
    df = _load_latest_cleaned(file_path)
    numeric_df = df.select_dtypes(include=[np.number])

    total = len(df)
    missing_total = int(df.isna().sum().sum())
    missing_rate = round(missing_total / (total * len(df.columns)) * 100, 2) if total > 0 else 0

    kpis: Dict[str, Any] = {
        "total_records": total,
        "clean_records": total - int(df.duplicated().sum()),
        "missing_rate_pct": missing_rate,
        "numeric_columns": len(numeric_df.columns),
        "categorical_columns": len(df.select_dtypes(exclude=[np.number]).columns),
    }

    if not numeric_df.empty:
        for col in numeric_df.columns[:3]:  # top 3 numeric KPIs
            kpis[f"{col}_mean"] = round(float(numeric_df[col].mean()), 4)
            kpis[f"{col}_std"] = round(float(numeric_df[col].std()), 4)

    return kpis


def get_chart_data(file_path: Optional[str] = None) -> Dict[str, Any]:
    df = _load_latest_cleaned(file_path)
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(0)
    charts: Dict[str, Any] = {}

    numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
    cat_cols = list(df.select_dtypes(exclude=[np.number]).columns)

    # Bar chart: value counts of first categorical
    if cat_cols:
        col = cat_cols[0]
        vc = df[col].value_counts().head(10)
        charts["bar_chart"] = {
            "title": f"Distribution of {col}",
            "x": list(vc.index.astype(str)),
            "y": list(vc.values.tolist()),
            "column": col,
        }

    # Line chart: first numeric column trend
    if numeric_cols:
        col = numeric_cols[0]
        sample = df[col].dropna().head(100)
        charts["line_chart"] = {
            "title": f"Trend of {col}",
            "x": list(range(len(sample))),
            "y": [round(v, 4) for v in sample.tolist()],
            "column": col,
        }

    # Correlation heatmap data
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr().round(3).fillna(0)
        charts["correlation"] = {
            "title": "Correlation Matrix",
            "columns": numeric_cols,
            "matrix": corr.values.tolist(),
        }

    # Histogram for second numeric column
    if len(numeric_cols) >= 2:
        col = numeric_cols[1]
        hist, edges = np.histogram(df[col].dropna(), bins=20)
        charts["histogram"] = {
            "title": f"Histogram of {col}",
            "bins": [round(e, 4) for e in edges.tolist()],
            "counts": hist.tolist(),
            "column": col,
        }

    return charts
