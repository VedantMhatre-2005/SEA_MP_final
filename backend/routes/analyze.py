"""
analyze.py - /analyze route.

POST /analyze:
  1. Validates ProjectInput
  2. Runs the negotiation engine (multi-agent loop)
  3. Optionally creates a Jira issue
  4. Returns full NegotiationResult
"""

import logging
from fastapi import APIRouter, HTTPException

from core.schemas import ProjectInput, NegotiationResult
from core import negotiation_engine
from integrations import jira_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=NegotiationResult,
    summary="Run ASPRAMS multi-agent risk simulation",
    description=(
        "Accepts project details and runs the iterative Estimation Agent ↔ Risk Agent "
        "negotiation loop powered by Google Gemini. Returns all negotiation rounds and the "
        "final agreed effort estimate."
    ),
)
async def analyze_project(project: ProjectInput) -> NegotiationResult:
    """Main simulation endpoint."""
    logger.info(
        "Starting simulation | desc=%s... | team=%d | duration=%d | complexity=%s",
        project.description[:40],
        project.team_size,
        project.duration,
        project.complexity,
    )

    try:
        # ── Run multi-agent negotiation ───────────────────────────────────────
        result: NegotiationResult = negotiation_engine.run(project)

        # ── Extract final round reasoning for Jira ───────────────────────────
        final_reasoning = ""
        if result.rounds:
            final_reasoning = result.rounds[-1].risk_agent.reason

        # ── Create Jira issue (non-blocking; errors are swallowed) ────────────
        issue_key = jira_service.create_issue(
            description=project.description,
            team_size=project.team_size,
            duration=project.duration,
            complexity=project.complexity,
            final_effort=result.final_effort,
            reasoning=final_reasoning,
            converged=result.converged,
        )

        # Attach Jira key to result if created
        result.jira_issue_key = issue_key

        logger.info(
            "Simulation complete | rounds=%d | final_effort=%.1f | converged=%s | jira=%s",
            len(result.rounds),
            result.final_effort,
            result.converged,
            issue_key or "N/A",
        )

        return result

    except Exception as exc:
        logger.exception("Simulation failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(exc)}",
        )
