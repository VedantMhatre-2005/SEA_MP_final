"""
schemas.py - Pydantic models for request/response validation.
Defines the data contracts for the ASPRAMS API.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional


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
    available_budget: float = Field(
        ..., ge=1000, description="Available budget for the project (INR)", example=1000000.0
    )


class RegisterRequest(BaseModel):
    """Register a new user account."""
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Login with email and password."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class AuthUser(BaseModel):
    """Authenticated user profile returned to frontend."""
    id: str
    name: str
    email: EmailStr


class AuthTokenResponse(BaseModel):
    """JWT token response after successful login."""
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: AuthUser


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


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


class ExplainabilityOutput(BaseModel):
    """Output from the Explainability Agent."""
    executive_summary: str = Field(..., description="High-level summary for stakeholders")
    risk_drivers: list[str] = Field(..., description="Top 3 risk factors identified")
    mitigation_recommendations: list[str] = Field(..., description="Specific mitigation actions")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence [0.0-1.0]")
    negotiation_insight: str = Field(..., description="Insight from agent negotiation")


class BudgetAnalysis(BaseModel):
    """Budget-related analysis."""
    available_budget: float = Field(..., description="User-provided available budget (INR)")
    required_budget: float = Field(..., description="Estimated required budget (INR)")
    budget_variance: float = Field(..., description="Variance as percentage (-1.0 to 1.0)")
    is_affordable: bool = Field(..., description="True if required <= available")
    cost_per_personweek: float = Field(..., description="Average cost per person-week (INR)")


class RiskAssessment(BaseModel):
    """Comprehensive risk assessment with ML scoring."""
    ml_risk_score: float = Field(..., ge=0, le=1, description="ML-computed risk score [0.0-1.0]")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(..., description="Risk category")
    budget_risk: bool = Field(..., description="True if budget is a risk factor")
    explainability: ExplainabilityOutput = Field(..., description="Natural language explanation")
    budget_analysis: BudgetAnalysis = Field(..., description="Budget assessment details")


class NegotiationResult(BaseModel):
    """Full result returned by the negotiation engine."""
    rounds: list[NegotiationRound]
    final_effort: float
    converged: bool  # True if ACCEPT was reached; False if max rounds exceeded
    risk_assessment: Optional[RiskAssessment] = None  # NEW: ML-based risk and explainability (added by endpoint)
    jira_issue_key: Optional[str] = None  # Set if Jira issue was created


class HistoryItem(BaseModel):
    """Stored user simulation record."""
    id: str
    created_at: datetime
    project_input: ProjectInput
    result: NegotiationResult
