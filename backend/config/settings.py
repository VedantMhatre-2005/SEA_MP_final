"""
settings.py - Centralized configuration management.
Loads all secrets and config from .env file using python-dotenv.
"""

import os
from dotenv import load_dotenv

# Load .env file from the project root (two levels up from this file)
load_dotenv()

# ─── Google Gemini ──────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ─── Jira Integration ───────────────────────────────────────────────────────
JIRA_EMAIL: str = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN: str = os.getenv("JIRA_API_TOKEN", "")
JIRA_DOMAIN: str = os.getenv("JIRA_DOMAIN", "")        # e.g. yourcompany.atlassian.net
JIRA_PROJECT_KEY: str = os.getenv("JIRA_PROJECT_KEY", "")  # e.g. PROJ

# ─── App Settings ────────────────────────────────────────────────────────────
MAX_NEGOTIATION_ROUNDS: int = int(os.getenv("MAX_NEGOTIATION_ROUNDS", "5"))
ALLOWED_ORIGINS: list[str] = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")
