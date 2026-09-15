"""Test Health Endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_live(client):
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "alive"


@pytest.mark.asyncio
async def test_health_ready(client):
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "ready"
    assert data["data"]["checks"]["database"] == "ok"
