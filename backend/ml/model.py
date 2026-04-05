"""
model.py - Risk Scoring ML Model.

Implements a trained Linear Regression model for predicting software project risk.
Model is trained on synthetic data and persisted to disk for inference.
"""

import logging
import os
from pathlib import Path
from typing import Dict

import numpy as np
from joblib import dump, load
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from .synthetic_data import generate_synthetic_data, get_feature_names

logger = logging.getLogger(__name__)

# Model persistence paths
MODEL_DIR = Path(__file__).parent / "pretrained"
MODEL_PATH = MODEL_DIR / "risk_model.joblib"
SCALER_PATH = MODEL_DIR / "scaler.joblib"
META_PATH = MODEL_DIR / "meta.joblib"
MODEL_VERSION = "inr-v1"


class RiskScoringModel:
    """
    Trained ML model for predicting software project risk scores.
    
    Uses Linear Regression trained on synthetic project data to map project
    features to a continuous risk score [0.0, 1.0], which is then categorized
    as LOW, MEDIUM, or HIGH risk.
    """

    def __init__(self):
        """Initialize the risk model. Loads pretrained model or trains new one."""
        self.model = None
        self.scaler = None
        self.feature_names = get_feature_names()
        self._load_or_train()

    def _load_or_train(self):
        """Load pretrained model if available, otherwise train new one."""
        if MODEL_PATH.exists() and SCALER_PATH.exists() and META_PATH.exists():
            logger.info(f"Loading pretrained model from {MODEL_PATH}")
            try:
                meta = load(META_PATH)
                if meta.get("version") != MODEL_VERSION:
                    raise ValueError("Model version mismatch; retraining required")
                self.model = load(MODEL_PATH)
                self.scaler = load(SCALER_PATH)
                logger.info("Model loaded successfully")
                return
            except Exception as e:
                logger.warning(f"Failed to load model: {e}. Training new model.")

        logger.info("Training new risk model on synthetic data...")
        self._train_model()

    def _train_model(self):
        """Generate synthetic data and train the model."""
        # Generate synthetic dataset
        X, y = generate_synthetic_data(n_samples=1000, random_state=42)

        # Split: 80% train, 20% test (for validation purposes)
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Standardize features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Train Linear Regression
        self.model = LinearRegression()
        self.model.fit(X_train_scaled, y_train)

        # Evaluate on test set
        X_test_scaled = self.scaler.transform(X_test)
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)

        logger.info(f"Model training complete. R² scores - Train: {train_score:.3f}, Test: {test_score:.3f}")

        # Persist model
        os.makedirs(MODEL_DIR, exist_ok=True)
        dump(self.model, MODEL_PATH)
        dump(self.scaler, SCALER_PATH)
        dump({"version": MODEL_VERSION}, META_PATH)
        logger.info(f"Model saved to {MODEL_PATH}")

    def predict(self, features: Dict[str, float]) -> Dict[str, any]:
        """
        Predict risk score and level for a project.

        Args:
            features: Dictionary of feature names to values (from feature_engine.extract_features)

        Returns:
            Dictionary with:
                - risk_score: float [0.0, 1.0]
                - risk_level: str "LOW", "MEDIUM", or "HIGH"
                - feature_importance: list of (feature_name, importance) tuples
        """
        if self.model is None or self.scaler is None:
            logger.error("Model not initialized")
            return self._default_prediction()

        try:
            # Convert features dict to ordered array
            feature_vector = np.array(
                [[features.get(name, 0.0) for name in self.feature_names]]
            )

            # Scale features
            feature_scaled = self.scaler.transform(feature_vector)

            # Predict risk score
            risk_score = float(self.model.predict(feature_scaled)[0])

            # Clip to [0, 1]
            risk_score = np.clip(risk_score, 0.0, 1.0)

            # Categorize risk level
            if risk_score < 0.33:
                risk_level = "LOW"
            elif risk_score < 0.66:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"

            # Calculate feature importance (coefficient magnitude)
            coefficients = self.model.coef_
            feature_importance = list(
                zip(self.feature_names, np.abs(coefficients))
            )
            feature_importance.sort(key=lambda x: x[1], reverse=True)

            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "feature_importance": feature_importance,
            }

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._default_prediction()

    def _default_prediction(self) -> Dict[str, any]:
        """Fallback prediction when model fails."""
        return {
            "risk_score": 0.5,
            "risk_level": "MEDIUM",
            "feature_importance": [(name, 0.0) for name in self.feature_names],
        }
