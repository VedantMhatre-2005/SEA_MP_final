"""
test_api.py - Simple integration test for ASPRAMS API.
Runs against a live server; used in CI pipeline.
"""

import pytest
import httpx

BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_health():
    """GET /health should return status ok."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_root():
    """GET / should return a welcome message."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "message" in response.json()
