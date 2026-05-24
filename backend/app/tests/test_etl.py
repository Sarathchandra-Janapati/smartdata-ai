import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from app.etl.extractor import extract_csv, extract_file
from app.etl.transformer import (
    drop_duplicates, handle_missing_values, normalize_column_names,
    encode_categoricals, remove_outliers_iqr, transform,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Age": [25, 30, 35, 30, None, 28],
        "Salary": [50000, 60000, 70000, 60000, 45000, 52000],
        "Department": ["IT", "HR", "IT", "HR", "Finance", "IT"],
        "Active": [1, 0, 1, 0, 1, None],
    })


@pytest.fixture
def sample_csv(tmp_path):
    df = pd.DataFrame({"col_a": [1, 2, 3], "col_b": ["x", "y", "z"]})
    path = str(tmp_path / "test.csv")
    df.to_csv(path, index=False)
    return path


# ── Extractor tests ────────────────────────────────────────────────────────────

def test_extract_csv(sample_csv):
    df = extract_csv(sample_csv)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "col_a" in df.columns


def test_extract_file_csv(sample_csv):
    df = extract_file(sample_csv)
    assert isinstance(df, pd.DataFrame)


def test_extract_csv_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_csv("/nonexistent/path/file.csv")


def test_extract_unsupported_format(tmp_path):
    p = str(tmp_path / "file.txt")
    open(p, "w").close()
    with pytest.raises(ValueError, match="Unsupported"):
        extract_file(p)


# ── Transformer tests ──────────────────────────────────────────────────────────

def test_drop_duplicates(sample_df):
    df_clean, removed = drop_duplicates(sample_df)
    assert isinstance(removed, int)
    assert removed >= 0
    assert len(df_clean) <= len(sample_df)


def test_handle_missing_values(sample_df):
    df_clean, report = handle_missing_values(sample_df)
    assert df_clean.isna().sum().sum() == 0
    assert isinstance(report, dict)


def test_normalize_column_names():
    df = pd.DataFrame({"First Name": [1], "Last-Name": [2], "AGE ": [3]})
    df = normalize_column_names(df)
    assert "first_name" in df.columns
    assert "last_name" in df.columns
    assert "age" in df.columns


def test_encode_categoricals(sample_df):
    df, _ = handle_missing_values(sample_df)
    df_enc, encoders = encode_categoricals(df)
    assert "Department" in [k for k in encoders]
    assert df_enc["Department"].dtype in [np.int32, np.int64, int]


def test_remove_outliers(sample_df):
    df, _ = handle_missing_values(sample_df)
    df_clean, removed = remove_outliers_iqr(df)
    assert isinstance(removed, int)


def test_full_transform(sample_df):
    df_out, report = transform(sample_df)
    assert isinstance(df_out, pd.DataFrame)
    assert df_out.isna().sum().sum() == 0
    assert "duplicates_removed" in report
    assert "missing_handled" in report
