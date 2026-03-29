"""
risk_agent.py - Risk Analysis Agent.

Role: Critically evaluates an optimistic effort estimate by identifying
technical, operational, and delivery risks.  Returns ACCEPT if the estimate
is reasonable, or COUNTER with a risk-adjusted figure.
"""

import json
import logging
import re

import google.generativeai as genai

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from core.schemas import AgentResponse

logger = logging.getLogger(__name__)


def _build_prompt(
    description: str,
    team_size: int,
    duration: int,
    complexity: str,
    current_effort: float,
    round_number: int,
) -> str:
    """Constructs the Gemini prompt for the Risk Analysis Agent."""
    return f"""
You are a skeptical Software Risk Analysis Agent.
Your role is to critically evaluate the proposed effort estimate and identify risks.

Project Details:
- Description: {description}
- Team Size: {team_size} developers
- Planned Duration: {duration} weeks
- Complexity: {complexity}
- Current Effort Estimate (proposed): {current_effort:.1f} person-weeks
- Negotiation Round: {round_number}

Instructions:
1. Identify 2-3 key risks (integration complexity, scope creep, team ramp-up, external dependencies, etc.).
2. Determine if the estimate adequately covers these risks.
3. If the estimate is reasonable (within acceptable risk tolerance), set "decision" to "ACCEPT".
4. If the estimate is too optimistic, set "decision" to "COUNTER" and provide a risk-adjusted "effort".
5. On round 3 or later, be more willing to ACCEPT if the estimates are converging within 15%.

Return ONLY a valid JSON object with exactly these keys:
- "effort": risk-adjusted effort in person-weeks (float). If ACCEPT, use the same value as current.
- "decision": "ACCEPT" or "COUNTER"
- "reason": concise explanation of risks identified and your decision (2-4 sentences)

Respond ONLY with the JSON object. No markdown, no extra text.
Example: {{"effort": 30.0, "decision": "COUNTER", "reason": "..."}}
""".strip()


def run(
    description: str,
    team_size: int,
    duration: int,
    complexity: str,
    current_effort: float,
    round_number: int,
) -> AgentResponse:
    """
    Calls Gemini to risk-adjust an effort estimate.

    Args:
        description: Project description text.
        team_size: Number of developers.
        duration: Planned duration in weeks.
        complexity: One of low / medium / high / critical.
        current_effort: The estimation agent's proposed effort this round.
        round_number: Current negotiation round (1-indexed).

    Returns:
        AgentResponse with effort, decision ("ACCEPT" or "COUNTER"), and reason.
    """
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = _build_prompt(
        description, team_size, duration, complexity, current_effort, round_number
    )

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Strip markdown code fences if present
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)

        data = json.loads(raw_text)
        return AgentResponse(**data)

    except json.JSONDecodeError as exc:
        logger.error("Risk Agent JSON parse error: %s | raw: %s", exc, raw_text)
        # Graceful fallback – apply a 20% risk buffer and counter
        return AgentResponse(
            effort=round(current_effort * 1.20, 1),
            decision="COUNTER",
            reason="Gemini response could not be parsed. Applying 20% risk buffer as fallback.",
        )
    except Exception as exc:
        logger.exception("Risk Agent unexpected error: %s", exc)
        raise
