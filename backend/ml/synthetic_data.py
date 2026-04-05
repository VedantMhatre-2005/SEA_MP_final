"""
synthetic_data.py - Synthetic project data generator for ML model training.

Generates realistic software project scenarios with risk outcomes using
domain knowledge and statistical distributions.
"""

import numpy as np
from typing import Tuple


def generate_synthetic_data(n_samples: int = 1000, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates synthetic software project data for training the risk model.

    Args:
        n_samples: Number of synthetic projects to generate
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (X, y) where X is features array and y is risk scores
    """
    np.random.seed(random_state)

    data = []

    for _ in range(n_samples):
        # ─── User-Provided Inputs ────────────────────────────────────────
        team_size = np.random.randint(3, 51)  # 3-50 developers
        planned_duration = np.random.randint(4, 53)  # 4-52 weeks
        complexity_numeric = np.random.randint(1, 5)  # 1=low, 4=critical

        # ─── Simulated Effort Estimation (COCOMO-like) ─────────────────
        # Higher complexity & team size → more effort
        base_effort = 15 + (complexity_numeric * 10) + (team_size * 1.2)
        # Add stochastic variation
        effort_estimate = base_effort + np.random.normal(0, 5)
        effort_estimate = max(effort_estimate, 5)  # Ensure positive

        # ─── Derived Features ──────────────────────────────────────────
        effort_density = effort_estimate / planned_duration  # person-weeks per week
        schedule_slack = (effort_estimate / team_size) / planned_duration  # feasibility ratio
        team_size_norm = team_size / 25.0  # normalized around typical size

        # ─── Synthetic Risk Factors ────────────────────────────────────
        # Scope change rate (higher → higher risk)
        scope_change_rate = np.random.beta(2, 5) * 0.5  # 0.0-0.5, skewed low

        # Team experience (lower → higher risk)
        team_experience_months = np.random.exponential(15)  # skewed low, 0-infinity
        team_experience_months = min(team_experience_months, 120)  # cap at 120 months

        # External dependencies (more → higher risk)
        external_dependencies = np.random.poisson(2)  # avg 2, variable

        # Requirements clarity (lower → higher risk)
        requirement_clarity = np.random.beta(2, 2)  # 0.0-1.0, uniform-ish

        # Infrastructure readiness (lower → higher risk)
        infra_readiness = np.random.beta(3, 2)  # 0.0-1.0, skewed high

        # Technical debt (higher → higher risk)
        tech_debt = np.random.exponential(2)
        tech_debt = min(tech_debt, 10)  # cap at 10

        # Budget constraint (available budget simulated in INR)
        required_costper_pw = np.random.uniform(35000, 80000)  # INR per person-week
        required_cost = effort_estimate * required_costper_pw
        available_budget = required_cost * np.random.uniform(0.8, 1.5)  # 0.8x to 1.5x required

        budget_variance = (available_budget - required_cost) / required_cost

        # ─── Synthesize Risk Score ────────────────────────────────────
        # Risk is combination of multiple factors
        risk = 0.0

        # Factor 1: Effort density (high density = tight schedule = risk)
        risk += 0.20 * min(effort_density / 10.0, 1.0)  # normalized

        # Factor 2: Scope changes
        risk += 0.15 * scope_change_rate

        # Factor 3: Team experience (inexperienced = risk)
        team_exp_ratio = min(team_experience_months / 60.0, 1.0)  # 0-60 is considered experienced
        risk += 0.15 * (1.0 - team_exp_ratio)

        # Factor 4: External dependencies
        risk += 0.10 * min(external_dependencies / 5.0, 1.0)

        # Factor 5: Requirement clarity (unclear = risk)
        risk += 0.15 * (1.0 - requirement_clarity)

        # Factor 6: Infrastructure readiness
        risk += 0.10 * (1.0 - infra_readiness)

        # Factor 7: Technical debt
        risk += 0.10 * min(tech_debt / 10.0, 1.0)

        # Factor 8: Budget constraint (tight budget = risk)
        risk += 0.05 * min(max(0, -budget_variance), 1.0)  # only negative variance adds risk

        # Add some noise
        risk += np.random.normal(0, 0.05)

        # Clip to [0, 1]
        risk_score = np.clip(risk, 0, 1)

        # ─── Store feature vector ─────────────────────────────────────
        features = [
            team_size,
            planned_duration,
            effort_estimate,
            complexity_numeric,
            effort_density,
            schedule_slack,
            team_size_norm,
            scope_change_rate,
            team_experience_months,
            external_dependencies,
            requirement_clarity,
            infra_readiness,
            tech_debt,
            budget_variance,
        ]

        data.append({"features": features, "risk_score": risk_score})

    # Convert to numpy arrays
    X = np.array([d["features"] for d in data])
    y = np.array([d["risk_score"] for d in data])

    return X, y


def get_feature_names() -> list[str]:
    """Returns the names of features in the order they appear in generated data."""
    return [
        "team_size",
        "planned_duration_weeks",
        "estimated_effort_personweeks",
        "complexity_score",
        "effort_density",
        "schedule_slack",
        "team_size_norm",
        "scope_change_rate",
        "team_experience_months",
        "external_dependencies",
        "requirement_clarity",
        "infrastructure_readiness",
        "technical_debt_score",
        "budget_variance",
    ]
