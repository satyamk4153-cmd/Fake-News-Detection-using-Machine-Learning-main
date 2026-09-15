"""Test Analysis, Credibility Assessment, and Ownership Isolation."""

import pytest


@pytest.mark.asyncio
async def test_credible_news_analysis(client):
    payload = {
        "headline": "Federal Reserve Holds Benchmark Rates Steady",
        "text": "The Federal Reserve concluded its policy meeting Wednesday by maintaining its benchmark interest rate steady amid moderation in consumer inflation indices, officials reported.",
        "input_type": "article"
    }
    response = await client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]

    # Verify prediction structure
    assert data["prediction"]["label"] in ["LIKELY CREDIBLE", "UNCERTAIN / NEEDS VERIFICATION"]
    assert 0.0 <= data["prediction"]["calibrated_probability"] <= 1.0
    assert data["prediction"]["model_agreement"] in ["High", "Medium", "Low"]

    # Verify claims extraction
    assert len(data["claims"]) > 0
    assert "claim_id" in data["claims"][0]

    # Verify explanation signals
    assert data["explanation"] is not None
    assert "supporting_signals" in data["explanation"]


@pytest.mark.asyncio
async def test_sensational_news_analysis(client):
    payload = {
        "headline": "BOMBSHELL SHOCKING PROOF",
        "text": "SHOCKING BOMBSHELL! Corrupt elites are secretly poisoning water supplies with nanochips to control you! Wake up before this is banned!",
        "input_type": "article"
    }
    response = await client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]

    assert data["prediction"]["label"] == "LIKELY MISLEADING"
    assert data["prediction"]["calibrated_probability"] < 0.35


@pytest.mark.asyncio
async def test_insufficient_input_rejection(client):
    payload = {
        "headline": "Short",
        "text": "Too brief.",
        "input_type": "article"
    }
    response = await client.post("/api/v1/analysis", json=payload)
    assert response.status_code in [400, 422]
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_unsupported_language_rejection(client):
    payload = {
        "headline": "Новый отчет о технологиях",
        "text": "Это совершенно русский текст без английских слов для тестирования детектора языка системы.",
        "input_type": "article"
    }
    response = await client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 400
    res = response.json()
    assert res["success"] is False
    assert res["error"]["code"] == "UNSUPPORTED_LANGUAGE"


@pytest.mark.asyncio
async def test_user_analysis_isolation_and_delete(client):
    # Register user 1
    u1_reg = await client.post("/api/v1/auth/register", json={"email": "u1@test.com", "password": "Password123!"})
    t1 = u1_reg.json()["data"]["access_token"]

    # User 1 creates analysis
    res_a1 = await client.post(
        "/api/v1/analysis",
        json={"headline": "Test Story Title", "text": "According to official reports, scientists confirmed the test data Wednesday.", "input_type": "article"},
        headers={"Authorization": f"Bearer {t1}"}
    )
    a1_id = res_a1.json()["data"]["id"]

    # User 1 can view it
    res_get_u1 = await client.get(f"/api/v1/analysis/{a1_id}", headers={"Authorization": f"Bearer {t1}"})
    assert res_get_u1.status_code == 200

    # Register user 2
    u2_reg = await client.post("/api/v1/auth/register", json={"email": "u2@test.com", "password": "Password123!"})
    t2 = u2_reg.json()["data"]["access_token"]

    # User 2 attempts to view User 1's analysis -> 403 Forbidden
    res_get_u2 = await client.get(f"/api/v1/analysis/{a1_id}", headers={"Authorization": f"Bearer {t2}"})
    assert res_get_u2.status_code == 403

    # User 2 attempts to delete User 1's analysis -> 403 Forbidden
    res_del_u2 = await client.delete(f"/api/v1/analysis/{a1_id}", headers={"Authorization": f"Bearer {t2}"})
    assert res_del_u2.status_code == 403

    # User 1 successfully deletes own analysis
    res_del_u1 = await client.delete(f"/api/v1/analysis/{a1_id}", headers={"Authorization": f"Bearer {t1}"})
    assert res_del_u1.status_code == 200
