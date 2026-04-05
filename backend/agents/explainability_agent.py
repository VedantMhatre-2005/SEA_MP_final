"""
explainability_agent.py - Explainability and Reasoning Agent.

Role: Synthesizes outputs from Estimation Agent, Risk Agent, and ML model
to generate comprehensive, human-readable explanations and mitigation recommendations.
Uses Google Gemini API for natural language synthesis.
"""

import json
import logging
import re

import google.generativeai as genai

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from core.schemas import (
    NegotiationResult,
    ProjectInput,
    ExplainabilityOutput,
)

logger = logging.getLogger(__name__)


def _build_prompt(
    project: ProjectInput,
    negotiation_result: NegotiationResult,
    ml_risk_score: float,
    risk_level: str,
) -> str:
    """Constructs a comprehensive prompt for the Explainability Agent."""

    # Extract key information from negotiation rounds
    rounds_summary = ""
    for round_data in negotiation_result.rounds:
        rounds_summary += f"""
Round {round_data.round_number}:
  Estimation Agent: effort={round_data.estimation_agent.effort:.1f} pw
    Reason: {round_data.estimation_agent.reason}
  Risk Agent: effort={round_data.risk_agent.effort:.1f} pw, decision={round_data.risk_agent.decision}
    Reason: {round_data.risk_agent.reason}
"""

    prompt = f"""
You are an expert Software Engineering Explainability Agent.
Your role is to synthesize complex technical analysis into clear, actionable insights.

PROJECT CONTEXT:
- Description: {project.description}
- Team Size: {project.team_size} developers
- Planned Duration: {project.duration} weeks
- Complexity: {project.complexity.upper()}
- Available Budget: INR {project.available_budget:,.0f}

AGENT NEGOTIATION SUMMARY:
{rounds_summary}

FINAL ASSESSMENT:
- Final Effort Estimate: {negotiation_result.final_effort:.1f} person-weeks
- Converged: {negotiation_result.converged}
- ML Risk Score: {ml_risk_score:.2f} (0=low, 1=high)
- Risk Level: {risk_level.upper()}

YOUR TASKS:
1. Analyze the negotiation trajectory (convergence speed, agreement level)
2. Identify the TOP 3 risk drivers from Risk Agent findings
3. Generate SPECIFIC mitigation recommendations (not generic)
4. Assess confidence in the estimate (0.0-1.0 based on convergence & agreement)
5. Provide insight into what negotiation reveals about project viability

RESPONSE FORMAT (STRICT JSON, NO MARKDOWN):
{{
  "executive_summary": "2-3 sentence summary for stakeholders",
  "risk_drivers": [
    "Specific risk #1 from negotiation",
    "Specific risk #2 from negotiation",
    "Specific risk #3 from negotiation"
  ],
  "mitigation_recommendations": [
    "Concrete action for risk #1",
    "Concrete action for risk #2",
    "Concrete action for risk #3"
  ],
  "confidence": 0.75,
  "negotiation_insight": "2-3 sentence observation about what negotiation reveals"
}}

Respond ONLY with valid JSON. No markdown, no explanation.
"""
    return prompt.strip()


def run(
    project: ProjectInput,
    negotiation_result: NegotiationResult,
    ml_risk_score: float,
    risk_level: str,
) -> ExplainabilityOutput:
    """
    Calls Gemini to generate comprehensive explainability output.

    Args:
        project: Original ProjectInput
        negotiation_result: Full NegotiationResult from negotiation engine
        ml_risk_score: ML model's computed risk score (0.0-1.0)
        risk_level: Categorical risk level (LOW/MEDIUM/HIGH)

    Returns:
        ExplainabilityOutput with synthesized reasoning
    """
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = _build_prompt(project, negotiation_result, ml_risk_score, risk_level)

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Extract JSON from response
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            logger.error("Explainability Agent failed to return valid JSON")
            return _fallback_explainability(project, negotiation_result, ml_risk_score, risk_level)

        data = json.loads(json_match.group())

        return ExplainabilityOutput(
            executive_summary=data.get("executive_summary", ""),
            risk_drivers=data.get("risk_drivers", []),
            mitigation_recommendations=data.get("mitigation_recommendations", []),
            confidence=float(data.get("confidence", 0.5)),
            negotiation_insight=data.get("negotiation_insight", ""),
        )

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Explainability Agent parsing error: {e}")
        return _fallback_explainability(project, negotiation_result, ml_risk_score, risk_level)


def _fallback_explainability(
    project: ProjectInput,
    negotiation_result: NegotiationResult,
    ml_risk_score: float,
    risk_level: str,
) -> ExplainabilityOutput:
    """
    Fallback if Gemini call fails.
    Constructs basic explanation from negotiation data.
    """
    final_round = negotiation_result.rounds[-1] if negotiation_result.rounds else None

    # Extract risks from final round if available
    risks = []
    if final_round and final_round.risk_agent.reason:
        # Split by common delimiters and take first 3 sentences
        sentences = re.split(r'[.!?]+', final_round.risk_agent.reason)
        risks = [s.strip() for s in sentences if s.strip()][:3]

    if not risks:
        risks = [
            "Integration complexity with external systems",
            "Team ramp-up and knowledge gaps",
            "Scope and requirement clarity",
        ]

    convergence_status = "quickly" if len(negotiation_result.rounds) <= 2 else "over multiple rounds"

    return ExplainabilityOutput(
        executive_summary=f"Project estimated at {negotiation_result.final_effort:.1f} person-weeks "
        f"with {risk_level} risk. Agents converged {convergence_status}, indicating "
        f"{'good agreement on feasibility.' if negotiation_result.converged else 'ongoing concerns about feasibility.'}",
        risk_drivers=risks or [
            "Technical integration complexity",
            "Team scaling and onboarding",
            "Requirement volatility",
        ],
        mitigation_recommendations=[
            "Conduct architecture and design review before development",
            "Implement phased team onboarding with mentorship",
            "Lock requirements and establish change control process",
        ],
        confidence=0.8 if negotiation_result.converged else 0.6,
        negotiation_insight=f"Agents completed {len(negotiation_result.rounds)} round(s) of negotiation. "
        f"{'Convergence indicates balanced estimate.' if negotiation_result.converged else 'Non-convergence suggests estimate may be optimistic.'}",
    )
