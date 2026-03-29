"""
estimation_agent.py - Optimistic Estimation Agent.

Role: Given project details, produces an optimistic effort estimate
using Google Gemini API.  Returns structured JSON conforming to AgentResponse.
"""

import json
import logging
import re

import google.generativeai as genai

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from core.schemas import AgentResponse

logger = logging.getLogger(__name__)


def _build_prompt(description: str, team_size: int, duration: int, complexity: str) -> str:
    """Constructs the Gemini prompt for the Estimation Agent."""
    return f"""
You are an optimistic Software Project Estimation Agent.
Your role is to provide an OPTIMISTIC (best-case) effort estimate for the software project below.

Project Details:
- Description: {description}
- Team Size: {team_size} developers
- Planned Duration: {duration} weeks
- Complexity: {complexity}

Instructions:
1. Analyze the project from an optimistic standpoint (assume things go smoothly).
2. Calculate a total effort estimate in **person-weeks**.
3. Return your response as a valid JSON object with exactly these keys:
   - "effort": a positive number (person-weeks, float)
   - "decision": always "COUNTER" for the first estimation (you are proposing, not accepting)
   - "reason": a concise explanation of your estimate (2-3 sentences)

Respond ONLY with the JSON object. No markdown, no explanation outside the JSON.
Example: {{"effort": 24.5, "decision": "COUNTER", "reason": "..."}}
""".strip()


def run(
    description: str,
    team_size: int,
    duration: int,
    complexity: str,
    previous_effort: float | None = None,
) -> AgentResponse:
    """
    Calls Gemini to produce an optimistic effort estimate.

    Args:
        description: Project description text.
        team_size: Number of developers.
        duration: Planned duration in weeks.
        complexity: One of low / medium / high / critical.
        previous_effort: If set, the agent is asked to revise towards this figure.

    Returns:
        AgentResponse with effort, decision, and reason.
    """
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = _build_prompt(description, team_size, duration, complexity)

    # If this is a follow-up round, inject the Risk Agent's counter-offer
    if previous_effort is not None:
        prompt += f"""

NOTE: The Risk Analysis Agent countered with an effort of {previous_effort:.1f} person-weeks.
Re-evaluate your estimate considering the risks raised and provide a revised OPTIMISTIC response.
"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Strip markdown code fences if present
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)

        data = json.loads(raw_text)
        return AgentResponse(**data)

    except json.JSONDecodeError as exc:
        logger.error("Estimation Agent JSON parse error: %s | raw: %s", exc, raw_text)
        # Graceful fallback – return a default estimate
        return AgentResponse(
            effort=float(team_size * duration * 0.6),
            decision="COUNTER",
            reason="Gemini response could not be parsed. Using heuristic fallback estimate.",
        )
    except Exception as exc:
        logger.exception("Estimation Agent unexpected error: %s", exc)
        raise
