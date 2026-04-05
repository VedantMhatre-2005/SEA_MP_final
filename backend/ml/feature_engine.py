"""
feature_engine.py - Feature extraction from project inputs and agent outputs.

Transforms ProjectInput and NegotiationResult into a feature vector suitable
for the ML risk scoring model.
"""

import logging
from typing import Dict

from core.schemas import ProjectInput, NegotiationResult

logger = logging.getLogger(__name__)


def extract_features(project: ProjectInput, negotiation_result: NegotiationResult) -> Dict[str, float]:
    """
    Extracts 14 features from user input and negotiation results for ML risk model.

    Args:
        project: Original ProjectInput from user
        negotiation_result: Output from multi-agent negotiation

    Returns:
        Dictionary mapping feature names to numeric values, suitable for model.predict()
    """

    final_effort = negotiation_result.final_effort

    # ─── Direct User Inputs ──────────────────────────────────────────────────
    team_size = float(project.team_size)
    planned_duration = float(project.duration)
    complexity_map = {"low": 1.0, "medium": 2.0, "high": 3.0, "critical": 4.0}
    complexity_score = float(complexity_map.get(project.complexity, 2.0))

    # ─── Derived Features from Effort Estimate ──────────────────────────────
    effort_density = final_effort / max(planned_duration, 1.0)  # person-weeks per week
    schedule_slack = (final_effort / max(team_size, 1.0)) / max(planned_duration, 1.0)
    team_size_norm = team_size / 25.0  # normalized

    # ─── Synthetic Risk Factors (estimated from negotiation) ─────────────────
    # These are derived from the negotiation trajectory and agent reasoning

    # Scope change rate: estimated from risk agent's mentions of scope creep
    scope_change_rate = _estimate_scope_change(negotiation_result)

    # Team experience: estimated from effort convergence (if converges quickly, assume experienced)
    team_experience_months = _estimate_team_experience(negotiation_result)

    # External dependencies: count mentioned in risk agent's reasoning
    external_dependencies = _count_dependencies(negotiation_result)

    # Requirement clarity: inverse of negotiation rounds (more rounds = less clarity)
    requirement_clarity = _estimate_requirement_clarity(negotiation_result, planned_duration)

    # Infrastructure readiness: assume infrastructure is ready if effort is reasonable
    infra_readiness = _estimate_infra_readiness(negotiation_result, planned_duration, team_size)

    # Technical debt: assume average technical debt for mid-complexity projects
    tech_debt = _estimate_technical_debt(complexity_score)

    # Budget variance
    required_cost = final_effort * 50000.0  # assume ~INR 50,000 per person-week average
    available_budget = project.available_budget
    budget_variance = (available_budget - required_cost) / max(required_cost, 1.0)

    # ─── Feature Dictionary ──────────────────────────────────────────────────
    features = {
        "team_size": team_size,
        "planned_duration_weeks": planned_duration,
        "estimated_effort_personweeks": final_effort,
        "complexity_score": complexity_score,
        "effort_density": effort_density,
        "schedule_slack": schedule_slack,
        "team_size_norm": team_size_norm,
        "scope_change_rate": scope_change_rate,
        "team_experience_months": team_experience_months,
        "external_dependencies": external_dependencies,
        "requirement_clarity": requirement_clarity,
        "infrastructure_readiness": infra_readiness,
        "technical_debt_score": tech_debt,
        "budget_variance": budget_variance,
    }

    logger.debug(f"Extracted features: {features}")

    return features


def _estimate_scope_change(result: NegotiationResult) -> float:
    """Estimate scope change rate from Risk Agent's reasoning."""
    if not result.rounds:
        return 0.1

    # Count mentions of scope-related keywords in risk agent's reasons
    risk_text = " ".join(
        [r.risk_agent.reason for r in result.rounds]
    ).lower()

    scope_keywords = ["scope creep", "requirement", "change", "boundary", "unclear"]
    mentions = sum(1 for keyword in scope_keywords if keyword in risk_text)

    # Map mentions to percentage: 0 mentions -> 0.05, 5+ mentions -> 0.35
    return min(0.05 + (mentions * 0.06), 0.4)


def _estimate_team_experience(result: NegotiationResult) -> float:
    """Estimate team experience from convergence speed and agreement."""
    # Quick convergence suggests experienced team (less negotiation needed)
    # More rounds suggest inexperienced team (more risk, more discussion)
    num_rounds = len(result.rounds)

    if num_rounds == 1 and result.converged:
        # Perfect agreement immediately = very experienced
        return 60.0
    elif num_rounds <= 2 and result.converged:
        # Quick agreement = experienced
        return 40.0
    elif num_rounds <= 3 and result.converged:
        # Moderate negotiation = intermediate
        return 20.0
    else:
        # Long negotiation or no convergence = inexperienced
        return 6.0


def _count_dependencies(result: NegotiationResult) -> float:
    """Count external dependencies mentioned in risk agent's reasoning."""
    if not result.rounds:
        return 0.0

    risk_text = " ".join(
        [r.risk_agent.reason for r in result.rounds]
    ).lower()

    dep_keywords = [
        "integration",
        "external",
        "third-party",
        "api",
        "dependency",
        "service",
    ]

    mentions = sum(1 for keyword in dep_keywords if keyword in risk_text)
    return float(min(mentions, 10))  # Cap at 10


def _estimate_requirement_clarity(result: NegotiationResult, planned_duration: float) -> float:
    """Estimate requirement clarity based on negotiation."""
    # More rounds of negotiation typically indicate unclear requirements
    num_rounds = len(result.rounds)

    # Short duration + many rounds = unclear requirements
    duration_factor = max(1.0 - (planned_duration / 52.0), 0.0)  # shorter = factor up

    clarity = 1.0 - (num_rounds * 0.15) - (duration_factor * 0.2)

    return max(min(clarity, 1.0), 0.2)  # Keep in [0.2, 1.0]


def _estimate_infra_readiness(
    result: NegotiationResult, planned_duration: float, team_size: float
) -> float:
    """Estimate infrastructure readiness."""
    # Assume infrastructure is ready if team is available and timeline is reasonable
    final_effort = result.final_effort if result else 0.0

    # Ratio of available effort to required effort as proxy
    if planned_duration == 0 or team_size == 0:
        return 0.7

    available_effort = team_size * planned_duration
    ratio = final_effort / max(available_effort, 1.0)

    if ratio < 0.8:
        # Overestimating effort = likely infrastructure issues
        return 0.5
    elif ratio < 1.2:
        # Reasonable fit = infrastructure OK
        return 0.9
    else:
        # Underestimating effort = infrastructure concerns
        return 0.6


def _estimate_technical_debt(complexity_score: float) -> float:
    """Estimate technical debt based on project complexity."""
    # Higher complexity projects typically have more technical debt
    # Assume: low (1) = 1.0 debt, critical (4) = 6.0 debt

    base_debt = 1.0 + (complexity_score - 1.0) * 1.5
    return min(base_debt, 10.0)
