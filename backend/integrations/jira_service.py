"""
jira_service.py - Jira REST API integration.

Creates a Jira issue containing the project details and ASPRAMS simulation
results after every successful /analyze run.

Requires environment variables:
  JIRA_EMAIL        - Atlassian account email
  JIRA_API_TOKEN    - Jira API token (from https://id.atlassian.com/manage-profile/security/api-tokens)
  JIRA_DOMAIN       - e.g. yourcompany.atlassian.net  (no https://)
  JIRA_PROJECT_KEY  - e.g. PROJ
"""

import logging
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

from config.settings import (
    JIRA_API_TOKEN,
    JIRA_DOMAIN,
    JIRA_EMAIL,
    JIRA_PROJECT_KEY,
)

logger = logging.getLogger(__name__)


def _is_configured() -> bool:
    """Returns True only if all required Jira env vars are set."""
    return all([JIRA_EMAIL, JIRA_API_TOKEN, JIRA_DOMAIN, JIRA_PROJECT_KEY])


def create_issue(
    description: str,
    team_size: int,
    duration: int,
    complexity: str,
    final_effort: float,
    reasoning: str,
    converged: bool,
) -> Optional[str]:
    """
    Creates a Jira Story issue with ASPRAMS simulation results.

    Args:
        description: Software project description.
        team_size: Number of developers.
        duration: Planned duration in weeks.
        complexity: Project complexity level.
        final_effort: Final agreed effort in person-weeks.
        reasoning: Risk agent's reasoning from the final round.
        converged: Whether negotiation reached ACCEPT.

    Returns:
        The Jira issue key (e.g. "PROJ-42") if successful, else None.
    """
    if not _is_configured():
        logger.warning(
            "Jira integration skipped: one or more JIRA_* environment variables are not set."
        )
        return None

    url = f"https://{JIRA_DOMAIN}/rest/api/3/issue"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    status_text = "✅ Converged (ACCEPTED)" if converged else "⚠️ Max rounds reached (no consensus)"

    # Jira API v3 uses Atlassian Document Format (ADF) for rich text
    adf_description = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "ASPRAMS Risk Assessment Results"}],
            },
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": f"Simulation Status: {status_text}",
                        "marks": [{"type": "strong"}],
                    }
                ],
            },
            {
                "type": "table",
                "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
                "content": [
                    _jira_table_row("Field", "Value", header=True),
                    _jira_table_row("Project Description", description),
                    _jira_table_row("Team Size", f"{team_size} developers"),
                    _jira_table_row("Duration", f"{duration} weeks"),
                    _jira_table_row("Complexity", complexity.capitalize()),
                    _jira_table_row("Final Effort Estimate", f"{final_effort:.1f} person-weeks"),
                ],
            },
            {
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Risk Agent Reasoning"}],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": reasoning}],
            },
        ],
    }

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"[ASPRAMS] Risk Assessment – {description[:60]}{'...' if len(description) > 60 else ''}",
            "description": adf_description,
            "issuetype": {"name": "Story"},
            "labels": ["asprams", "risk-assessment", "automated"],
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=10)
        response.raise_for_status()
        issue_key = response.json().get("key")
        logger.info("Jira issue created: %s", issue_key)
        return issue_key

    except requests.exceptions.HTTPError as exc:
        logger.error(
            "Jira API HTTP error %s: %s",
            exc.response.status_code,
            exc.response.text[:500],
        )
        return None
    except requests.exceptions.RequestException as exc:
        logger.error("Jira API connection error: %s", exc)
        return None


def _jira_table_row(cell1: str, cell2: str, header: bool = False) -> dict:
    """Helper to build an ADF table row with two cells."""
    cell_type = "tableHeader" if header else "tableCell"
    return {
        "type": "tableRow",
        "content": [
            {
                "type": cell_type,
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": cell1, "marks": [{"type": "strong"}] if header else []}],
                    }
                ],
            },
            {
                "type": cell_type,
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": cell2}],
                    }
                ],
            },
        ],
    }
