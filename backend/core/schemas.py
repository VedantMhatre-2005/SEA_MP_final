"""
schemas.py - Pydantic models for request/response validation.
Defines the data contracts for the ASPRAMS API.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional


# ─── Request Schemas ─────────────────────────────────────────────────────────

class ProjectInput(BaseModel):
    """Input payload for the /analyze endpoint."""
    description: str = Field(
        ...,
        min_length=10,
        description="High-level description of the software project",
        example="Build a real-time inventory management system with multi-warehouse support.",
    )
    team_size: int = Field(
        ..., ge=1, le=100, description="Number of developers in the team", example=5
    )
    duration: int = Field(
        ..., ge=1, le=365, description="Planned duration of the project in weeks", example=12
    )
    complexity: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Subjective complexity level of the project", example="medium"
    )


# ─── Agent / Engine Schemas ───────────────────────────────────────────────────

class AgentResponse(BaseModel):
    """Structured response returned by each agent after Gemini call."""
    effort: float = Field(..., description="Effort estimate in person-weeks")
    decision: Literal["ACCEPT", "COUNTER"] = Field(
        ..., description="Agent's decision on the current estimate"
    )
    reason: str = Field(..., description="Agent's reasoning for its decision")


class NegotiationRound(BaseModel):
    """Represents a single round of agent negotiation."""
    round_number: int
    estimation_agent: AgentResponse
    risk_agent: AgentResponse


class NegotiationResult(BaseModel):
    """Full result returned by the negotiation engine."""
    rounds: list[NegotiationRound]
    final_effort: float
    converged: bool  # True if ACCEPT was reached; False if max rounds exceeded
    jira_issue_key: Optional[str] = None  # Set if Jira issue was created
