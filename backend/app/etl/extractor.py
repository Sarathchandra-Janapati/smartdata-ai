import pandas as pd
from pathlib import Path
from app.core.logger import etl_logger


def extract_csv(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    etl_logger.info(f"Extracting CSV: {path.name}")
    df = pd.read_csv(path, low_memory=False)
    etl_logger.info(f"Extracted {len(df)} rows, {len(df.columns)} columns from {path.name}")
    return df


def extract_excel(file_path: str, sheet_name: str = 0) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    etl_logger.info(f"Extracting Excel: {path.name} sheet={sheet_name}")
    df = pd.read_excel(path, sheet_name=sheet_name)
    etl_logger.info(f"Extracted {len(df)} rows, {len(df.columns)} columns from {path.name}")
    return df


def extract_json(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    etl_logger.info(f"Extracting JSON: {path.name}")
    df = pd.read_json(path)
    etl_logger.info(f"Extracted {len(df)} rows from {path.name}")
    return df


def extract_file(file_path: str) -> pd.DataFrame:
    ext = Path(file_path).suffix.lower()
    if ext == ".csv":
        return extract_csv(file_path)
    elif ext in (".xlsx", ".xls"):
        return extract_excel(file_path)
    elif ext == ".json":
        return extract_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
