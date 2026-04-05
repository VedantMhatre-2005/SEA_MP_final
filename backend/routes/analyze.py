"""
analyze.py - /analyze route.

POST /analyze:
  1. Validates ProjectInput
  2. Runs the negotiation engine (multi-agent loop)
  3. Runs ML risk scoring and explainability agent
  4. Optionally creates a Jira issue
  5. Returns enhanced NegotiationResult with risk assessment
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from fastapi import Depends

from core.schemas import ProjectInput, NegotiationResult, BudgetAnalysis, RiskAssessment
from core.security import get_current_user
from core import negotiation_engine
from agents import explainability_agent
from ml import RiskScoringModel, extract_features
from db.mongo import get_db
from integrations import jira_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize ML model on startup
try:
    risk_model = RiskScoringModel()
    logger.info("Risk scoring model initialized")
except Exception as e:
    logger.error(f"Failed to initialize risk model: {e}")
    risk_model = None


@router.post(
    "/analyze",
    response_model=NegotiationResult,
    summary="Run ASPRAMS multi-agent risk simulation with ML scoring",
    description=(
        "Accepts project details and runs the iterative Estimation Agent ↔ Risk Agent "
        "negotiation loop powered by Google Gemini. Computes ML-based risk score and "
        "generates explainable reasoning. Returns all negotiation rounds, ML risk assessment, "
        "and mitigation recommendations."
    ),
)
async def analyze_project(
    project: ProjectInput,
    current_user: dict = Depends(get_current_user),
) -> NegotiationResult:
    """Main simulation endpoint with ML risk assessment and explainability."""
    logger.info(
        "Starting simulation | desc=%s... | team=%d | duration=%d | complexity=%s | budget=INR %.0f",
        project.description[:40],
        project.team_size,
        project.duration,
        project.complexity,
        project.available_budget,
    )

    try:
        # ── Step 1: Run multi-agent negotiation ─────────────────────────────
        result: NegotiationResult = negotiation_engine.run(project)

        # ── Step 2: Extract ML features and compute risk score ──────────────
        features = extract_features(project, result)
        ml_prediction = risk_model.predict(features) if risk_model else {"risk_score": 0.5, "risk_level": "MEDIUM"}

        ml_risk_score = ml_prediction["risk_score"]
        risk_level = ml_prediction["risk_level"]

        logger.info(
            "ML risk assessment | score=%.2f | level=%s",
            ml_risk_score,
            risk_level,
        )

        # ── Step 3: Generate explainability via Gemini ───────────────────────
        explanation = explainability_agent.run(
            project=project,
            negotiation_result=result,
            ml_risk_score=ml_risk_score,
            risk_level=risk_level,
        )

        # ── Step 4: Compute budget analysis (INR) ────────────────────────────
        required_cost = result.final_effort * 50000.0  # INR per person-week heuristic
        cost_per_pw = required_cost / max(result.final_effort, 1.0)
        budget_variance = (project.available_budget - required_cost) / max(required_cost, 1.0)
        is_affordable = project.available_budget >= required_cost

        budget_analysis = BudgetAnalysis(
            available_budget=project.available_budget,
            required_budget=required_cost,
            budget_variance=budget_variance,
            is_affordable=is_affordable,
            cost_per_personweek=cost_per_pw,
        )

        # ── Step 5: Identify budget risk ──────────────────────────────────────
        budget_risk = not is_affordable or budget_variance < -0.15  # Risk if unaffordable or >15% over

        # ── Step 6: Create final risk assessment ──────────────────────────────
        risk_assessment = RiskAssessment(
            ml_risk_score=ml_risk_score,
            risk_level=risk_level,
            budget_risk=budget_risk,
            explainability=explanation,
            budget_analysis=budget_analysis,
        )

        # Attach risk assessment to result
        result.risk_assessment = risk_assessment

        # ── Step 7: Persist input + output for history ───────────────────────
        db = get_db()
        stored_result = result.model_dump(mode="json")
        db.analyses.insert_one(
            {
                "user_id": current_user["id"],
                "project_input": project.model_dump(mode="json"),
                "result": stored_result,
                "created_at": datetime.now(timezone.utc),
            }
        )

        # ── Step 8: Extract final reasoning for Jira ──────────────────────────
        final_reasoning = ""
        if result.rounds:
            final_reasoning = result.rounds[-1].risk_agent.reason

        # ── Step 9: Create Jira issue (non-blocking) ─────────────────────────
        issue_key = jira_service.create_issue(
            description=project.description,
            team_size=project.team_size,
            duration=project.duration,
            complexity=project.complexity,
            final_effort=result.final_effort,
            reasoning=final_reasoning,
            converged=result.converged,
        )

        result.jira_issue_key = issue_key

        logger.info(
            "Simulation complete | rounds=%d | final_effort=%.1f | converged=%s | risk=%s | budget=%s | jira=%s",
            len(result.rounds),
            result.final_effort,
            result.converged,
            risk_level,
            "affordable" if is_affordable else "over-budget",
            issue_key or "N/A",
        )

        return result

    except Exception as exc:
        logger.exception("Simulation failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(exc)}",
        )
