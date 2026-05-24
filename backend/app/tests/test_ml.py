import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from app.ml.preprocessing import preprocess


@pytest.fixture
def churn_df():
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "tenure": np.random.randint(1, 72, n),
        "monthly_charges": np.random.uniform(20, 120, n),
        "total_charges": np.random.uniform(100, 8000, n),
        "contract_type": np.random.choice(["Month-to-month", "One year", "Two year"], n),
        "internet_service": np.random.choice(["DSL", "Fiber optic", "No"], n),
        "churn": np.random.choice([0, 1], n),
    })


def test_preprocess_output_shape(churn_df):
    X_train, X_test, y_train, y_test, meta = preprocess(churn_df, "churn")
    assert X_train.shape[1] == X_test.shape[1]
    assert len(y_train) > len(y_test)
    assert "features" in meta
    assert "n_features" in meta


def test_preprocess_no_missing(churn_df):
    X_train, X_test, y_train, y_test, _ = preprocess(churn_df, "churn")
    assert not np.isnan(X_train).any()
    assert not np.isnan(X_test).any()


def test_preprocess_missing_target(churn_df):
    with pytest.raises(ValueError, match="Target column"):
        preprocess(churn_df, "nonexistent_column")


def test_predict_mock():
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([1])
    mock_model.predict_proba.return_value = np.array([[0.2, 0.8]])

    mock_bundle = {
        "model": mock_model,
        "meta": {
            "features": ["tenure", "monthly_charges"],
            "target_classes": ["No", "Yes"],
        },
    }

    with patch("app.ml.predict._load_model", return_value=mock_bundle):
        from app.ml.predict import predict
        result = predict({"tenure": 12.0, "monthly_charges": 70.0})

        assert result["prediction"] == 1
        assert result["label"] == "Yes"
        assert 0 <= result["confidence"] <= 1
        assert "probabilities" in result
