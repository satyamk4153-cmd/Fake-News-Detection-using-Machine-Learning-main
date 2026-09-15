"""Test Authentication, Registration, and User Profile."""

import pytest


@pytest.mark.asyncio
async def test_register_and_login_flow(client):
    # 1. Register first user (becomes ADMIN)
    reg_payload = {"email": "admin@truthlens.org", "password": "SecurePassword123!"}
    res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res_reg.status_code == 200
    data_reg = res_reg.json()
    assert data_reg["success"] is True
    assert "access_token" in data_reg["data"]
    token = data_reg["data"]["access_token"]

    # 2. Get profile with token
    res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    me_data = res_me.json()["data"]
    assert me_data["email"] == "admin@truthlens.org"
    assert me_data["role"] == "ADMIN"

    # 3. Duplicate registration is rejected
    res_dup = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res_dup.status_code == 422
    assert res_dup.json()["success"] is False

    # 4. Login with correct password
    res_login = await client.post("/api/v1/auth/login", json=reg_payload)
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()["data"]

    # 5. Login with invalid password fails (401)
    res_bad = await client.post("/api/v1/auth/login", json={"email": "admin@truthlens.org", "password": "WrongPassword!"})
    assert res_bad.status_code == 401
    assert res_bad.json()["success"] is False
