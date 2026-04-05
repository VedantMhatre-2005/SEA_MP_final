"""White-box tests for backend.ml.model.RiskScoringModel.

These tests avoid training or loading the real ML model. Instead, they
exercise the internal branches of predict() and _default_prediction()
directly with deterministic doubles.
"""

from __future__ import annotations

from dataclasses import dataclass
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.model import RiskScoringModel


pytestmark = pytest.mark.whitebox


@dataclass
class IdentityScaler:
    def transform(self, values):
        return np.asarray(values)


@dataclass
class FixedPredictionModel:
    predicted_value: float

    @property
    def coef_(self):
        return np.array([0.2, 0.8, 0.5])

    def predict(self, values):
        return np.array([self.predicted_value])


def make_model(predicted_value: float) -> RiskScoringModel:
    model = RiskScoringModel.__new__(RiskScoringModel)
    model.model = FixedPredictionModel(predicted_value)
    model.scaler = IdentityScaler()
    model.feature_names = ["alpha", "beta", "gamma"]
    return model


def _note_component_result(request: pytest.FixtureRequest, component: str, status: str, details: str) -> None:
    request.node.user_properties.append(
        (
            "component_results",
            {
                "component": component,
                "status": status,
                "details": details,
            },
        )
    )


def test_predict_low_risk_category_and_feature_ranking(request: pytest.FixtureRequest):
    model = make_model(0.12)

    result = model.predict({"alpha": 1.0, "beta": 2.0, "gamma": 3.0})

    assert result["risk_score"] == 0.12
    assert result["risk_level"] == "LOW"
    assert result["feature_importance"][0] == ("beta", 0.8)
    assert result["feature_importance"][1] == ("gamma", 0.5)
    assert result["feature_importance"][2] == ("alpha", 0.2)
    _note_component_result(
        request,
        "Low risk branch",
        "Passed",
        "A predicted score below 0.33 correctly mapped to the LOW risk category and preserved feature ranking.",
    )


def test_predict_medium_risk_category(request: pytest.FixtureRequest):
    model = make_model(0.5)

    result = model.predict({"alpha": 1.0, "beta": 2.0, "gamma": 3.0})

    assert result["risk_score"] == 0.5
    assert result["risk_level"] == "MEDIUM"
    _note_component_result(
        request,
        "Medium risk branch",
        "Passed",
        "A predicted score in the middle band correctly mapped to the MEDIUM risk category.",
    )


def test_predict_high_risk_category(request: pytest.FixtureRequest):
    model = make_model(0.91)

    result = model.predict({"alpha": 1.0, "beta": 2.0, "gamma": 3.0})

    assert result["risk_score"] == 0.91
    assert result["risk_level"] == "HIGH"
    _note_component_result(
        request,
        "High risk branch",
        "Passed",
        "A predicted score above 0.66 correctly mapped to the HIGH risk category.",
    )


def test_default_prediction_when_model_is_missing(request: pytest.FixtureRequest):
    model = RiskScoringModel.__new__(RiskScoringModel)
    model.model = None
    model.scaler = None
    model.feature_names = ["alpha", "beta", "gamma"]

    result = model._default_prediction()

    assert result["risk_score"] == 0.5
    assert result["risk_level"] == "MEDIUM"
    assert result["feature_importance"] == [("alpha", 0.0), ("beta", 0.0), ("gamma", 0.0)]
    _note_component_result(
        request,
        "Fallback prediction path",
        "Passed",
        "When the model or scaler is unavailable, the fallback prediction returns a safe default MEDIUM risk result.",
    )