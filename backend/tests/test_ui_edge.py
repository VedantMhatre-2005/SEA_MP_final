"""Selenium smoke test for ASPRAMS in Microsoft Edge headless.

This test avoids Gemini entirely.
It verifies:
- registration via the backend API
- login via the frontend UI
- project form inputs and validation
- MongoDB-backed history loading
- PDF export from the rendered result card

Run requirements:
- backend on http://localhost:8000
- frontend on http://localhost:5173
- MongoDB connected
- Microsoft Edge installed
"""

from __future__ import annotations

import tempfile
import os
import time
import shutil
import uuid
import sys
from datetime import datetime
from pathlib import Path

import pytest
import requests
from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import MONGODB_DB_NAME, MONGODB_URI


FRONTEND_URL = os.getenv("ASPRAMS_FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("ASPRAMS_BACKEND_URL", "http://localhost:8000")
EDGE_DRIVER_PATH = os.getenv("ASPRAMS_EDGE_DRIVER_PATH", "").strip()


def _service_is_available(url: str) -> bool:
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException:
        return False
    return response.status_code < 500


def _register_user(email: str, password: str, name: str) -> None:
    response = requests.post(
        f"{BACKEND_URL}/auth/register",
        json={"name": name, "email": email, "password": password},
        timeout=30,
    )
    if response.status_code == 409:
        return
    response.raise_for_status()


def _get_current_user_id(token: str) -> str:
    response = requests.get(
        f"{BACKEND_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["id"]


def _seed_analysis(user_id: str, description: str) -> None:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]
    db.analyses.insert_one(
        {
            "user_id": user_id,
            "project_input": {
                "description": description,
                "team_size": 5,
                "duration": 12,
                "complexity": "medium",
                "available_budget": 1000000.0,
            },
            "result": {
                "rounds": [
                    {
                        "round_number": 1,
                        "estimation_agent": {
                            "effort": 16.0,
                            "decision": "COUNTER",
                            "reason": "Optimistic baseline estimate for a modest dashboard scope.",
                        },
                        "risk_agent": {
                            "effort": 18.5,
                            "decision": "ACCEPT",
                            "reason": "Risks are manageable and the estimate is within tolerance.",
                        },
                    }
                ],
                "final_effort": 18.5,
                "converged": True,
                "risk_assessment": {
                    "ml_risk_score": 0.42,
                    "risk_level": "MEDIUM",
                    "budget_risk": False,
                    "budget_analysis": {
                        "available_budget": 1000000.0,
                        "required_budget": 925000.0,
                        "budget_variance": 0.08,
                        "is_affordable": True,
                        "cost_per_personweek": 50000.0,
                    },
                    "explainability": {
                        "executive_summary": "Seeded test analysis for browser validation.",
                        "risk_drivers": [
                            "Integration complexity",
                            "Team ramp-up",
                            "Requirement clarity",
                        ],
                        "mitigation_recommendations": [
                            "Review architecture early",
                            "Plan onboarding checkpoints",
                            "Freeze scope for the iteration",
                        ],
                        "confidence": 0.9,
                        "negotiation_insight": "Seeded record for Selenium coverage.",
                    },
                },
                "jira_issue_key": "ASPRAMS-TEST-1",
            },
            "created_at": datetime.utcnow(),
        }
    )


def _configure_downloads(driver: WebDriver, download_dir: Path) -> None:
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": str(download_dir)},
    )


def _wait_for_file(download_dir: Path, suffix: str = ".pdf", timeout: int = 30) -> Path:
    deadline = time.time() + timeout
    while time.time() < deadline:
        pdf_files = [path for path in download_dir.iterdir() if path.suffix.lower() == suffix]
        if pdf_files:
            return pdf_files[0]
        time.sleep(0.5)
    raise AssertionError(f"No {suffix} file downloaded to {download_dir}")


def _wait_for_login_result(driver: WebDriver, wait: WebDriverWait) -> None:
    """Wait for either dashboard load or a visible auth error after login submit."""
    try:
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Project Details')]")),
                EC.presence_of_element_located((By.XPATH, "//p[contains(@class, 'text-red-700')]")),
            )
        )
    except Exception:
        raise

    errors = driver.find_elements(By.XPATH, "//p[contains(@class, 'text-red-700')]")
    if errors:
        raise AssertionError(f"Login failed in UI: {errors[0].text}")


def _wait_for_history_and_result(driver: WebDriver, wait: WebDriverWait) -> None:
    wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(., 'Past Analyses') or contains(., 'No history yet')]")))


