"""
ML Module - Risk Scoring and Feature Engineering

Provides machine learning-based risk assessment using synthetic data training
and feature generation from project inputs and agent outputs.
"""

from .model import RiskScoringModel
from .feature_engine import extract_features

__all__ = ["RiskScoringModel", "extract_features"]
