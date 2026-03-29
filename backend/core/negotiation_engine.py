"""
negotiation_engine.py - Orchestrates the multi-agent estimation negotiation loop.

Flow:
  Round 1..N:
    1. Estimation Agent proposes/revises an optimistic effort estimate.
    2. Risk Agent evaluates → returns ACCEPT or COUNTER with risk-adjusted effort.
    3. If Risk Agent ACCEPTs, negotiation ends (converged).
    4. If max rounds exceeded, the latest Risk Agent effort is used as final.
"""

import logging
from config.settings import MAX_NEGOTIATION_ROUNDS
from core.schemas import AgentResponse, NegotiationRound, NegotiationResult, ProjectInput
from agents import estimation_agent, risk_agent

logger = logging.getLogger(__name__)


def run(project: ProjectInput) -> NegotiationResult:
    """
    Executes the full agent negotiation loop for the given project.

    Args:
        project: Validated ProjectInput containing description, team_size, duration, complexity.

    Returns:
        NegotiationResult containing all rounds, the final effort, and convergence status.
    """
    rounds: list[NegotiationRound] = []
    previous_risk_effort: float | None = None
    converged = False
    final_effort = 0.0

    for round_num in range(1, MAX_NEGOTIATION_ROUNDS + 1):
        logger.info("--- Negotiation Round %d ---", round_num)

        # ── Step 1: Estimation Agent ──────────────────────────────────────────
        est_response: AgentResponse = estimation_agent.run(
            description=project.description,
            team_size=project.team_size,
            duration=project.duration,
            complexity=project.complexity,
            previous_effort=previous_risk_effort,  # None on round 1
        )
        logger.info(
            "EstimationAgent → effort=%.1f, decision=%s",
            est_response.effort,
            est_response.decision,
        )

        # ── Step 2: Risk Agent ────────────────────────────────────────────────
        risk_response: AgentResponse = risk_agent.run(
            description=project.description,
            team_size=project.team_size,
            duration=project.duration,
            complexity=project.complexity,
            current_effort=est_response.effort,
            round_number=round_num,
        )
        logger.info(
            "RiskAgent → effort=%.1f, decision=%s",
            risk_response.effort,
            risk_response.decision,
        )

        # ── Record round ──────────────────────────────────────────────────────
        rounds.append(
            NegotiationRound(
                round_number=round_num,
                estimation_agent=est_response,
                risk_agent=risk_response,
            )
        )

        final_effort = risk_response.effort

        # ── Check termination condition ───────────────────────────────────────
        if risk_response.decision == "ACCEPT":
            converged = True
            logger.info("Negotiation converged in round %d with effort=%.1f", round_num, final_effort)
            break

        # Pass Risk Agent's counter-offer back to Estimation Agent next round
        previous_risk_effort = risk_response.effort

    if not converged:
        logger.warning(
            "Max negotiation rounds (%d) reached. Using last Risk Agent effort=%.1f",
            MAX_NEGOTIATION_ROUNDS,
            final_effort,
        )

    return NegotiationResult(
        rounds=rounds,
        final_effort=final_effort,
        converged=converged,
    )