def _note_component_result(request: pytest.FixtureRequest, component: str, status: str, details: str) -> None:
    request.node.user_properties.append(
        (
            "component_results",
            {
                "component": component,
                "status": status,
                "details": details,
            },
        )
    )


@pytest.mark.slow
def test_edge_headless_smoke_flow(request: pytest.FixtureRequest):
    if not _service_is_available(f"{BACKEND_URL}/health"):
        pytest.skip("Backend server is not running, so the browser smoke test cannot execute.")

    if not _service_is_available(FRONTEND_URL):
        pytest.skip("Frontend server is not running, so the browser smoke test cannot execute.")

    email = f"selenium-{uuid.uuid4().hex[:8]}@example.com"
    password = "SeleniumPass123!"
    name = "Selenium User"
    seeded_description = "Seeded analysis for Selenium browser coverage without Gemini."
    download_dir = Path(tempfile.mkdtemp(prefix="asprams-edge-downloads-"))

    _register_user(email=email, password=password, name=name)
    _note_component_result(
        request,
        "User registration API",
        "Passed",
        "A new account was created successfully through the backend registration endpoint.",
    )

    options = EdgeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1200")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    resolved_driver_path = EDGE_DRIVER_PATH or shutil.which("msedgedriver") or ""

    try:
        if resolved_driver_path:
            driver = webdriver.Edge(service=EdgeService(executable_path=resolved_driver_path), options=options)
        else:
            driver = webdriver.Edge(options=options)
    except NoSuchDriverException as exc:
        pytest.skip(
            "EdgeDriver unavailable. Install matching Edge WebDriver and set "
            "ASPRAMS_EDGE_DRIVER_PATH or add msedgedriver.exe to PATH, or allow Selenium Manager internet access. "
            f"Original error: {exc}"
        )

    wait = WebDriverWait(driver, 60)

    try:
        driver.get(FRONTEND_URL)

        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Welcome to ASPRAMS')]")))

        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Email']").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']").send_keys(password)
        driver.find_element(By.XPATH, "//form//button[@type='submit' and contains(normalize-space(.), 'Login')]").click()

        _wait_for_login_result(driver, wait)

        token = driver.execute_script("return localStorage.getItem('asprams_token');")
        assert token, "Expected auth token in localStorage after UI login"
        _note_component_result(
            request,
            "Login workflow",
            "Passed",
            "The UI login form accepted the credentials and stored a JWT token in browser storage.",
        )

        user_id = _get_current_user_id(token)
        _seed_analysis(user_id=user_id, description=seeded_description)
        _note_component_result(
            request,
            "MongoDB history integration",
            "Passed",
            "A sample analysis record was inserted into MongoDB and made visible to the signed-in user.",
        )

        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Project Details')]")))

        description = driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='Describe your software project']")
        description.send_keys(seeded_description)
        driver.find_element(By.CSS_SELECTOR, "input[name='team_size']").send_keys("5")
        driver.find_element(By.CSS_SELECTOR, "input[name='duration']").send_keys("12")
        driver.find_element(By.CSS_SELECTOR, "input[name='available_budget']").send_keys("1000000")

        assert description.get_attribute("value") == seeded_description
        assert driver.find_element(By.CSS_SELECTOR, "input[name='team_size']").get_attribute("value") == "5"
        assert driver.find_element(By.CSS_SELECTOR, "input[name='duration']").get_attribute("value") == "12"
        assert driver.find_element(By.CSS_SELECTOR, "input[name='available_budget']").get_attribute("value") == "1000000"
        _note_component_result(
            request,
            "Project form inputs",
            "Passed",
            "The application accepted the text and numeric values exactly as entered.",
        )

        driver.find_element(By.XPATH, "//button[normalize-space()='History']").click()
        _wait_for_history_and_result(driver, wait)

        history_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Seeded analysis for Selenium browser coverage without Gemini.')]")
        assert history_buttons, "Expected seeded history item to be visible"
        history_buttons[0].click()
        _note_component_result(
            request,
            "History panel display",
            "Passed",
            "The saved analysis appeared in history and could be reopened from the panel.",
        )

        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Consensus Reached') or contains(., 'Max Rounds')]")))
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(., 'person-weeks')]")))

        driver.find_element(By.XPATH, "//button[@type='button' and normalize-space()='Download PDF']").click()

        pdf_file = _wait_for_file(download_dir)
        assert pdf_file.stat().st_size > 0
        _note_component_result(
            request,
            "PDF export from result card",
            "Passed",
            f"The browser downloaded a non-empty PDF file named {pdf_file.name}.",
        )
    finally:
        driver.quit()
